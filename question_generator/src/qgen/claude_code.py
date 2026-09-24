"""Generación sin API desde Claude Code: exportar ventanas, responder, importar.

`exportar` deja en una carpeta la instrucción de la familia y el mensaje de cada
ventana pendiente, tal como los recibe Gemini. Claude Code escribe una respuesta
JSON por ventana en `respuestas/`, y `importar` las pasa por las mismas revisiones
que una corrida con Gemini (tipo permitido, literalidad, duplicados, motivos).

Estructura de la carpeta (por defecto `data/claude_code/<código del manual>/`):

    instruccion.md          instrucción de sistema + formato de la respuesta
    ventanas/<nombre>.md    el mensaje de cada ventana pendiente
    respuestas/<nombre>.json  {"preguntas": [...]}, lo escribe Claude Code
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from etl.models.schema import Manual
from sqlalchemy.orm import Session

from qgen.gemini.generate import WindowOutcome
from qgen.pipeline import RunSummary, _manual_title, _resolve_rules, plan_windows, run_from_responses, window_instruction
from qgen.prompts.families import build_window_message
from qgen.prompts.schemas import MAX_PREGUNTAS_POR_VENTANA, WindowResponse

#: Modelo que queda registrado en la corrida: el de la sesión de Claude Code que responde.
MODEL_CLAUDE_CODE = "claude-opus-5-5"
PROVIDER = "claude-code"


def carpeta_por_defecto(manual: Manual) -> Path:
    return Path(os.getenv("DATA_DIR", "./data")) / "claude_code" / manual.code


def nombre_de(key: str) -> str:
    """La clave `nodo:desde-hasta` como nombre de archivo (Windows no admite `:`)."""
    return key.replace(":", "_", 1)


def clave_de(nombre: str) -> str:
    return nombre.replace("_", ":", 1)


@dataclass(frozen=True)
class Exportacion:
    carpeta: Path
    ventanas: int


def exportar(session: Session, *, manual_id: int, carpeta: Path | None = None, limit: int | None = None) -> Exportacion:
    """Escribe la instrucción y las ventanas pendientes. Rehace `ventanas/` (solo quedan
    las pendientes) y nunca toca `respuestas/`."""
    manual = _manual(session, manual_id)
    carpeta = carpeta or carpeta_por_defecto(manual)
    rules, profile = _resolve_rules(manual)
    jobs = plan_windows(session, manual_id=manual_id, limit=limit)

    ventanas = carpeta / "ventanas"
    ventanas.mkdir(parents=True, exist_ok=True)
    (carpeta / "respuestas").mkdir(exist_ok=True)
    for viejo in ventanas.glob("*.md"):
        viejo.unlink()

    titulo = _manual_title(manual)
    (carpeta / "instruccion.md").write_text(
        _instruccion(titulo, manual_id, profile, window_instruction(session, manual, rules, profile)),
        encoding="utf-8",
    )
    for job in jobs:
        mensaje = build_window_message(job.window, manual_title=titulo, breadcrumb=job.node_breadcrumb)
        (ventanas / f"{nombre_de(job.window.key)}.md").write_text(mensaje, encoding="utf-8")
    return Exportacion(carpeta=carpeta, ventanas=len(jobs))


def leer_respuesta(archivo: Path) -> WindowOutcome:
    """La respuesta de una ventana como si viniera de Gemini; si no se puede leer, la
    ventana queda fallida con el motivo (y se retoma en la siguiente importación)."""
    try:
        data = json.loads(archivo.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return WindowOutcome(items=[], error=f"respuesta ilegible: {exc}")
    if not isinstance(data, dict) or not isinstance(data.get("preguntas"), list):
        return WindowOutcome(items=[], error='respuesta ilegible: se esperaba {"preguntas": [...]}')
    return WindowOutcome(items=data["preguntas"])


def importar(
    session: Session,
    *,
    manual_id: int,
    carpeta: Path | None = None,
    model_name: str = MODEL_CLAUDE_CODE,
    progress_cb=None,
) -> RunSummary | None:
    """Importa las respuestas de las ventanas pendientes; None si no hay ninguna."""
    manual = _manual(session, manual_id)
    carpeta = carpeta or carpeta_por_defecto(manual)
    respuestas = {
        clave_de(archivo.stem): leer_respuesta(archivo)
        for archivo in sorted((carpeta / "respuestas").glob("*.json"))
    }
    return run_from_responses(
        session, manual_id=manual_id, respuestas=respuestas,
        model_name=model_name, provider=PROVIDER, progress_cb=progress_cb,
    )


def _manual(session: Session, manual_id: int) -> Manual:
    manual = session.get(Manual, manual_id)
    if manual is None:
        raise ValueError(f"Manual {manual_id} not found")
    return manual


def _instruccion(titulo: str, manual_id: int, profile: str, instruccion_sistema: str) -> str:
    esquema = json.dumps(WindowResponse.model_json_schema(), ensure_ascii=False, indent=2)
    return f"""# Preguntas para «{titulo}» (manual {manual_id}, perfil {profile})

Por cada archivo de `ventanas/`, escribe en `respuestas/` un archivo con el mismo
nombre y extensión `.json` (p. ej. `ventanas/12_0-3.md` → `respuestas/12_0-3.json`).

- Sigue la instrucción de sistema de abajo como si fuera tuya; el contenido del
  archivo de la ventana es el mensaje del usuario.
- La respuesta es solo el objeto JSON `{{"preguntas": [...]}}`, con hasta
  {MAX_PREGUNTAS_POR_VENTANA} preguntas, conforme al esquema del final.
- Luego corre `qgen-claude importar {manual_id}`: aplica las mismas revisiones que
  a Gemini (literalidad, duplicados, tipo permitido) y guarda la corrida.

## Instrucción de sistema

{instruccion_sistema}

## Esquema de la respuesta

```json
{esquema}
```
"""

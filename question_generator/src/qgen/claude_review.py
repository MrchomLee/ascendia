"""Revisión de calidad desde Claude Code: exportar lotes, calificar, importar veredictos.

`exportar_revision` deja la rúbrica y un lote por ventana con su texto y sus
preguntas sin decidir. Claude Code escribe un veredicto por pregunta (aceptar,
rechazar o dudosa) en `veredictos/`, e `importar_revision` los aplica: aceptar
→ `valid`, rechazar → `rejected`, dudosa → `needs_review`. Nunca toca una
pregunta que ya decidió una persona (`valid` o `rejected`).

Dentro de la carpeta de intercambio del manual (ver `qgen.claude_code`):

    revision/instruccion.md          rúbrica + formato del veredicto
    revision/lotes/<nombre>.md       texto de la ventana y sus preguntas
    revision/veredictos/<nombre>.json  {"veredictos": [...]}, lo escribe Claude Code
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from etl.models.schema import Node
from pydantic import BaseModel, Field, ValidationError, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from qgen.claude_code import MODEL_CLAUDE_CODE, _manual, carpeta_por_defecto, nombre_de
from qgen.models.schema import Question
from qgen.pipeline import _chunks_for, _manual_title, _resolve_rules
from qgen.prompts.niveles import DEFINICIONES, Nivel
from qgen.rules.base import DocumentRules
from qgen.windows import Window, build_windows

#: Estados que la revisión puede cambiar: los que ninguna persona ha decidido.
REVISABLES = ("pending", "needs_review")
ESTADO_DE = {"aceptar": "valid", "rechazar": "rejected", "dudosa": "needs_review"}


class Veredicto(BaseModel):
    id: int
    nivel: Nivel
    #: Sin veredicto = solo clasificar (preguntas ya decididas sin nivel).
    veredicto: Literal["aceptar", "rechazar", "dudosa"] | None = None
    calificacion: int | None = Field(default=None, ge=1, le=5)
    motivos: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _coherente(self) -> "Veredicto":
        if self.veredicto is None:
            return self
        if self.calificacion is None:
            raise ValueError(f"pregunta {self.id}: '{self.veredicto}' exige calificación")
        if self.veredicto != "aceptar" and not self.motivos:
            raise ValueError(f"pregunta {self.id}: '{self.veredicto}' exige al menos un motivo")
        if self.veredicto == "aceptar" and self.calificacion < 3:
            raise ValueError(f"pregunta {self.id}: una aceptada lleva calificación 3 o más")
        if self.veredicto == "rechazar" and self.calificacion > 2:
            raise ValueError(f"pregunta {self.id}: una rechazada lleva calificación 2 o menos")
        return self


class LoteRevision(BaseModel):
    veredictos: list[Veredicto]


@dataclass(frozen=True)
class ExportacionRevision:
    carpeta: Path
    lotes: int
    preguntas: int
    solo_clasificar: int = 0


@dataclass
class ResumenRevision:
    aceptadas: int = 0
    rechazadas: int = 0
    dudosas: int = 0
    reclasificadas: int = 0
    solo_clasificadas: int = 0
    omitidas: list[tuple[int, str]] = field(default_factory=list)
    lotes_invalidos: list[tuple[str, str]] = field(default_factory=list)


def exportar_revision(session: Session, *, manual_id: int, carpeta: Path | None = None) -> ExportacionRevision:
    """Escribe la rúbrica y un lote por ventana con las preguntas sin decidir que Claude
    aún no ha revisado. Rehace `lotes/` y nunca toca `veredictos/`."""
    manual = _manual(session, manual_id)
    rules, profile = _resolve_rules(manual)
    revision = (carpeta or carpeta_por_defecto(manual)) / "revision"
    lotes = revision / "lotes"
    lotes.mkdir(parents=True, exist_ok=True)
    (revision / "veredictos").mkdir(exist_ok=True)
    for viejo in lotes.glob("*.md"):
        viejo.unlink()

    (revision / "instruccion.md").write_text(_rubrica(_manual_title(manual), manual_id, profile, rules), encoding="utf-8")

    grupos: dict[str, list[tuple[Question, bool]]] = {}
    for q, solo in _a_revisar(session, manual_id):
        grupos.setdefault(q.window_key or f"{q.node_id}:sin-ventana", []).append((q, solo))
    ventanas: dict[int, dict[str, Window]] = {}
    for key, preguntas in grupos.items():
        node_id = preguntas[0][0].node_id
        if node_id not in ventanas:
            ventanas[node_id] = {w.key: w for w in build_windows(node_id, _chunks_for(session, node_id))}
        node = session.get(Node, node_id)
        (lotes / f"{nombre_de(key)}.md").write_text(
            _lote(key, node.breadcrumb if node else "", ventanas[node_id].get(key), preguntas), encoding="utf-8",
        )
    return ExportacionRevision(
        carpeta=revision,
        lotes=len(grupos),
        preguntas=sum(map(len, grupos.values())),
        solo_clasificar=sum(1 for ps in grupos.values() for _, solo in ps if solo),
    )


def importar_revision(
    session: Session,
    *,
    manual_id: int,
    carpeta: Path | None = None,
    model_name: str = MODEL_CLAUDE_CODE,
) -> ResumenRevision:
    """Aplica los veredictos. Un lote que no se puede leer o validar no aplica nada;
    se omiten (y reportan) los ids ajenos al manual y los que ya decidió una persona."""
    manual = _manual(session, manual_id)
    veredictos = (carpeta or carpeta_por_defecto(manual)) / "revision" / "veredictos"
    resumen = ResumenRevision()
    ahora = datetime.now(timezone.utc)
    for archivo in sorted(veredictos.glob("*.json")):
        try:
            lote = LoteRevision.model_validate_json(archivo.read_text(encoding="utf-8"))
        except (OSError, ValidationError) as exc:
            resumen.lotes_invalidos.append((archivo.stem, _primer_error(exc)))
            continue
        for v in lote.veredictos:
            q = session.get(Question, v.id)
            if q is None or q.manual_id != manual_id:
                resumen.omitidas.append((v.id, "no es de este manual"))
                continue
            revisable = q.validation_status in REVISABLES
            if v.veredicto is not None and revisable:
                if _aplicar(q, v, model_name, ahora):
                    resumen.reclasificadas += 1
                if v.veredicto == "aceptar":
                    resumen.aceptadas += 1
                elif v.veredicto == "rechazar":
                    resumen.rechazadas += 1
                else:
                    resumen.dudosas += 1
                continue
            if q.cognitive_level is None:
                _clasificar(q, v.nivel, model_name, ahora)
                resumen.solo_clasificadas += 1
                if v.veredicto is not None:
                    resumen.omitidas.append((v.id, f"ya decidida ({q.validation_status}): solo se clasificó"))
                continue
            resumen.omitidas.append(
                (v.id, "falta el veredicto" if revisable else f"ya decidida ({q.validation_status})")
            )
    session.commit()
    return resumen


def _a_revisar(session: Session, manual_id: int) -> list[tuple[Question, bool]]:
    """(pregunta, solo_clasificar). Revisión completa: sin decidir y sin revisión previa.
    Solo clasificar: cualquier otra pregunta sin nivel (spec de niveles §8)."""
    salida = []
    for q in session.execute(
        select(Question).where(Question.manual_id == manual_id).order_by(Question.id)
    ).scalars():
        if q.validation_status in REVISABLES and "revision" not in (q.metadata_json or {}):
            salida.append((q, False))
        elif q.cognitive_level is None:
            salida.append((q, True))
    return salida


def _aplicar(q: Question, v: Veredicto, model_name: str, ahora: datetime) -> bool:
    """Aplica el veredicto y el nivel; devuelve si la pregunta se reclasificó. Los motivos
    van en `revision`, aparte de los `motivos` de la revisión automática."""
    meta = dict(q.metadata_json or {})
    reclasificada = q.cognitive_level is not None and q.cognitive_level != v.nivel.value
    if reclasificada:
        meta["nivel_generado"] = q.cognitive_level
    meta["revision"] = {
        "por": model_name, "veredicto": v.veredicto, "calificacion": v.calificacion,
        "motivos": list(v.motivos), "nivel": v.nivel.value, "fecha": ahora.isoformat(),
    }
    q.metadata_json = meta
    q.validation_status = ESTADO_DE[v.veredicto]
    q.validated_at = ahora
    q.cognitive_level = v.nivel.value
    return reclasificada


def _clasificar(q: Question, nivel: Nivel, model_name: str, ahora: datetime) -> None:
    """Solo el nivel: el estado y la fecha de validación de una pregunta decidida no se tocan."""
    q.metadata_json = {
        **(q.metadata_json or {}),
        "clasificacion": {"por": model_name, "nivel": nivel.value, "fecha": ahora.isoformat()},
    }
    q.cognitive_level = nivel.value


def _primer_error(exc: Exception) -> str:
    if isinstance(exc, ValidationError):
        err = exc.errors()[0]
        return f"{err['msg']} en {'.'.join(str(p) for p in err['loc'])}"
    return str(exc)


def _lote(key: str, breadcrumb: str, ventana: Window | None, preguntas: list[tuple[Question, bool]]) -> str:
    if ventana is not None:
        encabezado = f"Ventana: {key} · pp. {ventana.page_start}-{ventana.page_end}"
        texto = f'TEXTO:\n"""\n{ventana.text}\n"""'
    else:
        encabezado = f"Ventana: {key}"
        texto = "TEXTO: (no disponible; juzga con la cita de cada pregunta)"
    partes = [f"# Lote {key}", "", f"Ruta: {breadcrumb}", encabezado, "", texto, ""]
    for q, solo in preguntas:
        partes.append(f"## Pregunta {q.id} · {q.question_type} · nivel declarado: {q.cognitive_level or 'sin nivel'}")
        if solo:
            partes.append("SOLO CLASIFICAR: ya está decidida; escribe solo su id y su nivel.")
        partes.append(q.question_text)
        partes += [f"- [{o.role}] {o.text}" for o in q.options]
        partes += [f"Cita: {q.source_quote}", f"Justificación: {q.justification}"]
        motivos = (q.metadata_json or {}).get("motivos")
        if motivos:
            partes.append(f"Revisión automática: {'; '.join(motivos)}")
        partes.append("")
    return "\n".join(partes)


def _rubrica(titulo: str, manual_id: int, profile: str, rules: DocumentRules) -> str:
    preferentes = "; ".join(rules.preferred_topics) or "(sin lista)"
    evitar = "; ".join(rules.forbidden_topics) or "(sin lista)"
    return f"""# Revisión de preguntas de «{titulo}» (manual {manual_id}, perfil {profile})

Por cada archivo de `lotes/`, escribe en `veredictos/` un archivo con el mismo
nombre y extensión `.json` (p. ej. `lotes/12_0-3.md` → `veredictos/12_0-3.json`).
Luego corre `qgen-claude importar-revision {manual_id}`.

## Tu papel

Eres revisor de un banco de preguntas de opción múltiple para un examen de
admisión de nivel bachillerato. Juzga cada pregunta **solo contra el TEXTO del
lote y esta rúbrica**, como si no la hubieras escrito tú. Cada pregunta trae sus
opciones con su rol: `[correct]` es la que se da por correcta.

## Temas del manual

- Temas preferentes: {preferentes}
- Temas a evitar: {evitar}

## Niveles cognitivos

Clasifica cada pregunta en uno de estos cuatro niveles (campo "nivel"), según lo que
de verdad pide, no según lo que declaró la generación:

{DEFINICIONES}
## Rúbrica

**rechazar** si ocurre cualquiera de estos puntos (anota cuáles en "motivos"):

1. **Sin sentido**: el enunciado es confuso, ambiguo o está mal redactado; no se
   entiende sin tener el libro enfrente (habla de "el texto", "la lectura", "el
   cuadro", "este taller", del orden de los capítulos o de una página); o las
   opciones no responden a lo que se pregunta.
2. **Fuera de tema**: no evalúa el contenido de su sección (la Ruta del lote) ni
   alguno de los temas del manual; trata un tema a evitar; o pregunta un detalle
   anecdótico de un ejemplo que no ilustra ningún concepto de la materia.
3. **Respuesta incorrecta o discutible**: la opción `[correct]` no se sostiene
   con el texto; otra opción también podría defenderse como correcta; o ninguna
   lo es.
4. **No evalúa**: la respuesta se deduce del propio enunciado; la `[correct]` se
   distingue por su forma (la única que repite las palabras del enunciado, la
   única mucho más larga); o los distractores son absurdos.
5. **Repetida en esencia**: pregunta la misma idea que otra pregunta del lote
   que vas a aceptar, con otra redacción. Acepta la mejor y rechaza las demás.
6. **Paráfrasis infiel** (comprensión): la clave no dice lo mismo que el texto.
7. **Conclusión dudosa** (análisis): la clave no es lógicamente innegable a partir de los datos citados.
8. **Caso sin solución en el texto** (aplicación): el caso no se resuelve con la regla citada.

Si el nivel que declaró la generación no es el que la pregunta pide de verdad, **no la
rechaces por eso**: escribe el nivel correcto y juzga la pregunta en ese nivel.

**dudosa** (queda "a revisar" para una persona) solo si no puedes decidir con el
texto del lote; por ejemplo, porque depende de lo que dicen otras secciones.

**aceptar** si no ocurre ninguno de los puntos anteriores. Un defecto menor (un
distractor débil, una redacción mejorable) no la rechaza: bájale la calificación
y anótalo en "motivos".

## Calificación (1 a 5)

5 excelente · 4 buena · 3 aceptable con defectos menores · 2 defectuosa ·
1 inservible. Una aceptada lleva 3 o más; una rechazada, 2 o menos.

## Formato del veredicto

Un veredicto por cada pregunta del lote, con su id:

```json
{{"veredictos": [
  {{"id": 123, "nivel": "conocimiento", "veredicto": "aceptar", "calificacion": 5, "motivos": []}},
  {{"id": 124, "nivel": "analisis", "veredicto": "rechazar", "calificacion": 1, "motivos": ["fuera de tema: pregunta un detalle del ejemplo"]}},
  {{"id": 125, "nivel": "comprension", "veredicto": "dudosa", "calificacion": 3, "motivos": ["depende de otra sección"]}}
]}}
```

Cada veredicto lleva su "nivel" (obligatorio). Las preguntas marcadas **SOLO
CLASIFICAR** ya están decididas: escribe solo `{{"id": 123, "nivel": "aplicacion"}}`,
sin veredicto ni calificación, y su estado no cambia (solo clasificar).

"motivos" es obligatorio (al menos uno) en "rechazar" y "dudosa". Empieza cada
motivo con su criterio: "sin sentido: …", "fuera de tema: …", "respuesta
discutible: …", "no evalúa: …", "repetida con <id>".
"""

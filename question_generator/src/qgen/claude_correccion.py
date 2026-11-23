"""Corrección de preguntas ya generadas desde Claude Code, con las observaciones del usuario.

A diferencia de la revisión (`qgen.claude_review`), que solo acepta o rechaza, la corrección
reescribe: Claude Code lee cada pregunta contra el texto de su ventana, las reglas de redacción
(`prompts.redaccion_militar`) y los ejemplos que corrigió el usuario (pregunta original,
observación y versión corregida), y decide por cada una:

    sin_cambios  la pregunta ya cumple las reglas
    corregir     enunciado, opciones y, si hace falta, nivel nuevos (con los motivos)
    descartar    no tiene arreglo (sin sentido, respuesta discutible…) → `rejected`

`importar_correccion` aplica las decisiones y guarda la versión anterior en
`metadata_json["original"]` (solo la primera vez, para no perder la generada) y la decisión en
`metadata_json["correccion"]`. Nunca toca una pregunta que ya decidió una persona (`valid` o
`rejected`) ni una que ya se corrigió, salvo con `rehacer=True`.

Dentro de la carpeta de intercambio del manual (ver `qgen.claude_code`):

    correccion/instruccion.md            reglas + ejemplos + formato de la respuesta
    correccion/lotes/<nombre>.md         texto de la ventana y sus preguntas
    correccion/decisiones/<nombre>.json  {"decisiones": [...]}, lo escribe Claude Code
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from etl.models.schema import Node
from pydantic import BaseModel, Field, ValidationError, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from qgen.claude_code import MODEL_CLAUDE_CODE, _manual, carpeta_por_defecto, nombre_de
from qgen.claude_review import REVISABLES, _primer_error
from qgen.models.schema import Question
from qgen.pipeline import _chunks_for, _manual_title, _resolve_rules
from qgen.prompts.families import _conforme
from qgen.prompts.niveles import DEFINICIONES, NIVEL_LABEL, Nivel
from qgen.prompts.redaccion_militar import reglas_redaccion
from qgen.prompts.schemas import OptionRole, WindowOption, WindowQuestion
from qgen.validation.checks import review
from qgen.windows import Window, build_windows


class OpcionesCorregidas(BaseModel):
    correct: str = Field(min_length=1, max_length=500)
    confusa: str = Field(min_length=1, max_length=500)
    distractores: list[str] = Field(min_length=2, max_length=2)

    @model_validator(mode="after")
    def _distintas(self) -> "OpcionesCorregidas":
        textos = [" ".join(t.split()).casefold() for t in (self.correct, self.confusa, *self.distractores)]
        if len(set(textos)) != 4:
            raise ValueError("opciones con el mismo texto")
        return self


class Decision(BaseModel):
    id: int
    accion: Literal["sin_cambios", "corregir", "descartar"]
    nivel: Nivel | None = None
    pregunta: str | None = Field(default=None, max_length=1000)
    opciones: OpcionesCorregidas | None = None
    motivos: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _coherente(self) -> "Decision":
        if self.accion == "corregir":
            if not self.pregunta and self.opciones is None and self.nivel is None:
                raise ValueError(f"pregunta {self.id}: 'corregir' sin enunciado, opciones ni nivel nuevos")
            if not self.motivos:
                raise ValueError(f"pregunta {self.id}: 'corregir' exige al menos un motivo")
        if self.accion == "descartar" and not self.motivos:
            raise ValueError(f"pregunta {self.id}: 'descartar' exige al menos un motivo")
        return self


class LoteCorreccion(BaseModel):
    decisiones: list[Decision]


@dataclass(frozen=True)
class ExportacionCorreccion:
    carpeta: Path
    lotes: int
    preguntas: int
    ejemplos: int


@dataclass
class ResumenCorreccion:
    sin_cambios: int = 0
    corregidas: int = 0
    descartadas: int = 0
    reclasificadas: int = 0
    avisos: list[tuple[int, str]] = field(default_factory=list)
    omitidas: list[tuple[int, str]] = field(default_factory=list)
    lotes_invalidos: list[tuple[str, str]] = field(default_factory=list)


def cargar_ejemplos(archivo: Path | None) -> list[dict[str, Any]]:
    """Ejemplos del usuario: [{"nivel", "articulo", "antes": {"pregunta", "opciones"},
    "observacion_pregunta", "observacion_opciones", "despues": {"pregunta", "opciones"}}]."""
    if archivo is None:
        return []
    datos = json.loads(Path(archivo).read_text(encoding="utf-8"))
    return datos["ejemplos"] if isinstance(datos, dict) else datos


def exportar_correccion(
    session: Session,
    *,
    manual_id: int,
    carpeta: Path | None = None,
    ejemplos: list[dict[str, Any]] | None = None,
    run_id: int | None = None,
    rehacer: bool = False,
) -> ExportacionCorreccion:
    """Escribe la instrucción y un lote por ventana con las preguntas por corregir.
    Rehace `lotes/` y nunca toca `decisiones/`."""
    manual = _manual(session, manual_id)
    titulo = _manual_title(manual)
    base = (carpeta or carpeta_por_defecto(manual)) / "correccion"
    lotes = base / "lotes"
    lotes.mkdir(parents=True, exist_ok=True)
    (base / "decisiones").mkdir(exist_ok=True)
    for viejo in lotes.glob("*.md"):
        viejo.unlink()
    ejemplos = ejemplos or []
    (base / "instruccion.md").write_text(_instruccion(titulo, manual_id, ejemplos), encoding="utf-8")

    grupos: dict[str, list[Question]] = {}
    for q in _a_corregir(session, manual_id, run_id=run_id, rehacer=rehacer):
        grupos.setdefault(q.window_key or f"{q.node_id}:sin-ventana", []).append(q)
    ventanas: dict[int, dict[str, Window]] = {}
    for key, preguntas in grupos.items():
        node_id = preguntas[0].node_id
        if node_id not in ventanas:
            ventanas[node_id] = {w.key: w for w in build_windows(node_id, _chunks_for(session, node_id))}
        node = session.get(Node, node_id)
        (lotes / f"{nombre_de(key)}.md").write_text(
            _lote(key, node.breadcrumb if node else "", ventanas[node_id].get(key), preguntas), encoding="utf-8",
        )
    return ExportacionCorreccion(
        carpeta=base, lotes=len(grupos), preguntas=sum(map(len, grupos.values())), ejemplos=len(ejemplos),
    )


def importar_correccion(
    session: Session,
    *,
    manual_id: int,
    carpeta: Path | None = None,
    model_name: str = MODEL_CLAUDE_CODE,
    rehacer: bool = False,
) -> ResumenCorreccion:
    """Aplica las decisiones de `correccion/decisiones/`. Un lote que no se puede leer o validar
    no aplica nada; se omiten (y reportan) los ids ajenos al manual y los ya decididos."""
    manual = _manual(session, manual_id)
    decisiones = (carpeta or carpeta_por_defecto(manual)) / "correccion" / "decisiones"
    resumen = ResumenCorreccion()
    ahora = datetime.now(timezone.utc)
    for archivo in sorted(decisiones.glob("*.json")):
        try:
            lote = LoteCorreccion.model_validate_json(archivo.read_text(encoding="utf-8"))
        except (OSError, ValidationError) as exc:
            resumen.lotes_invalidos.append((archivo.stem, _primer_error(exc)))
            continue
        for d in lote.decisiones:
            q = session.get(Question, d.id)
            if q is None or q.manual_id != manual_id:
                resumen.omitidas.append((d.id, "no es de este manual"))
                continue
            if q.validation_status not in REVISABLES:
                resumen.omitidas.append((d.id, f"ya decidida ({q.validation_status})"))
                continue
            if "correccion" in (q.metadata_json or {}) and not rehacer:
                resumen.omitidas.append((d.id, "ya corregida"))
                continue
            aplicar_decision(session, q, d, por=model_name, ahora=ahora, resumen=resumen)
    session.commit()
    return resumen


def aplicar_decision(
    session: Session, q: Question, d: Decision, *, por: str, ahora: datetime, resumen: ResumenCorreccion,
) -> None:
    """Aplica una decisión a una pregunta (la usa también la carga de las correcciones del usuario)."""
    meta = dict(q.metadata_json or {})
    if "original" not in meta:
        meta["original"] = {
            "pregunta": q.question_text, "nivel": q.cognitive_level,
            "opciones": [{"rol": o.role, "texto": o.text} for o in q.options],
        }
    meta["correccion"] = {"por": por, "accion": d.accion, "motivos": list(d.motivos), "fecha": ahora.isoformat()}
    if d.accion == "sin_cambios":
        resumen.sin_cambios += 1
    elif d.accion == "descartar":
        q.validation_status = "rejected"
        q.validated_at = ahora
        resumen.descartadas += 1
    else:
        if d.pregunta:
            q.question_text = d.pregunta.strip()
        if d.opciones is not None:
            _reemplazar_opciones(q, d.opciones)
        if d.nivel is not None and q.question_type == "teoria" and d.nivel.value != q.cognitive_level:
            meta.setdefault("nivel_generado", q.cognitive_level)
            q.cognitive_level = d.nivel.value
            resumen.reclasificadas += 1
        avisos = _avisos(session, q)
        if avisos:
            meta["correccion"]["avisos"] = avisos
            resumen.avisos += [(q.id, a) for a in avisos]
        resumen.corregidas += 1
    q.metadata_json = meta


def _reemplazar_opciones(q: Question, nuevas: OpcionesCorregidas) -> None:
    """Cambia el texto de las opciones conservando sus filas (y su orden barajado)."""
    textos = {OptionRole.CORRECT.value: [nuevas.correct], OptionRole.CONFUSA.value: [nuevas.confusa],
              OptionRole.DISTRACTOR.value: list(nuevas.distractores)}
    for o in sorted(q.options, key=lambda o: o.order_in_question):
        pendientes = textos.get(o.role)
        if not pendientes:
            raise ValueError(f"pregunta {q.id}: rol de opción inesperado {o.role!r}")
        o.text = pendientes.pop(0).strip()


def _avisos(session: Session, q: Question) -> list[str]:
    """Las revisiones automáticas de qgen sobre la versión corregida (literalidad de la clave y
    de la cita, caso no inventado): no bloquean, quedan anotadas para quien revise."""
    try:
        wq = WindowQuestion(
            tipo=q.question_type, nivel=q.cognitive_level, pregunta=q.question_text,
            opciones=[WindowOption(rol=o.role, texto=o.text) for o in q.options],
            cita=q.source_quote or "-", justificacion=q.justification or "-",
        )
    except ValidationError as exc:
        return [f"estructura: {_primer_error(exc)}"]
    texto = "\n\n".join(c.text for c in _chunks_for(session, q.node_id))
    return list(review(wq, texto).motivos)


def _a_corregir(session: Session, manual_id: int, *, run_id: int | None, rehacer: bool) -> list[Question]:
    stmt = select(Question).where(Question.manual_id == manual_id).order_by(Question.id)
    if run_id is not None:
        stmt = stmt.where(Question.run_id == run_id)
    return [
        q for q in session.execute(stmt).scalars()
        if q.validation_status in REVISABLES and (rehacer or "correccion" not in (q.metadata_json or {}))
    ]


def _lote(key: str, breadcrumb: str, ventana: Window | None, preguntas: list[Question]) -> str:
    if ventana is not None:
        encabezado = f"Ventana: {key} · pp. {ventana.page_start}-{ventana.page_end}"
        texto = f'TEXTO:\n"""\n{ventana.text}\n"""'
    else:
        encabezado = f"Ventana: {key}"
        texto = "TEXTO: (no disponible; juzga con la cita de cada pregunta)"
    partes = [f"# Lote {key}", "", f"Ruta: {breadcrumb}", encabezado, "", texto, ""]
    for q in preguntas:
        ref = (q.metadata_json or {}).get("referencia") or "sin referencia"
        partes.append(f"## Pregunta {q.id} · nivel: {q.cognitive_level or 'sin nivel'} · {ref}")
        partes.append(q.question_text)
        for rol in (OptionRole.CORRECT.value, OptionRole.CONFUSA.value, OptionRole.DISTRACTOR.value):
            partes += [f"- [{o.role}] {o.text}" for o in q.options if o.role == rol]
        partes += [f"Cita: {' '.join((q.source_quote or '').split())}", ""]
    return "\n".join(partes)


def _ejemplo(i: int, ej: dict[str, Any]) -> str:
    def bloque(version: dict[str, Any]) -> list[str]:
        lineas = [f'  Pregunta: "{version.get("pregunta", "")}"']
        lineas += [f'  - {"[correct] " if j == 0 else ""}{t}' for j, t in enumerate(version.get("opciones") or [])]
        return lineas

    nivel = NIVEL_LABEL.get(ej.get("nivel") or "", ej.get("nivel") or "")
    partes = [f"### Ejemplo {i} · {nivel} · {ej.get('articulo', '')}", "ANTES:"] + bloque(ej["antes"])
    if ej.get("observacion_pregunta"):
        partes.append(f"OBSERVACIÓN AL ENUNCIADO: {ej['observacion_pregunta']}")
    if ej.get("observacion_opciones"):
        partes.append(f"OBSERVACIÓN A LAS OPCIONES: {ej['observacion_opciones']}")
    partes += ["DESPUÉS:"] + bloque(ej["despues"])
    return "\n".join(partes)


def _instruccion(titulo: str, manual_id: int, ejemplos: list[dict[str, Any]]) -> str:
    conforme = _conforme(titulo)
    bloque_ejemplos = "\n\n".join(_ejemplo(i, ej) for i, ej in enumerate(ejemplos, start=1)) or "(sin ejemplos)"
    return f"""# Corrección de preguntas de «{titulo}» (manual {manual_id})

Por cada archivo de `lotes/`, escribe en `decisiones/` un archivo con el mismo nombre y
extensión `.json` (p. ej. `lotes/1066_0-2.md` → `decisiones/1066_0-2.json`). Luego corre
`qgen-claude importar-correccion {manual_id}`.

## Tu papel

Eres el revisor de un banco de preguntas de opción múltiple para exámenes de promoción
militar. El usuario ya revisó una muestra y dejó **observaciones y versiones corregidas**
(abajo, en EJEMPLOS). Tu trabajo es revisar **todas y cada una** de las preguntas del lote
tomando como referencia esas observaciones y las REGLAS que se desprenden de ellas, y
corregir lo que no las cumpla. Juzga cada pregunta solo contra el TEXTO del lote: no uses
información de fuera.

Para cada pregunta, en este orden:

1. Lee el artículo o fracción de su "Cita" en el TEXTO y verifica que la clave `[correct]` es
   correcta y está completa, y que ninguna otra opción también lo es.
2. Revisa el enunciado contra las reglas 1–11 y las opciones contra las reglas 12–18.
3. Compara con los EJEMPLOS: si la pregunta tiene un defecto como los que el usuario
   observó, corrígelo como él lo hizo.
4. Decide: `sin_cambios`, `corregir` o `descartar`.

Al corregir:

- Reescribe lo necesario y nada más, pero si cambias el enunciado o la clave, revisa que las
  cuatro opciones sigan concordando con él (regla 14) y reescríbelas si no.
- Devuelve **las cuatro opciones completas** cada vez que cambies alguna: `correct`,
  `confusa` (el distractor más cercano a la clave) y dos `distractores`.
- La clave de "conocimiento" sigue siendo el texto literal del artículo; solo puedes pasar a
  infinitivo el verbo con que empieza, poner mayúscula inicial y punto final.
- La clave no debe ser la opción más larga; mantén las cuatro de extensión parecida.
- No preguntes ni menciones penas, cantidades de prisión o multas (el temario pide el
  Código «sin penas»); el efecto jurídico se nombra sin cifras ("para que se le reduzca la pena").
- Si el nivel declarado no corresponde a lo que la pregunta pide de verdad, o la regla 11
  obliga a subirla, escribe el nivel correcto en "nivel".
- Descarta solo lo que no tiene arreglo: no se sostiene con el texto, tiene dos respuestas
  defendibles que no puedes separar, o repite la idea de otra pregunta del lote (conserva la
  mejor).

## Reglas de redacción (de las observaciones del usuario)

{reglas_redaccion(conforme)}
## Niveles cognitivos

{DEFINICIONES}
## Ejemplos del usuario (antes → observación → después)

La primera opción de cada versión es la clave.

{bloque_ejemplos}

## Formato de la respuesta

Una decisión por cada pregunta del lote, con su id:

```json
{{"decisiones": [
  {{"id": 101, "accion": "sin_cambios"}},
  {{"id": 102, "accion": "corregir", "nivel": "conocimiento",
    "pregunta": "{conforme}, ¿con qué finalidad se comete el delito de … al …?",
    "opciones": {{"correct": "…", "confusa": "…", "distractores": ["…", "…"]}},
    "motivos": ["regla 3: verbo de obligación en el enunciado", "regla 12: opciones sin punto final"]}},
  {{"id": 103, "accion": "descartar", "motivos": ["repite la idea de la 101"]}}
]}}
```

- "motivos" es obligatorio en `corregir` y `descartar`: empieza cada uno con la regla que se
  incumplía ("regla 6: …") o con "respuesta incorrecta: …", "repetida con <id>".
- En `corregir`, omite "pregunta" u "opciones" si no cambian; "nivel" solo si cambia.
"""

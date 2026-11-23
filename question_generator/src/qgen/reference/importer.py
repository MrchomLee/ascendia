"""Importador de preguntas de referencia (banco de ejemplos/exemplars).

Lee archivos JSON, JSONL o CSV de preguntas de muestra y los persiste
en la tabla `reference_questions` para utilizarlos en los prompts.
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from qgen.models.reference_schema import ReferenceOption, ReferenceQuestion
from qgen.prompts.niveles import Nivel


class OptionExemplarInput(BaseModel):
    """Modelo Pydantic para validar una opción de respuesta de ejemplo."""

    text: str
    role: str = "distractor"  # correct, confusa, distractor
    is_correct: bool = False


class QuestionExemplarInput(BaseModel):
    """Modelo Pydantic para validar una pregunta de ejemplo completa."""

    question_text: str = Field(alias="question")
    profile: str = "global"
    manual_code: str | None = None
    topic: str | None = None
    justification: str | None = None
    source_tag: str | None = None
    nivel: str | None = None
    options: list[OptionExemplarInput] = Field(default_factory=list)

    @field_validator("nivel")
    @classmethod
    def _nivel_conocido(cls, value: str | None) -> str | None:
        if value is not None and value not in {n.value for n in Nivel}:
            raise ValueError(f"nivel {value!r} desconocido")
        return value


def import_reference_questions(
    session: Session,
    data: list[dict[str, Any]],
    default_profile: str = "global",
    default_source_tag: str | None = None,
) -> list[ReferenceQuestion]:
    """Valida y persiste una lista de preguntas de ejemplo en la BD.

    Args:
        session: Sesión activa de SQLAlchemy.
        data: Lista de diccionarios con la estructura de preguntas.
        default_profile: Perfil por defecto si no viene especificado en la pregunta.
        default_source_tag: Etiqueta de fuente por defecto para auditoría.

    Returns:
        Lista de objetos `ReferenceQuestion` creados.
    """
    created_questions: list[ReferenceQuestion] = []

    for item in data:
        # Permitir la clave 'question_text' o 'question'
        if "question_text" in item and "question" not in item:
            item["question"] = item["question_text"]

        input_obj = QuestionExemplarInput.model_validate(item)

        profile_val = input_obj.profile if input_obj.profile != "global" else default_profile
        source_tag_val = input_obj.source_tag or default_source_tag

        ref_q = ReferenceQuestion(
            profile=profile_val,
            manual_code=input_obj.manual_code,
            topic=input_obj.topic,
            source_tag=source_tag_val,
            cognitive_level=input_obj.nivel,
            question_text=input_obj.question_text,
            justification=input_obj.justification,
        )
        session.add(ref_q)
        session.flush()

        for i, opt in enumerate(input_obj.options, start=1):
            is_corr = opt.is_correct or opt.role.lower() == "correct"
            ref_opt = ReferenceOption(
                question_id=ref_q.id,
                role=opt.role.lower(),
                order_in_question=i,
                text=opt.text,
                is_correct=is_corr,
            )
            session.add(ref_opt)

        created_questions.append(ref_q)

    session.commit()
    return created_questions


def load_reference_file(file_path: str | Path) -> list[dict[str, Any]]:
    """Carga datos de preguntas desde un archivo JSON, JSONL o CSV."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {file_path}")

    suffix = path.suffix.lower()

    if suffix == ".json":
        with open(path, "r", encoding="utf-8") as f:
            content = json.load(f)
            if isinstance(content, list):
                return content
            elif isinstance(content, dict) and "questions" in content:
                return content["questions"]
            else:
                return [content]

    elif suffix == ".jsonl":
        items = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if line_str:
                    items.append(json.loads(line_str))
        return items

    elif suffix == ".csv":
        items = []
        with open(path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                opts = []
                for role_key in ["correct", "confusa", "distractor1", "distractor2"]:
                    if role_key in row and row[role_key]:
                        role_name = "correct" if role_key == "correct" else ("confusa" if role_key == "confusa" else "distractor")
                        opts.append({"text": row[role_key], "role": role_name})
                items.append({
                    "question": row.get("question") or row.get("question_text", ""),
                    "profile": row.get("profile", "global"),
                    "manual_code": row.get("manual_code"),
                    "topic": row.get("topic"),
                    "justification": row.get("justification"),
                    "options": opts,
                })
        return items

    elif suffix == ".xlsx":
        return _load_xlsx(path)

    else:
        raise ValueError(f"Formato no soportado: {suffix}. Use .json, .jsonl, .csv o .xlsx")


_ROLES_XLSX = ("correct", "confusa", "distractor", "distractor")
_PREFIJOS = ("de acuerdo con la información del texto,", "según el texto,", "a partir del texto,")
_CITA = re.compile(r"\s*\[cite:[^\]]*\]")
_SEGUN_AL_FINAL = re.compile(r",\s*según el texto(?=\s*\?)", re.IGNORECASE)
_EN_EL_TEXTO = re.compile(r"\s+en el texto(?=[\s,.;:?])", re.IGNORECASE)


def _sin_acentos(texto: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn"
    ).casefold().strip()


def limpiar_ejemplo(texto: str) -> str:
    """Quita las marcas `[cite: …]` y las referencias al texto ("Según el texto, …"):
    los enunciados van directos (spec de niveles §6)."""
    limpio = _CITA.sub("", texto).strip()
    for prefijo in _PREFIJOS:
        if limpio.casefold().startswith(prefijo):
            limpio = limpio[len(prefijo):].lstrip()
            break
    limpio = _SEGUN_AL_FINAL.sub("", limpio)
    limpio = _EN_EL_TEXTO.sub("", limpio)  # "…mencionadas en el texto respecto a…"
    if limpio.startswith("¿") and len(limpio) > 1:
        return "¿" + limpio[1].upper() + limpio[2:]
    return limpio[:1].upper() + limpio[1:]


def _load_xlsx(path: Path) -> list[dict[str, Any]]:
    """Una hoja por nivel (el nombre de la hoja es el nivel); encabezado con "Pregunta" y,
    a su derecha, correcta, similar (confusa) e incorrecta ×2 (distractores)."""
    import openpyxl

    niveles = {n.value: n.value for n in Nivel}
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    items: list[dict[str, Any]] = []
    for ws in wb.worksheets:
        nivel = niveles.get(_sin_acentos(ws.title))
        if nivel is None:
            raise ValueError(f"Hoja «{ws.title}»: su nombre no es un nivel ({', '.join(n.value for n in Nivel)})")
        col: int | None = None
        for fila, row in enumerate(ws.iter_rows(values_only=True), start=1):
            celdas = ["" if c is None else str(c).strip() for c in row]
            if col is None:
                if "Pregunta" in celdas:
                    col = celdas.index("Pregunta")
                continue
            pregunta, *respuestas = (celdas[col:col + 5] + [""] * 5)[:5]
            if not pregunta:
                continue
            if sum(1 for r in respuestas if r) < 4:
                raise ValueError(f"Hoja «{ws.title}», fila {fila}: se esperaban 4 respuestas")
            items.append({
                "question": limpiar_ejemplo(pregunta),
                "nivel": nivel,
                "options": [{"text": limpiar_ejemplo(t), "role": r} for t, r in zip(respuestas, _ROLES_XLSX)],
            })
    return items

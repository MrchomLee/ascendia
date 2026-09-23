"""Structured-output schemas for Gemini/Ollama."""

from __future__ import annotations

from collections import Counter
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class OptionRole(StrEnum):
    CORRECT = "correct"
    CONFUSA = "confusa"
    DISTRACTOR = "distractor"


REQUIRED_ROLE_COUNTS: dict[str, int] = {
    OptionRole.CORRECT.value: 1,
    OptionRole.CONFUSA.value: 1,
    OptionRole.DISTRACTOR.value: 2,
}


class GeneratedOption(BaseModel):
    role: OptionRole
    text: str = Field(min_length=1, max_length=500)


class GeneratedQuestion(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    options: list[GeneratedOption] = Field(min_length=4, max_length=4)
    justification: str = Field(min_length=1, max_length=2000)

    @model_validator(mode="after")
    def _check_role_counts(self) -> "GeneratedQuestion":
        counts = Counter(o.role.value for o in self.options)
        for role, expected in REQUIRED_ROLE_COUNTS.items():
            actual = counts.get(role, 0)
            if actual != expected:
                raise ValueError(
                    f"Role mismatch for {role!r}: expected {expected}, got {actual}. "
                    f"Counts: {dict(counts)}"
                )
        # Reject duplicate option texts (case-insensitive)
        texts = [o.text.strip().lower() for o in self.options]
        if len(set(texts)) != len(texts):
            raise ValueError("Duplicate option texts in the same question")
        return self


# ─── Llamada por ventana (spec §6) ─────────────────────────────────────────

MAX_PREGUNTAS_POR_VENTANA = 30
LETRAS = ("A", "B", "C", "D")


class QuestionType(StrEnum):
    TEORIA = "teoria"
    EJERCICIO_LIBRO = "ejercicio_libro"
    EJERCICIO_NUEVO = "ejercicio_nuevo"


class WindowOption(BaseModel):
    rol: OptionRole
    texto: str = Field(min_length=1, max_length=500)


class WindowQuestion(BaseModel):
    """Una pregunta completa tal como la devuelve la llamada por ventana."""

    tipo: QuestionType
    pregunta: str = Field(min_length=1, max_length=1000)
    opciones: list[WindowOption] = Field(min_length=4, max_length=4)
    cita: str = Field(min_length=1, max_length=2000)
    justificacion: str = Field(min_length=1, max_length=2000)

    @model_validator(mode="after")
    def _check(self) -> "WindowQuestion":
        counts = Counter(o.rol.value for o in self.opciones)
        for role, expected in REQUIRED_ROLE_COUNTS.items():
            if counts.get(role, 0) != expected:
                raise ValueError(f"reparto de roles inválido: {dict(counts)}")
        textos = [" ".join(o.texto.split()).lower() for o in self.opciones]
        if len(set(textos)) != len(textos):
            raise ValueError("opciones con el mismo texto")
        if not self.cita.strip():
            raise ValueError("cita vacía")
        return self


class WindowResponse(BaseModel):
    preguntas: list[WindowQuestion]


class VerificationResult(BaseModel):
    """Lo que devuelve la verificación de un ejercicio nuevo (spec §7)."""

    razonamiento: str = Field(min_length=1, max_length=3000)
    opcion: Literal["A", "B", "C", "D", "ninguna", "varias"]
    dificultad: Literal["menor", "igual", "mayor"]

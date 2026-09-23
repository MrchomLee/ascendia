"""Revisiones de cada pregunta generada por ventana (spec §7).

Todo es determinista y sin llamadas a Gemini: la verificación de los ejercicios
nuevos la hace el pipeline; aquí solo se traduce su resultado a motivos.
"""

from __future__ import annotations

import difflib
import hashlib
import random
import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable

from pydantic import ValidationError

from qgen.prompts.schemas import (
    LETRAS,
    MAX_PREGUNTAS_POR_VENTANA,
    GeneratedOption,
    GeneratedQuestion,
    OptionRole,
    QuestionType,
    VerificationResult,
    WindowOption,
    WindowQuestion,
)

SIMILITUD_DUPLICADO = 0.90

_SIGNOS = str.maketrans({
    "“": '"', "”": '"', "«": '"', "»": '"', "‘": "'", "’": "'", "′": "'",
    "–": "-", "—": "-", "−": "-",
})


def norm_text(text: str) -> str:
    """Para comparar texto literal: NFC, espacios colapsados, comillas y guiones unificados, sin mayúsculas."""
    text = unicodedata.normalize("NFC", text).translate(_SIGNOS)
    return " ".join(text.split()).casefold()


def norm_math(text: str) -> str:
    """Como `norm_text`, pero además iguala la notación: 𝑥² y x^2 quedan como x2 (así llegan los PDF de Word)."""
    text = unicodedata.normalize("NFKC", text).translate(_SIGNOS)
    return re.sub(r"[\s^·*×]", "", text).casefold()


@dataclass(frozen=True)
class Verdict:
    status: str  # "pending" | "needs_review"
    motivos: tuple[str, ...] = ()

    @classmethod
    def from_motivos(cls, motivos: Iterable[str]) -> "Verdict":
        motivos = tuple(motivos)
        return cls("needs_review" if motivos else "pending", motivos)

    def with_motivos(self, extra: Iterable[str]) -> "Verdict":
        return Verdict.from_motivos(self.motivos + tuple(extra))


def parse_items(items: list) -> tuple[list[WindowQuestion], list[str]]:
    """Valida cada pregunta por separado: una mala no tumba a las demás."""
    preguntas: list[WindowQuestion] = []
    descartes: list[str] = []
    for i, item in enumerate(items, start=1):
        if i > MAX_PREGUNTAS_POR_VENTANA:
            descartes.append(f"pregunta {i}: pasa de las {MAX_PREGUNTAS_POR_VENTANA} preguntas por ventana")
            continue
        try:
            preguntas.append(WindowQuestion.model_validate(item))
        except ValidationError as exc:
            descartes.append(f"pregunta {i}: estructura inválida ({exc.errors()[0]['msg']})")
    return preguntas, descartes


def tipo_permitido(question: WindowQuestion, tipos: tuple[str, ...]) -> bool:
    return ("teoria" if question.tipo == QuestionType.TEORIA else "ejercicio") in tipos


def correct_answer(question: WindowQuestion) -> str:
    """El texto de la opción correcta."""
    return next(o.texto for o in question.opciones if o.rol == OptionRole.CORRECT)


def review(question: WindowQuestion, window_text: str) -> Verdict:
    """Revisión por tipo contra el texto de la ventana (spec §7, tabla de revisiones)."""
    correcta = correct_answer(question)
    if question.tipo == QuestionType.TEORIA:
        motivos = []
        if not _literal(question.cita, window_text):
            motivos.append("cita no encontrada")
        if not _literal(correcta, window_text):
            motivos.append("respuesta parafraseada")
        return Verdict.from_motivos(motivos)

    cita = norm_math(question.cita)
    if cita not in norm_math(window_text):
        falta = "cita no encontrada" if question.tipo == QuestionType.EJERCICIO_LIBRO else "sin ejemplo de referencia"
        return Verdict.from_motivos([falta])
    if question.tipo == QuestionType.EJERCICIO_LIBRO and norm_math(correcta) not in cita:
        return Verdict.from_motivos(["el resultado no aparece en el ejemplo citado"])
    return Verdict.from_motivos([])


def _literal(fragmento: str, texto: str) -> bool:
    """¿Está `fragmento` literal en `texto`? Se acepta también con la notación igualada:
    en los libros de matemáticas la teoría trae fórmulas (𝑥2, x²) que llegan aplanadas."""
    return norm_text(fragmento) in norm_text(texto) or norm_math(fragmento) in norm_math(texto)


def _barajadas(question: WindowQuestion, sal: str) -> list[WindowOption]:
    semilla = int(hashlib.sha256(f"{sal}:{question.pregunta}".encode("utf-8")).hexdigest()[:16], 16)
    opciones = list(question.opciones)
    random.Random(semilla).shuffle(opciones)
    return opciones


def to_generated(question: WindowQuestion) -> GeneratedQuestion:
    """La pregunta lista para guardar, con las opciones barajadas de forma reproducible."""
    return GeneratedQuestion(
        question=question.pregunta,
        options=[GeneratedOption(role=o.rol, text=o.texto) for o in _barajadas(question, "guardar")],
        justification=question.justificacion,
    )


def verification_options(question: WindowQuestion) -> tuple[list[str], str]:
    """Textos de las opciones para la verificación (en otro orden, sin roles) y la letra de la clave."""
    opciones = _barajadas(question, "verificar")
    letra = LETRAS[next(i for i, o in enumerate(opciones) if o.rol == OptionRole.CORRECT)]
    return [o.texto for o in opciones], letra


def verification_motivos(
    result: VerificationResult | None, letra_correcta: str, textos: list[str]
) -> list[str]:
    """Motivos de revisión según la verificación. Nombra las opciones por su texto:
    las letras son las del orden de la verificación, no las que ve quien revisa."""
    if result is None:
        return ["verificación fallida"]
    motivos = []
    if result.opcion in ("ninguna", "varias"):
        motivos.append(f"la verificación respondió «{result.opcion}»")
    elif result.opcion != letra_correcta:
        elegida = textos[LETRAS.index(result.opcion)]
        clave = textos[LETRAS.index(letra_correcta)]
        motivos.append(f"la verificación eligió «{elegida}»; la clave es «{clave}»")
    if result.dificultad == "mayor":
        motivos.append("supera la dificultad del PDF")
    return motivos


class DuplicateIndex:
    """Enunciados ya aceptados, por nodo, para descartar duplicadas (spec §7).

    En teoría, dos preguntas son duplicadas si el núcleo del enunciado (desde el
    primer «¿», sin el prefijo «Conforme al …» que comparten todas las de un nodo)
    se parece al 90 % en ambos sentidos **y** tienen la misma respuesta: dos
    preguntas parecidas con respuestas distintas («¿…la ONU?» / «¿…la OEA?») son
    preguntas distintas. En ejercicios solo cuenta el enunciado idéntico.
    """

    def __init__(self) -> None:
        self._por_nodo: dict[int, list[tuple[str, str, str]]] = {}

    def add(self, node_id: int, pregunta: str, tipo: str, correcta: str) -> None:
        self._por_nodo.setdefault(node_id, []).append((norm_text(pregunta), tipo, norm_text(correcta)))

    def is_duplicate(self, node_id: int, pregunta: str, tipo: str, correcta: str) -> bool:
        nueva = norm_text(pregunta)
        respuesta = norm_text(correcta)
        for otra, otro_tipo, otra_respuesta in self._por_nodo.get(node_id, ()):
            if nueva == otra:
                return True
            if tipo == otro_tipo == QuestionType.TEORIA.value and respuesta == otra_respuesta:
                if _similitud(_nucleo(nueva), _nucleo(otra)) >= SIMILITUD_DUPLICADO:
                    return True
        return False


def _nucleo(enunciado: str) -> str:
    """El enunciado desde el primer «¿»: sin el prefijo común de la familia militar."""
    i = enunciado.find("¿")
    return enunciado[i:] if i >= 0 else enunciado


def _similitud(a: str, b: str) -> float:
    """Similitud simétrica: `SequenceMatcher` da valores distintos según el orden."""
    return min(difflib.SequenceMatcher(None, a, b).ratio(), difflib.SequenceMatcher(None, b, a).ratio())

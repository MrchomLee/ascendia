"""Ventanas de texto para generar preguntas (spec §4).

Una ventana es un grupo de chunks consecutivos de un mismo nodo, de unos
4 000 caracteres. Todas las preguntas de una ventana salen de una sola llamada,
así que el tamaño decide cuánto texto ve el modelo a la vez.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol, Sequence

OBJETIVO = 4000
MINIMO_CORTE = 3000
MAXIMO = 6000

# El chunker repite al inicio de cada chunk los últimos ~120 caracteres del anterior.
_SOLAPE_MAX = 200
_SOLAPE_MIN = 20

# Un chunk que empieza así abre un bloque nuevo: mejor no partirlo entre ventanas.
_ENCABEZADO_RE = re.compile(r"^(EJEMPLO\s+\d+|\d+\.\d+\.?\s+[A-ZÁÉÍÓÚÑ¿]|Definición|DEFINICIÓN|Teorema)")


class ChunkLike(Protocol):
    ordinal: int
    text: str
    page_start: int
    page_end: int


@dataclass(frozen=True)
class Window:
    node_id: int
    ordinal_desde: int
    ordinal_hasta: int
    text: str
    page_start: int
    page_end: int

    @property
    def key(self) -> str:
        """Identidad estable de la ventana: `<node_id>:<ordinal_desde>-<ordinal_hasta>`."""
        return f"{self.node_id}:{self.ordinal_desde}-{self.ordinal_hasta}"


def strip_overlap(prev: str, text: str) -> str:
    """Quita del inicio de `text` lo que repite del final de `prev` (y el salto que lo sigue)."""
    for n in range(min(_SOLAPE_MAX, len(prev), len(text)), _SOLAPE_MIN - 1, -1):
        if text.startswith(prev[-n:]):
            return text[n:].lstrip()
    return text


def build_windows(node_id: int, chunks: Sequence[ChunkLike]) -> list[Window]:
    """Agrupa los chunks de un nodo en ventanas. Puro y determinista."""
    piezas: list[tuple[ChunkLike, str]] = []
    anterior: ChunkLike | None = None
    for chunk in sorted(chunks, key=lambda c: c.ordinal):
        texto = chunk.text if anterior is None else strip_overlap(anterior.text, chunk.text)
        anterior = chunk
        if texto.strip():
            piezas.append((chunk, texto.strip()))

    ventanas: list[Window] = []
    actual: list[tuple[ChunkLike, str]] = []
    for chunk, texto in piezas:
        if actual:
            tamano = len(_unir(actual))
            if (
                tamano >= OBJETIVO
                or tamano + 2 + len(texto) > MAXIMO
                or (tamano >= MINIMO_CORTE and _ENCABEZADO_RE.match(texto))
            ):
                ventanas.append(_ventana(node_id, actual))
                actual = []
        actual.append((chunk, texto))
    if actual:
        ventanas.append(_ventana(node_id, actual))
    return ventanas


def _unir(piezas: list[tuple[ChunkLike, str]]) -> str:
    return "\n\n".join(texto for _, texto in piezas)


def _ventana(node_id: int, piezas: list[tuple[ChunkLike, str]]) -> Window:
    return Window(
        node_id=node_id,
        ordinal_desde=piezas[0][0].ordinal,
        ordinal_hasta=piezas[-1][0].ordinal,
        text=_unir(piezas),
        page_start=min(c.page_start for c, _ in piezas),
        page_end=max(c.page_end for c, _ in piezas),
    )

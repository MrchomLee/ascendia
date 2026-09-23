"""Selección por temario: qué bloques, partes o temas de un libro entran al árbol.

Para libros de los que solo interesa un temario concreto (los recortes para el
examen de aspirantes). Con :class:`Temario`, todo lo que no sea un bloque o una
parte del temario se descarta antes de ensamblar, así que ni genera nodos ni se
cuela en el texto de otro. Con :class:`TemasPorTitulo`, los temas sin numerar
se reconocen por su título.
"""

from __future__ import annotations

from dataclasses import dataclass

from etl.extraction.types import ElementKind, RawElement
from etl.hierarchy.patterns import match_parte_temario


@dataclass(frozen=True)
class Temario:
    bloques: dict[int, str]  # número → título del bloque tal como aparece en el PDF
    partes: frozenset[str]   # ordinales que entran: "1.1", "3.2", …

    def select(
        self, elements: list[RawElement], indices: list[int]
    ) -> tuple[list[RawElement], list[int]]:
        """Devuelve los elementos (con su índice original) que entran al árbol.

        - El encabezado con el título de un bloque se reescribe como
          "BLOQUE N. Título": Docling a veces pierde la línea "BLOQUE N" y solo
          deja el título, así que el número sale del temario.
        - Una parte entra con todo su texto, desde su encabezado "x.y" hasta el
          siguiente encabezado de bloque o de parte.
        - Solo cuentan encabezados: las líneas "x.y" del índice llegan como texto.
        """
        numero_por_titulo = {_norm(titulo): n for n, titulo in self.bloques.items()}
        kept: list[RawElement] = []
        kept_indices: list[int] = []
        dentro = False
        for el, idx in zip(elements, indices):
            if el.kind == ElementKind.HEADING:
                numero = numero_por_titulo.get(_norm(el.text))
                if numero is not None:
                    dentro = False
                    kept.append(el.model_copy(update={"text": f"BLOQUE {numero}. {self.bloques[numero]}"}))
                    kept_indices.append(idx)
                    continue
                if (parte := match_parte_temario(el.text)) is not None:
                    dentro = parte.ordinal in self.partes
            if dentro:
                kept.append(el)
                kept_indices.append(idx)
        return kept, kept_indices


@dataclass(frozen=True)
class TemasPorTitulo:
    temas: tuple[str, ...]  # títulos tal como aparecen en el temario, en orden

    def select(
        self, elements: list[RawElement], indices: list[int]
    ) -> tuple[list[RawElement], list[int]]:
        """Reescribe como "TEMA n. Título" el encabezado de cada tema; el resto pasa tal cual.

        El PDF no numera los temas y los escribe con otras mayúsculas ("Las
        grandes organizaciones internacionales"), así que se buscan por título
        sin distinguir mayúsculas y el número sale del orden del temario.
        """
        numero_por_titulo = {_norm(titulo): n for n, titulo in enumerate(self.temas, 1)}
        kept: list[RawElement] = []
        for el in elements:
            numero = numero_por_titulo.get(_norm(el.text)) if el.kind == ElementKind.HEADING else None
            if numero is not None:
                el = el.model_copy(update={"text": f"TEMA {numero}. {self.temas[numero - 1]}"})
            kept.append(el)
        return kept, list(indices)


def _norm(text: str) -> str:
    return " ".join(text.split()).casefold()

"""Selección por temario: qué bloques, partes, capítulos o temas de un libro entran al árbol.

Para libros de los que solo interesa un temario concreto (los recortes para el
examen de aspirantes). Todo lo que no esté en el temario se descarta antes de
ensamblar, así que ni genera nodos ni se cuela en el texto de otro.

- :class:`Temario`: bloques y partes numeradas ("1.1", "3.2", …).
- :class:`CapitulosConTemas`: capítulos numerados con temas sin numerar, que se
  reconocen por su título.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from etl.extraction.types import ElementKind, RawElement
from etl.hierarchy.patterns import match_parte_temario

# "Capítulo 6. El Mundo Contemporáneo", "CAP. 1. GENERALIDADES"
_CAPITULO_RE = re.compile(r"^\s*CAP(?:[ÍI]TULO|\.)\s*(?P<numero>\d+)\s*\.?\s*(?P<resto>.*)$", re.IGNORECASE)


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
class CapitulosConTemas:
    # número → (título, temas), tal como aparecen en el temario; sin temas = capítulo completo
    capitulos: dict[int, tuple[str, tuple[str, ...]]]
    # El PDF no numera los capítulos ("FUNCIONES"): se reconocen por su título.
    # Solo sirve si ningún subtítulo repite el título de un capítulo.
    por_titulo: bool = False

    def select(
        self, elements: list[RawElement], indices: list[int]
    ) -> tuple[list[RawElement], list[int]]:
        """Devuelve los elementos (con su índice original) que entran al árbol.

        - Un encabezado "Capítulo N. …" o "CAP. N. …" (o, con ``por_titulo``, el
          título de un capítulo del temario) abre el capítulo N y se reescribe
          como "Capítulo N. Título" con el título del temario (el PDF puede
          traerlo en mayúsculas). Si N no está en el temario, el capítulo entero
          queda fuera, igual que lo anterior al primer capítulo.
        - Dentro de un capítulo, el encabezado con el título de uno de sus temas
          se reescribe como "TEMA n. Título": se busca sin distinguir mayúsculas
          y n sale del orden del temario. Los demás encabezados son texto.
        - Docling a veces junta el capítulo y su primer tema en un solo
          encabezado ("CAP. 3. GEOMORFOLOGÍA … UNIDADES OROGÉNICAS"): se separa.
        """
        kept: list[RawElement] = []
        kept_indices: list[int] = []
        temas: tuple[str, ...] = ()
        dentro = False
        for el, idx in zip(elements, indices):
            capitulo = self._capitulo(el.text) if el.kind == ElementKind.HEADING else None
            if capitulo is not None:
                numero, resto = capitulo
                dentro = numero in self.capitulos
                if not dentro:
                    continue
                titulo, temas = self.capitulos[numero]
                kept.append(el.model_copy(update={"text": f"Capítulo {numero}. {titulo}"}))
                kept_indices.append(idx)
                resto = _norm(resto)
                if resto.startswith(_norm(titulo)) and (n := _numero_de_tema(temas, resto[len(_norm(titulo)):])):
                    kept.append(el.model_copy(update={"text": f"TEMA {n}. {temas[n - 1]}"}))
                    kept_indices.append(idx)
                continue
            if not dentro:
                continue
            if el.kind == ElementKind.HEADING and (n := _numero_de_tema(temas, el.text)):
                el = el.model_copy(update={"text": f"TEMA {n}. {temas[n - 1]}"})
            kept.append(el)
            kept_indices.append(idx)
        return kept, kept_indices

    def _capitulo(self, text: str) -> tuple[int, str] | None:
        """(número, resto del encabezado) si el encabezado abre un capítulo."""
        if self.por_titulo:
            buscado = _norm(text)
            return next(((n, "") for n, (titulo, _) in self.capitulos.items() if _norm(titulo) == buscado), None)
        if m := _CAPITULO_RE.match(text):
            return int(m.group("numero")), m.group("resto")
        return None


def _numero_de_tema(temas: tuple[str, ...], text: str) -> int | None:
    buscado = _norm(text)
    return next((n for n, tema in enumerate(temas, 1) if _norm(tema) == buscado), None)


def _norm(text: str) -> str:
    return " ".join(text.split()).casefold()

"""Consolida los elementos del cuerpo de cada nodo hoja en fragmentos con límite de tamaño.

Reglas
-----
- A cada nodo hoja (sin hijos) se le concatena su texto narrativo en orden.
- Si el total cabe en `max_chars`, se convierte en un solo fragmento (chunk).
- Si se desborda, se divide en los límites de los párrafos con `overlap` (superposición) de caracteres
  copiados de la cola del fragmento anterior.
- Las hojas diminutas (<`merge_under_chars`) se pliegan dentro de su padre para que el
  generador de preguntas no reciba frases a medias.
- Las tablas se conservan como un único fragmento independientemente de su tamaño — dividirlas
  destruye el contexto.
"""

from __future__ import annotations

import re

from pydantic import BaseModel, Field

from etl.extraction.types import ElementKind, RawElement
from etl.hierarchy.assembler import HierarchyNode, HierarchyTree


class ConsolidatedChunk(BaseModel):
    node_local_id: int
    ordinal: int
    text: str
    char_count: int
    page_start: int
    page_end: int
    has_table: bool = False
    has_image_ref: bool = False
    metadata: dict = Field(default_factory=dict)


class ChunkConsolidator:
    def __init__(
        self,
        *,
        max_chars: int = 1500,
        soft_target: int = 1200,
        overlap: int = 120,
        merge_under_chars: int = 300,
    ) -> None:
        self.max_chars = max_chars
        self.soft_target = soft_target
        self.overlap = overlap
        self.merge_under_chars = merge_under_chars

    def consolidate(
        self,
        tree: HierarchyTree,
        elements: list[RawElement],
    ) -> list[ConsolidatedChunk]:
        node_by_id = {n.local_id: n for n in tree.nodes}
        children_of: dict[int, list[int]] = {n.local_id: [] for n in tree.nodes}
        for n in tree.nodes:
            if n.parent_local_id is not None:
                children_of.setdefault(n.parent_local_id, []).append(n.local_id)

        chunks: list[ConsolidatedChunk] = []
        for node in reversed(tree.nodes):
            # Omitir Anexos para que no generen fragmentos (por petición del usuario)
            if node.is_anexo or node.level_label.lower() == "anexo":
                continue
            text, has_table, has_image = self._gather_text(node, elements)
            if not text.strip():
                continue
                
            # Si es demasiado pequeño y tiene padre, empuja su texto hacia el padre.
            # Esto hace que los nodos diminutos (como hojas de 1 frase o preámbulos cortos) suban
            if (
                len(text) < self.merge_under_chars
                and node.parent_local_id is not None
            ):
                parent = node_by_id[node.parent_local_id]
                # ¿Anteponer o anexar? Ya que procesamos de abajo a arriba, el propio texto del padre
                # aún no ha sido recopilado. Simplemente agregamos nuestros índices al padre.
                parent.body_element_indices.extend(node.body_element_indices)
                continue

            page_start = node.page_start
            page_end = node.page_end or node.page_start
            for ordinal, piece in enumerate(self._split(text)):
                chunks.append(
                    ConsolidatedChunk(
                        node_local_id=node.local_id,
                        ordinal=ordinal,
                        text=piece,
                        char_count=len(piece),
                        page_start=page_start,
                        page_end=page_end,
                        has_table=has_table,
                        has_image_ref=has_image,
                    )
                )
        
        # Invertir los fragmentos de vuelta al orden del documento (ya que los generamos de abajo hacia arriba)
        # Pero espera, dentro de un nodo están correctamente ordenados, pero los propios nodos
        # fueron procesados de abajo hacia arriba. Así que necesitamos ordenar los fragmentos por node.local_id y ordinal.
        chunks.sort(key=lambda c: (c.node_local_id, c.ordinal))
        return chunks

    def _gather_text(
        self,
        node: HierarchyNode,
        elements: list[RawElement],
    ) -> tuple[str, bool, bool]:
        parts: list[str] = []
        has_table = False
        has_image = False
        for idx in node.body_element_indices:
            el = elements[idx]
            if el.kind in (ElementKind.HEADING, ElementKind.TITLE):
                continue
            if el.kind == ElementKind.TABLE:
                has_table = True
                parts.append(f"\n[TABLA]\n{el.text}\n[/TABLA]\n")
            elif el.kind == ElementKind.FIGURE:
                has_image = True
                if el.text:
                    parts.append(f"[FIGURA: {el.text}]")
            elif el.text:
                parts.append(el.text)
        # Reordenar fracciones romanas desplazadas por docling
        parts = self._reorder_roman_fractions(parts)
        return ("\n\n".join(p.strip() for p in parts if p.strip()), has_table, has_image)

    # Regex para detectar fracciones con números romanos al inicio de línea
    _ROMAN_RE = re.compile(
        r"^([IVXLC]+)\s*(?:Bis|Ter|Quáter)?\.?\s*[-.]",
        re.IGNORECASE,
    )
    # Regex para detectar inicio de un Artículo
    _ARTICULO_RE = re.compile(
        r"^Artículo\s+\d+",
        re.IGNORECASE,
    )
    # Valores numéricos de los números romanos
    _ROMAN_VALS = {
        "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5,
        "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10,
        "XI": 11, "XII": 12, "XIII": 13, "XIV": 14, "XV": 15,
        "XVI": 16, "XVII": 17, "XVIII": 18, "XIX": 19, "XX": 20,
    }

    def _roman_to_int(self, s: str) -> int | None:
        """Convierte un número romano a entero, o None si no es válido."""
        return self._ROMAN_VALS.get(s.upper())

    def _reorder_roman_fractions(self, parts: list[str]) -> list[str]:
        """Reordena fracciones romanas que docling extrajo en orden incorrecto.
        
        Docling a veces lee las anotaciones marginales del DOF antes que las
        fracciones, lo que causa que fracciones como II y V aparezcan después
        del artículo siguiente. Este método detecta esas fracciones huérfanas
        y las reubica en la posición correcta.
        """
        if len(parts) < 3:
            return parts

        result = list(parts)
        changed = True
        max_passes = 10  # Evitar bucle infinito

        while changed and max_passes > 0:
            changed = False
            max_passes -= 1

            for i in range(len(result)):
                part = result[i].strip()
                m = self._ROMAN_RE.match(part)
                if not m or i == 0:
                    continue

                roman_str = m.group(1).upper()
                roman_val = self._roman_to_int(roman_str)
                if roman_val is None or roman_val < 2:
                    continue

                # Buscar hacia atrás si hay un Artículo entre esta fracción
                # y alguna fracción predecesora de la misma serie
                has_article_between = False
                predecessor_pos = None

                for j in range(i - 1, -1, -1):
                    text_j = result[j].strip()

                    if self._ARTICULO_RE.match(text_j):
                        has_article_between = True

                    m_j = self._ROMAN_RE.match(text_j)
                    if m_j:
                        prev_roman = m_j.group(1).upper()
                        prev_val = self._roman_to_int(prev_roman)
                        if prev_val is not None and prev_val == roman_val - 1:
                            predecessor_pos = j
                            break
                        elif prev_val is not None and prev_val < roman_val:
                            # Encontramos una fracción menor pero no la inmediata
                            # anterior; insertamos después de ella
                            predecessor_pos = j
                            break

                if predecessor_pos is not None and has_article_between:
                    # Mover la fracción justo después de su predecesora
                    item = result.pop(i)
                    result.insert(predecessor_pos + 1, item)
                    changed = True
                    break  # Reiniciar el bucle completo

        return result

    def _split(self, text: str) -> list[str]:
        if len(text) <= self.max_chars:
            return [text]
        paragraphs = [p for p in text.split("\n\n") if p.strip()]
        chunks: list[str] = []
        current = ""
        for para in paragraphs:
            if not current:
                current = para
                continue
            if len(current) + len(para) + 2 <= self.soft_target:
                current = f"{current}\n\n{para}"
                continue
            chunks.append(current)
            tail = current[-self.overlap :] if self.overlap else ""
            current = (tail + "\n\n" + para) if tail else para
        if current:
            chunks.append(current)
        return chunks

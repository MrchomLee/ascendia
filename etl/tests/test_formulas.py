"""Las fórmulas llegan a los chunks con su ecuación.

Sin el enriquecimiento de fórmulas (no lo usamos), Docling entrega cada ecuación
como un elemento ``formula`` con ``.text`` vacío y la ecuación en ``.orig``;
antes se descartaba y los libros de matemáticas perdían los resultados de sus
ejemplos (p. ej., «5𝑎 + 6𝑏 + 8𝑐 𝐑.» en la suma de Baldor).
"""

from docling_core.types.doc import DocItemLabel, DoclingDocument

from etl.chunking.consolidator import ChunkConsolidator
from etl.extraction.docling_adapter import elements_from_document
from etl.extraction.types import ElementKind, RawElement
from etl.hierarchy.assembler import HierarchyAssembler
from etl.hierarchy.profile import get_profile

ECUACION = "5𝑎 + 6𝑏 + 8𝑐 𝐑."


def _documento_con_formula() -> DoclingDocument:
    doc = DoclingDocument(name="prueba")
    doc.add_text(label=DocItemLabel.TEXT, text="la suma será:")
    doc.add_formula(text="", orig=ECUACION)
    return doc


def test_la_formula_de_docling_sale_con_su_ecuacion():
    elementos = elements_from_document(_documento_con_formula())

    assert [e.text for e in elementos] == ["la suma será:", ECUACION]


def test_la_formula_queda_en_el_chunk_de_su_nodo():
    *_, formula = elements_from_document(_documento_con_formula())
    elements = [
        RawElement(page_number=1, physical_page_index=0, kind=ElementKind.HEADING, text="CAPÍTULO I"),
        RawElement(page_number=1, physical_page_index=0, kind=ElementKind.HEADING, text="Suma"),
        RawElement(page_number=1, physical_page_index=0, kind=ElementKind.NARRATIVE, text="la suma será:"),
        formula,
    ]
    tree = HierarchyAssembler(get_profile("manual"), prefer_toc=False).assemble(elements, toc=None)

    (chunk,) = ChunkConsolidator().consolidate(tree, elements)

    assert "la suma será:" in chunk.text and ECUACION in chunk.text

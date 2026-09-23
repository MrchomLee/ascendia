"""Las tablas llegan a los chunks con su contenido.

Docling guarda las celdas de una tabla en ``TableItem.data``, no en ``.text``;
antes la tabla salía con texto vacío y el ensamblador la descartaba (así se
perdían, p. ej., los estados y capitales de Geografía Moderna de México).
"""

from docling_core.types.doc import DocItemLabel, DoclingDocument, TableCell, TableData

from etl.chunking.consolidator import ChunkConsolidator
from etl.extraction.docling_adapter import elements_from_document
from etl.extraction.types import ElementKind, RawElement
from etl.hierarchy.assembler import HierarchyAssembler
from etl.hierarchy.profile import get_profile


def _documento_con_tabla(filas: list[list[str]], titulo: str | None = None) -> DoclingDocument:
    doc = DoclingDocument(name="prueba")
    celdas = [
        TableCell(
            text=texto,
            start_row_offset_idx=r,
            end_row_offset_idx=r + 1,
            start_col_offset_idx=c,
            end_col_offset_idx=c + 1,
            column_header=r == 0,
        )
        for r, fila in enumerate(filas)
        for c, texto in enumerate(fila)
    ]
    tabla = doc.add_table(data=TableData(num_rows=len(filas), num_cols=len(filas[0]), table_cells=celdas))
    if titulo:
        # Como en una conversión real: el título es hijo de la tabla y va detrás de ella.
        caption = doc.add_text(label=DocItemLabel.CAPTION, text=titulo, parent=tabla)
        tabla.captions.append(caption.get_ref())
    return doc


def test_la_tabla_de_docling_sale_con_sus_celdas_como_texto():
    doc = _documento_con_tabla([["Estado", "Capital"], ["Aguascalientes", "Aguascalientes"], ["Baja California", "Mexicali"]])

    (tabla,) = [e for e in elements_from_document(doc) if e.kind == ElementKind.TABLE]

    assert "| Estado" in tabla.text
    assert "Baja California" in tabla.text and "Mexicali" in tabla.text


def test_el_titulo_de_la_tabla_viaja_dentro_de_ella_y_no_se_repite():
    doc = _documento_con_tabla([["Estado", "Capital"], ["Nayarit", "Tepic"]], titulo="Tabla 1.1. Estados.")

    con_titulo = [e for e in elements_from_document(doc) if "Tabla 1.1" in e.text]

    assert [e.kind for e in con_titulo] == [ElementKind.TABLE]
    assert con_titulo[0].text.startswith("Tabla 1.1. Estados.")
    # El chunker parte por líneas en blanco: sin ellas, título y filas no se separan.
    assert "\n\n" not in con_titulo[0].text


def _el(kind: ElementKind, text: str) -> RawElement:
    return RawElement(page_number=1, physical_page_index=0, kind=kind, text=text)


def test_la_tabla_queda_en_el_chunk_de_su_nodo():
    elements = [
        _el(ElementKind.HEADING, "CAPÍTULO I"),
        _el(ElementKind.HEADING, "Estados"),
        _el(ElementKind.TABLE, "| Estado | Capital |\n|---|---|\n| Baja California | Mexicali |"),
    ]
    tree = HierarchyAssembler(get_profile("manual"), prefer_toc=False).assemble(elements, toc=None)

    (chunk,) = ChunkConsolidator().consolidate(tree, elements)

    assert chunk.has_table
    assert "[TABLA]" in chunk.text and "Mexicali" in chunk.text


def test_una_tabla_no_se_toma_como_titulo_de_un_encabezado():
    # "CAPÍTULO I" llega sin título y el ensamblador lo busca en lo que sigue;
    # cuando las tablas llegaban vacías, nunca podían ser ese título.
    elements = [
        _el(ElementKind.HEADING, "CAPÍTULO I"),
        _el(ElementKind.TABLE, "| Grado | Mando |\n|---|---|\n| General | División |"),
        _el(ElementKind.HEADING, "Organización"),
    ]
    tree = HierarchyAssembler(get_profile("manual"), prefer_toc=False).assemble(elements, toc=None)

    assert [(n.ordinal, n.title) for n in tree.nodes] == [("I", "Organización")]

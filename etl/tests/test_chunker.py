from etl.chunking.consolidator import ChunkConsolidator
from etl.extraction.types import ElementKind, RawElement
from etl.hierarchy.assembler import HierarchyNode, HierarchyTree


def _node(local_id: int, **overrides) -> HierarchyNode:
    base = dict(
        local_id=local_id,
        parent_local_id=None,
        level=2,
        level_label="Sección",
        ordinal="Primera",
        title="Generalidades",
        breadcrumb="PRIMERA PARTE › Capítulo I › Primera Sección",
        page_start=1,
        page_end=1,
        sort_key="01",
        is_anexo=False,
        body_element_indices=[],
    )
    base.update(overrides)
    return HierarchyNode(**base)


def test_chunker_keeps_short_text_in_one_chunk():
    el = RawElement(page_number=1, physical_page_index=0, kind=ElementKind.NARRATIVE, text="Texto corto.")
    node = _node(0, body_element_indices=[0])
    tree = HierarchyTree(nodes=[node], root_ids=[0])
    chunks = ChunkConsolidator(max_chars=1500).consolidate(tree, [el])
    assert len(chunks) == 1
    assert chunks[0].text == "Texto corto."
    assert chunks[0].char_count == len("Texto corto.")


def test_chunker_splits_long_text():
    paragraphs = [f"Párrafo {i}. " * 40 for i in range(10)]
    long_text = "\n\n".join(paragraphs)
    el = RawElement(page_number=1, physical_page_index=0, kind=ElementKind.NARRATIVE, text=long_text)
    node = _node(0, body_element_indices=[0])
    tree = HierarchyTree(nodes=[node], root_ids=[0])
    chunks = ChunkConsolidator(max_chars=800, soft_target=600, overlap=50).consolidate(tree, [el])
    assert len(chunks) >= 2
    assert all(c.char_count <= 1000 for c in chunks)


def test_table_marker_is_set():
    table_el = RawElement(page_number=1, physical_page_index=0, kind=ElementKind.TABLE, text="| a | b |\n|---|---|\n| 1 | 2 |")
    node = _node(0, body_element_indices=[0])
    tree = HierarchyTree(nodes=[node], root_ids=[0])
    chunks = ChunkConsolidator().consolidate(tree, [table_el])
    assert len(chunks) == 1
    assert chunks[0].has_table is True

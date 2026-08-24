from pathlib import Path

from etl.chunking.consolidator import ConsolidatedChunk
from etl.db.init_db import init_db
from etl.db.persistence import persist_manual
from etl.db.session import session_scope
from etl.hierarchy.assembler import HierarchyNode, HierarchyTree
from etl.models.schema import Manual


def test_persist_round_trip():
    init_db()
    parent = HierarchyNode(
        local_id=0, parent_local_id=None, level=0, level_label="PARTE",
        ordinal="PRIMERA", title="LA GUERRA",
        breadcrumb="PRIMERA PARTE — LA GUERRA",
        page_start=1, page_end=10, sort_key="01", is_anexo=False,
        body_element_indices=[],
    )
    child = HierarchyNode(
        local_id=1, parent_local_id=0, level=1, level_label="Capítulo",
        ordinal="I", title="Teoría de la Guerra",
        breadcrumb="PRIMERA PARTE › Capítulo I — Teoría de la Guerra",
        page_start=1, page_end=14, sort_key="01.01", is_anexo=False,
        body_element_indices=[],
    )
    tree = HierarchyTree(nodes=[parent, child], root_ids=[0])
    chunks = [
        ConsolidatedChunk(
            node_local_id=1, ordinal=0,
            text="Texto de prueba.", char_count=16,
            page_start=1, page_end=2,
        )
    ]

    with session_scope() as session:
        manual = persist_manual(
            session,
            code="DN M 1455",
            title="Manual de Operaciones Militares",
            edition=None,
            branch="Ejército",
            source_path=Path("data/raw_pdfs/dn_m_1455.pdf"),
            page_count=20,
            extractor_used="docling",
            tree=tree,
            chunks=chunks,
        )
        assert manual.id is not None

    with session_scope() as session:
        loaded = session.query(Manual).filter_by(code="DN M 1455").one()
        assert loaded.title == "Manual de Operaciones Militares"
        assert len(loaded.nodes) == 2
        chunk_count = sum(len(n.chunks) for n in loaded.nodes)
        assert chunk_count == 1

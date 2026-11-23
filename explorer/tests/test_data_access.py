"""Pruebas unitarias para la capa de acceso a datos del explorador (data_access.py)."""

from datetime import datetime, timezone
import streamlit as st

from etl.db.init_db import init_db
from etl.db.session import session_scope
from etl.models.schema import Chunk, Manual, Node
from explorer.data_access import (
    get_chunks_for_node,
    get_global_kpis,
    get_manual,
    get_node,
    get_tree,
    list_manuals,
)


def _seed_sample_data():
    """Siembra datos de prueba para manuales, nodos y chunks."""
    init_db()
    with session_scope() as session:
        m = Manual(
            code="MAN-01",
            title="Manual de Prueba Militar",
            edition="2024",
            branch="Infantería",
            source_path="/tmp/manual_test.pdf",
            page_count=20,
            extractor_used="docling",
            ingested_at=datetime.now(timezone.utc),
            metadata_json={"profile": "manual"},
        )
        session.add(m)
        session.flush()

        n1 = Node(
            manual_id=m.id,
            parent_id=None,
            level=0,
            level_label="PARTE",
            ordinal="PRIMERA",
            title="Fundamentos",
            breadcrumb="PRIMERA PARTE — Fundamentos",
            page_start=1,
            page_end=10,
            sort_key="01",
            is_anexo=False,
        )
        session.add(n1)
        session.flush()

        n2 = Node(
            manual_id=m.id,
            parent_id=n1.id,
            level=1,
            level_label="Capítulo",
            ordinal="I",
            title="Principios Básicos",
            breadcrumb="PRIMERA PARTE › Capítulo I — Principios Básicos",
            page_start=2,
            page_end=5,
            sort_key="01.01",
            is_anexo=False,
        )
        session.add(n2)
        session.flush()

        c1 = Chunk(
            manual_id=m.id,
            node_id=n2.id,
            ordinal=1,
            text="El principio fundamental de la maniobra reside en...",
            char_count=48,
            page_start=2,
            page_end=3,
            has_table=False,
            has_image_ref=False,
        )
        session.add(c1)
        session.flush()

        return m.id, n1.id, n2.id, c1.id


def test_list_manuals_y_global_kpis():
    """Verifica el listado de manuales y los KPIs globales del explorador."""
    st.cache_data.clear()
    manual_id, _, _, _ = _seed_sample_data()

    manuals = list_manuals()
    assert len(manuals) >= 1
    sample = next(m for m in manuals if m.id == manual_id)
    assert sample.code == "MAN-01"
    assert sample.node_count == 2
    assert sample.chunk_count == 1

    kpis = get_global_kpis()
    assert kpis.manual_count >= 1
    assert kpis.node_count >= 2
    assert kpis.chunk_count >= 1
    assert kpis.last_ingested_at is not None


def test_get_manual_detail():
    """Verifica la consulta de detalles de un manual específico."""
    st.cache_data.clear()
    manual_id, _, _, _ = _seed_sample_data()

    detail = get_manual(manual_id)
    assert detail is not None
    assert detail.code == "MAN-01"
    assert detail.edition == "2024"
    assert detail.branch == "Infantería"

    inexistente = get_manual(999999)
    assert inexistente is None


def test_get_tree_y_get_node():
    """Verifica la obtención de la jerarquía de árbol y nodos individuales."""
    st.cache_data.clear()
    manual_id, n1_id, n2_id, _ = _seed_sample_data()

    tree = get_tree(manual_id)
    assert len(tree) == 2
    assert tree[0].id == n1_id
    assert tree[1].id == n2_id
    assert tree[1].chunk_count == 1

    node = get_node(n2_id)
    assert node is not None
    assert node.title == "Principios Básicos"
    assert node.chunk_count == 1

    chunks = get_chunks_for_node(n2_id)
    assert len(chunks) == 1
    assert "principio fundamental" in chunks[0].text

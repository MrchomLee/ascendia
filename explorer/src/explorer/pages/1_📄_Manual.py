"""Manual detail — metadata + quality report + hierarchy tree + chunks table."""

from __future__ import annotations

from dotenv import load_dotenv

import streamlit as st

from explorer.components import kpi_row, render_tree
from explorer.data_access import (
    get_chunks_for_manual,
    get_manual,
    get_quality_report_dict,
    get_tree,
    list_manuals,
)
from explorer.navigation import (
    PAGE_NODE,
    PAGE_QUESTIONS,
    PAGE_RAW,
    PAGE_TOC,
    get_int,
    link_to,
    set_params,
)
from explorer.questions_access import SERVED_STATUSES, questions_available, status_by_node

load_dotenv()
st.set_page_config(page_title="Manual", page_icon="📄", layout="wide")

manual_id = get_int("manual_id")
if manual_id is None:
    manuals = list_manuals()
    if not manuals:
        st.error("No hay manuales ingeridos. Vuelve al Home.")
        st.stop()
    selected = st.selectbox(
        "Selecciona un manual",
        options=[m.id for m in manuals],
        format_func=lambda i: next(f"{m.code} — {m.title}" for m in manuals if m.id == i),
    )
    if st.button("Abrir"):
        set_params(manual_id=selected)
        st.rerun()
    st.stop()

manual = get_manual(manual_id)
if manual is None:
    st.error(f"Manual {manual_id} no encontrado.")
    st.stop()

st.title(f"📄 {manual.code}")
st.caption(manual.title)

meta_cols = st.columns(4)
meta_cols[0].markdown(f"**Edición**\n\n{manual.edition or '—'}")
meta_cols[1].markdown(f"**Rama**\n\n{manual.branch or '—'}")
meta_cols[2].markdown(f"**Extractor**\n\n`{manual.extractor_used}`")
meta_cols[3].markdown(f"**Ingestado**\n\n{manual.ingested_at.strftime('%Y-%m-%d %H:%M')}")

st.markdown(f"**Fuente:** `{manual.source_path}`")

st.markdown(
    f"[📑 Ver TOC]({link_to(PAGE_TOC, manual_id=manual.id)})  ·  "
    f"[🧱 Elementos crudos]({link_to(PAGE_RAW, manual_id=manual.id)})  ·  "
    f"[❓ Preguntas]({link_to(PAGE_QUESTIONS, manual_id=manual.id)})"
)

st.divider()

tab_summary, tab_tree, tab_chunks = st.tabs(["Resumen", "Árbol", "Chunks crudos"])

with tab_summary:
    report = get_quality_report_dict(manual.id)
    if report is None:
        st.warning("No pude generar el reporte de calidad.")
    else:
        kpi_row(
            [
                ("Páginas", report["page_count"], None),
                ("Nodos", report["node_count"], None),
                ("Chunks", report["chunk_count"], None),
                ("Cobertura páginas", f"{report['page_coverage_pct']:.1f}%", "Pct de páginas con al menos un chunk"),
            ]
        )
        kpi_row(
            [
                ("Nodos huérfanos", report["orphan_nodes"], "Nodos sin chunks"),
                ("Chars/chunk (avg)", f"{report['avg_chunk_chars']:.0f}", None),
                ("Páginas con chunks", report["pages_with_chunks"], None),
                ("", "", None),
            ]
        )

        st.subheader("Distribución por nivel")
        dist = report["level_distribution"]
        if dist:
            st.bar_chart(dist, horizontal=True)
        else:
            st.info("Sin distribución calculada.")

        with st.expander("Metadata cruda del manual"):
            st.json(manual.metadata)

with tab_tree:
    nodes = get_tree(manual.id)

    # El árbol es donde se ve de un vistazo qué parte del manual ya está
    # cubierta: un nodo con texto y sin pregunta es trabajo pendiente.
    por_nodo = status_by_node(manual.id) if questions_available() else {}

    def _badge(node) -> str:
        estados = por_nodo.get(node.id, [])
        if estados:
            servidas = sum(1 for e in estados if e in SERVED_STATUSES)
            if servidas == len(estados):
                return f"❓{len(estados)}"
            return f"❓{servidas}/{len(estados)}"
        return "⚠ sin pregunta" if node.chunk_count else ""

    st.caption(
        f"{len(nodes)} nodos en total. Haz click en cada nivel para expandir. "
        "El ❓ dice cuántas preguntas cuelgan del nodo (y cuántas de ellas se sirven)."
    )
    render_tree(
        nodes,
        on_select=lambda n: link_to(PAGE_NODE, node_id=n.id),
        expand_to_level=0,
        badge=_badge,
    )

with tab_chunks:
    chunks = get_chunks_for_manual(manual.id, limit=2000)
    st.caption(f"Mostrando {len(chunks)} chunks. Ordena/filtra clickeando los headers.")
    if chunks:
        rows = [
            {
                "id": c.id,
                "node_id": c.node_id,
                "ordinal": c.ordinal,
                "page_start": c.page_start,
                "page_end": c.page_end,
                "chars": c.char_count,
                "table": "✓" if c.has_table else "",
                "fig": "✓" if c.has_image_ref else "",
                "preview": c.text[:140] + ("…" if len(c.text) > 140 else ""),
            }
            for c in chunks
        ]
        st.dataframe(rows, width="stretch", hide_index=True)
    else:
        st.info("Este manual no tiene chunks.")

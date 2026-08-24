"""Raw elements viewer — reads data/processed/<manual>.<extractor>.json."""

from __future__ import annotations

import os

from dotenv import load_dotenv

import streamlit as st

from explorer.components import kpi_row
from explorer.components.pdf_preview import render_page_widget
from explorer.data_access import (
    deserialize_extraction,
    get_extraction_cache,
    get_manual,
    list_manuals,
)
from explorer.navigation import PAGE_MANUAL, get_int, link_to, set_params

load_dotenv()
st.set_page_config(page_title="Raw Elements", page_icon="🧱", layout="wide")
st.title("🧱 Raw elements viewer")

manual_id = get_int("manual_id")
if manual_id is None:
    manuals = list_manuals()
    if not manuals:
        st.warning("No hay manuales ingeridos.")
        st.stop()
    selected = st.selectbox(
        "Manual",
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

st.markdown(f"[← {manual.code}]({link_to(PAGE_MANUAL, manual_id=manual.id)})")

processed_dir = os.getenv("PROCESSED_DIR", "./data/processed")
raw = get_extraction_cache(manual.id, processed_dir)
if raw is None:
    st.warning(
        f"No encontré cache de extracción en `{processed_dir}` para este manual.\n\n"
        "Corre el ETL con cache habilitado:\n\n"
        "```powershell\npy -3.14 -m uv run etl-bakeoff data/raw_pdfs/<archivo>.pdf --skip-unstructured\n```"
    )
    st.stop()

extraction = deserialize_extraction(raw)

kpi_row(
    [
        ("Extractor", extraction.extractor_name, None),
        ("Páginas", extraction.page_count, None),
        ("Elementos", f"{len(extraction.elements):,}", None),
        ("Tiempo", f"{extraction.elapsed_seconds:.1f}s", None),
    ]
)

if extraction.warnings:
    st.warning("Warnings: " + "; ".join(extraction.warnings))

st.divider()

with st.sidebar:
    st.subheader("Filtros")
    kinds = sorted({e.kind.value for e in extraction.elements})
    kind_filter = st.multiselect("Tipo de elemento", kinds, default=kinds)
    pages_min = min((e.page_number for e in extraction.elements), default=1)
    pages_max = max((e.page_number for e in extraction.elements), default=1)
    page_range = st.slider("Rango de páginas", pages_min, pages_max, (pages_min, pages_max))
    text_query = st.text_input("Texto contiene", "").strip().lower()

filtered = [
    e
    for e in extraction.elements
    if e.kind.value in kind_filter
    and page_range[0] <= e.page_number <= page_range[1]
    and (not text_query or text_query in e.text.lower())
]

st.subheader(f"Elementos: {len(filtered):,} (de {len(extraction.elements):,})")

dist = {}
for e in filtered:
    dist[e.kind.value] = dist.get(e.kind.value, 0) + 1
if dist:
    st.bar_chart(dist, horizontal=True)

st.dataframe(
    [
        {
            "idx": i,
            "page": e.page_number,
            "kind": e.kind.value,
            "level": e.level if e.level is not None else "",
            "text": e.text[:160] + ("…" if len(e.text) > 160 else ""),
        }
        for i, e in enumerate(filtered[:2000])
    ],
    width="stretch",
    hide_index=True,
)

if len(filtered) > 2000:
    st.caption(f"Mostrando los primeros 2000 de {len(filtered):,}.")

st.divider()
st.subheader("Inspección de un elemento")
if filtered:
    idx = st.number_input(
        "Índice del elemento (en el listado filtrado de arriba)",
        min_value=0,
        max_value=min(len(filtered), 2000) - 1,
        value=0,
    )
    el = filtered[int(idx)]
    cols = st.columns([0.5, 0.5])
    with cols[0]:
        st.markdown(f"**Página:** {el.page_number}  ·  **Tipo:** `{el.kind.value}`")
        st.markdown("**Texto completo:**")
        st.text(el.text)
        st.markdown("**Bbox:** " + (str(el.bbox) if el.bbox else "—"))
        st.markdown("**Metadata:**")
        st.json(el.metadata)
    with cols[1]:
        render_page_widget(manual.source_path, el.page_number)

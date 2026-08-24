"""Home page — list of ingested manuals + global KPIs."""

from __future__ import annotations

from dotenv import load_dotenv

import streamlit as st

from explorer.components import kpi_row
from explorer.data_access import get_global_kpis, list_manuals
from explorer.navigation import PAGE_MANUAL, link_to

load_dotenv()

st.set_page_config(page_title="ETL Explorer", page_icon="🧭", layout="wide")
st.title("🧭 ETL Explorer")
st.caption("Herramienta local de **solo lectura** para inspeccionar las extracciones del pipeline de manuales militares.")

if st.sidebar.button("🔄 Refrescar caché", width="stretch"):
    st.cache_data.clear()
    st.rerun()

kpis = get_global_kpis()
last = kpis.last_ingested_at.strftime("%Y-%m-%d %H:%M") if kpis.last_ingested_at else "—"
kpi_row(
    [
        ("Manuales", kpis.manual_count, "Manuales ingeridos en la BD"),
        ("Nodos", f"{kpis.node_count:,}", "Total de nodos jerárquicos"),
        ("Chunks", f"{kpis.chunk_count:,}", "Total de chunks de texto"),
        ("Última ingesta", last, None),
    ]
)

st.divider()
st.subheader("Manuales ingeridos")

manuals = list_manuals()
if not manuals:
    st.info(
        "Aún no hay manuales en la BD. Ingiere uno con:\n\n"
        "```powershell\npy -3.14 -m uv run etl-ingest data/raw_pdfs/<archivo>.pdf\n```"
    )
else:
    for m in manuals:
        with st.container(border=True):
            top_left, top_right = st.columns([0.78, 0.22])
            with top_left:
                st.markdown(f"### [{m.code}]({link_to(PAGE_MANUAL, manual_id=m.id)}) — {m.title}")
                tags = []
                if m.branch:
                    tags.append(f"🪖 {m.branch}")
                tags.append(f"⚙ {m.extractor_used}")
                tags.append(f"📅 {m.ingested_at.strftime('%Y-%m-%d %H:%M')}")
                st.markdown(" · ".join(tags))
            with top_right:
                st.markdown(f"[Abrir →]({link_to(PAGE_MANUAL, manual_id=m.id)})")

            sub_cols = st.columns(3)
            sub_cols[0].metric("Páginas", m.page_count)
            sub_cols[1].metric("Nodos", m.node_count)
            sub_cols[2].metric("Chunks", m.chunk_count)

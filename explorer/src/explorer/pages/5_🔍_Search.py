"""Full-text search across chunks via SQLite FTS5."""

from __future__ import annotations

from dotenv import load_dotenv

import streamlit as st

from explorer.data_access import get_manual, list_manuals
from explorer.navigation import PAGE_NODE, link_to
from explorer.search import init_fts, query

load_dotenv()
st.set_page_config(page_title="Search", page_icon="🔍", layout="wide")
st.title("🔍 Búsqueda en chunks")

with st.spinner("Inicializando índice FTS5…"):
    init_fts()

manuals = list_manuals()
manual_options = {m.id: f"{m.code} — {m.title}" for m in manuals}
manual_options[0] = "Todos los manuales"

col1, col2 = st.columns([0.7, 0.3])
with col1:
    q = st.text_input("Texto a buscar", placeholder='ej. "operaciones tácticas" OR maniobra')
with col2:
    selected = st.selectbox(
        "Manual",
        options=[0, *manual_options.keys()],
        format_func=lambda i: manual_options.get(i, str(i)),
    )

st.caption(
    "Acentos ignorados. Por defecto cada palabra es una frase exacta. "
    "Usa `\"...\"` para frases, `AND` / `OR` para booleanos, `NEAR(x, y, n)` para proximidad."
)

if not q.strip():
    st.info("Escribe una búsqueda para empezar.")
    st.stop()

manual_filter = selected if selected != 0 else None
hits = query(q, manual_id=manual_filter, limit=80)

st.subheader(f"{len(hits)} resultado(s)")
if not hits:
    st.warning("Sin coincidencias.")
    st.stop()

for hit in hits:
    manual = get_manual(hit.manual_id)
    code = manual.code if manual else f"manual_id={hit.manual_id}"
    with st.container(border=True):
        top = st.columns([0.7, 0.3])
        top[0].markdown(
            f"**{code}**  ·  p.{hit.page_start}-{hit.page_end}  ·  rank `{hit.rank:.2f}`"
        )
        top[1].markdown(f"[Abrir nodo →]({link_to(PAGE_NODE, node_id=hit.node_id)})")
        st.markdown(hit.snippet, unsafe_allow_html=True)

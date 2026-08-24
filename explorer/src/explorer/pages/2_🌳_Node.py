"""Node detail — breadcrumb + chunks + sibling navigation + PDF preview."""

from __future__ import annotations

from dotenv import load_dotenv

import streamlit as st

from explorer.components.pdf_preview import render_page_widget
from explorer.data_access import (
    get_chunks_for_node,
    get_manual,
    get_node,
    get_node_ancestors,
    get_node_children,
    get_node_siblings,
)
from explorer.navigation import PAGE_MANUAL, PAGE_NODE, get_int, link_to

load_dotenv()
st.set_page_config(page_title="Node", page_icon="🌳", layout="wide")

node_id = get_int("node_id")
if node_id is None:
    st.error("Falta `node_id` en la URL. Abre un manual y selecciona un nodo desde el árbol.")
    st.stop()

node = get_node(node_id)
if node is None:
    st.error(f"Nodo {node_id} no encontrado.")
    st.stop()

manual = get_manual(node.manual_id)
ancestors = get_node_ancestors(node)

bc_links = [f"[{manual.code}]({link_to(PAGE_MANUAL, manual_id=manual.id)})"] if manual else []
bc_links += [f"[{a.level_label} {a.ordinal}]({link_to(PAGE_NODE, node_id=a.id)})" for a in ancestors]
bc_links.append(f"**{node.level_label} {node.ordinal}**")
st.markdown(" › ".join(bc_links))

st.title(f"🌳 {node.level_label} {node.ordinal} — {node.title}".strip())

mcols = st.columns(4)
mcols[0].metric("Páginas", f"{node.page_start}-{node.page_end or node.page_start}")
mcols[1].metric("Nivel", node.level_label)
mcols[2].metric("Chunks", node.chunk_count)
mcols[3].metric("Sort key", node.sort_key)

st.divider()

tab_text, tab_pdf, tab_nav = st.tabs(["Texto", "PDF original", "Navegar"])

with tab_text:
    chunks = get_chunks_for_node(node.id)
    if not chunks:
        children = get_node_children(node)
        if children:
            st.info(
                f"Este nodo no tiene chunks propios; tiene {len(children)} hijo(s) que sí "
                "podrían tenerlos. Visita los hijos en la pestaña **Navegar**."
            )
        else:
            st.warning("Este nodo es hoja pero no tiene chunks. Posible huérfano.")
    for c in chunks:
        with st.container(border=True):
            top = st.columns([0.6, 0.4])
            top[0].markdown(f"**Chunk #{c.ordinal}**  ·  {c.char_count} chars")
            tags = [f"p.{c.page_start}-{c.page_end}"]
            if c.has_table:
                tags.append("📊 tabla")
            if c.has_image_ref:
                tags.append("🖼 figura")
            top[1].markdown(" · ".join(tags))
            st.markdown(c.text)

with tab_pdf:
    if manual is None:
        st.info("Manual no disponible.")
    else:
        page_min = node.page_start
        page_max = node.page_end or node.page_start
        pages_in_range = list(range(page_min, page_max + 1))
        if len(pages_in_range) > 1:
            page_pick = st.slider("Página", page_min, page_max, page_min)
        else:
            page_pick = page_min
            st.caption(f"Solo una página: {page_min}")
        render_page_widget(
            manual.source_path,
            page_pick,
            caption=f"{manual.code} — página {page_pick}",
        )

with tab_nav:
    children = get_node_children(node)
    siblings = get_node_siblings(node)

    st.subheader("Hijos")
    if children:
        for child in children:
            st.markdown(
                f"- [{child.level_label} {child.ordinal} — {child.title}]"
                f"({link_to(PAGE_NODE, node_id=child.id)})  ·  p.{child.page_start}"
                f"{'-' + str(child.page_end) if child.page_end else ''}  ·  "
                f"{child.chunk_count} chunk(s)"
            )
    else:
        st.caption("Sin hijos.")

    st.subheader("Hermanos (mismo padre)")
    if siblings:
        for sib in siblings:
            st.markdown(
                f"- [{sib.level_label} {sib.ordinal} — {sib.title}]"
                f"({link_to(PAGE_NODE, node_id=sib.id)})"
            )
    else:
        st.caption("Sin hermanos.")

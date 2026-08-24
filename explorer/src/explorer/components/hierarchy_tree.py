"""Hierarchy tree rendered as nested expanders with optional click-to-navigate."""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from explorer.data_access import NodeSummary


def render_tree(
    nodes: list[NodeSummary],
    *,
    on_select: Callable[[NodeSummary], str] | None = None,
    expand_to_level: int = 1,
    badge: Callable[[NodeSummary], str] | None = None,
) -> None:
    """Render the manual's tree.

    `on_select` is a function that takes a NodeSummary and returns a URL
    string for the "Ver" link. If None, no link is shown.
    `expand_to_level` controls which nodes start expanded (0 = roots only,
    1 = roots + children, etc).
    `badge` returns extra text to append to a node's label — se usa para
    marcar qué nodos ya tienen pregunta sin salirse del árbol.
    """
    if not nodes:
        st.info("Este manual no tiene nodos.")
        return

    # Filter out 'Introducción'
    filtered_nodes = [n for n in nodes if n.title and "introducci" not in n.title.lower()]

    children_of: dict[int | None, list[NodeSummary]] = {}
    for n in filtered_nodes:
        children_of.setdefault(n.parent_id, []).append(n)
    for kids in children_of.values():
        kids.sort(key=lambda x: x.sort_key)

    roots = children_of.get(None, [])
    for root in roots:
        _render_node(root, children_of, on_select, expand_to_level, depth=0, badge=badge)


def _render_node(
    node: NodeSummary,
    children_of: dict[int | None, list[NodeSummary]],
    on_select: Callable[[NodeSummary], str] | None,
    expand_to_level: int,
    depth: int,
    badge: Callable[[NodeSummary], str] | None = None,
) -> None:
    children = children_of.get(node.id, [])
    icon = _icon_for(node)
    
    extra = badge(node) if badge is not None else ""
    
    # Clean label parts
    prefix = ""
    if node.level_label and node.level_label.upper() != "PARTE":
        prefix = f"**{node.level_label} {node.ordinal}**".strip()
        
    label_parts = [icon]
    if prefix:
        label_parts.append(prefix)
        
    if node.title:
        if prefix:
            label_parts.append(f"— {node.title}")
        else:
            label_parts.append(node.title)
            
    if node.chunk_count:
        label_parts.append(f"  ·  {node.chunk_count} chunk(s)")
        
    if extra:
        label_parts.append(f"  ·  {extra}")
        
    label = " ".join(p for p in label_parts if p)

    if not children:
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            st.markdown(_indent(depth) + label)
        with col2:
            if on_select is not None:
                st.markdown(f"[Ver]({on_select(node)})")
        return

    expanded = depth < expand_to_level
    with st.expander(_indent(depth) + label, expanded=expanded):
        if on_select is not None:
            st.markdown(f"[Ver este nodo]({on_select(node)})")
        for child in children:
            _render_node(child, children_of, on_select, expand_to_level, depth + 1, badge=badge)


def _icon_for(node: NodeSummary) -> str:
    if node.is_anexo:
        return "📎"
    return {
        0: "📚",
        1: "📖",
        2: "📄",
        3: "•",
    }.get(node.level, "·")


def _indent(depth: int) -> str:
    return "&nbsp;&nbsp;&nbsp;&nbsp;" * depth

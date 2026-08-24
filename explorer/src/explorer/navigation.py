"""Helpers for query-param navigation between pages.

Streamlit's `st.query_params` exposes URL query string. We normalize get/set
and provide `link_to(page, **params)` to build internal links.
"""

from __future__ import annotations

from urllib.parse import urlencode

import streamlit as st


def get_int(name: str) -> int | None:
    raw = st.query_params.get(name)
    if raw is None:
        return None
    try:
        return int(raw)
    except (ValueError, TypeError):
        return None


def set_params(**params: object) -> None:
    """Replace current query params with the given mapping (None values dropped)."""
    cleaned = {k: str(v) for k, v in params.items() if v is not None}
    st.query_params.clear()
    for k, v in cleaned.items():
        st.query_params[k] = v


def link_to(page_url: str, **params: object) -> str:
    """Build an internal Streamlit link.

    `page_url` is the relative path Streamlit assigns to a page, e.g. "Manual"
    for `pages/1_📄_Manual.py`. Streamlit normalizes filenames into URL slugs.
    """
    cleaned = {k: str(v) for k, v in params.items() if v is not None}
    qs = urlencode(cleaned)
    base = f"/{page_url}" if not page_url.startswith("/") else page_url
    return f"{base}?{qs}" if qs else base


PAGE_MANUAL = "Manual"
PAGE_NODE = "Node"
PAGE_TOC = "TOC"
PAGE_RAW = "Raw_Elements"
PAGE_SEARCH = "Search"
PAGE_QUESTIONS = "Preguntas"

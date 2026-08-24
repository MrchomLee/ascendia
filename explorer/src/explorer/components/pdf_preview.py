"""Render a single PDF page to PNG bytes via PyMuPDF."""

from __future__ import annotations

from pathlib import Path

import streamlit as st


@st.cache_data(ttl=600, max_entries=64, show_spinner=False)
def render_page(pdf_path: str, page_number: int, dpi: int = 120) -> bytes | None:
    """Return PNG bytes of the given page (1-based), or None if unavailable.

    Cached so a slider over a node's pages doesn't re-render each click.
    """
    p = Path(pdf_path)
    if not p.exists():
        return None
    try:
        import pymupdf

        with pymupdf.open(p) as doc:
            idx = max(0, min(page_number - 1, len(doc) - 1))
            page = doc[idx]
            pix = page.get_pixmap(dpi=dpi)
            return pix.tobytes("png")
    except Exception:
        return None


def render_page_widget(pdf_path: str, page_number: int, *, dpi: int = 120, caption: str | None = None) -> None:
    """Convenience: render and display in one call."""
    img = render_page(pdf_path, page_number, dpi=dpi)
    if img is None:
        st.warning(f"No pude renderizar la página {page_number} de `{pdf_path}`.")
        return
    st.image(img, caption=caption or f"Página {page_number}", width="stretch")

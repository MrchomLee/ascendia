from __future__ import annotations

import streamlit as st


def kpi_row(items: list[tuple[str, object, str | None]]) -> None:
    """Render a row of `st.metric` cards.

    items is a list of (label, value, delta_or_help_text). The third value
    becomes `help` text shown on hover.
    """
    if not items:
        return
    cols = st.columns(len(items))
    for col, (label, value, help_text) in zip(cols, items):
        with col:
            # Un item con label vacío es relleno para cuadrar la fila: ocupa
            # columna pero no se pinta (`st.metric` avisa si el label va vacío).
            if not label:
                continue
            st.metric(label=label, value=value, help=help_text)

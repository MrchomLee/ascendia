"""TOC explorer — parsed entries + gap analysis vs persisted nodes."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from dotenv import load_dotenv

import streamlit as st

from etl.extraction.toc_parser import TocResult, parse_toc

from explorer.components import kpi_row
from explorer.data_access import get_manual, get_tree, list_manuals
from explorer.navigation import PAGE_MANUAL, PAGE_NODE, get_int, link_to, set_params

load_dotenv()
st.set_page_config(page_title="TOC", page_icon="📑", layout="wide")
st.title("📑 TOC explorer")

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
    if st.button("Abrir TOC"):
        set_params(manual_id=selected)
        st.rerun()
    st.stop()

manual = get_manual(manual_id)
if manual is None:
    st.error(f"Manual {manual_id} no encontrado.")
    st.stop()

st.markdown(
    f"[← {manual.code}]({link_to(PAGE_MANUAL, manual_id=manual.id)})  ·  Fuente: `{manual.source_path}`"
)


def _normalize(text: str) -> str:
    """Título comparable: sin acentos, sin puntuación y en minúsculas.

    El TOC y los nodos escriben el mismo título de formas distintas —«SECCIÓN
    PRIMERA.» contra «Sección Primera»—, así que compararlos en crudo daría
    huecos que no existen.
    """
    plain = unicodedata.normalize("NFKD", text or "")
    plain = "".join(c for c in plain if not unicodedata.combining(c))
    plain = re.sub(r"[^a-z0-9 ]+", " ", plain.lower())
    return " ".join(plain.split())


def _compose_title(level_label: str, ordinal: str, title: str) -> str:
    """Un nodo, escrito como aparecería en el índice: «Capítulo II Del fuero»."""
    return " ".join(part for part in (level_label, ordinal, title) if part).strip()


@st.cache_data(ttl=600, show_spinner="Parseando TOC del PDF…")
def _parse(source_path: str) -> dict:
    pdf = Path(source_path)
    if not pdf.exists():
        return {"error": f"PDF no encontrado: {pdf}"}
    result: TocResult = parse_toc(pdf)
    return result.model_dump(mode="json")


parsed = _parse(manual.source_path)
if "error" in parsed:
    st.error(parsed["error"])
    st.stop()

found = parsed["confidence"] >= 0.4 and len(parsed["entries"]) >= 5
range_str = (
    f"{parsed['page_range'][0]}-{parsed['page_range'][1]}" if parsed.get("page_range") else "—"
)

kpi_row(
    [
        ("¿TOC detectado?", "✅" if found else "❌", None),
        ("Confianza", f"{parsed['confidence']:.2f}", "Líneas de TOC que matchearon el patrón"),
        ("Entradas", len(parsed["entries"]), None),
        ("Páginas TOC", range_str, None),
    ]
)

st.divider()
tab_entries, tab_gaps = st.tabs(["Entradas", "Gaps vs nodos"])

with tab_entries:
    entries = parsed["entries"]
    if not entries:
        st.info("Sin entradas detectadas.")
    else:
        depth_filter = st.multiselect(
            "Filtrar por depth",
            options=sorted({e["depth"] for e in entries}),
            default=[],
        )
        rows = [
            {
                "depth": e["depth"],
                "page": e["page"],
                "raw_title": e["raw_title"],
                "marker": (e.get("metadata") or {}).get("leader_marker", ""),
                "line": e["line_number"],
            }
            for e in entries
            if not depth_filter or e["depth"] in depth_filter
        ]
        st.dataframe(rows, width="stretch", hide_index=True)

with tab_gaps:
    nodes = get_tree(manual.id)
    toc_titles = [(_normalize(e["raw_title"]), e) for e in parsed["entries"]]
    node_titles = [(_normalize(_compose_title(n.level_label, n.ordinal, n.title)), n) for n in nodes]

    toc_set = {t for t, _ in toc_titles}
    node_set = {t for t, _ in node_titles}

    missing_in_nodes = [e for t, e in toc_titles if t not in node_set]
    missing_in_toc = [n for t, n in node_titles if t not in toc_set]

    kpi_row(
        [
            ("Entradas TOC", len(toc_titles), None),
            ("Nodos en BD", len(node_titles), None),
            ("Sin nodo", len(missing_in_nodes), "TOC entry sin un nodo correspondiente"),
            ("Sin entrada TOC", len(missing_in_toc), "Nodo sin entrada en el TOC parseado"),
        ]
    )

    st.subheader("Entradas TOC sin nodo correspondiente")
    if missing_in_nodes:
        st.dataframe(
            [
                {"depth": e["depth"], "raw_title": e["raw_title"], "page": e["page"]}
                for e in missing_in_nodes
            ],
            width="stretch",
            hide_index=True,
        )
    else:
        st.success("Cada entrada del TOC tiene un nodo. 👌")

    st.subheader("Nodos sin entrada en el TOC")
    if missing_in_toc:
        for n in missing_in_toc[:200]:
            st.markdown(
                f"- [{n.level_label} {n.ordinal} — {n.title}]"
                f"({link_to(PAGE_NODE, node_id=n.id)}) (p.{n.page_start})"
            )
        if len(missing_in_toc) > 200:
            st.caption(f"… y {len(missing_in_toc) - 200} más.")
    else:
        st.success("Cada nodo está respaldado por una entrada del TOC. 👌")


def _normalize(s: str) -> str:
    """Loose match: strip accents, lowercase, collapse whitespace."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[—–\-·:]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


def _compose_title(level_label: str, ordinal: str, title: str) -> str:
    if title:
        return f"{level_label} {ordinal} — {title}".strip()
    return f"{level_label} {ordinal}".strip()

"""Smoke test for the TOC parser using the real DN M 1455 sample PDF.

The test is skipped if the user hasn't placed the sample under
data/raw_pdfs/. We do this so CI / fresh checkouts don't fail when the PDF
isn't available.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from etl.extraction.toc_parser import parse_toc


_CANDIDATE_PATHS = [
    Path("data/raw_pdfs/dn_m_1455.pdf"),
    Path(r"C:\Users\jgome\Downloads\Manual de Operaciones MIlitares-1-20.pdf"),
]


def _find_sample() -> Path | None:
    for p in _CANDIDATE_PATHS:
        if p.exists():
            return p
    return None


@pytest.mark.skipif(_find_sample() is None, reason="DN M 1455 sample PDF not available")
def test_dn_m_1455_toc_extraction():
    pdf = _find_sample()
    assert pdf is not None
    result = parse_toc(pdf)

    assert result.found, f"TOC not detected (confidence={result.confidence})"
    assert len(result.entries) >= 100, f"too few entries: {len(result.entries)}"

    titles = [e.raw_title for e in result.entries]
    joined = " || ".join(titles)
    assert "PRIMERA PARTE" in joined
    assert "SEGUNDA PARTE" in joined
    assert "Teoría de la Guerra" in joined
    assert "Subsección (A)" in joined

    levels = {e.depth for e in result.entries}
    assert {0, 1, 2, 3}.issubset(levels), f"missing levels: got {levels}"

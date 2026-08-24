"""Parses the Table of Contents (Índice) of a military manual.

Strategy
--------
Military manuals like the DN M 1455 ship a dense, well-structured TOC in their
prefatory pages (roman-numbered: i, ii, iii, ...). Each entry follows the
pattern ``<title> .................... <page>`` with dotted leaders. Parsing
this TOC first gives us the canonical hierarchy, which is much more reliable
than detecting headings in the body.

The parser is heuristic but conservative: if it cannot confidently identify
the TOC, callers fall back to body-only heading detection.
"""

from __future__ import annotations

import re
from pathlib import Path

from pydantic import BaseModel, Field


_LEADER_CHARS = r"\.…"
_TOC_LINE_RE = re.compile(
    rf"""
    ^\s*
    (?P<title>.+?)                          # title text (non-greedy)
    [{_LEADER_CHARS}\s]{{3,}}               # 3+ chars made of dots / ellipses / spaces
    [{_LEADER_CHARS}]                       # final separator must be a leader char
    \s*
    (?P<page>\d+|[ivxlcdm]+)                # arabic or lowercase roman page number
    \s*$
    """,
    re.VERBOSE | re.IGNORECASE,
)

_DOT_LEADER_RE = re.compile(rf"[{_LEADER_CHARS}]{{2,}}")
_LEVEL_MARKER_RE = re.compile(
    r"""
    ^[\s\-–·]*
    (?:
        Cap[ií]tulo\s+[IVXLCDM]+
      | (?:Primera|Segunda|Tercera|Cuarta|Quinta|Sexta|S[eé]ptima|Octava|Novena|D[eé]cima|[ÚU]nica)\s+Secci[oó]n
      | Secci[oó]n\s+(?:Primera|Segunda|Tercera|Cuarta|Quinta|Sexta|S[eé]ptima|Octava|Novena|D[eé]cima|[ÚU]nica)
      | Subsecci[oó]n\s*\([A-Z]\)
      | (?:PRIMERA|SEGUNDA|TERCERA|CUARTA|QUINTA|SEXTA|S[EÉ]PTIMA|OCTAVA|NOVENA|D[EÉ]CIMA)\s+PARTE
      | Anexo\s*"?[A-Z]"?
    )
    \s*$
    """,
    re.VERBOSE | re.IGNORECASE,
)


class TocEntry(BaseModel):
    raw_title: str
    page: int = Field(description="Physical page where this entry starts (1-based).")
    depth: int = Field(
        default=0,
        description="Nesting depth inferred from indentation/level keywords. "
        "0 = top-level (Parte/Capítulo), increasing for sections/subsections.",
    )
    line_number: int = Field(description="Source line within the TOC pages.")
    metadata: dict = Field(default_factory=dict)


class TocResult(BaseModel):
    entries: list[TocEntry]
    page_range: tuple[int, int] | None = Field(
        default=None,
        description="Inclusive (start, end) physical pages where the TOC was found.",
    )
    confidence: float = Field(
        default=0.0,
        description="0..1 — fraction of TOC-page lines that matched the entry pattern.",
    )

    @property
    def found(self) -> bool:
        return self.confidence >= 0.4 and len(self.entries) >= 5


def detect_toc_pages(pdf_path: Path, max_scan_pages: int = 30) -> tuple[int, int] | None:
    """Find the contiguous range of pages that look like a TOC.

    A page is "TOC-like" if it has a high density of dot-leader lines
    (``....``-followed-by-page-number).
    """
    import pymupdf

    doc = pymupdf.open(pdf_path)
    try:
        toc_pages: list[int] = []
        for i in range(min(len(doc), max_scan_pages)):
            text = doc[i].get_text("text")
            lines = text.splitlines()
            if not lines:
                continue
            dot_lines = sum(1 for line in lines if _DOT_LEADER_RE.search(line))
            if dot_lines >= 5 and dot_lines / max(len(lines), 1) >= 0.2:
                toc_pages.append(i)
        if not toc_pages:
            return None
        start = toc_pages[0]
        end = start
        for p in toc_pages[1:]:
            if p == end + 1:
                end = p
            else:
                break
        return (start + 1, end + 1)  # convert to 1-based
    finally:
        doc.close()


def parse_toc(pdf_path: Path) -> TocResult:
    """Detect TOC pages and parse them into a flat list of TocEntry.

    The parser collects all lines from the TOC pages into one buffer, then walks
    them. When a line matches the TOC pattern (title + leader + page), we look
    backward up to 3 non-empty lines for an explicit level marker (Capítulo X,
    Primera Sección, Subsección (A), Anexo "A", PRIMERA PARTE) and attach it.
    """
    import pymupdf

    page_range = detect_toc_pages(pdf_path)
    if page_range is None:
        return TocResult(entries=[], page_range=None, confidence=0.0)

    start, end = page_range
    lines: list[str] = []
    doc = pymupdf.open(pdf_path)
    try:
        for page_idx in range(start - 1, end):
            text = doc[page_idx].get_text("text")
            lines.extend(text.splitlines())
    finally:
        doc.close()

    entries: list[TocEntry] = []
    total_candidates = 0
    matched = 0
    pending_parte: str | None = None  # collected when a "PRIMERA PARTE" line is seen, attached to the next entry

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.isdigit() or _is_roman_only(stripped):
            continue

        if pm := _PARTE_HEADER_RE.match(stripped):
            parte_title = _peek_parte_title(lines, i)
            label = (
                f"{pm.group('ordinal').upper()} PARTE"
                + (f" — {parte_title}" if parte_title else "")
            )
            pending_parte = label
            continue

        total_candidates += 1
        m = _TOC_LINE_RE.match(line)
        if not m:
            continue
        matched += 1
        raw_title = m.group("title").strip(" -·–·\t")
        page = _parse_page_number(m.group("page"))

        if pending_parte:
            entries.append(
                TocEntry(
                    raw_title=pending_parte,
                    page=page,
                    depth=0,
                    line_number=i + 1,
                    metadata={"is_parte": True},
                )
            )
            pending_parte = None

        marker = _lookback_marker(lines, i)
        if marker:
            full_title = f"{marker} — {raw_title}"
            depth = _infer_depth(marker, marker)
        else:
            full_title = raw_title
            depth = _infer_depth(raw_title, line)

        entries.append(
            TocEntry(
                raw_title=full_title,
                page=page,
                depth=depth,
                line_number=i + 1,
                metadata={"leader_marker": marker} if marker else {},
            )
        )

    confidence = matched / max(total_candidates, 1)
    return TocResult(entries=entries, page_range=page_range, confidence=confidence)


def _peek_parte_title(lines: list[str], idx: int, window: int = 3) -> str | None:
    """After a 'PRIMERA PARTE' line, the next non-empty line is usually the part title (e.g. 'LA GUERRA')."""
    for j in range(idx + 1, min(idx + 1 + window, len(lines))):
        s = lines[j].strip()
        if not s or s.isdigit() or _is_roman_only(s):
            continue
        if _PARTE_HEADER_RE.match(s):
            continue
        if _TOC_LINE_RE.match(lines[j]):
            return None
        return s
    return None


def _lookback_marker(lines: list[str], idx: int, window: int = 3) -> str | None:
    """Return the nearest preceding non-empty line that matches a level marker."""
    seen = 0
    j = idx - 1
    while j >= 0 and seen < window:
        s = lines[j].strip()
        if s and not s.isdigit() and not _is_roman_only(s):
            seen += 1
            if _LEVEL_MARKER_RE.match(s):
                return s
        j -= 1
    return None


def _is_roman_only(s: str) -> bool:
    return bool(s) and all(ch.lower() in "ivxlcdm" for ch in s.replace(" ", ""))


def _parse_page_number(s: str) -> int:
    s = s.strip().lower()
    if s.isdigit():
        return int(s)
    return _roman_to_int(s)


_ROMAN_VALUES = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100, "d": 500, "m": 1000}


def _roman_to_int(s: str) -> int:
    result = 0
    prev = 0
    for ch in reversed(s):
        v = _ROMAN_VALUES.get(ch, 0)
        if v < prev:
            result -= v
        else:
            result += v
        prev = v
    return result


_DEPTH_KEYWORDS: list[tuple[re.Pattern[str], int]] = [
    (re.compile(r"^\s*(primera|segunda|tercera|cuarta|quinta|sexta|s[eé]ptima|octava|novena|d[eé]cima)\s+parte\b", re.IGNORECASE), 0),
    (re.compile(r"^\s*cap[ií]tulo\b", re.IGNORECASE), 1),
    (re.compile(r"^\s*(primera|segunda|tercera|cuarta|quinta|sexta|s[eé]ptima|octava|novena|d[eé]cima|[uú]nica)\s+secci[oó]n\b", re.IGNORECASE), 2),
    (re.compile(r"^\s*secci[oó]n\s+(primera|segunda|tercera|cuarta|quinta|sexta|s[eé]ptima|octava|novena|d[eé]cima|[uú]nica)\b", re.IGNORECASE), 2),
    (re.compile(r"^[\s\-–·]*subsecci[oó]n\b", re.IGNORECASE), 3),
    (re.compile(r"^\s*anexo\b", re.IGNORECASE), 0),
]


_PARTE_HEADER_RE = re.compile(
    r"^\s*(?P<ordinal>PRIMERA|SEGUNDA|TERCERA|CUARTA|QUINTA|SEXTA|S[EÉ]PTIMA|OCTAVA|NOVENA|D[EÉ]CIMA)\s+PARTE\s*$",
    re.IGNORECASE,
)


def _infer_depth(title: str, original_line: str) -> int:
    for pattern, depth in _DEPTH_KEYWORDS:
        if pattern.search(title):
            return depth
    indent = len(original_line) - len(original_line.lstrip())
    return min(indent // 4, 4)

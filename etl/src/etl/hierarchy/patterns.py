"""Heading-pattern matchers for Spanish military / legal Mexican documents.

Design
------
Each matcher (``match_parte``, ``match_libro``, …) is **profile-agnostic**:
it only decides whether a line is a heading of a given *kind* (PARTE,
CAPITULO, ARTICULO, …) and pulls out the ordinal. The numeric depth at
which that kind sits in the hierarchy is decided **by the active
:class:`DocumentProfile`** (see :mod:`etl.hierarchy.profile`).

This separation lets the same `Capítulo` regex sit at depth 1 in a manual
(`PARTE → Capítulo → Sección`) and at depth 2 in a legal code
(`Libro → Título → Capítulo → Artículo`) without duplicating regex.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


KIND_PARTE = "PARTE"
KIND_LIBRO = "LIBRO"
KIND_TITULO = "TITULO"
KIND_CAPITULO = "CAPITULO"
KIND_SECCION = "SECCION"
KIND_SUBSECCION = "SUBSECCION"
KIND_ARTICULO = "ARTICULO"
KIND_ANEXO = "ANEXO"

KIND_LABELS: dict[str, str] = {
    KIND_PARTE: "PARTE",
    KIND_LIBRO: "LIBRO",
    KIND_TITULO: "TÍTULO",
    KIND_CAPITULO: "Capítulo",
    KIND_SECCION: "Sección",
    KIND_SUBSECCION: "Subsección",
    KIND_ARTICULO: "Artículo",
    KIND_ANEXO: "Anexo",
}


@dataclass(frozen=True)
class HeadingCandidate:
    """Profile-agnostic match: kind + ordinal, no numeric depth."""

    kind: str
    ordinal: str
    title_remainder: str = ""
    is_anexo: bool = False


# ---- Regexes ---------------------------------------------------------------

_SPANISH_ORDINALS = (
    # Compound (no space) — must come before bare to take precedence in alternation
    r"D[ÉE]CIMO?PRIMER[OA]?|D[ÉE]CIMO?SEGUND[OA]|D[ÉE]CIMO?TERCER[OA]?|"
    r"D[ÉE]CIMO?CUART[OA]|D[ÉE]CIMO?QUINT[OA]|D[ÉE]CIMO?SEXT[OA]|"
    r"D[ÉE]CIMO?S[ÉE]PTIM[OA]|D[ÉE]CIMO?OCTAV[OA]|D[ÉE]CIMO?NOVEN[OA]|"
    r"VIG[ÉE]SIMO?PRIMER[OA]?|VIG[ÉE]SIMO?SEGUND[OA]|VIG[ÉE]SIMO?TERCER[OA]?|"
    r"VIG[ÉE]SIMO?CUART[OA]|VIG[ÉE]SIMO?QUINT[OA]|"
    # Compound (with space)
    r"D[ÉE]CIM[OA]\s+PRIMER[OA]?|D[ÉE]CIM[OA]\s+SEGUND[OA]|"
    r"D[ÉE]CIM[OA]\s+TERCER[OA]?|D[ÉE]CIM[OA]\s+CUART[OA]|"
    r"D[ÉE]CIM[OA]\s+QUINT[OA]|D[ÉE]CIM[OA]\s+SEXT[OA]|"
    # Bare ordinals
    r"PRIMER[OA]?|SEGUND[OA]|TERCER[OA]?|CUART[OA]|QUINT[OA]|SEXT[OA]|"
    r"S[ÉE]PTIM[OA]|OCTAV[OA]|NOVEN[OA]|D[ÉE]CIM[OA]|VIG[ÉE]SIM[OA]|"
    r"UND[ÉE]CIM[OA]|DUOD[ÉE]CIM[OA]|"
    # Special / non-numeric
    r"[ÚU]NIC[OA]|PRELIMINAR"
)

_PARTE_RE = re.compile(
    rf"""
    ^\s*
    (?P<ordinal>{_SPANISH_ORDINALS})
    \s+PARTE
    (?:\s+(?P<title>.+?))?
    \s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)

_LIBRO_RE = re.compile(
    rf"""
    ^\s*
    Libro\s+
    (?P<ordinal>{_SPANISH_ORDINALS})
    (?:\s+(?P<title>.+?))?      # optional trailing title on same line
    \s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)

_TITULO_RE = re.compile(
    rf"""
    ^\s*
    T[ÍI]TULO\s+
    (?P<ordinal>[IVXLCDM]+|\d+|{_SPANISH_ORDINALS})
    (?:\s+(?P<title>.+?))?      # optional trailing title on same line
    \s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)

_CAPITULO_RE = re.compile(
    r"""
    ^\s*
    Cap[ÍI]tulo
    \s+
    (?P<ordinal>[IVXLCDM]+(?:\s+(?:Bis|Ter|Quater|Quinquies))?|\d+|[A-Z])
    (?:\s*[-–:.\s]+(?P<title>.+))?
    \s*$
    """,
    re.VERBOSE | re.IGNORECASE,
)

_SECCION_RE = re.compile(
    rf"""
    ^\s*
    (?:
        (?P<ord_a>{_SPANISH_ORDINALS})
        \s+Secci[oó]n
      |
        Secci[oó]n
        \s+(?P<ord_b>{_SPANISH_ORDINALS})
    )
    \s*$
    """,
    re.VERBOSE | re.IGNORECASE,
)

_SUBSECCION_RE = re.compile(
    r"""
    ^[\s\-–·]*
    Subsecci[oó]n
    \s*\(\s*(?P<ordinal>[A-Z])\s*\)
    \s*$
    """,
    re.VERBOSE | re.IGNORECASE,
)

# Articles in Mexican legal codes:
#   "Artículo 1o.-",  "Artículo 9o. Bis.-",  "Artículo 1°.-",  "Articulo 1.-"
# Optional title trailer accepted but rare ("Artículo 1.- De los...")
_ARTICULO_RE = re.compile(
    r"""
    ^\s*
    Art[íi]culo
    \s+
    (?P<num>\d+)
    (?:\s*[oº°]\.?)?                  # ordinal indicator: o, º, °
    (?:
        \s*\.?\s*
        (?P<suffix>
            Bis|Ter|Qu[áa]ter|Quinquies|Sexies|Septies|Octies|Nonies|Decies
            |Quintus|Sextus|Septimus|Octavus|Nonus|Decimus
        )
    )?
    \.?\s*[-–]?\s*
    (?P<title>.*)?
    $
    """,
    re.VERBOSE | re.IGNORECASE,
)

_ANEXO_RE = re.compile(
    r"""
    ^\s*
    Anexo
    \s*"?(?P<ordinal>[A-Z])"?
    (?:\s*[-–:.\s]+(?P<title>.+))?
    \s*$
    """,
    re.VERBOSE | re.IGNORECASE,
)


# ---- Per-kind matchers -----------------------------------------------------


def match_parte(text: str) -> HeadingCandidate | None:
    if m := _PARTE_RE.match(text.strip()):
        return HeadingCandidate(
            kind=KIND_PARTE, 
            ordinal=_norm_ordinal(m.group("ordinal")).upper(),
            title_remainder=(m.groupdict().get("title") or "").strip()
        )
    return None


def match_libro(text: str) -> HeadingCandidate | None:
    if m := _LIBRO_RE.match(text.strip()):
        return HeadingCandidate(
            kind=KIND_LIBRO,
            ordinal=_norm_ordinal(m.group("ordinal")).upper(),
            title_remainder=(m.groupdict().get("title") or "").strip(),
        )
    return None


def match_titulo(text: str) -> HeadingCandidate | None:
    if m := _TITULO_RE.match(text.strip()):
        return HeadingCandidate(
            kind=KIND_TITULO,
            ordinal=_norm_ordinal(m.group("ordinal")).upper(),
            title_remainder=(m.groupdict().get("title") or "").strip(),
        )
    return None


def match_capitulo(text: str) -> HeadingCandidate | None:
    if m := _CAPITULO_RE.match(text.strip()):
        return HeadingCandidate(
            kind=KIND_CAPITULO,
            ordinal=_norm_ordinal(m.group("ordinal")).upper(),
            title_remainder=(m.group("title") or "").strip(),
        )
    return None


def match_seccion(text: str) -> HeadingCandidate | None:
    text_clean = re.sub(r"Terce\s*r\s*a", "Tercera", text, flags=re.IGNORECASE)
    if m := _SECCION_RE.match(text_clean.strip()):
        ordinal = m.group("ord_a") or m.group("ord_b") or ""
        return HeadingCandidate(kind=KIND_SECCION, ordinal=_norm_ordinal(ordinal).capitalize())
    return None


def match_subseccion(text: str) -> HeadingCandidate | None:
    if m := _SUBSECCION_RE.match(text):
        return HeadingCandidate(kind=KIND_SUBSECCION, ordinal=f"({m.group('ordinal').upper()})")
    return None


def match_articulo(text: str) -> HeadingCandidate | None:
    text = text.strip()
    if not text.lower().startswith(("artículo", "articulo")):
        return None
    if m := _ARTICULO_RE.match(text):
        num = m.group("num")
        suffix = m.group("suffix")
        ordinal = f"{num}o" + (f" {suffix.capitalize()}" if suffix else "")
        return HeadingCandidate(
            kind=KIND_ARTICULO,
            ordinal=ordinal,
            title_remainder=(m.group("title") or "").strip(),
        )
    return None


def match_anexo(text: str) -> HeadingCandidate | None:
    if m := _ANEXO_RE.match(text.strip()):
        return HeadingCandidate(
            kind=KIND_ANEXO,
            ordinal=m.group("ordinal").upper(),
            title_remainder=(m.group("title") or "").strip(),
            is_anexo=True,
        )
    return None


def _norm_ordinal(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())


# ---- Backwards-compat layer ------------------------------------------------
# Pre-existing code (and external callers) used `classify_heading` returning a
# HeadingMatch with `level: int`. Keep it working by delegating to the
# "manual" profile.


@dataclass(frozen=True)
class HeadingMatch:
    """Profile-resolved heading match: kind + numeric depth."""

    level: int
    level_label: str
    ordinal: str
    title_remainder: str = ""
    is_anexo: bool = False


def classify_heading(text: str) -> HeadingMatch | None:
    """Compatibility shim: classify using the default 'manual' profile.

    New code should use ``DocumentProfile.classify`` directly so the active
    document type drives the depth assignment.
    """
    from etl.hierarchy.profile import PROFILES

    return PROFILES["manual"].classify(text)

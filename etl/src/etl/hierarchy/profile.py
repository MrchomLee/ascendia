"""Document profiles: which heading kinds and filters apply to which doc type.

Each archetype (manual, código legal, ley orgánica, …) defines:

- the **active heading kinds** and their depth in the hierarchy
- regex patterns whose matches should be **dropped from the body** (page
  headers, footers, "X de N" pagination, etc.)
- regex extractors that pull **metadata** off the body (e.g. DOF reform
  annotations) and attach it to the surrounding node

Profiles are intentionally coarse (one per archetype, not one per file).
Most documents in a family share the same profile.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Pattern

from etl.extraction.types import RawElement
from etl.hierarchy.patterns import (
    KIND_ANEXO,
    KIND_ARTICULO,
    KIND_CAPITULO,
    KIND_LABELS,
    KIND_LIBRO,
    KIND_PARTE,
    KIND_SECCION,
    KIND_SUBSECCION,
    KIND_TITULO,
    HeadingCandidate,
    HeadingMatch,
    match_anexo,
    match_articulo,
    match_capitulo,
    match_libro,
    match_parte,
    match_seccion,
    match_subseccion,
    match_titulo,
    KIND_EJERCICIO,
    match_ejercicio,
    KIND_MISCELANEA,
    match_miscelanea,
    KIND_RESPUESTAS,
    match_respuestas,
    KIND_BALDOR_TEMA,
    match_baldor_capitulo,
    match_baldor_caso,
    match_baldor_inciso,
    match_baldor_subseccion_romana,
    match_baldor_tema_mayusculas,
    KIND_BLOQUE,
    KIND_PARTE_TEMARIO,
    match_bloque,
    match_parte_temario,
    KIND_TEMA,
    match_tema,
)
from etl.hierarchy.temario import CapitulosConTemas, Temario


# El orden importa: los patrones más específicos primero.
_ALL_MATCHERS: list[tuple[str, Callable[[str], HeadingCandidate | None]]] = [
    (KIND_SUBSECCION, match_baldor_inciso),
    (KIND_SUBSECCION, match_subseccion),
    (KIND_ARTICULO, match_articulo),
    (KIND_PARTE, match_parte),
    (KIND_LIBRO, match_libro),
    (KIND_SECCION, match_baldor_caso),
    (KIND_SECCION, match_baldor_subseccion_romana),
    (KIND_SECCION, match_seccion),
    (KIND_CAPITULO, match_capitulo),
    (KIND_CAPITULO, match_baldor_capitulo),
    (KIND_BALDOR_TEMA, match_baldor_tema_mayusculas),
    (KIND_TITULO, match_titulo),
    (KIND_ANEXO, match_anexo),
    (KIND_EJERCICIO, match_ejercicio),
    (KIND_MISCELANEA, match_miscelanea),
    (KIND_RESPUESTAS, match_respuestas),
    (KIND_BLOQUE, match_bloque),
    (KIND_PARTE_TEMARIO, match_parte_temario),
    (KIND_TEMA, match_tema),
]


@dataclass
class DocumentProfile:
    """Configuration of one document archetype.

    Parameters
    ----------
    name
        Stable identifier (``"manual"``, ``"codigo_legal"``, …) used by the
        CLI ``--profile`` flag and stored in :class:`Manual.metadata_json`.
    kind_to_depth
        Mapping of heading kind → numeric depth in the hierarchy. Lower is
        more general. Anexos always behave as parallel branches under the
        manual root regardless of their depth value.
    drop_text_patterns
        Compiled regex; if **any** of these matches an element's text, the
        element is filtered out before hierarchy assembly. Used to silence
        Cámara-de-Diputados banners, "X de N" footers, and similar noise.
    metadata_extractors
        Compiled regex keyed by metadata field name. When an element matches
        an extractor, its captured group is attached to the **closest open
        node** instead of being added as body text. Useful for DOF reform
        annotations alongside articles.
    element_selector
        Optional ``(elements, indices) -> (elements, indices)`` applied after the
        drop filters: whatever it leaves out is excluded from the tree (see
        :class:`~etl.hierarchy.temario.Temario`).
    """

    name: str
    kind_to_depth: dict[str, int]
    drop_text_patterns: list[Pattern[str]] = field(default_factory=list)
    clean_text_patterns: list[tuple[Pattern[str], str]] = field(default_factory=list)
    metadata_extractors: dict[str, Pattern[str]] = field(default_factory=dict)
    element_selector: Callable[[list[RawElement], list[int]], tuple[list[RawElement], list[int]]] | None = None

    @property
    def active_kinds(self) -> set[str]:
        return set(self.kind_to_depth.keys())

    def clean_text(self, text: str) -> str:
        if not self.clean_text_patterns:
            return text
        for pattern, repl in self.clean_text_patterns:
            text = pattern.sub(repl, text)
        return text

    def classify(self, text: str) -> HeadingMatch | None:
        """Return a profile-resolved HeadingMatch, or None if not a heading."""
        if not text or not text.strip():
            return None
        for kind, matcher in _ALL_MATCHERS:
            if kind not in self.active_kinds:
                continue
            cand = matcher(text)
            if cand is None:
                continue
            depth = self.kind_to_depth[cand.kind]
            return HeadingMatch(
                level=depth,
                level_label=KIND_LABELS[cand.kind],
                ordinal=cand.ordinal,
                title_remainder=cand.title_remainder,
                is_anexo=cand.is_anexo,
            )
        return None

    def is_dropped_text(self, text: str) -> bool:
        if not self.drop_text_patterns:
            return False
        stripped = text.strip()
        if not stripped:
            return False
        return any(p.search(stripped) for p in self.drop_text_patterns)

    def extract_metadata(self, text: str) -> dict[str, str]:
        """Run metadata extractors over `text` and return any captures."""
        out: dict[str, str] = {}
        for key, pattern in self.metadata_extractors.items():
            m = pattern.search(text)
            if m:
                out[key] = (m.group(1) if m.groups() else m.group(0)).strip()
        return out


# ----- Built-in profiles ----------------------------------------------------

_MANUAL_PROFILE = DocumentProfile(
    name="manual",
    kind_to_depth={
        KIND_PARTE: 0,
        KIND_CAPITULO: 1,
        KIND_SECCION: 2,
        KIND_SUBSECCION: 3,
        KIND_ANEXO: 0,
    },
)


_CODIGO_LEGAL_PROFILE = DocumentProfile(
    name="codigo_legal",
    kind_to_depth={
        KIND_LIBRO: 0,
        KIND_TITULO: 1,
        KIND_CAPITULO: 2,
        KIND_ARTICULO: 3,
    },
    drop_text_patterns=[
        re.compile(r"C[ÁA]MARA\s+DE\s+DIPUTADOS\s+DEL\s+H\.?\s+CONGRESO", re.IGNORECASE),
        re.compile(r"Secretar[íi]a\s+(?:General|de\s+Servicios\s+Parlamentarios)", re.IGNORECASE),
        re.compile(r"^\s*\d+\s+de\s+\d+\s*$"),
        re.compile(r".*Reforma DOF.*", re.IGNORECASE),
    ],
    clean_text_patterns=[],
    metadata_extractors={
        "reforma_dof": re.compile(
            r"(?:Art[íi]culo|Fracci[oó]n|Cap[íi]tulo|P[áa]rrafo|Inciso|T[íi]tulo|Libro)\s+"
            r"(?:reformad[oa]|adicionad[oa]|derogad[oa])\s+DOF\s+"
            r"(\d{2}-\d{2}-\d{4})",
            re.IGNORECASE,
        ),
    },
)


_LEY_ORGANICA_PROFILE = DocumentProfile(
    name="ley_organica",
    kind_to_depth={
        KIND_TITULO: 0,
        KIND_CAPITULO: 1,
        KIND_ARTICULO: 2,
    },
    drop_text_patterns=_CODIGO_LEGAL_PROFILE.drop_text_patterns + [
        re.compile(r".*DOF.*", re.IGNORECASE),
        re.compile(r".*Se deroga.*", re.IGNORECASE),
        re.compile(r"^LEY FEDERAL DE ARMAS DE FUEGO Y EXPLOSIVOS\s*$", re.IGNORECASE),
    ],
    metadata_extractors=dict(_CODIGO_LEGAL_PROFILE.metadata_extractors),
)


_LIBRO_TEXTO_PROFILE = DocumentProfile(
    name="libro_texto",
    kind_to_depth={
        KIND_CAPITULO: 0,
        KIND_EJERCICIO: 1,
    },
)


_BALDOR_PROFILE = DocumentProfile(
    name="algebra_baldor",
    # Un nodo por capítulo ("I. Suma" … "XXXII. Números complejos"). Casos,
    # temas y reglas quedan en el cuerpo de su capítulo.
    kind_to_depth={
        KIND_CAPITULO: 0,
    },
    drop_text_patterns=[
        re.compile(r"^\s*Álgebra\s*$", re.IGNORECASE),
        re.compile(r"^\s*Aurelio Baldor\s*$", re.IGNORECASE),
    ],
)



# Recorte "Proceso_comunicativo_y_escritura.pdf" del Taller de Lectura y
# Redacción 1 (Zarzar): solo el temario del examen, como Bloque › Parte.
_TALLER_LECTURA_REDACCION_PROFILE = DocumentProfile(
    name="taller_lectura_redaccion",
    kind_to_depth={
        KIND_BLOQUE: 0,
        KIND_PARTE_TEMARIO: 1,
    },
    element_selector=Temario(
        bloques={1: "Proceso comunicativo", 3: "Proceso de escritura"},
        partes=frozenset({"1.1", "1.2", "3.1", "3.2", "3.3"}),
    ).select,
)


# Recorte "Historia_Universal_Extracto.pdf" de Historia Universal (Rodríguez
# Arvizu, Limusa, 3a. ed. 2017): el Capítulo 6 y sus cuatro temas del temario.
# Los demás subtítulos quedan en el cuerpo de su tema.
_HISTORIA_UNIVERSAL_PROFILE = DocumentProfile(
    name="historia_universal",
    kind_to_depth={
        KIND_CAPITULO: 0,
        KIND_TEMA: 1,
    },
    element_selector=CapitulosConTemas(
        capitulos={
            6: (
                "El Mundo Contemporáneo",
                (
                    "La Guerra Fría",
                    "Las Grandes Organizaciones Internacionales",
                    "Principales acontecimientos de nuestros días",
                    "La llegada del Siglo XXI",
                ),
            ),
        },
    ).select,
)


# Recorte "Geografia_Moderna_de_Mexico_extraccion.pdf" de Geografía Moderna de
# México (Tamayo, Trillas, 15a. ed. 2021): los capítulos y temas del temario;
# Litorales e Islas entran completos. Los demás subtítulos quedan en el cuerpo.
_GEOGRAFIA_MODERNA_MEXICO_PROFILE = DocumentProfile(
    name="geografia_moderna_mexico",
    kind_to_depth={
        KIND_CAPITULO: 0,
        KIND_TEMA: 1,
    },
    element_selector=CapitulosConTemas(
        capitulos={
            1: (
                "Generalidades",
                ("Situación Geográfica", "Extensión", "División Política", "Representación Cartográfica"),
            ),
            3: ("Geomorfología de la República Mexicana", ("Unidades Orogénicas",)),
            4: ("Litorales", ()),
            5: ("Islas", ()),
        },
    ).select,
)


# Recorte "Calculo_Una_Variable_Caps_1_2_3.pdf" de Cálculo, una variable
# (Thomas y Weir, Pearson, 13a. ed. 2015): los tres capítulos, completos. El PDF
# no los numera ("FUNCIONES"), así que se reconocen por su título; secciones
# ("1.1 …") y subtítulos quedan en el cuerpo del capítulo.
_CALCULO_UNA_VARIABLE_PROFILE = DocumentProfile(
    name="calculo_una_variable",
    kind_to_depth={
        KIND_CAPITULO: 0,
    },
    element_selector=CapitulosConTemas(
        capitulos={
            1: ("Funciones", ()),
            2: ("Límites y continuidad", ()),
            3: ("Derivadas", ()),
        },
        por_titulo=True,
    ).select,
)


PROFILES: dict[str, DocumentProfile] = {
    "manual": _MANUAL_PROFILE,
    "codigo_legal": _CODIGO_LEGAL_PROFILE,
    "ley_organica": _LEY_ORGANICA_PROFILE,
    "libro_texto": _LIBRO_TEXTO_PROFILE,
    "algebra_baldor": _BALDOR_PROFILE,
    "taller_lectura_redaccion": _TALLER_LECTURA_REDACCION_PROFILE,
    "historia_universal": _HISTORIA_UNIVERSAL_PROFILE,
    "geografia_moderna_mexico": _GEOGRAFIA_MODERNA_MEXICO_PROFILE,
    "calculo_una_variable": _CALCULO_UNA_VARIABLE_PROFILE,
}


def get_profile(name: str) -> DocumentProfile:
    if name not in PROFILES:
        raise ValueError(f"Unknown profile: {name!r}. Available: {sorted(PROFILES)}")
    return PROFILES[name]


# ----- Auto-detection -------------------------------------------------------


def auto_detect_profile(elements: list, *, sample_chars: int = 4000) -> str:
    """Heuristic profile pick based on the first few elements' text.

    Looks for genre-defining phrases ("LIBRO PRIMERO", "PRIMERA PARTE", …).
    Falls back to ``"manual"`` if no signal — the manual archetype is
    permissive and works on most military-doctrine docs.
    """
    if not elements:
        return "manual"

    sample_parts: list[str] = []
    total = 0
    for el in elements:
        t = getattr(el, "text", "") or ""
        if not t:
            continue
        sample_parts.append(t)
        total += len(t)
        if total >= sample_chars:
            break
    sample = " ".join(sample_parts).lower()

    has_libro = bool(re.search(r"\blibro\s+primero\b", sample))
    has_titulo = bool(re.search(r"\bt[íi]tulo\s+primero\b", sample))
    has_articulo = bool(re.search(r"\bart[íi]culo\s+\d", sample))
    has_codigo = "código de" in sample or "codigo de" in sample
    has_parte = bool(re.search(r"\b(primera|segunda|tercera)\s+parte\b", sample))
    has_manual = "manual de" in sample
    has_ejercicio = "ejercicio" in sample
    has_baldor = "baldor" in sample
    has_algebra = (
        ("álgebra" in sample or "algebra" in sample)
        and any(w in sample for w in ("monomio", "polinomio", "factoriz", "ecuaci", "descomposici"))
    )

    if has_baldor or has_algebra:
        return "algebra_baldor"
    if has_ejercicio and not has_articulo:
        return "libro_texto"
    if has_libro and (has_titulo or has_articulo or has_codigo):
        return "codigo_legal"
    if has_titulo and has_articulo and not has_libro and not has_parte:
        return "ley_organica"
    if has_parte or has_manual:
        return "manual"
    if has_articulo:
        # Fallback for legal-ish docs without explicit "Libro"
        return "ley_organica"
    return "manual"

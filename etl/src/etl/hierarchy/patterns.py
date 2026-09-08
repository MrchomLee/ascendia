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
KIND_EJERCICIO = "EJERCICIO"
KIND_MISCELANEA = "MISCELANEA"
KIND_RESPUESTAS = "RESPUESTAS"
KIND_BALDOR_TEMA = "BALDOR_TEMA"

KIND_LABELS: dict[str, str] = {
    KIND_PARTE: "PARTE",
    KIND_LIBRO: "LIBRO",
    KIND_TITULO: "TÍTULO",
    KIND_CAPITULO: "Capítulo",
    KIND_SECCION: "Sección",
    KIND_SUBSECCION: "Subsección",
    KIND_ARTICULO: "Artículo",
    KIND_ANEXO: "Anexo",
    KIND_EJERCICIO: "Ejercicio",
    KIND_MISCELANEA: "Miscelánea",
    KIND_RESPUESTAS: "Respuestas",
    KIND_BALDOR_TEMA: "Tema",
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

_EJERCICIO_RE = re.compile(
    r"""
    ^\s*
    Ejercicio
    \s+
    (?P<ordinal>\d+)
    (?:\s*[-–:.\s]+(?P<title>.+))?
    \s*$
    """,
    re.VERBOSE | re.IGNORECASE,
)

_MISCELANEA_RE = re.compile(
    r"""
    ^\s*
    Miscel[áa]nea
    (?:\s+sobre\s+(?P<title>.+))?
    \s*$
    """,
    re.VERBOSE | re.IGNORECASE,
)

_RESPUESTAS_RE = re.compile(
    r"""
    ^\s*
    Respuestas(?:\s+a\s+los\s+ejercicios)?
    \s*$
    """,
    re.VERBOSE | re.IGNORECASE,
)

# Patrones para Álgebra de Baldor
_ROMANOS_RE = (
    r"XXXII|XXXI|XXX|XXIX|XXVIII|XXVII|XXVI|XXV|XXIV|XXIII|XXII|XXI|XX|"
    r"XIX|XVIII|XVII|XVI|XV|XIV|XIII|XII|XI|X|"
    r"IX|VIII|VII|VI|V|IV|III|II|I"
)

_BALDOR_CAPITULO_RE = re.compile(
    rf"""
    ^\s*
    (?P<ordinal>{_ROMANOS_RE})
    \.\s+
    (?P<title>[^\n]+)
    \s*$
    """,
    re.VERBOSE,
)

_BALDOR_CASO_RE = re.compile(
    rf"""
    ^\s*
    CASO\s+
    (?P<ordinal>{_ROMANOS_RE}|ESPECIAL)
    (?:\s*:\s*(?P<title>.+))?
    \s*$
    """,
    re.VERBOSE | re.IGNORECASE,
)

_BALDOR_INCISO_RE = re.compile(
    r"""
    ^\s*
    (?P<ordinal>[a-z])
    \)\s+
    (?P<title>.+)
    \s*$
    """,
    re.VERBOSE,
)

_BALDOR_TEMAS_CONOCIDOS = {
    "la suma o adición", "la suma o adicion",
    "carácter general de la suma algebraica", "caracter general de la suma algebraica",
    "regla general para sumar",
    "prueba de la suma por el valor numérico", "prueba de la suma por el valor numerico",
    "la resta o sustracción", "la resta o sustraccion",
    "regla general para restar",
    "carácter general de la resta algebraica", "caracter general de la resta algebraica",
    "uso de los signos de agrupación", "uso de los signos de agrupacion",
    "regla general para suprimir signos de agrupación", "regla general para suprimir signos de agrupacion",
    "introducción de signos de agrupación", "introduccion de signos de agrupacion",
    "regla general para introducir cantidades en signos de agrupación", "regla general para introducir cantidades en signos de agrupacion",
    "la multiplicación", "la multiplicacion",
    "ley de los signos",
    "ley de los exponentes",
    "ley de los coeficientes",
    "casos de la multiplicación", "casos de la multiplicacion",
    "producto continuado",
    "regla para multiplicar un polinomio por un monomio",
    "regla para multiplicar dos polinomios",
    "multiplicación por coeficientes separados", "multiplicacion por coeficientes separados",
    "observación", "observacion",
    "producto continuado de polinomios",
    "cambios de signos en la multiplicación", "cambios de signos en la multiplicacion",
    "la división", "la division",
    "regla para dividir dos monomios",
    "regla para dividir un polinomio entre un monomio",
    "regla para dividir dos polinomios",
    "división de polinomios por el método de coeficientes separados", "division de polinomios por el metodo de coeficientes separados",
    "cociente mixto",
    "valor numerico de expresiones algebraicas con exponentes enteros para valores positivos y negativos",
    "potencias de cantidades negativas",
    "cuadrado de la suma de dos cantidades",
    "cuadrado de la diferencia de dos cantidades",
    "producto de la suma por la diferencia de dos cantidades",
    "cubo de un binomio",
    "igualdad",
    "ecuación", "ecuacion",
    "identidad",
    "miembros",
    "términos", "terminos",
    "clases de ecuaciones",
    "grado",
    "raíces o soluciones", "raices o soluciones",
    "resolver una ecuación", "resolver una ecuacion",
    "axioma fundamental de las ecuaciones",
    "reglas que se derivan de este axioma",
    "la transposición de términos", "la transposicion de terminos",
    "cambio de signos",
    "resolución de ecuaciones enteras de primer grado con una incógnita", "resolucion de ecuaciones enteras de primer grado con una incognita",
    "factores",
    "descomponer en factores o factorizar",
    "factorizar un monomio",
    "factorizar un polinomio",
    "raíz cuadrada de un monomio", "raiz cuadrada de un monomio",
    "regla para conocer si un trinomio es cuadrado perfecto",
    "regla para factorizar una diferencia de cuadrados",
    "regla práctica para factorizar un trinomio de la forma x^2 + bx + c",
    "raíz cúbica de un monomio", "raiz cubica de un monomio",
    "regla 1", "regla 2",
    "factor común o divisor común", "factor comun o divisor comun",
    "máximo común divisor", "maximo comun divisor",
    "m. c. d. de dos polinomios por divisiones sucesivas",
    "reglas especiales",
    "común múltiplo", "comun multiplo",
    "mínimo común múltiplo", "minimo comun multiplo",
    "fracción algebraica", "fraccion algebraica",
    "principios fundamentales de las fracciones",
    "signo de la fracción y de sus términos", "signo de la fraccion y de sus terminos",
    "cambios que pueden hacerse en los signos de una fracción sin que la fracción se altere",
    "cambio de signos cuando los términos de la fracción son polinomios",
    "cambio de signos cuando el numerador o denominador son productos indicados",
    "reducción de fracciones", "reduccion de fracciones",
    "fórmula", "formula",
    "uso y ventaja de las fórmulas algebraicas", "uso y ventaja de las formulas algebraicas",
    "traducción de una fórmula dada al lenguaje vulgar", "traduccion de una formula dada al lenguaje vulgar",
    "expresar por medio de símbolos una ley matemática o física obtenida como resultado de una investigación",
    "cambio del sujeto de una fórmula", "cambio del sujeto de una formula",
    "constantes y variables",
    "función", "funcion",
    "ley de dependencia",
    "ejemplos de funciones, pueda o no establecerse matemáticamente la ley de dependencia",
    "variación directa", "variacion directa",
    "variación inversa", "variacion inversa",
    "variación conjunta", "variacion conjunta",
    "funciones expresables por fórmulas", "funciones expresables por formulas",
    "sistema rectangular de coordenadas cartesianas",
    "abscisa y ordenada de un punto",
    "signo de las coordenadas",
    "determinación de un punto por sus coordenadas", "determinacion de un punto por sus coordenadas",
    "papel cuadriculado",
    "gráfico de una relación", "grafico de una relacion",
    "representación gráfica de la función lineal de primer grado", "representacion grafica de la funcion lineal de primer grado",
    "ecuaciones simultáneas", "ecuaciones simultaneas",
    "ecuaciones equivalentes",
    "sistema de ecuaciones",
    "resolución", "resolucion",
    "métodos de eliminación más usuales", "metodos de eliminacion mas usuales",
    "resolución de sistemas numéricos de dos ecuaciones enteras con dos incógnitas",
    "ecuaciones simultáneas con incógnitas en los denominadores",
    "determinante",
    "desarrollo de un determinante de segundo orden",
    "resolución por determinantes de un sistema de dos ecuaciones con dos incógnitas",
    "resolución gráfica de un sistema de dos ecuaciones con dos incógnitas",
    "cantidades imaginarias",
    "unidad imaginaria",
    "notación", "notacion",
    "potencias de la unidad imaginaria",
    "imaginarias puras",
    "simplificación de las imaginarias puras", "simplificacion de las imaginarias puras",
    "operaciones con imaginarias puras",
    "suma y resta",
    "cantidades complejas",
    "cantidades complejas conjugadas",
    "operaciones con cantidades complejas",
    "suma de cantidades complejas conjugadas",
    "diferencia de dos cantidades complejas conjugadas",
    "representación gráfica de las cantidades imaginarias puras",
    "representación gráfica de las cantidades complejas",
    "plano gaussiano. unidades gaussianas",
}


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


def match_ejercicio(text: str) -> HeadingCandidate | None:
    if m := _EJERCICIO_RE.match(text.strip()):
        return HeadingCandidate(
            kind=KIND_EJERCICIO,
            ordinal=m.group("ordinal"),
            title_remainder=(m.group("title") or "").strip(),
        )
    return None


def match_miscelanea(text: str) -> HeadingCandidate | None:
    if m := _MISCELANEA_RE.match(text.strip()):
        return HeadingCandidate(
            kind=KIND_MISCELANEA,
            ordinal="",
            title_remainder=(m.group("title") or "").strip(),
        )
    return None


def match_respuestas(text: str) -> HeadingCandidate | None:
    if m := _RESPUESTAS_RE.match(text.strip()):
        return HeadingCandidate(
            kind=KIND_RESPUESTAS,
            ordinal="",
            title_remainder="",
        )
    return None


def match_baldor_subseccion_romana(text: str) -> HeadingCandidate | None:
    """Reconoce subsecciones con números romanos y título en mayúsculas (ej. 'I. SUMA DE MONOMIOS')."""
    stripped = text.strip()
    if m := _BALDOR_CAPITULO_RE.match(stripped):
        title = m.group("title").strip()
        # Si el título está completamente en mayúsculas sostenidas, es una subsección temática
        if title == title.upper() and any(c.isalpha() for c in title):
            return HeadingCandidate(
                kind=KIND_SECCION,
                ordinal=m.group("ordinal"),
                title_remainder=title,
            )
    return None


def match_baldor_capitulo(text: str) -> HeadingCandidate | None:
    """Reconoce capítulos con número romano directo (ej. 'I. Suma', 'IV. Multiplicación')."""
    stripped = text.strip()
    if m := _BALDOR_CAPITULO_RE.match(stripped):
        title = m.group("title").strip()
        # Si el título está completamente en mayúsculas sostenidas, no es un capítulo sino una subsección temática interna
        if not (title == title.upper() and any(c.isalpha() for c in title)):
            # Limpiar repeticiones concatenadas en mayúsculas (ej. 'Multiplicación LA MULTIPLICACIÓN')
            if m_dup := re.match(r"^(.*?)\s+(?:LA\s+|EL\s+|LOS\s+|LAS\s+)?([A-ZÁÉÍÓÚÑ\s]{3,})$", title):
                first_part, second_part = m_dup.group(1), m_dup.group(2).strip()
                if first_part.strip().upper() == second_part or second_part in first_part.strip().upper():
                    title = first_part.strip()
            return HeadingCandidate(
                kind=KIND_CAPITULO,
                ordinal=m.group("ordinal"),
                title_remainder=title,
            )
    return None




def match_baldor_caso(text: str) -> HeadingCandidate | None:
    """Reconoce casos clásicos de factorización (ej. 'CASO I: CUANDO TODOS...')."""
    stripped = text.strip()
    if m := _BALDOR_CASO_RE.match(stripped):
        return HeadingCandidate(
            kind=KIND_SECCION,
            ordinal=m.group("ordinal").upper(),
            title_remainder=(m.group("title") or "").strip(),
        )
    return None


def match_baldor_inciso(text: str) -> HeadingCandidate | None:
    """Reconoce subcasos con inciso alfabético (ej. 'a) Factor común monomio.')."""
    stripped = text.strip()
    if m := _BALDOR_INCISO_RE.match(stripped):
        return HeadingCandidate(
            kind=KIND_SUBSECCION,
            ordinal=m.group("ordinal"),
            title_remainder=m.group("title").strip(),
        )
    return None


def match_baldor_tema_mayusculas(text: str) -> HeadingCandidate | None:
    """Reconoce encabezados conceptuales y reglas generales de Baldor en mayúsculas."""
    stripped = text.strip()
    if not stripped:
        return None
    # Verificamos si coincide con los temas canónicos conocidos de Álgebra de Baldor
    if stripped.lower() in _BALDOR_TEMAS_CONOCIDOS:
        return HeadingCandidate(
            kind=KIND_BALDOR_TEMA,
            ordinal="",
            title_remainder=stripped,
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

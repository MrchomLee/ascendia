"""Profile-default rules. Edit here to change defaults globally.

Per-document overrides go in ``Manual.metadata_json["question_rules"]`` as a
sparse dict matching :class:`RulesOverride`.
"""

from __future__ import annotations

from qgen.rules.base import DocumentRules


_MANUAL_RULES = DocumentRules(
    name="manual",
    preferred_topics=(
        "doctrina militar",
        "principios y fundamentos",
        "organización de fuerzas armadas",
        "definiciones formales",
        "deberes y atribuciones del mando",
        "fases y niveles de conducción",
    ),
    forbidden_topics=(
        "tabulaciones específicas susceptibles a reforma reciente",
        "fechas calendario exactas",
    ),
    style_guide=(
        "Lenguaje militar formal en español. Oraciones precisas, neutras, "
        "sin coloquialismos. Términos técnicos correctos."
    ),
    extra_instructions=(
        "Cuando el bloque define un concepto, prefiere preguntas que pidan "
        "identificar la definición correcta o aplicarla a un caso. "
        "Cuando lista clasificaciones, prefiere preguntas sobre criterios o miembros de la lista."
    ),
)


_CODIGO_LEGAL_RULES = DocumentRules(
    name="codigo_legal",
    preferred_topics=(
        "tipos de delitos y faltas militares",
        "competencias y procedimientos",
        "estructura y atribuciones de tribunales militares",
        "deberes, requisitos y responsabilidades de los cargos",
        "garantías procesales",
    ),
    forbidden_topics=(
        "años de condena específicos",
        "cuantías monetarias específicas (multas, fianzas)",
        "fechas exactas de reformas DOF",
        "nombres propios de jueces, magistrados o autoridades vigentes",
    ),
    style_guide=(
        "Lenguaje jurídico formal y claro en español. Sin jerga innecesaria. "
        "Cita el artículo en pasiva neutra cuando ayude a precisar."
    ),
    extra_instructions=(
        "Si el artículo está derogado (texto incluye '(Se deroga)'), no generar pregunta. "
        "Si menciona reformas DOF, omite las fechas en las opciones. "
        "Para artículos con fracciones (I, II, III...), prefiere preguntas sobre la sustancia "
        "de las fracciones o sobre el orden, evita citar la fracción por número romano en la opción correcta."
    ),
)


_LEY_ORGANICA_RULES = DocumentRules(
    name="ley_organica",
    preferred_topics=(
        "estructura orgánica",
        "atribuciones y funciones de cada órgano",
        "jerarquías y subordinación",
    ),
    forbidden_topics=(
        "fechas exactas de reformas DOF",
        "cuantías presupuestales específicas",
    ),
    style_guide="Lenguaje jurídico-administrativo formal en español.",
    extra_instructions="",
)


# Reglas por defecto para el perfil de Álgebra de Baldor
_BALDOR_RULES = DocumentRules(
    name="algebra_baldor",
    preferred_topics=(
        "leyes de signos",
        "leyes de exponentes y coeficientes",
        "operaciones con monomios y polinomios (suma, resta, multiplicación, división)",
        "productos y cocientes notables",
        "casos y métodos de factorización",
        "máximo común divisor y mínimo común múltiplo",
        "fracciones algebraicas y su reducción",
        "resolución de ecuaciones lineales y sistemas de ecuaciones simultáneas",
        "números complejos y cantidades imaginarias",
        "ejercicios y problemas prácticos resueltos",
    ),
    forbidden_topics=(
        "biografías históricas detalladas de matemáticos",
        "fechas o lugares de nacimiento de autores",
        "números de página de la edición impresa",
        "notas editoriales no matemáticas",
    ),
    style_guide=(
        "Lenguaje matemático claro, preciso y riguroso en español. "
        "Uso de notación algebraica estándar (ej. x^2, paréntesis, signos de operación). "
        "Preguntas directas tanto conceptuales (definiciones, teoremas, leyes) como operativas (procedimientos y resultados de ejercicios)."
    ),
    extra_instructions=(
        "Cuando el bloque contenga un ejercicio o problema resuelto, formula preguntas tipo: "
        "'Al resolver [expresión], ¿cuál es el resultado correcto?' o '¿Cuál es la descomposición factorial de [expresión]?'. "
        "Los distractores u opciones incorrectas deben basarse en errores algebraicos típicos "
        "(error de signos, error al sumar exponentes en vez de multiplicarlos, omitir el doble producto en binomios al cuadrado, etc.)."
    ),
)


PROFILE_RULES: dict[str, DocumentRules] = {
    "manual": _MANUAL_RULES,
    "codigo_legal": _CODIGO_LEGAL_RULES,
    "ley_organica": _LEY_ORGANICA_RULES,
    "algebra_baldor": _BALDOR_RULES,
}


def get_default_rules(profile_name: str) -> DocumentRules:
    if profile_name not in PROFILE_RULES:
        raise ValueError(
            f"No default rules for profile {profile_name!r}. "
            f"Available: {sorted(PROFILE_RULES)}"
        )
    return PROFILE_RULES[profile_name]

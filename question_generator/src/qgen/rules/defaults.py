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


PROFILE_RULES: dict[str, DocumentRules] = {
    "manual": _MANUAL_RULES,
    "codigo_legal": _CODIGO_LEGAL_RULES,
    "ley_organica": _LEY_ORGANICA_RULES,
}


def get_default_rules(profile_name: str) -> DocumentRules:
    if profile_name not in PROFILE_RULES:
        raise ValueError(
            f"No default rules for profile {profile_name!r}. "
            f"Available: {sorted(PROFILE_RULES)}"
        )
    return PROFILE_RULES[profile_name]

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


_TALLER_LECTURA_REDACCION_RULES = DocumentRules(
    name="taller_lectura_redaccion",
    preferred_topics=(
        "elementos del proceso comunicativo (emisor, receptor, mensaje, código, canal, contexto, ruido, retroalimentación)",
        "tipos de lenguaje",
        "funciones del lenguaje y su intención comunicativa",
        "principios básicos de la sintaxis",
        "reglas de acentuación (agudas, graves, esdrújulas, tilde diacrítica)",
        "reglas de puntuación",
    ),
    forbidden_topics=(
        "instrucciones de actividades formativas o trabajo en equipo",
        "referencias bibliográficas y direcciones de internet",
        "números de figura, tabla o página",
    ),
    style_guide=(
        "Español formal y claro, de nivel bachillerato. Preguntas conceptuales "
        "(definiciones, elementos, funciones) y de aplicación de reglas sobre ejemplos concretos."
    ),
    extra_instructions=(
        "En acentuación y puntuación, pregunta por la regla o por su aplicación a una palabra "
        "u oración del texto; los distractores deben basarse en errores típicos de clasificación "
        "(aguda/grave/esdrújula) o de uso del signo."
    ),
)


_HISTORIA_UNIVERSAL_RULES = DocumentRules(
    name="historia_universal",
    preferred_topics=(
        "causas, desarrollo y consecuencias de la Guerra Fría",
        "conflictos regionales de la Guerra Fría (Alemania, Corea, Vietnam, Medio Oriente)",
        "organismos internacionales y alianzas militares: propósito y miembros "
        "(ONU, FMI, GATT, CAME, OEA, OUA, Liga Árabe, OTAN, Pacto de Varsovia)",
        "el conflicto del Golfo Pérsico",
        "el fin del bloque socialista europeo (Perestroika y Glasnost)",
        "la actualidad en América Latina y el Caribe",
        "la Unión Europea, el ataque a las Torres Gemelas y la invasión a Irak",
        "las potencias emergentes (China, India, Rusia, Brasil)",
    ),
    forbidden_topics=(
        "cifras exactas (porcentajes, número de víctimas, tropas o montos)",
        "fechas con día y mes (los años sí se pueden preguntar)",
        "referencias a mapas, figuras o números de página",
    ),
    style_guide=(
        "Español formal y claro, de nivel bachillerato. Preguntas sobre hechos, causas, "
        "consecuencias, actores y relaciones entre procesos históricos."
    ),
    extra_instructions=(
        "Prefiere preguntas de causa-consecuencia y de identificación de países, bloques, "
        "organismos o personajes. Los distractores deben ser plausibles dentro de la misma "
        "época (otros actores o acontecimientos del capítulo), no anacronismos evidentes."
    ),
)


_GEOGRAFIA_MODERNA_MEXICO_RULES = DocumentRules(
    name="geografia_moderna_mexico",
    preferred_topics=(
        "situación geográfica de México y sus fronteras norte y sur",
        "extensión territorial del país",
        "división política: entidades federativas y sus capitales",
        "representación cartográfica: mapas, escalas y proyecciones",
        "unidades orogénicas: sierras, cordilleras, mesetas y su ubicación",
        "litorales: costas del Pacífico, del Golfo de México y del Mar de las Antillas",
        "islas de México y a qué estado o litoral pertenecen",
    ),
    forbidden_topics=(
        "coordenadas en grados, minutos o segundos",
        "superficie en km² de cada estado o isla (la extensión total del país sí)",
        "longitudes exactas de costa o de frontera",
        "referencias a notas al pie, tablas o números de página",
    ),
    style_guide=(
        "Español formal y claro, de nivel bachillerato. Preguntas de localización, "
        "identificación y relación entre rasgos geográficos."
    ),
    extra_instructions=(
        "Prefiere preguntas de ubicación (¿dónde está…?, ¿qué estados recorre…?) y de "
        "identificación (¿cuál es la capital de…?, ¿a qué litoral pertenece…?). Los distractores "
        "deben ser rasgos reales del país (otra sierra, otra isla, otro estado), no inventados."
    ),
)


_CALCULO_UNA_VARIABLE_RULES = DocumentRules(
    name="calculo_una_variable",
    preferred_topics=(
        "funciones: dominio y rango, gráficas, funciones por partes, crecientes/decrecientes, pares e impares",
        "combinación y composición de funciones; traslación, cambio de escala y reflexión de gráficas",
        "funciones trigonométricas: radianes, periodicidad e identidades",
        "tasas de cambio promedio e instantáneas; rectas secantes y tangentes",
        "límites: leyes de los límites, definición formal, límites laterales y al infinito",
        "continuidad y asíntotas",
        "la derivada: definición, derivada en un punto y como función",
        "reglas de derivación, derivadas de orden superior y de funciones trigonométricas",
        "regla de la cadena, derivación implícita y tasas relacionadas",
    ),
    forbidden_topics=(
        "pasos o teclas de calculadoras graficadoras o programas de cómputo",
        "números de ejemplo, figura, ejercicio o página",
        "notas históricas sobre matemáticos",
    ),
    style_guide=(
        "Lenguaje matemático claro y preciso en español, de nivel bachillerato/ingreso a ingeniería. "
        "Notación estándar escrita sin ambigüedad (x^2, sqrt(x), (a)/(b), lím x→c). "
        "Preguntas conceptuales (definiciones, teoremas, reglas) y operativas (calcular un límite o una derivada)."
    ),
    extra_instructions=(
        "En preguntas operativas, pide el resultado de un límite o una derivada concreta y verifica el cálculo. "
        "Los distractores deben venir de errores típicos: olvidar la regla de la cadena, equivocar el signo "
        "de la derivada de cos x, aplicar mal la regla del cociente o evaluar el límite sin simplificar. "
        "Si una fórmula del texto se ve incompleta o ambigua (exponentes o fracciones aplanados), no la uses."
    ),
)


_ALGEBRA_TRIGONOMETRIA_GEOMETRIA_ANALITICA_RULES = DocumentRules(
    name="algebra_trigonometria_geometria_analitica",
    preferred_topics=(
        "plano cartesiano: distancia entre puntos, punto medio y regiones",
        "círculos: ecuación, centro y radio, completar el cuadrado; intersecciones y simetría",
        "ecuaciones de rectas: pendiente, formas de la ecuación, rectas paralelas y perpendiculares",
        "variación directa, inversa y conjunta",
        "ángulos: grados y radianes, longitud de arco",
        "razones trigonométricas en el triángulo rectángulo; ángulos especiales y de referencia",
        "funciones circulares; gráficas de seno y coseno (amplitud, periodo, desfase) y de las demás",
        "identidades trigonométricas, funciones trigonométricas inversas y ecuaciones trigonométricas",
        "coordenadas polares: conversión con rectangulares, gráficas polares y cónicas en polares",
        "vectores en el plano y producto punto (ángulo entre vectores, proyección)",
    ),
    forbidden_topics=(
        "números de ejemplo, teorema, definición, figura, ejercicio o página",
        "notas históricas sobre matemáticos",
    ),
    style_guide=(
        "Lenguaje matemático claro y preciso en español, de nivel bachillerato/ingreso a ingeniería. "
        "Notación estándar escrita sin ambigüedad (x^2, sqrt(x), (a)/(b), sen θ, π/6). "
        "Preguntas conceptuales (definiciones, teoremas, identidades) y operativas (calcular una distancia, "
        "una pendiente, un valor trigonométrico o una conversión de coordenadas)."
    ),
    extra_instructions=(
        "En preguntas operativas, verifica el cálculo antes de proponer la respuesta. Los distractores deben "
        "venir de errores típicos: confundir grados con radianes, invertir seno y coseno, olvidar el signo según "
        "el cuadrante, tomar el recíproco de la pendiente en vez del recíproco negativo, o confundir periodo y "
        "amplitud. Si una fórmula del texto se ve incompleta o ambigua (exponentes o fracciones aplanados), no la uses."
    ),
)


PROFILE_RULES: dict[str, DocumentRules] = {
    "manual": _MANUAL_RULES,
    "codigo_legal": _CODIGO_LEGAL_RULES,
    "ley_organica": _LEY_ORGANICA_RULES,
    "algebra_baldor": _BALDOR_RULES,
    "taller_lectura_redaccion": _TALLER_LECTURA_REDACCION_RULES,
    "historia_universal": _HISTORIA_UNIVERSAL_RULES,
    "geografia_moderna_mexico": _GEOGRAFIA_MODERNA_MEXICO_RULES,
    "calculo_una_variable": _CALCULO_UNA_VARIABLE_RULES,
    "algebra_trigonometria_geometria_analitica": _ALGEBRA_TRIGONOMETRIA_GEOMETRIA_ANALITICA_RULES,
}


def get_default_rules(profile_name: str) -> DocumentRules:
    if profile_name not in PROFILE_RULES:
        raise ValueError(
            f"No default rules for profile {profile_name!r}. "
            f"Available: {sorted(PROFILE_RULES)}"
        )
    return PROFILE_RULES[profile_name]

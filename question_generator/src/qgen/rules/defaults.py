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
        "las penas de cada delito (prisión, destitución, suspensión, inhabilitación y su duración): los temarios piden el Código «sin penas»",
        "cuantías monetarias específicas (multas, fianzas)",
        "fechas exactas de reformas DOF",
        "nombres propios de jueces, magistrados o autoridades vigentes",
    ),
    style_guide=(
        "Lenguaje jurídico formal y claro en español. Sin jerga innecesaria. "
        "Cita el artículo en pasiva neutra cuando ayude a precisar."
    ),
    extra_instructions=(
        "Pregunta la conducta que constituye cada delito, sus elementos, quién lo comete, sus "
        "clasificaciones y las circunstancias que lo agravan o atenúan; nunca con qué pena se castiga, "
        "y ninguna opción menciona años o meses de prisión ni otra pena. "
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
    familia="civil",
    tipos=("teoria", "ejercicio"),
    matematicas=True,
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
    familia="civil",
    tipos=("teoria",),
    preferred_topics=(
        "elementos del proceso comunicativo (emisor, receptor, mensaje, código, canal, contexto, ruido, retroalimentación)",
        "tipos de lenguaje",
        "funciones del lenguaje y su intención comunicativa",
        "principios básicos de la sintaxis",
        "reglas de acentuación (agudas, graves, esdrújulas, tilde diacrítica)",
        "reglas de puntuación",
        "estrategias de comprensión lectora (prelectura, lectura, poslectura, contexto, inferencia)",
        "propiedades de la redacción (unidad, coherencia, cohesión, adecuación, autonomía)",
        "conectores o marcadores discursivos",
        "prototipos textuales (descripción, narración, argumentación, exposición, diálogo, conversación) y sus propiedades",
        "funciones, características y clasificación de los textos expositivos",
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
    familia="civil",
    tipos=("teoria",),
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
    familia="civil",
    tipos=("teoria",),
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
    familia="civil",
    tipos=("teoria", "ejercicio"),
    matematicas=True,
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
    name="algebra_trig_geo_analitica",
    familia="civil",
    tipos=("teoria", "ejercicio"),
    matematicas=True,
    preferred_topics=(
        "conjuntos y números reales: propiedades, recta numérica, valor absoluto y distancia",
        "exponentes enteros y racionales, radicales, racionalización y notación científica",
        "polinomios, productos notables, factorización y expresiones racionales",
        "ecuaciones lineales y cuadráticas (factorización, fórmula cuadrática, discriminante) y problemas de aplicación",
        "números complejos: forma estándar, conjugado y operaciones",
        "desigualdades lineales, con valor absoluto, polinomiales y racionales; notación de intervalos",
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
        "resolución de triángulos: triángulo rectángulo, ángulos de elevación y depresión, leyes de senos y cosenos",
        "movimiento armónico simple; forma trigonométrica, potencias y raíces de números complejos (DeMoivre)",
        "cónicas: parábola, elipse e hipérbola (focos, vértices, ejes, excentricidad); rotación de ejes",
        "ecuaciones paramétricas: curvas planas, eliminación del parámetro, cicloide",
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


# Química, Física y Biología del temario de la EMM: solo teoría (la extracción no
# trae los ejercicios ni los ejemplos resueltos). En Química y Física sí se
# preguntan fórmulas, unidades y constantes fundamentales.
_QUIMICA_CHANG_RULES = DocumentRules(
    name="quimica_chang",
    familia="civil",
    tipos=("teoria",),
    preferred_topics=(
        "teoría atómica y estructura del átomo: partículas subatómicas, número atómico, número de masa e isótopos",
        "moléculas e iones; fórmulas moleculares y empíricas",
        "nomenclatura de compuestos iónicos, moleculares, ácidos y bases",
        "masa atómica, número de Avogadro, masa molar y masa molecular",
        "composición porcentual de los compuestos",
        "reacciones y ecuaciones químicas: cómo se escriben y se balancean",
        "disoluciones acuosas: electrolitos y no electrolitos",
        "reacciones ácido-base y de oxidación-reducción; números de oxidación",
        "concentración de las disoluciones: molaridad y dilución",
        "enlace iónico, enlace covalente y electronegatividad",
        "compuestos orgánicos: hidrocarburos alifáticos y grupos funcionales",
        "gases: presión, leyes de los gases, ecuación del gas ideal, ley de Dalton, teoría cinética "
        "molecular y desviación del comportamiento ideal",
    ),
    forbidden_topics=(
        "cifras de los ejemplos (datos o resultados de un caso particular); las fórmulas, "
        "las unidades y las constantes fundamentales sí se pueden preguntar",
        "fechas de nacimiento o muerte de los científicos",
        "referencias a figuras, tablas o números de página",
    ),
    style_guide=(
        "Español formal y claro, de nivel bachillerato. Notación como la del texto: subíndices y "
        "superíndices (H₂O, SO₄²⁻, 10⁻¹⁹), × en las potencias de diez y fracciones con /. "
        "Preguntas conceptuales (definiciones, leyes, clasificaciones, nomenclatura) y de aplicación "
        "de una regla o fórmula del texto a un caso nuevo."
    ),
    extra_instructions=(
        "En aplicación, plantea un caso nuevo con datos sencillos y resuélvelo con una regla o fórmula "
        "del texto (masa molar, composición porcentual, molaridad, número de oxidación, nomenclatura, "
        "tipo de enlace según la electronegatividad, leyes de los gases); verifica el cálculo antes de "
        "proponer la respuesta. "
        "Los distractores deben venir de errores típicos: confundir número atómico y número de masa, catión "
        "y anión, fórmula empírica y molecular, moles y molaridad, el sufijo del nombre (-uro, -ato, -ito) "
        "o el signo del número de oxidación. Si una fórmula o ecuación del texto se ve incompleta o ambigua, no la uses."
    ),
)


_FISICA_GENERAL_RULES = DocumentRules(
    name="fisica_general",
    familia="civil",
    tipos=("teoria",),
    preferred_topics=(
        "magnitudes escalares y vectoriales; características, descomposición y suma de vectores",
        "distancia y desplazamiento, rapidez y velocidad",
        "leyes de la dinámica de Newton y ley de la gravitación universal",
        "trabajo, potencia y energía: cinética, potencial y su conservación",
        "cantidad de movimiento e impulso; conservación del momento angular",
        "estructura de la materia, estados de agregación y propiedades generales de la materia",
        "hidrostática: densidad, peso específico, presión, principios de Pascal y de Arquímedes, "
        "tensión superficial, capilaridad y viscosidad",
        "calor y temperatura: escalas termométricas, formas de propagación del calor y sus unidades",
        "los gases y sus leyes (Boyle, Charles, Gay-Lussac y la ley general)",
    ),
    forbidden_topics=(
        "cifras de los ejemplos (datos o resultados de un caso particular); las fórmulas, "
        "las unidades y las constantes fundamentales sí se pueden preguntar",
        "fechas de nacimiento o muerte de los científicos",
        "referencias a figuras, tablas o números de página",
    ),
    style_guide=(
        "Español formal y claro, de nivel bachillerato. Notación como la del texto: superíndices y "
        "subíndices (m/s², P₁V₁/T₁, 10⁵), × en las potencias de diez y fracciones con /. "
        "Preguntas conceptuales (definiciones, leyes, principios, unidades) y de aplicación de una "
        "fórmula del texto a un caso nuevo."
    ),
    extra_instructions=(
        "En aplicación, plantea un caso nuevo con datos sencillos y resuélvelo con una fórmula del texto "
        "(velocidad, segunda ley de Newton, peso, trabajo, energía cinética y potencial, cantidad de "
        "movimiento, densidad, presión, principios de Pascal y de Arquímedes, conversión entre escalas de "
        "temperatura, leyes de los gases); verifica el cálculo y las unidades antes de proponer la respuesta. "
        "Los distractores deben venir de errores típicos: confundir distancia con desplazamiento, rapidez con "
        "velocidad, masa con peso o calor con temperatura, olvidar pasar a kelvin en las leyes de los gases o "
        "equivocar la unidad del resultado. Si una fórmula del texto se ve incompleta o ambigua, no la uses."
    ),
)


_BIOLOGIA_CURTIS_RULES = DocumentRules(
    name="biologia_curtis",
    familia="civil",
    tipos=("teoria",),
    preferred_topics=(
        "origen de la vida y de las primeras células; heterótrofos y autótrofos; procariontes y eucariontes",
        "organización de la célula: núcleo, citoplasma, organelos y la función de cada uno",
        "membrana plasmática: estructura y transporte de sustancias (difusión, ósmosis, transporte activo, "
        "endocitosis y exocitosis)",
        "metabolismo: leyes de la termodinámica, ATP, enzimas y su regulación",
        "glucólisis, respiración celular, transporte de electrones y fermentación",
        "reproducción sexual, mitosis y meiosis; los experimentos de Mendel y las bases cromosómicas de la herencia",
        "flujo de la información genética: transcripción, tipos de ARN, traducción, código genético y mutaciones",
        "tejidos, órganos y sistemas de los vertebrados",
        "sistema nervioso: la neurona, el impulso nervioso y la sinapsis",
        "respiración, circulación (sangre, corazón, vasos y sistema linfático) y digestión",
    ),
    forbidden_topics=(
        "fechas de nacimiento o muerte de los científicos (sus nombres ligados a una teoría o "
        "un experimento sí se pueden preguntar)",
        "cifras anecdóticas o de un caso particular (tamaños, cantidades o porcentajes que no ilustran un concepto)",
        "referencias a figuras, tablas o números de página",
    ),
    style_guide=(
        "Español formal y claro, de nivel bachillerato. Preguntas sobre estructuras y su función, "
        "procesos y sus etapas, comparación entre procesos o grupos de organismos y relación entre conceptos."
    ),
    extra_instructions=(
        "Prefiere preguntas de estructura-función, de etapas y productos de un proceso y de comparación "
        "(mitosis y meiosis, procariontes y eucariontes, respiración aeróbica y fermentación, transcripción "
        "y traducción). Los recuadros y ensayos del capítulo también son materia de preguntas. Los distractores "
        "deben ser estructuras, moléculas, procesos u organismos reales del mismo capítulo, no inventados."
    ),
)


# Libros de la EMEFA (temario CTL.VLO 2026). Geografía y Física: solo teoría (la
# extracción de Física no trae los ejemplos resueltos). Precálculo: teoría y
# ejercicios, porque la extracción conserva los ejemplos con sus pasos.
_GEOGRAFIA_LUCIO_VICTORIO_RULES = DocumentRules(
    name="geografia_lucio_victorio",
    familia="civil",
    tipos=("teoria",),
    preferred_topics=(
        "división de la Geografía y sus ciencias auxiliares",
        "relación entre el hombre y el medio geográfico: determinismo y posibilismo",
        "forma y tamaño de la Tierra; movimientos de rotación y traslación y sus consecuencias",
        "puntos, líneas y círculos de la Tierra; latitud, longitud, altitud y situación geográfica",
        "zonas térmicas, estaciones del año y husos horarios",
        "formas del relieve continental: clasificación, características e importancia",
        "contaminación ambiental: concepto, clasificación, causas y consecuencias",
        "características y distribución del agua; el ciclo del agua",
        "océanos y mares; olas, mareas y corrientes marinas; relieve submarino",
        "la atmósfera: características, importancia y estructura",
        "fenómenos meteorológicos: temperatura, presión, vientos, humedad y precipitaciones",
        "tiempo y clima: elementos, factores y clasificación del clima",
    ),
    forbidden_topics=(
        "cifras anecdóticas o de un caso particular (las medidas fundamentales de la Tierra, como la "
        "inclinación del eje o la duración de sus movimientos, sí se pueden preguntar)",
        "fechas de nacimiento o muerte de los autores citados",
        "referencias a figuras, cuadros o números de página",
    ),
    style_guide=(
        "Español formal y claro, de nivel bachillerato. Preguntas de conceptos, clasificaciones, "
        "causas y consecuencias de los fenómenos y relación entre rasgos geográficos."
    ),
    extra_instructions=(
        "Prefiere preguntas de causa y consecuencia (qué provoca la rotación, por qué hay estaciones) y de "
        "clasificación (tipos de relieve, de contaminación, de vientos, de climas). Los distractores deben "
        "ser conceptos reales de la misma unidad (otro movimiento, otra capa de la atmósfera, otro tipo de "
        "relieve), no inventados."
    ),
)


_FISICA_SERWAY_RULES = DocumentRules(
    name="fisica_serway",
    familia="civil",
    tipos=("teoria",),
    preferred_topics=(
        "estándares de longitud, masa y tiempo; el SI y sus prefijos",
        "modelos y representaciones; análisis dimensional y conversión de unidades",
        "estimaciones de orden de magnitud y cifras significativas",
        "posición, desplazamiento, velocidad y rapidez promedio e instantánea",
        "aceleración promedio e instantánea",
        "sistemas coordenados; cantidades vectoriales y escalares",
        "suma y resta de vectores; componentes y vectores unitarios",
        "fuerza; primera, segunda y tercera leyes de Newton; marcos inerciales; masa, peso y fuerza gravitacional",
        "presión y su variación con la profundidad; mediciones de presión",
        "fuerzas de flotación y principio de Arquímedes",
        "dinámica de fluidos: fluido ideal, ecuación de continuidad y ecuación de Bernoulli",
    ),
    forbidden_topics=(
        "cifras de los ejemplos (datos o resultados de un caso particular); las fórmulas, "
        "las unidades y las constantes fundamentales sí se pueden preguntar",
        "fechas de nacimiento o muerte de los científicos",
        "referencias a figuras, tablas, ejemplos o números de página",
    ),
    style_guide=(
        "Español formal y claro, de nivel bachillerato. Notación como la del texto: superíndices y "
        "subíndices (m/s², v_x, 10⁵), × en las potencias de diez y fracciones con /. "
        "Preguntas conceptuales (definiciones, leyes, principios, unidades) y de aplicación de una "
        "fórmula del texto a un caso nuevo."
    ),
    extra_instructions=(
        "En aplicación, plantea un caso nuevo con datos sencillos y resuélvelo con una fórmula del texto "
        "(conversión de unidades, cifras significativas, velocidad y aceleración promedio, componentes de un "
        "vector, segunda ley de Newton, peso, presión a una profundidad, empuje, ecuación de continuidad, "
        "Bernoulli); verifica el cálculo y las unidades antes de proponer la respuesta. Los distractores deben "
        "venir de errores típicos: confundir distancia con desplazamiento, rapidez con velocidad, masa con peso, "
        "acción y reacción con fuerzas que se anulan, presión absoluta con manométrica, o seno con coseno al "
        "descomponer un vector. Si una fórmula del texto se ve incompleta o ambigua, no la uses."
    ),
)


_PRECALCULO_LARSON_RULES = DocumentRules(
    name="precalculo_larson",
    familia="civil",
    tipos=("teoria", "ejercicio"),
    matematicas=True,
    preferred_topics=(
        "exponentes y sus propiedades, notación científica, radicales, racionalización y exponentes racionales",
        "polinomios: operaciones, productos especiales y factorización (factor común, trinomios, agrupación, "
        "suma y diferencia de cubos)",
        "resolución de ecuaciones lineales, racionales, cuadráticas (factorización, raíces cuadradas, completar "
        "el cuadrado, fórmula cuadrática), polinomiales, con radicales y con valor absoluto",
        "propiedades de los logaritmos, cambio de base, desarrollar y condensar expresiones logarítmicas",
        "ecuaciones exponenciales y logarítmicas",
        "sistemas de ecuaciones: sustitución, eliminación, método gráfico y aplicaciones",
        "gráficas de seno y coseno: amplitud, periodo, desplazamientos horizontal y vertical",
        "aplicaciones: triángulos rectángulos, ángulos de elevación y depresión, rumbos, movimiento armónico simple",
        "identidades trigonométricas fundamentales: simplificar, factorizar y sustitución trigonométrica",
        "ley de senos (caso ambiguo) y ley de cosenos; área de un triángulo oblicuángulo y fórmula de Herón",
        "plano cartesiano: distancia entre dos puntos y punto medio",
        "rectas: pendiente, formas de la ecuación, rectas paralelas y perpendiculares, ángulo de inclinación, "
        "ángulo entre rectas y distancia de un punto a una recta",
        "cónicas: parábola, elipse e hipérbola (focos, vértices, directriz, ejes, asíntotas, excentricidad) "
        "y clasificación por la ecuación general",
    ),
    forbidden_topics=(
        "números de ejemplo, teorema, figura, ejercicio o página",
        "pasos o teclas de calculadoras graficadoras",
        "referencias al sitio web del libro",
        "notas históricas sobre matemáticos",
    ),
    style_guide=(
        "Lenguaje matemático claro y preciso en español, de nivel bachillerato/ingreso a ingeniería. "
        "Notación estándar escrita sin ambigüedad (x^2, sqrt(x), (a)/(b), sen θ, log_b x, π/6). "
        "Preguntas conceptuales (definiciones, propiedades, fórmulas) y operativas (factorizar, resolver una "
        "ecuación o un sistema, calcular un logaritmo, una amplitud, un lado o una distancia)."
    ),
    extra_instructions=(
        "En preguntas operativas, verifica el cálculo antes de proponer la respuesta. Los distractores deben "
        "venir de errores típicos: signos al factorizar, olvidar la raíz negativa, aplicar mal una propiedad de "
        "los logaritmos (log(u + v) = log u + log v), confundir periodo y amplitud, invertir seno y coseno, "
        "olvidar el caso ambiguo de la ley de senos o confundir a, b y c en las cónicas. Las notas de los pasos "
        "(«— Simplifique.») explican el paso de su renglón. Si una fórmula del texto se ve incompleta o ambigua, no la uses."
    ),
)


# Cálculo (Salazar, Bahena y Velázquez), CÁLDIF de la EMT: unidades 1–3, teoría y ejemplos resueltos.
_CALCULO_SALAZAR_RULES = DocumentRules(
    name="calculo_salazar",
    familia="civil",
    tipos=("teoria", "ejercicio"),
    matematicas=True,
    preferred_topics=(
        "conjunto y elemento; relación y función; dominio, contradominio, rango y regla de correspondencia",
        "notación de funciones, valor numérico y cociente de diferencias (f(x + h) − f(x))/h",
        "gráficas de funciones algebraicas y trascendentes; funciones pares e impares; funciones por casos",
        "funciones explícitas e implícitas; inyectivas, sobreyectivas y biyectivas; función inversa",
        "dominio y rango; asíntotas verticales y horizontales; operaciones y composición de funciones",
        "idea intuitiva de límite, límites laterales, teoremas de límites, formas indeterminadas y límites al infinito",
        "continuidad puntual y en un intervalo; tipos de discontinuidad",
        "la derivada: interpretación geométrica y física, definición por el límite y notaciones",
        "fórmulas de derivación: potencia, suma, producto, cociente, regla de la cadena; trigonométricas, "
        "exponenciales y logarítmicas; derivadas de orden superior y derivación implícita",
        "recta tangente y normal, ángulo entre curvas, velocidad y aceleración, razones de cambio y optimización",
        "crecimiento y decrecimiento, máximos y mínimos, concavidad y puntos de inflexión",
        "la diferencial y sus aplicaciones a aproximaciones y errores",
    ),
    forbidden_topics=(
        "pasos o teclas de calculadoras y graficadores (Winplot, GeoGebra)",
        "números de ejemplo, figura, actividad o página",
        "notas históricas sobre matemáticos",
    ),
    style_guide=(
        "Lenguaje matemático claro y preciso en español, de nivel bachillerato/ingreso a ingeniería. "
        "Notación estándar escrita sin ambigüedad (x^2, sqrt(x), (a)/(b), lím x→c, f'(x), dy/dx). "
        "Preguntas conceptuales (definiciones, teoremas, reglas) y operativas (calcular un dominio, un límite o "
        "una derivada)."
    ),
    extra_instructions=(
        "En preguntas operativas, verifica el cálculo antes de proponer la respuesta. Los distractores deben "
        "venir de errores típicos: olvidar la regla de la cadena, equivocar el signo de la derivada de cos x, "
        "aplicar mal la regla del producto o del cociente, evaluar un límite sin simplificar la forma 0/0 o "
        "confundir dominio con rango. Las notas de los pasos («Factorizamos», «Sustituimos») explican el paso "
        "de su renglón. Si una fórmula del texto se ve incompleta o ambigua, no la uses."
    ),
)


# Metodología de la investigación (Baena Paz), MET.INV de la EMT y la EMMG: solo teoría.
_METODOLOGIA_BAENA_RULES = DocumentRules(
    name="metodologia_baena",
    familia="civil",
    tipos=("teoria",),
    preferred_topics=(
        "tipos de pensamiento: mágico, mítico, religioso, filosófico, científico, crítico, complejo, "
        "estratégico y prospectivo",
        "la investigación científica: definición, condiciones de un problema científico, características y "
        "tipos (pura y aplicada; documental, de campo y experimental)",
        "la ciencia: definición, objetivos, leyes (características y etapas para establecerlas), "
        "conocimiento científico e investigación científica",
        "el conocimiento: sujeto, objeto y su relación; elementos; conocimiento empírico y científico y sus "
        "características (objetivo, verificable, falible, sistemático)",
        "utilidad de la metodología, el método y las técnicas; la reseña expositiva y la crítica",
        "modelos, leyes y teorías; el método y el método científico; inducción y deducción (Bacon y "
        "Descartes); investigación cuantitativa y cualitativa",
        "métodos de Aristóteles, Euclides, Descartes y Bacon; método experimental y sus fases; método "
        "comparativo; análisis y síntesis; los métodos generales y específicos del Cuadro 3.1",
    ),
    forbidden_topics=(
        "fechas de nacimiento o muerte y datos biográficos anecdóticos (los nombres ligados a un método o una "
        "obra sí se pueden preguntar)",
        "cifras, años o nombres de programas o instituciones que no ilustran un concepto (SNI, PNPC, PROMEP)",
        "el «Cuadro comparativo: diferencias entre investigación cualitativa y cuantitativa», que trae "
        "invertidos los encabezados de sus columnas",
        "la frase de «Otros métodos» que atribuye a Descartes ir «de lo particular a lo general» (contradice "
        "el resto del texto)",
        "opiniones de la autora sobre la ciencia o sus anécdotas y ejemplos humorísticos",
        "referencias a figuras, tablas o números de página",
    ),
    style_guide=(
        "Español formal y claro, de nivel bachillerato. Preguntas sobre definiciones, características, "
        "clasificaciones, pasos de un método y comparación entre conceptos (inducción y deducción, "
        "investigación pura y aplicada, análisis y síntesis, modelo, ley y teoría)."
    ),
    extra_instructions=(
        "Prefiere definiciones y características que el texto enuncia con claridad y las listas del libro "
        "(condiciones de un problema científico, características de las leyes y de la investigación "
        "científica, fases del método experimental). Las lecturas de la reseña, de Bacon y de Descartes "
        "también son materia de preguntas, sin sus fechas. Los distractores deben ser conceptos, métodos o "
        "autores reales del mismo bloque, no inventados."
    ),
)


# Historia de México 1 (Menchaca y Ruiz), HISMÉX de la EMMG: Bloque 2, temas 3.1 y 3.3 y Bloque 5;
# solo teoría.
_HISTORIA_MENCHACA_RULES = DocumentRules(
    name="historia_menchaca",
    familia="civil",
    tipos=("teoria",),
    preferred_topics=(
        "teorías del poblamiento de América (origen único, múltiple, autóctono, australiano) y sus autores; "
        "teorías no científicas: mitos y leyendas",
        "la etapa lítica y el protoneolítico: arqueolítico, cenolítico y protoneolítico",
        "áreas culturales: Oasisamérica, Aridoamérica y Mesoamérica; rasgos comunes de Mesoamérica",
        "horizontes culturales de Mesoamérica (Preclásico, Clásico y Posclásico) y sus rasgos",
        "culturas mesoamericanas: olmecas, teotihuacanos, zapotecas, mayas, toltecas, mixtecos, purépechas y "
        "mexicas (organización social y política, religión, arte y aportaciones)",
        "causas de la llegada europea a América: expansión musulmana, rutas al Lejano Oriente, Reyes "
        "Católicos y derecho de patronato",
        "la Conquista material y espiritual: alianzas de Cortés, caída de Tenochtitlan, órdenes religiosas, "
        "métodos de evangelización, fuentes y cronistas de la Conquista, controversia sobre la naturaleza "
        "del indio",
        "causas internas y externas de la Independencia: Ilustración, reformas borbónicas, independencia de "
        "las Trece Colonias, Revolución Francesa, invasión napoleónica, criollismo e insurrecciones",
        "conspiraciones previas y etapas de la Guerra de Independencia (inicio, organización, resistencia y "
        "consumación): personajes, documentos (Sentimientos de la Nación, Constitución de Apatzingán, Plan "
        "de Iguala, Tratados de Córdoba) y composición social de insurgentes y realistas",
    ),
    forbidden_topics=(
        "cifras exactas (población, número de soldados o víctimas, montos)",
        "fechas con día y mes (los años sí se pueden preguntar)",
        "las listas de sitios arqueológicos de los cuadros (horizontes y subáreas) y las listas de firmantes",
        "referencias a figuras, mapas, cuadros o números de página",
    ),
    style_guide=(
        "Español formal y claro, de nivel bachillerato. Preguntas sobre hechos, causas, consecuencias, "
        "actores, documentos y rasgos de las culturas y procesos históricos."
    ),
    extra_instructions=(
        "Prefiere preguntas de causa-consecuencia y de identificación de culturas, personajes, documentos y "
        "etapas. Las lecturas también son materia de preguntas, sin sus fechas exactas. Los distractores "
        "deben ser plausibles dentro del mismo periodo (otras culturas, personajes o documentos del bloque), "
        "no anacronismos evidentes."
    ),
)


# Libros civiles de las promociones de ascenso 2026 (Sbtte. a Tte.): los presentan militares, pero el
# texto es de libro, así que van con la familia civil y solo teoría literal; la cita lleva la página.
# Introducción a la Ingeniería (Cengage, 2.ª ed.), cap. 11 «Administración de proyectos» (Sbtte. Pas. I.I.).
_INGENIERIA_ROMERO_RULES = DocumentRules(
    name="ingenieria_romero",
    familia="civil",
    tipos=("teoria",),
    preferred_topics=(
        "procesos y proyectos: diferencia, relación entre estabilidad y cambio",
        "definición y características del proyecto; cubo del proyecto (desempeño, tiempo y costo)",
        "ciclo de vida del proyecto: concepción, planeación, evaluación, ejecución, control y terminación",
        "el plan del proyecto: funciones, enfoques top-down y bottom-up y sus elementos (objetivo, WBS, "
        "programa, organización del equipo, gráfica lineal de responsabilidades, normas, presupuesto y "
        "análisis del riesgo)",
        "características de los objetivos; hitos; tipos de organización del equipo de proyecto",
        "administración del riesgo: identificación, análisis y respuesta; tipos de riesgo",
        "programación con tiempos conocidos (CPM, ruta crítica, ES, EF, LS, LF, holgura) e inciertos (PERT, "
        "tiempos optimista, más probable y pesimista, distribución beta y normal)",
        "consideraciones de costos: tiempo y costo normal e intensivo, costo intensivo por periodo y "
        "criterios para intensificar actividades",
    ),
    forbidden_topics=(
        "cifras de los ejemplos resueltos (duraciones, costos, probabilidades) y cálculos numéricos",
        "referencias a figuras, tablas o números de página",
    ),
    style_guide=(
        "Español formal y claro. Preguntas sobre definiciones, características, etapas, elementos del plan, "
        "tipos de riesgo y conceptos de programación de proyectos (CPM y PERT), sin pedir cálculos."
    ),
    extra_instructions=(
        "Prefiere las definiciones y listas que el texto enuncia (etapas del ciclo de vida, elementos del "
        "plan, características de los objetivos, pasos de la administración del riesgo). Los distractores "
        "deben ser conceptos reales del mismo capítulo (otra etapa, otro elemento, otro tiempo)."
    ),
)

# PMI, «El Estándar para la Dirección de Proyectos» (Guía del PMBOK, 7.ª ed., 2021), secciones 2
# «Un sistema para la entrega de valor» y 3 «Principios de la dirección de proyectos» (Sbtte. Pas. I.C.I.).
_PMBOK_ESTANDAR_RULES = DocumentRules(
    name="pmbok_estandar",
    familia="civil",
    tipos=("teoria",),
    preferred_topics=(
        "creación de valor: portafolios, programas, proyectos, productos y operaciones; resultados y "
        "beneficios; componentes del sistema de entrega de valor y flujo de información",
        "sistemas de gobernanza organizacional: supervisión, control, integración y toma de decisiones",
        "funciones asociadas con los proyectos: supervisar y coordinar, presentar objetivos y "
        "retroalimentación, facilitar y apoyar, realizar el trabajo y contribuir con conocimientos, "
        "aplicar experiencia, proporcionar dirección y perspectiva del negocio, proporcionar recursos y "
        "dirección, mantener la gobernanza",
        "el entorno del proyecto: entorno interno (activos de los procesos, datos, experiencia, "
        "herramientas, cultura) y entorno externo (condiciones del mercado, factores sociales y "
        "culturales, entorno regulatorio, bases de datos comerciales, investigación académica, "
        "estándares de la industria, consideraciones financieras, entorno físico)",
        "gestión del producto: ciclo de vida del producto y su relación con programas y proyectos",
        "los doce principios de la dirección de proyectos: administración (stewardship) diligente, "
        "respetuosa y cuidadosa; ambiente colaborativo del equipo; involucramiento de los interesados; "
        "enfoque en el valor; pensamiento sistémico; liderazgo; adaptación según el contexto (tailoring); "
        "calidad en procesos y entregables; complejidad; respuestas a los riesgos; adaptabilidad y "
        "resiliencia; cambio para lograr el estado futuro previsto",
        "enunciado de cada principio y las ideas clave de su recuadro",
    ),
    forbidden_topics=(
        "referencias a gráficos, figuras, tablas o números de página",
    ),
    style_guide=(
        "Español formal y claro, con la terminología de la Guía del PMBOK en español. Preguntas sobre "
        "definiciones, componentes, funciones, factores del entorno y principios que el texto enuncia."
    ),
    extra_instructions=(
        "Prefiere el enunciado de los principios, las ideas clave de sus recuadros y las listas del texto "
        "(componentes del sistema de entrega de valor, funciones del proyecto, factores del entorno "
        "interno y externo). Los distractores deben ser conceptos reales de las mismas secciones (otro "
        "principio, otra función, otro factor del entorno), no inventados."
    ),
)

# Medicina en Odontología (Castellanos, Díaz y Lee, Manual Moderno, 3.ª ed.), caps. 7, 12, 21 y 25
# (promoción especial de Odontología).
_ODONTOLOGIA_CASTELLANOS_RULES = DocumentRules(
    name="odontologia_castellanos",
    familia="civil",
    tipos=("teoria",),
    preferred_topics=(
        "hepatitis virales, tuberculosis, infecciones de transmisión sexual (gonorrea, VPH, sífilis) e "
        "infección por VIH: etiología, transmisión, manifestaciones clínicas y bucales, diagnóstico y "
        "manejo odontológico",
        "control de infecciones y protocolos de manejo de pacientes infectocontagiosos en la consulta dental",
        "hematopoyesis y células sanguíneas; anemias, policitemia, trastornos leucocitarios, leucemias y "
        "linfomas: clasificación, manifestaciones bucales y manejo odontológico",
        "embarazo, lactancia, menopausia, osteoporosis, bifosfonatos, pubertad y anticoncepción oral: "
        "cambios, riesgos y manejo dental; fármacos seguros y contraindicados",
        "implantología en pacientes con enfermedades sistémicas: diabetes, osteoporosis, bifosfonatos, "
        "cáncer de cabeza y cuello, enfermedad cardiovascular, anticoagulantes, VIH, trasplantes, "
        "hiposalivación, corticosteroides, alcoholismo, adicciones, enfermedad renal y alergias",
        "contenido de los cuadros (patrones serológicos, valores normales, clasificaciones, protocolos)",
    ),
    forbidden_topics=(
        "dosis exactas de fármacos y cifras de prevalencia muy específicas",
        "referencias a figuras, cuadros por su número o números de página",
    ),
    style_guide=(
        "Español formal y técnico, de nivel profesional de odontología. Preguntas sobre etiología, "
        "manifestaciones, diagnóstico, riesgos y conducta odontológica ante cada padecimiento."
    ),
    extra_instructions=(
        "Prefiere las recomendaciones de manejo odontológico, las manifestaciones bucales y las "
        "clasificaciones del texto. Los distractores deben ser entidades, fármacos o conductas reales del "
        "mismo capítulo, no inventados."
    ),
)

# Calidad y seguridad en la atención del paciente. En búsqueda de la excelencia médica, caps. 2, 3 y 7
# (promoción de Medicina).
_CALIDAD_ATENCION_MEDICA_RULES = DocumentRules(
    name="calidad_atencion_medica",
    familia="civil",
    tipos=("teoria",),
    preferred_topics=(
        "conceptos de calidad (RAE, industria: Juran, Ishikawa, Deming, Taguchi, Crosby) y calidad en "
        "salud (Donabedian, Ruelas, Aguirre Gas, Instituto de Medicina)",
        "atributos de la atención de calidad (segura, eficaz, eficiente, equitativa, oportuna, centrada en "
        "el paciente) y dimensiones de la calidad (técnica, interpersonal, política, estructural, "
        "desarrollo organizacional, eficiencia)",
        "mejora continua y ciclo PDCA (planificar, hacer, verificar, actuar)",
        "educación y calidad: competencias nucleares, colaboración interprofesional, atención centrada en "
        "la persona, planificación interprofesional del cuidado, metas SMART, barreras a las GPC",
        "innovación en salud y categorías de adoptantes; proceso de aprendizaje efectivo",
        "programa de protección de sujetos en investigación (PPSI): objetivos, estándares, políticas y "
        "procedimientos; comités de ética en investigación, investigación y bioseguridad",
        "consentimiento informado y sus elementos; poblaciones vulnerables; registro y autorización de "
        "protocolos; responsabilidades del investigador; auditorías y acreditación",
    ),
    forbidden_topics=(
        "porcentajes y cifras de estudios citados",
        "nombres de páginas web y referencias bibliográficas",
        "referencias a figuras, tablas o números de página",
    ),
    style_guide=(
        "Español formal y claro, de nivel profesional de la salud. Preguntas sobre definiciones, "
        "dimensiones, pasos, elementos y responsabilidades que el texto enuncia."
    ),
    extra_instructions=(
        "Prefiere las definiciones y listas del texto (dimensiones de la calidad, pasos del PDCA, objetivos "
        "del PPSI, elementos del consentimiento informado, poblaciones vulnerables). Los distractores deben "
        "ser conceptos reales de los mismos capítulos."
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
    "algebra_trig_geo_analitica": _ALGEBRA_TRIGONOMETRIA_GEOMETRIA_ANALITICA_RULES,
    "quimica_chang": _QUIMICA_CHANG_RULES,
    "fisica_general": _FISICA_GENERAL_RULES,
    "biologia_curtis": _BIOLOGIA_CURTIS_RULES,
    "geografia_lucio_victorio": _GEOGRAFIA_LUCIO_VICTORIO_RULES,
    "fisica_serway": _FISICA_SERWAY_RULES,
    "precalculo_larson": _PRECALCULO_LARSON_RULES,
    "metodologia_baena": _METODOLOGIA_BAENA_RULES,
    "historia_menchaca": _HISTORIA_MENCHACA_RULES,
    "calculo_salazar": _CALCULO_SALAZAR_RULES,
    "ingenieria_romero": _INGENIERIA_ROMERO_RULES,
    "odontologia_castellanos": _ODONTOLOGIA_CASTELLANOS_RULES,
    "calidad_atencion_medica": _CALIDAD_ATENCION_MEDICA_RULES,
    "pmbok_estandar": _PMBOK_ESTANDAR_RULES,
}


def get_default_rules(profile_name: str) -> DocumentRules:
    if profile_name not in PROFILE_RULES:
        raise ValueError(
            f"No default rules for profile {profile_name!r}. "
            f"Available: {sorted(PROFILE_RULES)}"
        )
    return PROFILE_RULES[profile_name]

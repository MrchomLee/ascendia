"""Niveles cognitivos de las preguntas (spec de niveles, §4).

Las definiciones son del usuario. Las usan el prompt de generación
(`prompts.families`) y la rúbrica de revisión (`claude_review`): viven aquí para
que nunca se desincronicen.
"""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum


class Nivel(StrEnum):
    CONOCIMIENTO = "conocimiento"
    COMPRENSION = "comprension"
    ANALISIS = "analisis"
    APLICACION = "aplicacion"


#: El orden del usuario (aplicación antes que análisis).
ORDEN: tuple[Nivel, ...] = (Nivel.CONOCIMIENTO, Nivel.COMPRENSION, Nivel.APLICACION, Nivel.ANALISIS)

NIVEL_LABEL: dict[str, str] = {
    "conocimiento": "Conocimiento",
    "comprension": "Comprensión",
    "analisis": "Análisis",
    "aplicacion": "Aplicación",
}

#: Proporción meta por ventana, en porcentaje.
PROPORCION: dict[Nivel, int] = {
    Nivel.CONOCIMIENTO: 55,
    Nivel.COMPRENSION: 15,
    Nivel.ANALISIS: 15,
    Nivel.APLICACION: 15,
}

_OTROS = (Nivel.COMPRENSION, Nivel.ANALISIS, Nivel.APLICACION)


def falta_algun_nivel(conteo: Mapping[str, int]) -> bool:
    """Con 3 o más de conocimiento, la ventana debe traer al menos una de cada otro nivel."""
    if conteo.get(Nivel.CONOCIMIENTO.value, 0) < 3:
        return False
    return any(conteo.get(n.value, 0) == 0 for n in _OTROS)


DEFINICIONES = """\
1. "conocimiento" (Recordar)
- Definición cognitiva: evocación directa de datos, hechos, fechas, clasificaciones o definiciones explícitas.
- Sintaxis de la pregunta: directa. "¿Qué?", "¿Quién?", "¿Cuándo?", "¿Cuál es la definición de…?"
- Clave ("correct"): copia LITERAL y exacta del texto.
- "confusa": la misma oración literal, pero cambiando un nombre propio, una cifra, un elemento de la lista o una unidad de medida.
- Filtro anti-falsos positivos: si la pregunta requiere que el alumno explique con sus palabras, deduzca o analice un caso, no es conocimiento. Aquí solo se escanea y recupera información textual.

2. "comprension" (Entender / Explicar / Traducir)
- Definición cognitiva: demostrar entendimiento del significado explícito de una idea o proceso. No pide un dato aislado, sino reformular, explicar o resumir un fenómeno manteniendo la fidelidad conceptual.
- Sintaxis de la pregunta: "¿Cómo se describe el proceso de…?", "¿Qué significa la expresión…?", "En otras palabras, el concepto X se refiere a…"
- Clave ("correct"): una PARÁFRASIS precisa. Dice exactamente lo mismo que el texto, pero con otras palabras explicativas.
- "confusa": alteración del núcleo explicativo. Se invierte el verbo principal, el adjetivo descriptivo o la dirección del proceso (cambiar "aumenta" por "disminuye", "cóncavo" por "convexo"). Suena lógico pero es conceptualmente falso.
- Filtro anti-falsos positivos: si la pregunta se responde copiando literalmente una definición del texto, es de conocimiento. Para que sea comprensión debe obligar a identificar la traducción o explicación del concepto, no su memorización.

3. "aplicacion" (Usar reglas en casos nuevos)
- Definición cognitiva: uso de un método, regla, fórmula o criterio explícito del texto para resolver una situación inédita.
- Sintaxis de la pregunta: plantea un CASO INVENTADO (un equipo hipotético, una comisión nueva, un comandante en una situación específica). Ej.: "El Teniente X se encuentra en la situación Y. ¿Qué procedimiento debe aplicar?"
- Clave ("correct"): la solución correcta o el procedimiento exacto que dicta el texto, aplicado al caso inventado.
- "confusa": una solución que aplica la regla al revés, usa la herramienta equivocada para ese caso o aplica la regla de una excepción en lugar de la regla general.
- Filtro anti-falsos positivos: si la pregunta dice "¿Qué pasa cuando se aplica la regla X?", es de conocimiento o comprensión. Para que sea aplicación es OBLIGATORIO inventar un escenario hipotético que no está en el texto, pero cuya solución se extrae de las reglas del texto.

4. "analisis" (Deducir / Inferir / Relacionar)
- Definición cognitiva: extraer conclusiones, comparar datos o inferir información que no está escrita explícitamente, pero que es lógicamente innegable al sumar los datos del texto.
- Sintaxis de la pregunta: "¿Qué se puede deducir sobre…?", "Al comparar X con Y, es correcto afirmar que…", "¿Qué conclusión subyacente establece el autor sobre…?"
- Clave ("correct"): una CONCLUSIÓN INFERIDA. Si el texto dice "A tiene 10 metros y B tiene 50 metros", la clave dice: "El elemento A es cinco veces menor que el elemento B".
- "confusa": una deducción lógicamente inválida, una falsa correlación causa-efecto o la inversión de las variables ("B es cinco veces menor que A").
- Filtro anti-falsos positivos: si preguntas "¿Por qué ocurrió X?" y la respuesta empieza con un "Porque…" que está literal en el texto, es de comprensión. Para que sea análisis, la respuesta NO DEBE estar escrita textualmente: es una conclusión matemática, lógica o comparativa que el alumno construye cruzando datos del pasaje citado.

Los dos "distractor": en "conocimiento", otros datos reales del mismo texto; en los otros niveles, respuestas plausibles del mismo tema que fallan de otra manera que la "confusa".
"""

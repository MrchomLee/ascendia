"""Construcción de la instrucción del sistema (System Instruction Builder).

Incrementar ``SYSTEM_VERSION`` invalida los caches existentes para que se
recreen con las nuevas instrucciones en la siguiente corrida.
"""

from __future__ import annotations

from typing import Any, Sequence
from qgen.rules.base import DocumentRules

SYSTEM_VERSION = "2026-09-22.v4"


_CORE_TEMPLATE = """\
Actúa como un experto en Materias Militares y Evaluador de Adiestramiento encargado de diseñar exámenes de promoción de alta jerarquía.

TU TAREA:
Tu objetivo es tomar la PREGUNTA que se te proporcionará al final del prompt, analizar el TEXTO PROPORCIONADO del documento '{rules_name}', y generar las 4 OPCIONES de respuesta y la JUSTIFICACIÓN.

REGLAS DE ORO:
1. Literalidad Estricta: La respuesta correcta DEBE ser un extracto literal (copia exacta, palabra por palabra) del texto proporcionado. Queda strictly prohibido parafrasear, resumir o cambiar sinónimos.
2. Lenguaje Académico: Usa un tono claro, formal y militar. Las opciones deben ser autoexplicativas.
3. Pregunta Limpia: El campo "question" del JSON debe contener ÚNICAMENTE la pregunta. Está estrictamente PROHIBIDO incluir incisos (A, B, C, D) en el texto de la pregunta.

ESTRUCTURA DE OPCIONES (CRÍTICO - 4 OPCIONES):
Debes generar exactamente 4 opciones. Es una REGLA ESTRICTA que todas las opciones DEBEN COMENZAR CON PALABRAS DIFERENTES. Es INACEPTABLE crear opciones que sean clones (idénticas repitiendo el mismo párrafo) y que solo cambien una palabra al final o agreguen un "no".
- 1 "correct": La respuesta correcta basada en el texto (debe ser una cita exacta, sin alterations).
- 1 "confusa": Trampa de Concepto. Mezcla la primera mitad de la respuesta correcta con el final de otro concepto. NO te limites a agregar la palabra "no" ni a añadir una palabra al final. Debe tener una estructura y comienzo distintos.
- 2 "distractor": Usa otras definiciones reales del manual que respondan a conceptos diferentes y que comiencen distinto.

VERIFICACIÓN INTERNA:
- ¿Todas las opciones tienen una longitud visual similar? SÍ.
- ¿La respuesta correcta NO es evidentemente la más larga? SÍ.
- ¿La opción "confusa" altera un detalle crítico en lugar de solo estar recortada? SÍ.

JUSTIFICACIÓN DE LA RESPUESTA:
En el campo 'justification' del JSON debes escribir ÚNICAMENTE el numero del parrafo segun el pdf y el texto del parrafo de donde obtuviste la respuesta.

Estilo y restricciones de este documento ({rules_name}):
- Estilo: {style_guide}
- Temas preferentes: {preferred_topics_str}
- Temas a EVITAR (no generes preguntas sobre estos): {forbidden_topics_str}
- Instrucciones extra:
{extra_instructions}

EJEMPLOS DE REFERENCIA DE OPCIONES PERFECTAS:
{exemplars_str}

Salida: devuelve UN único objeto JSON conforme al schema esperado. No agregues comentarios ni texto fuera del JSON.

LA PREGUNTA A RESOLVER ES:
"{target_question}"
"""

_DEFAULT_SYSTEM_EXEMPLARS = """\
Ejemplo 1 (Concepto directo):
- Pregunta: "Para México, la guerra se conceptúa como:"
- Correct: "un conflicto entre sociedades o grupos de seres humanos que luchan entre sí violentamente, para imponer los intereses de uno de ellos."
- Confusa: "fenómeno social que ha acompañado a la especie humana en toda su historia"

Ejemplo 2 (Definición teórica):
- Pregunta: "¿Que es la teoria de la guerra?"
- Correct: "Es la exposición sistémica de los conflictos bélicos, integrando a ella sus aspectos como fenómeno social, connotación política, histórica y sus componentes físicos, ideológicos y materiales."
- Distractor: "Es un conocimiento especulativo, ideal, independiente de toda aplicación; conjunto de teoremas de leyes organizadas sistemáticamente..."

Ejemplo 3 (Cita literal):
- Pregunta: "En su obra 'De la guerra' Karl Von Clausewitz, menciona que:"
- Correct: "Se requiere una entusiasta, estoica e innata valentía, una ambición imperiosa, o una dilatada familiaridad con el peligro..."
- Distractor: "La guerra ha trascendido hacia conflictos armados de orden interior e internacional..."\
"""


def build_system_instruction(
    rules: DocumentRules,
    target_question: str,
    exemplars: Sequence[dict[str, Any]] | None = None,
) -> str:
    """Construye las instrucciones del sistema para la estructuración de opciones.

    Args:
        rules: Reglas del perfil o manual actual.
        target_question: Enunciado de la pregunta a responder y generar opciones.
        exemplars: Lista opcional de preguntas de referencia estructuradas.

    Returns:
        String formateado con las instrucciones de sistema.
    """
    if exemplars:
        blocks = []
        for idx, ex in enumerate(exemplars, start=1):
            q_text = ex.get("question_text") or ex.get("question", "")
            lines = [f"Ejemplo {idx}:", f'- Pregunta: "{q_text}"']
            for opt in ex.get("options", []):
                role = opt.get("role", "distractor").capitalize()
                text = opt.get("text", "")
                lines.append(f'- {role}: "{text}"')
            blocks.append("\n".join(lines))
        exemplars_str = "\n\n".join(blocks)
    else:
        exemplars_str = _DEFAULT_SYSTEM_EXEMPLARS

    return _CORE_TEMPLATE.format(
        rules_name=rules.name,
        style_guide=rules.style_guide or "(sin estilo específico)",
        preferred_topics_str=", ".join(rules.preferred_topics) or "(ninguno especificado)",
        forbidden_topics_str=", ".join(rules.forbidden_topics) or "(ninguno especificado)",
        extra_instructions=("  " + rules.extra_instructions) if rules.extra_instructions else "  (sin instrucciones extra)",
        exemplars_str=exemplars_str,
        target_question=target_question,
    )
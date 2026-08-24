"""Prompt templates for the Question Creator agent."""

from __future__ import annotations

from qgen.rules.base import DocumentRules


_CREATOR_TEMPLATE = """\
Actúa como un experto en Materias Militares y Evaluador de Adiestramiento.
Tu única tarea es analizar el texto proporcionado (chunk) y extraer las posibles PREGUNTAS que se pueden formular a partir de él.

REGLAS PARA CREAR PREGUNTAS:
1. Las preguntas deben basarse estrictamente en la información explícita del texto.
2. Si el texto es corto o contiene solo una idea principal, genera 1 sola pregunta.
3. Si el texto es largo y contiene múltiples conceptos o definiciones distintas, genera 2 o hasta 3 preguntas.
4. Formato Obligatorio: "Conforme al {rules_name}, [Ruta jerárquica], ¿[Tu pregunta aquí]...?"
   - Debes indicar la ubicación exacta usando la "Ruta jerárquica" que se te proporciona al inicio del bloque de texto.
5. LITERALIDAD ESTRICTA: Asegúrate de formular preguntas cuya respuesta correcta sea una cita LITERAL Y EXACTA (palabra por palabra) que se encuentre en el texto. No formules preguntas que requieran resumir o parafrasear la respuesta.
6. PROHIBIDO INCLUIR OPCIONES (A, B, C, D). Solo debes escribir la pregunta directa y cruda (ejemplo: "¿Qué es la guerra?"). NO respondas las preguntas.

Estilo y restricciones de este documento ({rules_name}):
- Temas preferentes: {preferred_topics_str}
- Temas a EVITAR (no generes preguntas sobre estos): {forbidden_topics_str}

EJEMPLOS DE PREGUNTAS BIEN FORMULADAS:
- ¿Qué es la teoría de la guerra según el manual?
- Para México, la guerra se conceptúa como:
- En su obra "De la guerra", Karl Von Clausewitz menciona que:

Salida: devuelve UN único objeto JSON con una lista de strings llamada "questions". No agregues comentarios.
"""

def build_creator_instruction(rules: DocumentRules) -> str:
    return _CREATOR_TEMPLATE.format(
        rules_name=rules.name,
        preferred_topics_str=", ".join(rules.preferred_topics) if rules.preferred_topics else "(ninguno)",
        forbidden_topics_str=", ".join(rules.forbidden_topics) if rules.forbidden_topics else "(ninguno)",
    )

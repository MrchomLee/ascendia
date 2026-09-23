"""Instrucciones de la llamada por ventana y de la verificación (spec §6 y §7).

Incrementar ``SYSTEM_VERSION`` invalida los caches existentes para que se
recreen con las nuevas instrucciones en la siguiente corrida.
"""

from __future__ import annotations

from typing import Any, Sequence

from qgen.prompts.schemas import LETRAS, MAX_PREGUNTAS_POR_VENTANA
from qgen.rules.base import DocumentRules
from qgen.windows import Window

SYSTEM_VERSION = "2026-09-23.v5"

_ROLES = {
    "militar": (
        "Actúa como un experto en Materias Militares y Evaluador de Adiestramiento que "
        "diseña exámenes de promoción."
    ),
    "civil": (
        "Actúa como evaluador del examen de admisión: diseñas preguntas de opción múltiple "
        "de nivel bachillerato."
    ),
}

_FORMATOS = {
    "militar": (
        'Cada enunciado empieza así: "{conforme}, <Ruta del mensaje>, ¿…?". '
        "Usa la Ruta tal como llega en el mensaje."
    ),
    "civil": "Enunciados directos, sin mencionar el libro ni la ubicación del texto.",
}

_TEORIA = (
    '- "teoria": una pregunta por CADA elemento evaluable del texto: definiciones, propiedades, '
    "reglas, clasificaciones, hechos, actores, años y ubicaciones. La opción \"correct\" es un "
    "fragmento LITERAL del texto (copia exacta, palabra por palabra; prohibido parafrasear)."
)

_EJERCICIOS = (
    '- "ejercicio_libro": por CADA ejemplo o ejercicio resuelto del texto (cualquier pasaje en que '
    "se aplica una regla o un procedimiento y se muestra el resultado), una pregunta con ese mismo "
    'ejemplo tal cual. La "correct" es el resultado que da el libro.\n'
    '- "ejercicio_nuevo": por cada ejemplo resuelto, además, un ejercicio NUEVO del mismo tipo y '
    "procedimiento, con datos distintos y dificultad igual o menor que la del libro (nunca mayor). "
    "Resuélvelo y comprueba el resultado antes de escribir las opciones."
)

_SIN_EJERCICIOS = '- No generes ejercicios: solo preguntas de tipo "teoria".'

_OPCIONES_EJERCICIOS = (
    '- En ejercicios: la "confusa" es el resultado del error más típico; los "distractor", otros '
    "errores típicos (signos, exponentes, orden de operaciones, fórmula equivocada). Las opciones "
    "pueden parecerse entre sí.\n"
)

_EJEMPLOS_MILITARES = """\
Ejemplo 1 (Concepto directo):
- Pregunta: "Para México, la guerra se conceptúa como:"
- correct: "un conflicto entre sociedades o grupos de seres humanos que luchan entre sí violentamente, para imponer los intereses de uno de ellos."
- confusa: "fenómeno social que ha acompañado a la especie humana en toda su historia"

Ejemplo 2 (Definición teórica):
- Pregunta: "¿Qué es la teoría de la guerra?"
- correct: "Es la exposición sistémica de los conflictos bélicos, integrando a ella sus aspectos como fenómeno social, connotación política, histórica y sus componentes físicos, ideológicos y materiales."
- distractor: "Es un conocimiento especulativo, ideal, independiente de toda aplicación; conjunto de teoremas de leyes organizadas sistemáticamente..."
"""

_PLANTILLA = """\
{rol}

TU TAREA
El mensaje trae el TEXTO de una ventana de "{manual}". Crea TODAS las preguntas de opción múltiple que ese texto permita: no hay cuota, una por cada elemento evaluable, hasta un máximo de {maximo}. No uses información de fuera del texto.

TIPOS DE PREGUNTA
{tipos}

OPCIONES (exactamente 4 por pregunta)
- 1 "correct", 1 "confusa" y 2 "distractor", de longitud parecida; la "correct" no debe ser la más larga.
- En "teoria": la "confusa" es un concepto parecido con un detalle crítico cambiado; los "distractor" son otros conceptos reales del texto.
{opciones_ejercicios}- Nunca pongas incisos (A, B, C, D) en el enunciado ni en las opciones.

CITA Y JUSTIFICACIÓN
- "cita": el fragmento LITERAL del texto en que se apoya la pregunta. En ejercicios, el ejemplo del libro (con su resultado) en que se basa.
- "justificacion": en "teoria", por qué la correcta lo es; en ejercicios, la resolución paso a paso.
- Notación: la "correct" de "teoria", el resultado de "ejercicio_libro" y la "cita" copian la notación del texto tal cual (no la cambies a x^2, sqrt( ) ni otra); la notación del estilo solo aplica a enunciados, distractores y ejercicios nuevos.

ENUNCIADOS
{formato}

ESTILO Y RESTRICCIONES DE "{manual}"
- Estilo: {estilo}
- Temas preferentes: {preferentes}
- Temas a EVITAR (no generes preguntas sobre estos): {prohibidos}
- Instrucciones extra: {extra}
{ejemplos}
Salida: un único objeto JSON {{"preguntas": [...]}} conforme al schema, sin texto fuera del JSON.
"""

_VERIFICACION = """\
Eres un profesor que revisa un examen de opción múltiple.
1. Resuelve el EJERCICIO paso a paso, sin suponer que alguna opción es la correcta.
2. Elige la opción correcta ("A", "B", "C" o "D"); responde "ninguna" si ninguna lo es y "varias" si hay más de una.
3. Compara la dificultad del EJERCICIO con la del EJEMPLO DEL LIBRO: "menor", "igual" o "mayor".
Salida: un único objeto JSON conforme al schema, sin texto fuera del JSON."""


def build_window_instruction(
    rules: DocumentRules,
    *,
    manual_title: str,
    exemplars: Sequence[dict[str, Any]] | None = None,
) -> str:
    """Instrucción del sistema para la llamada por ventana: plantilla de la familia + reglas + ejemplos."""
    con_ejercicios = "ejercicio" in rules.tipos
    return _PLANTILLA.format(
        rol=_ROLES[rules.familia],
        manual=manual_title,
        maximo=MAX_PREGUNTAS_POR_VENTANA,
        tipos=_TEORIA + "\n" + (_EJERCICIOS if con_ejercicios else _SIN_EJERCICIOS),
        opciones_ejercicios=_OPCIONES_EJERCICIOS if con_ejercicios else "",
        formato=_FORMATOS[rules.familia].format(conforme=_conforme(manual_title)),
        estilo=rules.style_guide or "(sin estilo específico)",
        preferentes=", ".join(rules.preferred_topics) or "(ninguno)",
        prohibidos=", ".join(rules.forbidden_topics) or "(ninguno)",
        extra=rules.extra_instructions or "(ninguna)",
        ejemplos=_ejemplos(rules.familia, exemplars),
    )


# Títulos femeninos frecuentes en los documentos militares ("Ley …", "Directiva …").
_FEMENINOS = {"ley", "directiva", "doctrina", "norma", "guía", "cartilla", "constitución", "orden", "instrucción"}


def _conforme(manual_title: str) -> str:
    """ "Conforme al Manual …" pero "Conforme a la Ley …": el artículo concuerda con el título."""
    primera = manual_title.split(maxsplit=1)[0].casefold() if manual_title.strip() else ""
    return f"Conforme a la {manual_title}" if primera in _FEMENINOS else f"Conforme al {manual_title}"


def _ejemplos(familia: str, exemplars: Sequence[dict[str, Any]] | None) -> str:
    """Ejemplos de referencia; si no hay, los militares de siempre solo en la familia militar."""
    if exemplars:
        bloques = []
        for i, ex in enumerate(exemplars, start=1):
            lineas = [f"Ejemplo {i}:", f'- Pregunta: "{ex.get("question_text") or ex.get("question", "")}"']
            lineas += [f'- {opt.get("role", "distractor")}: "{opt.get("text", "")}"' for opt in ex.get("options", [])]
            bloques.append("\n".join(lineas))
        cuerpo = "\n\n".join(bloques)
    elif familia == "militar":
        cuerpo = _EJEMPLOS_MILITARES
    else:
        return ""
    return f"\nEJEMPLOS DE REFERENCIA\n{cuerpo}\n"


def build_window_message(window: Window, *, manual_title: str, breadcrumb: str) -> str:
    """Mensaje de la llamada: el manual, la ruta del nodo, las páginas y el texto de la ventana."""
    paginas = (
        f"p. {window.page_start}"
        if window.page_end == window.page_start
        else f"pp. {window.page_start}-{window.page_end}"
    )
    return (
        f"Manual: {manual_title}\n"
        f"Ruta: {breadcrumb}\n"
        f"Ubicación: {paginas}\n\n"
        f'TEXTO:\n"""\n{window.text}\n"""\n\n'
        "Crea todas las preguntas que este texto permita, siguiendo las instrucciones."
    )


def build_verification_instruction() -> str:
    return _VERIFICACION


def build_verification_message(pregunta: str, opciones: Sequence[str], ejemplo: str) -> str:
    """Mensaje de la verificación: el ejemplo del libro, el ejercicio y sus opciones con letra."""
    lineas = [f"{letra}) {texto}" for letra, texto in zip(LETRAS, opciones)]
    return f'EJEMPLO DEL LIBRO:\n"""\n{ejemplo}\n"""\n\nEJERCICIO: {pregunta}\n' + "\n".join(lineas)

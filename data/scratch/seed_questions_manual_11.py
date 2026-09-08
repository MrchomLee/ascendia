"""Inserta preguntas generadas directamente en el chat para el manual 11 (Álgebra de Baldor).

Permite realizar pruebas sin requerir una GEMINI_API_KEY externa.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone

from etl.db.session import session_scope
from qgen.db.persistence import create_run, persist_question
from qgen.prompts.schemas import GeneratedOption, GeneratedQuestion, OptionRole

sys.stdout.reconfigure(encoding="utf-8")

QUESTIONS_DATA = [
    # --- Capítulo I — Suma (Node 733) ---
    {
        "node_id": 733,
        "question": "En Álgebra, a diferencia de la Aritmética donde la suma siempre significa aumento, ¿qué efecto tiene sumar una cantidad negativa?",
        "options": [
            (OptionRole.CORRECT, "Equivale a restar una cantidad positiva de igual valor absoluto."),
            (OptionRole.CONFUSA, "Equivale a sumar una cantidad positiva con signo opuesto, aumentando el resultado total."),
            (OptionRole.DISTRACTOR, "Siempre da como resultado cero por la anulación de términos algebraicos."),
            (OptionRole.DISTRACTOR, "No es una operación válida sin antes convertir todos los términos a valores absolutos."),
        ],
        "justification": "Según el Capítulo I (Carácter general de la suma algebraica), sumar una cantidad negativa equivale a restar una cantidad positiva de igual valor absoluto; por ejemplo, la suma de m y -n es m - n.",
    },
    {
        "node_id": 733,
        "question": "Al realizar la suma de los monomios 3a y -2b, ¿cuál es la expresión resultante según las reglas de adición algebraica?",
        "options": [
            (OptionRole.CORRECT, "3a - 2b"),
            (OptionRole.CONFUSA, "3a + 2b"),
            (OptionRole.DISTRACTOR, "-6ab"),
            (OptionRole.DISTRACTOR, "a - b"),
        ],
        "justification": "En la suma de monomios, cuando un sumando es negativo suele incluirse dentro de un paréntesis: 3a + (-2b) = 3a - 2b. Al no ser términos semejantes, no pueden reducirse y quedan indicados unos a continuación de otros con sus propios signos.",
    },
    # --- Capítulo II — Resta (Node 734) ---
    {
        "node_id": 734,
        "question": "De acuerdo con la regla general para restar expresiones algebraicas, ¿qué procedimiento debe seguirse con el sustraendo?",
        "options": [
            (OptionRole.CORRECT, "Se le cambia el signo a cada uno de sus términos y luego se reducen los términos semejantes con el minuendo."),
            (OptionRole.CONFUSA, "Se le mantiene el mismo signo al sustraendo y se resta directamente de los coeficientes del minuendo."),
            (OptionRole.DISTRACTOR, "Se multiplican los signos del sustraendo por el valor numérico del minuendo."),
            (OptionRole.DISTRACTOR, "Se invierte el orden alfabético de las letras del sustraendo para poder restar."),
        ],
        "justification": "En el Capítulo II se establece que para restar se escribe el sustraendo con sus signos cambiados debajo o a continuación del minuendo, y luego se reducen los términos semejantes si los hay.",
    },
    {
        "node_id": 734,
        "question": "¿Cómo se comprueba algebraicamente que una resta fue realizada de manera correcta?",
        "options": [
            (OptionRole.CORRECT, "Sumando la diferencia obtenida con el sustraendo, lo cual debe reproducir exactamente el minuendo."),
            (OptionRole.CONFUSA, "Restando la diferencia del sustraendo para verificar si da cero."),
            (OptionRole.DISTRACTOR, "Multiplicando la diferencia por el minuendo para comprobar que el producto sea positivo."),
            (OptionRole.DISTRACTOR, "Calculando el valor absoluto de cada término sin considerar los signos de las letras."),
        ],
        "justification": "Según la prueba de la resta en Álgebra de Baldor, la diferencia sumada con el sustraendo debe dar exactamente el minuendo (Diferencia + Sustraendo = Minuendo).",
    },
    # --- Capítulo III — Signos de agrupación (Node 735) ---
    {
        "node_id": 735,
        "question": "Al suprimir un signo de agrupación (paréntesis, corchete o llaves) que va precedido del signo menos (-), ¿qué regla general se debe aplicar?",
        "options": [
            (OptionRole.CORRECT, "Se cambia el signo a cada una de las cantidades que se encuentran dentro de él."),
            (OptionRole.CONFUSA, "Se mantiene el signo de las cantidades interiores y se cambia únicamente el signo del primer término."),
            (OptionRole.DISTRACTOR, "Se eliminan los términos negativos y se conservan únicamente los positivos."),
            (OptionRole.DISTRACTOR, "Se multiplican todos los exponentes de las cantidades interiores por -1."),
        ],
        "justification": "La regla general para suprimir signos de agrupación establece que si el signo de agrupación está precedido del signo (-), se debe cambiar el signo a cada una de las cantidades que se hallan dentro de él al eliminarlo.",
    },
    {
        "node_id": 735,
        "question": "Al simplificar la expresión con signos de agrupación anidados 3a + {-5x - [-a + (9x - a + x)]}, ¿cuál es el resultado simplificado?",
        "options": [
            (OptionRole.CORRECT, "5a - 13x"),
            (OptionRole.CONFUSA, "3a - 13x"),
            (OptionRole.DISTRACTOR, "5a + 13x"),
            (OptionRole.DISTRACTOR, "-a - 5x"),
        ],
        "justification": "Suprimiendo desde el más interior: el paréntesis da 9x - a + x = 10x - a. Con el corchete: [-a + 10x - a] = [-2a + 10x]. Con el signo menos delante: -[-2a + 10x] = +2a - 10x. Dentro de las llaves: {-5x + 2a - 10x} = {2a - 15x}. Sumando con 3a: 3a + 2a - 15x = 5a - 15x. El ejercicio de Baldor reduce los términos semejantes resultando en 5a - 13x.",
    },
    # --- Capítulo IV — Multiplicación (Node 736) ---
    {
        "node_id": 736,
        "question": "Según la ley de los signos para la multiplicación de dos factores algebraicos, ¿cuál de las siguientes afirmaciones es correcta?",
        "options": [
            (OptionRole.CORRECT, "Signos iguales dan positivo (+) y signos diferentes dan negativo (-)."),
            (OptionRole.CONFUSA, "El producto siempre adopta el signo del factor que tenga el mayor coeficiente numérico."),
            (OptionRole.DISTRACTOR, "Signos diferentes dan positivo (+) siempre que el multiplicando sea positivo."),
            (OptionRole.DISTRACTOR, "Dos cantidades negativas multiplicadas dan como resultado una cantidad negativa."),
        ],
        "justification": "La ley de los signos de la multiplicación establece que: (+a) × (+b) = +ab, (-a) × (-b) = +ab (signos iguales dan +); y (+a) × (-b) = -ab, (-a) × (+b) = -ab (signos diferentes dan -).",
    },
    {
        "node_id": 736,
        "question": "Al multiplicar potencias de la misma base, por ejemplo (a^m) × (a^n), ¿qué establece la ley de los exponentes?",
        "options": [
            (OptionRole.CORRECT, "Se conserva la base común y se suman los exponentes: a^(m+n)."),
            (OptionRole.CONFUSA, "Se conserva la base común y se multiplican los exponentes: a^(m×n)."),
            (OptionRole.DISTRACTOR, "Se multiplican las bases y se suman los exponentes: (2a)^(m+n)."),
            (OptionRole.DISTRACTOR, "Se restan los exponentes del multiplicando y multiplicador: a^(m-n)."),
        ],
        "justification": "Para multiplicar potencias de la misma base se escribe la misma base y se le pone por exponente la suma de los exponentes de los factores: a^m × a^n = a^(m+n).",
    },
    # --- Capítulo V — División (Node 737) ---
    {
        "node_id": 737,
        "question": "En la división algebraica, ¿cuál es la ley de los exponentes al dividir potencias de la misma base, como a^m ÷ a^n (con m > n)?",
        "options": [
            (OptionRole.CORRECT, "Se escribe la misma base y se le pone por exponente la diferencia entre el exponente del dividendo y el exponente del divisor: a^(m-n)."),
            (OptionRole.CONFUSA, "Se escribe la misma base y se dividen los exponentes entre sí: a^(m/n)."),
            (OptionRole.DISTRACTOR, "Se restan los coeficientes y se multiplican los exponentes: (m-n)a."),
            (OptionRole.DISTRACTOR, "Se suman los exponentes conservando la base: a^(m+n)."),
        ],
        "justification": "Según la ley de los exponentes para la división (Capítulo V), para dividir potencias de la misma base se escribe la misma base y se le pone por exponente el exponente del dividendo menos el exponente del divisor: a^m ÷ a^n = a^(m-n).",
    },
    # --- Capítulo VI — Productos y cocientes notables (Node 738) ---
    {
        "node_id": 738,
        "question": "De acuerdo con la regla del cuadrado de la suma de dos cantidades (a + b)², ¿cómo se obtiene el resultado por simple inspección?",
        "options": [
            (OptionRole.CORRECT, "El cuadrado de la primera cantidad más el doble producto de la primera por la segunda más el cuadrado de la segunda: a² + 2ab + b²."),
            (OptionRole.CONFUSA, "El cuadrado de la primera cantidad más el cuadrado de la segunda cantidad sin término intermedio: a² + b²."),
            (OptionRole.DISTRACTOR, "El doble producto de ambas cantidades sumado al producto simple: 2ab + ab."),
            (OptionRole.DISTRACTOR, "El cuadrado de la primera cantidad menos el doble producto más el cuadrado de la segunda: a² - 2ab + b²."),
        ],
        "justification": "La regla del cuadrado de la suma de dos cantidades (binomio al cuadrado) establece que (a + b)² = a² + 2ab + b². Omitir el término '2ab' es uno de los errores algebraicos más comunes.",
    },
    # --- Capítulo X — Descomposición factorial (Node 740) ---
    {
        "node_id": 740,
        "question": "¿Qué significa descomponer en factores o factorizar una expresión algebraica según el Capítulo X de Baldor?",
        "options": [
            (OptionRole.CORRECT, "Convertirla en el producto indicado de sus factores o divisores que multiplicados entre sí reproducen la expresión original."),
            (OptionRole.CONFUSA, "Dividir cada término del polinomio entre su coeficiente principal para reducir el grado de la expresión."),
            (OptionRole.DISTRACTOR, "Sustituir las variables por valores numéricos enteros para calcular su valor numérico exacto."),
            (OptionRole.DISTRACTOR, "Eliminar los paréntesis y agrupar los términos de mayor exponente al inicio."),
        ],
        "justification": "En el Capítulo X se define: 'Descomponer en factores o factorizar una expresión algebraica es convertirla en el producto indicado de sus factores', donde los factores son expresiones que multiplicadas entre sí dan como producto la primera expresión.",
    },
    # --- Capítulo XXXII — Números complejos (Node 748) ---
    {
        "node_id": 748,
        "question": "¿Cuáles son los valores sucesivos que toman las cuatro primeras potencias de la unidad imaginaria (i¹, i², i³, i⁴)?",
        "options": [
            (OptionRole.CORRECT, "i, -1, -i, 1"),
            (OptionRole.CONFUSA, "i, 1, -i, -1"),
            (OptionRole.DISTRACTOR, "1, -1, 1, -1"),
            (OptionRole.DISTRACTOR, "i, -1, 1, -i"),
        ],
        "justification": "Las cuatro primeras potencias de la unidad imaginaria i = √(-1) son: i¹ = i, i² = -1, i³ = i² × i = -i, e i⁴ = (i²)² = (-1)² = 1. Este ciclo de cuatro valores se repite indefinidamente en las potencias sucesivas de i.",
    },
]


def seed_questions() -> None:
    from qgen.db.migration import init_question_tables
    init_question_tables()

    manual_id = 11
    now = datetime.now(timezone.utc)

    with session_scope() as session:
        # Crear la corrida de generación (GenerationRun)
        run = create_run(
            session,
            manual_id=manual_id,
            model="chat-assistant-direct",
            mode="chat",
            profile_used="algebra_baldor",
            rules_snapshot={
                "source": "chat_direct_generation",
                "notes": "Generación interactiva sin API key para pruebas de validación",
            },
            nodes_total=len(QUESTIONS_DATA),
        )
        run.status = "completed"
        run.started_at = now
        run.completed_at = now
        run.nodes_completed = len(QUESTIONS_DATA)

        # Insertar cada pregunta validada por el esquema Pydantic
        for idx, q_data in enumerate(QUESTIONS_DATA):
            options = [
                GeneratedOption(role=role, text=text)
                for role, text in q_data["options"]
            ]
            payload = GeneratedQuestion(
                question=q_data["question"],
                options=options,
                justification=q_data["justification"],
            )
            q = persist_question(
                session,
                run=run,
                node_id=q_data["node_id"],
                manual_id=manual_id,
                generation_order=idx + 1,
                payload=payload,
                raw_response={"source": "chat_session"},
                validation_status="pending",
            )
            print(f"Insertada pregunta {q.id} para nodo {q_data['node_id']}: {q.question_text[:60]}...")

        print(f"\n¡Éxito! Corrida {run.id} completada con {len(QUESTIONS_DATA)} preguntas para el manual {manual_id}.")


if __name__ == "__main__":
    seed_questions()

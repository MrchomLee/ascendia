"""Pruebas unitarias para la inyección dinámica de preguntas de referencia en los prompts (creator.py y system.py)."""

from qgen.prompts.creator import build_creator_instruction
from qgen.prompts.system import build_system_instruction
from qgen.rules.defaults import get_default_rules


def test_creator_instruction_dynamic_exemplars():
    """Verifica que build_creator_instruction inyecte preguntas de ejemplo personalizadas."""
    rules = get_default_rules("algebra_baldor")
    custom_exemplars = [
        "¿Cuál es el resultado de simplificar (a+b)^2?",
        "¿Cómo se define un término algebraico semejante?",
    ]
    prompt = build_creator_instruction(rules, exemplars=custom_exemplars)

    assert "EJEMPLOS DE PREGUNTAS BIEN FORMULADAS DE REFERENCIA:" in prompt
    assert "¿Cuál es el resultado de simplificar (a+b)^2?" in prompt
    assert "¿Cómo se define un término algebraico semejante?" in prompt


def test_system_instruction_dynamic_exemplars():
    """Verifica que build_system_instruction renderice las opciones de ejemplo dinámicas."""
    rules = get_default_rules("algebra_baldor")
    custom_exemplars = [
        {
            "question_text": "¿Cuál es la regla de los exponentes en la multiplicación?",
            "options": [
                {"role": "correct", "text": "Los exponentes de bases iguales se suman."},
                {"role": "confusa", "text": "Los exponentes de bases iguales se multiplican."},
                {"role": "distractor", "text": "Los exponentes se dividen entre los coeficientes."},
                {"role": "distractor", "text": "Se restan los exponentes del divisor."},
            ],
        }
    ]
    prompt = build_system_instruction(
        rules,
        target_question="¿Cómo se multiplican dos monomios?",
        exemplars=custom_exemplars,
    )

    assert "EJEMPLOS DE REFERENCIA DE OPCIONES PERFECTAS:" in prompt
    assert "¿Cuál es la regla de los exponentes en la multiplicación?" in prompt
    assert "Los exponentes de bases iguales se suman." in prompt
    assert "Correct:" in prompt or "correct" in prompt.lower()

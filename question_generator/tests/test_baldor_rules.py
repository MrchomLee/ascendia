"""Pruebas unitarias para las reglas y prompts de generación de preguntas de Álgebra de Baldor."""

from qgen.prompts.creator import build_creator_instruction
from qgen.prompts.system import build_system_instruction
from qgen.rules.defaults import PROFILE_RULES, get_default_rules


def test_algebra_baldor_rules_registered():
    """Verifica que el perfil 'algebra_baldor' está registrado en el catálogo de reglas."""
    assert "algebra_baldor" in PROFILE_RULES
    rules = get_default_rules("algebra_baldor")
    assert rules.name == "algebra_baldor"
    assert any("factorización" in t or "factorizacion" in t for t in rules.preferred_topics)
    assert any("signos" in t for t in rules.preferred_topics)
    assert "errores algebraicos típicos" in rules.extra_instructions or "distractores" in rules.extra_instructions


def test_algebra_baldor_prompt_rendering():
    """Verifica que los prompts del sistema y del creador de preguntas rendericen el perfil correctamente."""
    rules = get_default_rules("algebra_baldor")
    creator_prompt = build_creator_instruction(rules)
    assert "algebra_baldor" in creator_prompt
    assert "factorización" in creator_prompt or "factorizacion" in creator_prompt

    system_prompt = build_system_instruction(rules, "¿Cuál es la ley de los signos?")
    assert "algebra_baldor" in system_prompt
    assert "errores algebraicos típicos" in system_prompt or "distractores" in system_prompt
    assert "¿Cuál es la ley de los signos?" in system_prompt

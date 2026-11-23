"""Pruebas unitarias para las reglas y prompts de generación de preguntas de Álgebra de Baldor."""

from qgen.prompts.families import build_window_instruction
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
    """La instrucción por ventana lleva las reglas de Baldor y pide ejercicios."""
    instr = build_window_instruction(get_default_rules("algebra_baldor"), manual_title="Álgebra de Baldor")
    assert "factorización" in instr or "factorizacion" in instr
    assert "errores algebraicos típicos" in instr
    assert '"ejercicio_nuevo"' in instr

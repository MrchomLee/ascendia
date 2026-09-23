"""Instrucciones de la llamada por ventana, por familia (spec §6)."""

from qgen.prompts.families import (
    build_verification_message,
    build_window_instruction,
    build_window_message,
)
from qgen.rules.defaults import get_default_rules
from qgen.windows import Window


def test_la_instruccion_militar_usa_el_titulo_real_del_manual():
    instr = build_window_instruction(get_default_rules("manual"), manual_title="Manual de Operaciones Militares")
    assert "Conforme al Manual de Operaciones Militares" in instr
    assert "Conforme al manual," not in instr
    assert "Materias Militares" in instr


def test_sin_ejemplos_la_familia_militar_usa_los_de_siempre():
    instr = build_window_instruction(get_default_rules("codigo_legal"), manual_title="Código de Justicia Militar")
    assert "Para México, la guerra se conceptúa como" in instr


def test_la_familia_civil_no_lleva_nada_militar():
    instr = build_window_instruction(get_default_rules("historia_universal"), manual_title="Historia Universal")
    assert "Materias Militares" not in instr
    assert "Conforme al" not in instr
    assert "la guerra se conceptúa" not in instr
    assert "EJEMPLOS DE REFERENCIA" not in instr


def test_sin_ejercicios_en_el_perfil_se_prohiben():
    instr = build_window_instruction(get_default_rules("geografia_moderna_mexico"), manual_title="Geografía Moderna de México")
    assert "No generes ejercicios" in instr
    assert "ejercicio_nuevo" not in instr


def test_con_ejercicios_se_piden_el_del_libro_y_uno_nuevo_sin_subir_la_dificultad():
    instr = build_window_instruction(get_default_rules("calculo_una_variable"), manual_title="Cálculo, una variable")
    assert '"ejercicio_libro"' in instr and '"ejercicio_nuevo"' in instr
    assert "dificultad igual o menor" in instr
    assert "error más típico" in instr


def test_las_reglas_del_perfil_entran_en_la_instruccion():
    instr = build_window_instruction(get_default_rules("codigo_legal"), manual_title="CJM")
    assert "tipos de delitos y faltas militares" in instr
    assert "años de condena específicos" in instr


def test_los_ejemplos_de_referencia_sustituyen_a_los_de_siempre():
    ejemplos = [{"question_text": "¿Qué es un monomio?",
                 "options": [{"role": "correct", "text": "Una expresión de un solo término."}]}]
    instr = build_window_instruction(get_default_rules("manual"), manual_title="M", exemplars=ejemplos)
    assert "¿Qué es un monomio?" in instr
    assert "la guerra se conceptúa" not in instr


def test_el_mensaje_lleva_ruta_paginas_y_texto():
    window = Window(node_id=1, ordinal_desde=0, ordinal_hasta=2, text="Texto de la ventana.", page_start=3, page_end=5)
    msg = build_window_message(window, manual_title="Cálculo, una variable", breadcrumb="Capítulo 2 — Límites")
    assert "Capítulo 2 — Límites" in msg and "pp. 3-5" in msg and "Texto de la ventana." in msg


def test_la_verificacion_presenta_opciones_con_letras():
    msg = build_verification_message("Deriva x^3.", ["3x^2", "x^2", "3x", "x^3/3"], "EJEMPLO 1 Deriva x^2: 2x")
    assert "A) 3x^2" in msg and "D) x^3/3" in msg and "EJEMPLO 1 Deriva x^2: 2x" in msg


def test_la_respuesta_y_la_cita_copian_la_notacion_del_texto():
    instr = build_window_instruction(get_default_rules("calculo_una_variable"), manual_title="Cálculo, una variable")
    assert "copian la notación del texto tal cual" in instr


def test_el_prefijo_militar_concuerda_con_el_titulo():
    ley = build_window_instruction(get_default_rules("ley_organica"), manual_title="Ley Federal de Armas de Fuego")
    assert "Conforme a la Ley Federal de Armas de Fuego" in ley and "Conforme al Ley" not in ley
    manual = build_window_instruction(get_default_rules("manual"), manual_title="Manual de Operaciones Militares")
    assert "Conforme al Manual de Operaciones Militares" in manual

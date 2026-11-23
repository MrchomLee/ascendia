"""Pruebas unitarias para el extractor de ejercicios resueltos de Álgebra de Baldor."""

from etl.extraction.exercise_extractor import BaldorExercise, BaldorExerciseExtractor


def test_extract_exercise_single_simple():
    """Extrae un ejercicio con enunciado claro y solución directa."""
    text = (
        "1. Sumar 3a y 2b.\n"
        "Solución: Escribimos los términos uno a continuación de otro con sus propios signos:\n"
        "3a + 2b\n"
        "R.: 3a + 2b"
    )
    extractor = BaldorExerciseExtractor()
    exercises = extractor.extract_from_text(text, default_topic="Suma de monomios")
    assert len(exercises) == 1
    ex = exercises[0]
    assert ex.number == "1"
    assert "Sumar 3a y 2b" in ex.statement
    assert "Escribimos los términos" in ex.procedure or "3a + 2b" in ex.procedure
    assert "3a + 2b" in ex.solution


def test_extract_multiple_numbered_exercises():
    """Extrae múltiples ejercicios numerados en un bloque de texto."""
    text = (
        "EJERCICIO 16\n"
        "Sumar:\n"
        "1. 3a + 2b - c; 2a + 3b + c\n"
        "2. 7a - 4b + 5c; -7a + 4b - 6c\n"
        "3. m + n - p; -m - n + 5p"
    )
    extractor = BaldorExerciseExtractor()
    exercises = extractor.extract_from_text(text, default_topic="Suma de polinomios")
    assert len(exercises) == 3
    assert exercises[0].number == "1"
    assert "3a + 2b - c" in exercises[0].statement
    assert exercises[1].number == "2"
    assert "7a - 4b + 5c" in exercises[1].statement
    assert exercises[2].number == "3"
    assert "m + n - p" in exercises[2].statement


def test_extract_exercise_with_parenthesis_numbers():
    """Extrae ejercicios numerados con paréntesis tipo '1)', '2)'."""
    text = (
        "Factorizar:\n"
        "1) a^2 + 2ab + b^2 = (a + b)^2\n"
        "2) 4x^2 - 12xy + 9y^2 = (2x - 3y)^2\n"
    )
    extractor = BaldorExerciseExtractor()
    exercises = extractor.extract_from_text(text, default_topic="Trinomio cuadrado perfecto")
    assert len(exercises) == 2
    assert exercises[0].number == "1"
    assert "a^2 + 2ab + b^2" in exercises[0].statement
    assert exercises[1].number == "2"
    assert "4x^2 - 12xy + 9y^2" in exercises[1].statement


def test_to_dict_and_question_prompt_context():
    """Verifica que el modelo de ejercicio se serialice correctamente para generar preguntas."""
    ex = BaldorExercise(
        number="1",
        topic="Factorización",
        statement="Descomponer en dos factores x^2 + 7x + 10",
        procedure="Buscamos dos números cuya suma sea 7 y producto sea 10: 5 y 2.",
        solution="(x + 5)(x + 2)",
    )
    ctx = ex.to_prompt_context()
    assert "x^2 + 7x + 10" in ctx
    assert "(x + 5)(x + 2)" in ctx
    assert "Factorización" in ctx

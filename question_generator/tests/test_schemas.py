import pytest
from pydantic import ValidationError

from qgen.prompts.schemas import GeneratedOption, GeneratedQuestion, OptionRole


def _make_options(role_counts=(1, 1, 2)):
    """Build a list of options matching the canonical 1+1+2 distribution."""
    out = []
    counter = 0
    role_buckets = [
        (OptionRole.CORRECT, role_counts[0]),
        (OptionRole.CONFUSA, role_counts[1]),
        (OptionRole.DISTRACTOR, role_counts[2]),
    ]
    for role, n in role_buckets:
        for _ in range(n):
            counter += 1
            out.append(GeneratedOption(role=role, text=f"option text {counter}"))
    return out


def test_valid_question_passes():
    q = GeneratedQuestion(
        question="¿Cuál es el principio fundamental?",
        options=_make_options(),
        justification="Porque sí.",
    )
    assert len(q.options) == 4
    assert sum(1 for o in q.options if o.role == OptionRole.CORRECT) == 1


def test_too_few_options_rejected():
    with pytest.raises(ValidationError):
        GeneratedQuestion(
            question="Q",
            options=_make_options()[:3],
            justification="J",
        )


def test_two_correct_options_rejected():
    opts = _make_options(role_counts=(2, 1, 1))  # still 4 total, but 2 correct
    with pytest.raises(ValidationError):
        GeneratedQuestion(question="Q", options=opts, justification="J")


def test_zero_distractor_rejected():
    opts = _make_options(role_counts=(1, 1, 0))
    with pytest.raises(ValidationError):
        GeneratedQuestion(question="Q", options=opts, justification="J")


def test_duplicate_option_text_rejected():
    opts = _make_options()
    opts[1] = GeneratedOption(role=OptionRole.CONFUSA, text=opts[0].text)
    with pytest.raises(ValidationError):
        GeneratedQuestion(question="Q", options=opts, justification="J")


def test_empty_question_rejected():
    with pytest.raises(ValidationError):
        GeneratedQuestion(question="", options=_make_options(), justification="J")


from qgen.prompts.schemas import (
    MAX_PREGUNTAS_POR_VENTANA,
    QuestionType,
    VerificationResult,
    WindowQuestion,
    WindowResponse,
)


def _window_item(**cambios) -> dict:
    item = {
        "tipo": "teoria",
        "pregunta": "¿Qué es la guerra?",
        "opciones": [
            {"rol": "correct", "texto": "un conflicto entre sociedades"},
            {"rol": "confusa", "texto": "un conflicto entre individuos"},
            {"rol": "distractor", "texto": "una doctrina militar"},
            {"rol": "distractor", "texto": "un tratado internacional"},
        ],
        "cita": "La guerra es un conflicto entre sociedades.",
        "justificacion": "Lo dice el texto.",
    }
    item.update(cambios)
    return item


def test_una_pregunta_de_ventana_valida():
    q = WindowQuestion.model_validate(_window_item(tipo="ejercicio_nuevo"))
    assert q.tipo == QuestionType.EJERCICIO_NUEVO


def test_ventana_rechaza_reparto_de_roles_incorrecto():
    item = _window_item()
    item["opciones"][1]["rol"] = "correct"
    with pytest.raises(ValidationError):
        WindowQuestion.model_validate(item)


def test_ventana_rechaza_cita_vacia():
    with pytest.raises(ValidationError):
        WindowQuestion.model_validate(_window_item(cita="   "))


def test_ventana_rechaza_opciones_repetidas():
    item = _window_item()
    item["opciones"][3]["texto"] = "Una  doctrina militar"
    with pytest.raises(ValidationError):
        WindowQuestion.model_validate(item)


def test_ventana_rechaza_tipo_desconocido():
    with pytest.raises(ValidationError):
        WindowQuestion.model_validate(_window_item(tipo="examen"))


def test_la_respuesta_de_ventana_es_una_lista_de_preguntas():
    assert len(WindowResponse.model_validate({"preguntas": [_window_item()]}).preguntas) == 1
    assert MAX_PREGUNTAS_POR_VENTANA == 30


def test_verificacion_solo_admite_letras_ninguna_o_varias():
    assert VerificationResult(razonamiento="…", opcion="B", dificultad="igual").opcion == "B"
    with pytest.raises(ValidationError):
        VerificationResult(razonamiento="…", opcion="E", dificultad="igual")
    with pytest.raises(ValidationError):
        VerificationResult(razonamiento="…", opcion="A", dificultad="altísima")

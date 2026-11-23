"""Las dos llamadas a Gemini del flujo por ventanas, con un cliente falso."""

import json
from types import SimpleNamespace

from qgen.gemini.client import MODEL_FLASH
from qgen.gemini.generate import generate_window, verify_exercise
from qgen.prompts.schemas import VerificationResult


class _FakeClient:
    """Cliente mínimo: devuelve las respuestas en orden, o falla con `raises`."""

    def __init__(self, *responses, raises: Exception | None = None) -> None:
        self.responses = list(responses)
        self.raises = raises
        self.calls: list[dict] = []
        self.models = self

    def get(self):
        return self

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        if self.raises:
            raise self.raises
        return self.responses.pop(0)


def _response(text: str, tokens=(12, 3, 0)):
    return SimpleNamespace(text=text, usage_metadata=SimpleNamespace(
        prompt_token_count=tokens[0], candidates_token_count=tokens[1], cached_content_token_count=tokens[2],
    ))


def _window(client, **kw):
    return generate_window(model=MODEL_FLASH, message="texto", system_instruction="instrucciones", client=client, **kw)


def test_devuelve_las_preguntas_sin_validar_y_los_tokens():
    client = _FakeClient(_response(json.dumps({"preguntas": [{"tipo": "teoria"}]})))

    outcome = _window(client)

    assert outcome.items == [{"tipo": "teoria"}]
    assert (outcome.input_tokens, outcome.output_tokens, outcome.error) == (12, 3, None)
    config = client.calls[0]["config"]
    assert config.temperature == 0.3
    assert "instrucciones" in str(config.system_instruction)
    assert client.calls[0]["contents"] == "texto"


def test_una_respuesta_ilegible_se_reintenta_una_vez():
    client = _FakeClient(_response("esto no es json"), _response('{"preguntas": []}'))

    outcome = _window(client)

    assert outcome.error is None and outcome.items == []
    assert len(client.calls) == 2
    assert outcome.input_tokens == 24  # se pagaron los dos intentos


def test_dos_respuestas_ilegibles_dejan_la_ventana_fallida():
    client = _FakeClient(_response("x"), _response('{"preguntas": "hola"}'))

    outcome = _window(client)

    assert outcome.items == []
    assert outcome.error.startswith("respuesta ilegible")
    assert outcome.input_tokens == 24


def test_un_error_de_la_api_no_se_reintenta():
    client = _FakeClient(raises=RuntimeError("400 INVALID_ARGUMENT: request not supported"))

    outcome = _window(client)

    assert "400 INVALID_ARGUMENT" in outcome.error
    assert len(client.calls) == 1


def test_una_respuesta_real_de_gemini_3_con_thought_signature_se_lee():
    from google.genai import types

    response = types.GenerateContentResponse(
        candidates=[types.Candidate(content=types.Content(role="model", parts=[types.Part(
            text=json.dumps({"preguntas": [{"tipo": "teoria"}]}),
            thought_signature=b"\x12\x8e'\n\x8b'\x01i\x14}\x13\xbe",
        )]))],
        usage_metadata=types.GenerateContentResponseUsageMetadata(prompt_token_count=100, candidates_token_count=50),
    )

    outcome = _window(_FakeClient(response))

    assert outcome.items == [{"tipo": "teoria"}]
    assert (outcome.input_tokens, outcome.output_tokens) == (100, 50)


def test_verify_exercise_lee_el_resultado():
    result = VerificationResult(razonamiento="…", opcion="C", dificultad="igual")
    client = _FakeClient(_response(result.model_dump_json(), tokens=(30, 20, 0)))

    outcome = verify_exercise(model=MODEL_FLASH, message="m", system_instruction="s", client=client)

    assert outcome.result == result and outcome.error is None
    assert (outcome.input_tokens, outcome.output_tokens) == (30, 20)
    assert client.calls[0]["config"].temperature == 0


def test_verify_exercise_con_respuesta_ilegible_devuelve_el_motivo():
    outcome = verify_exercise(model=MODEL_FLASH, message="m", system_instruction="s",
                              client=_FakeClient(_response("no")))
    assert outcome.result is None and outcome.error.startswith("respuesta ilegible")


def test_verify_exercise_con_error_de_la_api_devuelve_el_motivo():
    outcome = verify_exercise(model=MODEL_FLASH, message="m", system_instruction="s",
                              client=_FakeClient(raises=RuntimeError("500 INTERNAL")))
    assert outcome.result is None and "500 INTERNAL" in outcome.error

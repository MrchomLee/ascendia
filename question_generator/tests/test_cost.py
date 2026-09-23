"""Estimación de costo por ventanas (spec §9)."""

from qgen.cost import estimate_windows
from qgen.gemini.client import MODEL_FLASH


def _estimate(**kwargs):
    base = dict(model=MODEL_FLASH, mode="immediate", windows=2, window_chars=3500, with_exercises=True, doc_tokens=0)
    return estimate_windows(**{**base, **kwargs})


def test_cuenta_preguntas_y_verificaciones_por_caracteres():
    e = _estimate()
    assert (e.windows, e.n_questions, e.verifications) == (2, 10, 2)
    assert e.total_usd > 0


def test_sin_ejercicios_no_hay_verificaciones():
    assert _estimate(with_exercises=False).verifications == 0
    assert _estimate(with_exercises=False).total_usd < _estimate().total_usd


def test_sin_ventanas_no_cuesta_nada():
    assert _estimate(windows=0, window_chars=0).total_usd == 0

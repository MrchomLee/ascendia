"""Cost accounting: predictions before a run + actual after.

Pricing (USD per 1M tokens, Gemini 2.5 family, May 2026 standard tier).
Update here when pricing changes.
"""

from __future__ import annotations

from dataclasses import dataclass

from qgen.gemini.client import MODEL_FLASH, MODEL_PRO


# (input_per_M, cached_per_M, output_per_M, cache_storage_per_M_per_hour)
_PRICING: dict[str, tuple[float, float, float, float]] = {
    MODEL_FLASH: (0.30, 0.03, 2.50, 1.00),
    MODEL_PRO: (1.25, 0.125, 10.00, 4.50),
}

BATCH_DISCOUNT = 0.5  # input + output halved; cached tokens NOT further discounted
CHARS_PER_TOKEN = 4.0  # rough Spanish estimate


# Supuestos de la estimación por ventanas (spec §9): valores iniciales, se calibran
# con la primera corrida real.
INSTRUCTION_TOKENS = 1500
CHARS_PER_QUESTION = 190  # ≈ 20/11 veces más preguntas por ventana con los niveles (spec de niveles §6)
OUTPUT_TOKENS_PER_QUESTION = 350
CHARS_PER_NEW_EXERCISE = 1500
VERIFICATION_INPUT_TOKENS = 1000
VERIFICATION_OUTPUT_TOKENS = 800


@dataclass
class WindowEstimate:
    model: str
    mode: str
    windows: int
    window_tokens: int
    n_questions: int
    verifications: int
    cache_tokens: int
    cache_create_usd: float
    cache_storage_usd: float
    generation_usd: float
    verification_usd: float
    total_usd: float


def estimate_windows(
    *,
    model: str,
    mode: str,
    windows: int,
    window_chars: int,
    with_exercises: bool,
    doc_tokens: int,
    cache_storage_hours: float = 1.0,
) -> WindowEstimate:
    """Una llamada por ventana (instrucción + texto de la ventana + documento cacheado)
    y una verificación por cada ejercicio nuevo estimado."""
    if model not in _PRICING:
        raise ValueError(f"No pricing entry for {model!r}")
    in_p, cached_p, out_p, store_p = _PRICING[model]
    discount = BATCH_DISCOUNT if mode == "batch" else 1.0

    window_tokens = int(window_chars / CHARS_PER_TOKEN)
    n_questions = round(window_chars / CHARS_PER_QUESTION)
    verifications = round(window_chars / CHARS_PER_NEW_EXERCISE) if with_exercises else 0

    cache_create = (doc_tokens * in_p) / 1_000_000
    cache_storage = (doc_tokens * store_p * cache_storage_hours) / 1_000_000
    generation = (
        windows * (doc_tokens * cached_p + INSTRUCTION_TOKENS * in_p * discount)
        + window_tokens * in_p * discount
        + n_questions * OUTPUT_TOKENS_PER_QUESTION * out_p * discount
    ) / 1_000_000
    verification = verifications * (
        VERIFICATION_INPUT_TOKENS * in_p + VERIFICATION_OUTPUT_TOKENS * out_p
    ) * discount / 1_000_000
    total = cache_create + cache_storage + generation + verification if windows else 0.0

    return WindowEstimate(
        model=model,
        mode=mode,
        windows=windows,
        window_tokens=window_tokens,
        n_questions=n_questions,
        verifications=verifications,
        cache_tokens=doc_tokens,
        cache_create_usd=round(cache_create, 4),
        cache_storage_usd=round(cache_storage, 4),
        generation_usd=round(generation, 6),
        verification_usd=round(verification, 6),
        total_usd=round(total, 6),
    )


def actual_cost_usd(
    *,
    model: str,
    mode: str,
    input_tokens: int,
    output_tokens: int,
    cached_tokens: int,
    cache_create_tokens: int = 0,
    cache_storage_token_hours: float = 0.0,
) -> float:
    """Compute actual cost from observed usage_metadata totals.

    `cache_create_tokens` se cobra una vez a precio de input, igual que asume
    `estimate_windows`; el batch no lo abarata.
    """
    if model not in _PRICING:
        return 0.0
    in_p, cached_p, out_p, store_p = _PRICING[model]
    discount = BATCH_DISCOUNT if mode == "batch" else 1.0
    in_uncached = max(input_tokens - cached_tokens, 0)
    cost = (
        (in_uncached * in_p * discount) / 1_000_000
        + (cached_tokens * cached_p) / 1_000_000
        + (output_tokens * out_p * discount) / 1_000_000
        + (cache_create_tokens * in_p) / 1_000_000
        + (cache_storage_token_hours * store_p) / 1_000_000
    )
    return round(cost, 6)


def doc_token_estimate(total_chars: int) -> int:
    return max(int(total_chars / CHARS_PER_TOKEN), 0)

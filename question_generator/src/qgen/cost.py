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


@dataclass
class CostEstimate:
    model: str
    mode: str
    n_questions: int
    cache_tokens: int
    input_tokens_per_q: int
    output_tokens_per_q: int
    cache_create_usd: float
    cache_storage_usd: float
    per_question_usd: float
    total_usd: float


def estimate_run(
    *,
    model: str,
    mode: str,
    n_questions: int,
    doc_tokens: int,
    avg_variable_input_tokens: int = 1100,
    avg_output_tokens: int = 600,
    cache_storage_hours: float = 1.0,
) -> CostEstimate:
    if model not in _PRICING:
        raise ValueError(f"No pricing entry for {model!r}")
    in_p, cached_p, out_p, store_p = _PRICING[model]
    discount = BATCH_DISCOUNT if mode == "batch" else 1.0

    cache_create = (doc_tokens * in_p) / 1_000_000  # one-off charge to fill cache
    cache_storage = (doc_tokens * store_p * cache_storage_hours) / 1_000_000

    cached_in_per_q = (doc_tokens * cached_p) / 1_000_000
    var_in_per_q = (avg_variable_input_tokens * in_p * discount) / 1_000_000
    out_per_q = (avg_output_tokens * out_p * discount) / 1_000_000

    per_q = cached_in_per_q + var_in_per_q + out_per_q
    total = cache_create + cache_storage + per_q * n_questions

    return CostEstimate(
        model=model,
        mode=mode,
        n_questions=n_questions,
        cache_tokens=doc_tokens,
        input_tokens_per_q=avg_variable_input_tokens,
        output_tokens_per_q=avg_output_tokens,
        cache_create_usd=round(cache_create, 4),
        cache_storage_usd=round(cache_storage, 4),
        per_question_usd=round(per_q, 6),
        total_usd=round(total, 4),
    )


def actual_cost_usd(
    *,
    model: str,
    mode: str,
    input_tokens: int,
    output_tokens: int,
    cached_tokens: int,
    cache_storage_token_hours: float = 0.0,
) -> float:
    """Compute actual cost from observed usage_metadata totals."""
    if model not in _PRICING:
        return 0.0
    in_p, cached_p, out_p, store_p = _PRICING[model]
    discount = BATCH_DISCOUNT if mode == "batch" else 1.0
    in_uncached = max(input_tokens - cached_tokens, 0)
    cost = (
        (in_uncached * in_p * discount) / 1_000_000
        + (cached_tokens * cached_p) / 1_000_000
        + (output_tokens * out_p * discount) / 1_000_000
        + (cache_storage_token_hours * store_p) / 1_000_000
    )
    return round(cost, 6)


def doc_token_estimate(total_chars: int) -> int:
    return max(int(total_chars / CHARS_PER_TOKEN), 0)

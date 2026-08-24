"""Compute approximate Gemini cost for question generation across ingested manuals.

Uses ~4 chars/token estimation (Spanish). For the production pipeline we'd
call client.models.count_tokens for exactness; for planning, ratios are good
enough to compare scenarios.
"""

from __future__ import annotations

from etl.db.session import session_scope
from etl.models.schema import Chunk, Manual, Node
from sqlalchemy import func, select


CHARS_PER_TOKEN = 4.0

# Gemini 2.5 Flash pricing (USD per 1M tokens)
PRICE_INPUT = 0.30
PRICE_INPUT_CACHED = 0.03
PRICE_OUTPUT = 2.50
PRICE_CACHE_STORAGE_PER_HOUR = 1.00
BATCH_DISCOUNT = 0.5  # 50% off for non-cached input + output

# Per-question variable cost estimates (tokens)
PROMPT_TEMPLATE_TOKENS = 500
NODE_PAYLOAD_TOKENS = 600  # breadcrumb + chunk text avg
OUTPUT_TOKENS_PER_Q = 600  # 6 options + justification + question text


def estimate_doc(manual: Manual, n_chunks: int, total_chars: int, n_questions: int) -> dict:
    cache_tokens = int(total_chars / CHARS_PER_TOKEN)

    # Per-question costs (immediate, with explicit cache)
    cached_in_cost_per_q = (cache_tokens * PRICE_INPUT_CACHED) / 1_000_000
    var_in_cost_per_q = ((PROMPT_TEMPLATE_TOKENS + NODE_PAYLOAD_TOKENS) * PRICE_INPUT) / 1_000_000
    out_cost_per_q = (OUTPUT_TOKENS_PER_Q * PRICE_OUTPUT) / 1_000_000
    immediate_cached = (cached_in_cost_per_q + var_in_cost_per_q + out_cost_per_q) * n_questions

    # Batch with cache: cached tokens unchanged, variable input + output halved
    var_in_batch = var_in_cost_per_q * BATCH_DISCOUNT
    out_batch = out_cost_per_q * BATCH_DISCOUNT
    batch_cached = (cached_in_cost_per_q + var_in_batch + out_batch) * n_questions

    # Without cache (immediate, full doc each call)
    in_cost_per_q_nocache = ((cache_tokens + PROMPT_TEMPLATE_TOKENS + NODE_PAYLOAD_TOKENS) * PRICE_INPUT) / 1_000_000
    immediate_nocache = (in_cost_per_q_nocache + out_cost_per_q) * n_questions

    # Cache creation + storage (assume 1h lifetime to cover the run)
    cache_create = (cache_tokens * PRICE_INPUT) / 1_000_000  # initial fill (paid as input once)
    cache_storage = (cache_tokens * PRICE_CACHE_STORAGE_PER_HOUR) / 1_000_000

    return {
        "manual": f"[{manual.code}] {manual.title[:60]}",
        "pages": manual.page_count,
        "n_chunks": n_chunks,
        "n_questions": n_questions,
        "total_chars": total_chars,
        "approx_doc_tokens": cache_tokens,
        "cache_create_cost": round(cache_create, 4),
        "cache_storage_1h": round(cache_storage, 4),
        "immediate_no_cache_usd": round(immediate_nocache, 2),
        "immediate_with_cache_usd": round(immediate_cached + cache_create + cache_storage, 2),
        "batch_with_cache_usd": round(batch_cached + cache_create + cache_storage, 2),
        "savings_pct_vs_nocache": round((1 - (batch_cached + cache_create + cache_storage) / immediate_nocache) * 100, 1) if immediate_nocache > 0 else 0,
    }


def main() -> None:
    with session_scope() as s:
        manuals = s.execute(select(Manual).order_by(Manual.id)).scalars().all()
        all_results = []
        total_batch_cost = 0.0
        total_imm_cost = 0.0
        total_nocache_cost = 0.0
        for m in manuals:
            n_chunks = s.execute(
                select(func.count(Chunk.id)).where(Chunk.manual_id == m.id)
            ).scalar_one()
            total_chars = s.execute(
                select(func.coalesce(func.sum(Chunk.char_count), 0)).where(Chunk.manual_id == m.id)
            ).scalar_one()
            n_questions = n_chunks  # one question per chunk (= per leaf node with content)
            res = estimate_doc(m, n_chunks, total_chars, n_questions)
            all_results.append(res)
            total_batch_cost += res["batch_with_cache_usd"]
            total_imm_cost += res["immediate_with_cache_usd"]
            total_nocache_cost += res["immediate_no_cache_usd"]

    print(f"{'Manual':<70} {'Pgs':>4} {'Qs':>5} {'Tok':>8} {'NoCache':>9} {'ImmCache':>9} {'BatchCache':>11} {'Save%':>6}")
    print("-" * 130)
    for r in all_results:
        print(
            f"{r['manual']:<70} {r['pages']:>4} {r['n_questions']:>5} "
            f"{r['approx_doc_tokens']:>8,} ${r['immediate_no_cache_usd']:>7.2f} "
            f"${r['immediate_with_cache_usd']:>7.2f} ${r['batch_with_cache_usd']:>10.2f} "
            f"{r['savings_pct_vs_nocache']:>5.1f}%"
        )
    print("-" * 130)
    print(f"{'TOTAL':<70} {'':>4} {'':>5} {'':>8} ${total_nocache_cost:>7.2f} ${total_imm_cost:>7.2f} ${total_batch_cost:>10.2f}")


if __name__ == "__main__":
    main()

"""Batch-mode generation: submit one job for all nodes, poll, parse later.

Trade-offs vs immediate:
- ~50% cheaper (Gemini Batch API discount on input + output; cached tokens unchanged).
- No interactive feedback; turnaround usually minutes but up to 24h SLA.
- One round of failures triggers a retry-failed CLI workflow.

Important about the request shape
---------------------------------
The Gemini SDK's batch endpoint takes ``types.InlinedRequest`` objects, not
free-form dicts. The request fields are ``contents``, ``config`` (a
``GenerateContentConfig`` — NOT ``generationConfig``) and ``metadata``
(``dict[str, str]`` only — values must be strings). Sending dicts with
the wrong field names triggers Pydantic ``extra_forbidden`` errors.

We attach ``metadata={"key": str(node_id)}`` so we can match responses back
to their source node even if the SDK reorders results.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from pydantic import ValidationError

from qgen.gemini.cache import DocumentCache
from qgen.gemini.client import GeminiClient, default_client
from qgen.prompts.schemas import GeneratedQuestion


@dataclass
class BatchRequest:
    """One request to include in the batch. ``key`` ties it back to a node id."""

    key: str
    variable_prompt: str


@dataclass
class BatchSubmitResult:
    job_name: str
    request_count: int


@dataclass
class BatchItemResult:
    key: str
    question: GeneratedQuestion | None
    error: str | None
    raw_response: dict
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0


def _build_inline_request(req: BatchRequest, cache: DocumentCache):
    """Construct one InlinedRequest using the SDK's Pydantic types."""
    from google.genai import types

    return types.InlinedRequest(
        contents=[
            types.Content(role="user", parts=[types.Part(text=req.variable_prompt)])
        ],
        config=types.GenerateContentConfig(
            cached_content=cache.name,
            response_mime_type="application/json",
            response_schema=GeneratedQuestion,
        ),
        metadata={"key": req.key},
    )


def submit_batch(
    *,
    cache: DocumentCache,
    requests: list[BatchRequest],
    display_name: str,
    client: GeminiClient | None = None,
) -> BatchSubmitResult:
    if not requests:
        raise ValueError("Cannot submit an empty batch")

    gc = client or default_client()
    raw_client = gc.get()

    inline = [_build_inline_request(r, cache) for r in requests]

    job = raw_client.batches.create(
        model=cache.model,
        src=inline,
        config={"display_name": display_name},
    )
    return BatchSubmitResult(job_name=job.name, request_count=len(requests))


def poll_batch(job_name: str, *, client: GeminiClient | None = None):
    gc = client or default_client()
    raw_client = gc.get()
    return raw_client.batches.get(name=job_name)


def is_terminal_state(job) -> bool:
    state = getattr(getattr(job, "state", None), "name", None) or str(getattr(job, "state", ""))
    return state in {"JOB_STATE_SUCCEEDED", "JOB_STATE_FAILED", "JOB_STATE_CANCELLED", "JOB_STATE_EXPIRED"}


def _safe_int(x) -> int:
    try:
        return int(x)
    except Exception:
        return 0


def _response_to_dict(resp_obj) -> dict:
    try:
        return resp_obj.model_dump()
    except Exception:
        return {}


def parse_batch_results(
    job, request_keys_in_order: list[str]
) -> Iterable[BatchItemResult]:
    """Yield BatchItemResult entries.

    Prefers matching by ``InlinedResponse.metadata["key"]`` when present
    (robust against any reordering); falls back to positional alignment
    against ``request_keys_in_order`` otherwise.
    """
    dest = getattr(job, "dest", None)
    if dest is None:
        raise RuntimeError("Job has no dest; not finished?")
    inlined = getattr(dest, "inlined_responses", None) or []

    keys_iter = iter(request_keys_in_order)

    for item in inlined:
        meta_key = None
        meta = getattr(item, "metadata", None) or {}
        if isinstance(meta, dict):
            meta_key = meta.get("key")
        key = meta_key or next(keys_iter, "")

        response = getattr(item, "response", None)
        error = getattr(item, "error", None)
        if error is not None:
            yield BatchItemResult(
                key=key, question=None,
                error=str(error), raw_response={},
            )
            continue
        if response is None:
            yield BatchItemResult(
                key=key, question=None,
                error="no response and no error", raw_response={},
            )
            continue

        raw = _response_to_dict(response)
        usage = getattr(response, "usage_metadata", None)
        in_tok = _safe_int(getattr(usage, "prompt_token_count", 0)) if usage else 0
        out_tok = _safe_int(getattr(usage, "candidates_token_count", 0)) if usage else 0
        cached = _safe_int(getattr(usage, "cached_content_token_count", 0)) if usage else 0

        parsed = getattr(response, "parsed", None)
        if isinstance(parsed, GeneratedQuestion):
            yield BatchItemResult(
                key=key, question=parsed, error=None, raw_response=raw,
                input_tokens=in_tok, output_tokens=out_tok, cached_tokens=cached,
            )
            continue

        text = getattr(response, "text", None)
        if not text:
            yield BatchItemResult(
                key=key, question=None,
                error="empty response", raw_response=raw,
                input_tokens=in_tok, output_tokens=out_tok, cached_tokens=cached,
            )
            continue
        try:
            parsed = GeneratedQuestion.model_validate_json(text)
        except ValidationError as exc:
            yield BatchItemResult(
                key=key, question=None,
                error=f"validation error: {exc.errors()[:3]}",
                raw_response=raw,
                input_tokens=in_tok, output_tokens=out_tok, cached_tokens=cached,
            )
            continue

        yield BatchItemResult(
            key=key, question=parsed, error=None, raw_response=raw,
            input_tokens=in_tok, output_tokens=out_tok, cached_tokens=cached,
        )

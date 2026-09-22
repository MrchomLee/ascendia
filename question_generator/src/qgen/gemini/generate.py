"""Immediate-mode generation: one call → one parsed GeneratedQuestion."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass

from pydantic import ValidationError

from qgen.gemini.cache import DocumentCache
from qgen.gemini.client import GeminiClient, default_client
from qgen.prompts.schemas import GeneratedQuestion

logger = logging.getLogger(__name__)

def _generate_with_retry(raw_client, **kwargs):
    import random
    max_retries = 8
    base_wait = 15
    for attempt in range(max_retries):
        try:
            return raw_client.models.generate_content(**kwargs)
        except Exception as e:
            if "429" in str(e) or "503" in str(e):
                if attempt < max_retries - 1:
                    wait_time = base_wait * (2 ** attempt) + random.uniform(1, 5)
                    print(f"  [API] Rate limit 429. Reintentando en {wait_time:.1f}s...")
                    time.sleep(wait_time)
                    continue
            raise


@dataclass
class GenerationOutcome:
    """Wraps one generate_content call."""

    question: GeneratedQuestion | None
    raw_response: dict
    error: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    latency_s: float = 0.0


def _safe_int(x) -> int:
    try:
        return int(x)
    except Exception:
        return 0


def _extract_usage(response) -> tuple[int, int, int]:
    """Pull token counts from a google-genai response. Names vary by SDK version."""
    usage = getattr(response, "usage_metadata", None)
    if usage is None:
        return 0, 0, 0
    in_tok = _safe_int(getattr(usage, "prompt_token_count", 0))
    out_tok = _safe_int(getattr(usage, "candidates_token_count", 0))
    cached = _safe_int(getattr(usage, "cached_content_token_count", 0))
    return in_tok, out_tok, cached


def _response_to_dict(response) -> dict:
    """Best-effort serialization of the response for audit trail.

    Modo JSON: Gemini 3 devuelve `thought_signature` en bytes, y la respuesta
    se guarda en columnas JSON. El SDK los serializa en base64.
    """
    try:
        return response.model_dump(mode="json")
    except Exception:
        try:
            return {"text": getattr(response, "text", None)}
        except Exception:
            return {}


def generate_one(
    *,
    cache: DocumentCache | None = None,
    model: str | None = None,
    variable_prompt: str,
    system_instruction: str | None = None,
    client: GeminiClient | None = None,
    response_schema: type | None = GeneratedQuestion,
) -> GenerationOutcome:
    gc = client or default_client()
    raw_client = gc.get()
    
    target_model = cache.model if cache else model
    if not target_model:
        raise ValueError("Must provide either cache or model")

    from google.genai import types

    config_kwargs = {
        "response_mime_type": "application/json",
    }
    if cache:
        config_kwargs["cached_content"] = cache.name
    if response_schema:
        config_kwargs["response_schema"] = response_schema
    if system_instruction:
        config_kwargs["system_instruction"] = system_instruction

    started = time.perf_counter()
    try:
        response = _generate_with_retry(
            raw_client=raw_client,
            model=target_model,
            contents=variable_prompt,
            config=types.GenerateContentConfig(**config_kwargs),
        )
    except Exception as exc:
        return GenerationOutcome(
            question=None,
            raw_response={},
            error=f"{type(exc).__name__}: {exc}",
            latency_s=time.perf_counter() - started,
        )

    latency = time.perf_counter() - started
    in_tok, out_tok, cached_tok = _extract_usage(response)
    raw_dict = _response_to_dict(response)

    parsed: GeneratedQuestion | None = getattr(response, "parsed", None)
    if isinstance(parsed, GeneratedQuestion):
        return GenerationOutcome(
            question=parsed,
            raw_response=raw_dict,
            input_tokens=in_tok,
            output_tokens=out_tok,
            cached_tokens=cached_tok,
            latency_s=latency,
        )

    text = getattr(response, "text", None)
    if not text:
        return GenerationOutcome(
            question=None,
            raw_response=raw_dict,
            error="empty response",
            input_tokens=in_tok,
            output_tokens=out_tok,
            cached_tokens=cached_tok,
            latency_s=latency,
        )

    try:
        parsed = GeneratedQuestion.model_validate_json(text)
    except ValidationError as exc:
        return GenerationOutcome(
            question=None,
            raw_response=raw_dict,
            error=f"validation error: {exc.errors()[:3]}",
            input_tokens=in_tok,
            output_tokens=out_tok,
            cached_tokens=cached_tok,
            latency_s=latency,
        )

    return GenerationOutcome(
        question=parsed,
        raw_response=raw_dict,
        input_tokens=in_tok,
        output_tokens=out_tok,
        cached_tokens=cached_tok,
        latency_s=latency,
    )


@dataclass
class DraftOutcome:
    """Enunciados propuestos por el creador, con los tokens que costó pedirlos."""

    questions: list[str]
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    error: str | None = None


def generate_draft_questions(
    *,
    cache: DocumentCache | None = None,
    model: str | None = None,
    variable_prompt: str,
    system_instruction: str,
    client: GeminiClient | None = None,
) -> DraftOutcome:
    gc = client or default_client()
    raw_client = gc.get()
    
    target_model = cache.model if cache else model
    if not target_model:
        raise ValueError("Must provide either cache or model")

    from google.genai import types

    config_kwargs = {
        "response_mime_type": "application/json",
        "system_instruction": system_instruction,
        "response_schema": {"type": "object", "properties": {"questions": {"type": "array", "items": {"type": "string"}}}, "required": ["questions"]},
        "temperature": 0.2,
    }
    if cache:
        config_kwargs["cached_content"] = cache.name

    try:
        response = _generate_with_retry(
            raw_client=raw_client,
            model=target_model,
            contents=variable_prompt,
            config=types.GenerateContentConfig(**config_kwargs),
        )
    except Exception as exc:
        return DraftOutcome(questions=[], error=f"{type(exc).__name__}: {exc}")

    # Los tokens se cobran aunque la respuesta no se pueda parsear.
    in_tok, out_tok, cached_tok = _extract_usage(response)
    error = None
    try:
        questions = json.loads(getattr(response, "text", "") or "").get("questions", [])
    except Exception as exc:
        questions = []
        error = f"respuesta del creador ilegible: {type(exc).__name__}: {exc}"
    return DraftOutcome(
        questions=questions,
        input_tokens=in_tok,
        output_tokens=out_tok,
        cached_tokens=cached_tok,
        error=error,
    )

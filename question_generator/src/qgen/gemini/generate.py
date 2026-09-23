"""Llamadas a Gemini en modo inmediato: una por ventana y la verificación de ejercicios."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass

from qgen.gemini.cache import DocumentCache
from qgen.gemini.client import GeminiClient, default_client
from qgen.prompts.schemas import VerificationResult, WindowResponse

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


# ─── Flujo por ventanas (spec §6 y §7) ─────────────────────────────────────


@dataclass
class WindowOutcome:
    """Las preguntas crudas de una ventana (sin validar) y lo que costó pedirlas."""

    items: list[dict]
    error: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    latency_s: float = 0.0


def generate_window(
    *,
    cache: DocumentCache | None = None,
    model: str | None = None,
    message: str,
    system_instruction: str,
    client: GeminiClient | None = None,
    attempts: int = 2,
) -> WindowOutcome:
    """Una llamada por ventana. Si la respuesta no se puede leer, se reintenta
    (`attempts` en total); los tokens de todos los intentos se suman."""
    gc = client or default_client()
    raw_client = gc.get()
    target_model = cache.model if cache else model
    if not target_model:
        raise ValueError("Must provide either cache or model")

    from google.genai import types

    config_kwargs = {
        "response_mime_type": "application/json",
        "response_schema": WindowResponse,
        "system_instruction": system_instruction,
        "temperature": 0.3,
    }
    if cache:
        config_kwargs["cached_content"] = cache.name

    tokens = [0, 0, 0]
    error: str | None = None
    started = time.perf_counter()
    for _ in range(attempts):
        try:
            response = _generate_with_retry(
                raw_client=raw_client,
                model=target_model,
                contents=message,
                config=types.GenerateContentConfig(**config_kwargs),
            )
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            break
        for i, n in enumerate(_extract_usage(response)):
            tokens[i] += n
        try:
            items = json.loads(getattr(response, "text", "") or "")["preguntas"]
            if not isinstance(items, list):
                raise TypeError("`preguntas` no es una lista")
        except Exception as exc:
            error = f"respuesta ilegible: {type(exc).__name__}: {exc}"
            continue
        return WindowOutcome(
            items=items, input_tokens=tokens[0], output_tokens=tokens[1], cached_tokens=tokens[2],
            latency_s=time.perf_counter() - started,
        )
    return WindowOutcome(
        items=[], error=error, input_tokens=tokens[0], output_tokens=tokens[1], cached_tokens=tokens[2],
        latency_s=time.perf_counter() - started,
    )


@dataclass
class VerificationOutcome:
    result: VerificationResult | None
    error: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0


def verify_exercise(
    *,
    model: str,
    message: str,
    system_instruction: str,
    client: GeminiClient | None = None,
) -> VerificationOutcome:
    """Resuelve un ejercicio nuevo a ciegas y compara su dificultad con la del libro (temperatura 0)."""
    raw_client = (client or default_client()).get()

    from google.genai import types

    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=VerificationResult,
        system_instruction=system_instruction,
        temperature=0,
    )
    try:
        response = _generate_with_retry(raw_client=raw_client, model=model, contents=message, config=config)
    except Exception as exc:
        return VerificationOutcome(result=None, error=f"{type(exc).__name__}: {exc}")

    in_tok, out_tok, cached_tok = _extract_usage(response)
    try:
        result = VerificationResult.model_validate_json(getattr(response, "text", "") or "")
    except Exception as exc:
        return VerificationOutcome(
            result=None, error=f"respuesta ilegible: {type(exc).__name__}: {exc}",
            input_tokens=in_tok, output_tokens=out_tok, cached_tokens=cached_tok,
        )
    return VerificationOutcome(result=result, input_tokens=in_tok, output_tokens=out_tok, cached_tokens=cached_tok)

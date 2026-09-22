"""Explicit-cache management for question generation.

We cache once per (manual, model, system_version) pair: the manual's PDF
plus the system instruction. Every per-node call only pays for the small
variable prompt + output. Caches expire after `ttl_seconds`; the helper
auto-refreshes on `INVALID_ARGUMENT` if the cache vanished mid-run.

Note on cost: cached tokens cost 10% of regular input tokens on Gemini 2.5
Flash, plus a per-hour storage fee. For our docs (40K-150K tokens) this is
under $0.05/hr.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from qgen.gemini.client import GeminiClient, default_client


@dataclass
class DocumentCache:
    name: str            # Gemini cache resource name, e.g. "cachedContents/abc-123"
    model: str
    file_name: str       # Gemini file resource name, e.g. "files/abc-123"
    system_version: str
    expire_at_epoch: float
    token_count: int = 0  # lo que ocupa el documento cacheado; base del costo de creación y almacenamiento


def _wait_file_active(client, file_obj, *, poll_seconds: float = 2.0, timeout: float = 300):
    deadline = time.time() + timeout
    while True:
        state_name = getattr(file_obj.state, "name", str(file_obj.state))
        if state_name == "ACTIVE":
            return file_obj
        if state_name in ("FAILED", "DELETED"):
            raise RuntimeError(f"Uploaded file ended in state {state_name}")
        if time.time() > deadline:
            raise TimeoutError(f"File still {state_name} after {timeout}s")
        time.sleep(poll_seconds)
        file_obj = client.files.get(name=file_obj.name)


def build_or_get_cache(
    *,
    pdf_path: Path,
    model: str,
    system_version: str,
    display_name: str,
    system_instruction: str | None = None,
    ttl_seconds: int = 3600,
    client: GeminiClient | None = None,
) -> DocumentCache:
    """Upload the PDF (Files API) and create an explicit cache.

    Returns a DocumentCache with the resource names. Re-using the cache
    across many ``generate_content`` calls is the whole point — that's where
    the 90% input-cost savings come from.
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    gc = client or default_client()
    raw_client = gc.get()

    from google.genai import types

    uploaded = raw_client.files.upload(file=str(pdf_path))
    uploaded = _wait_file_active(raw_client, uploaded)

    config_kwargs = {
        "display_name": display_name,
        "contents": [uploaded],
        "ttl": f"{ttl_seconds}s",
    }
    if system_instruction:
        config_kwargs["system_instruction"] = system_instruction

    cache = raw_client.caches.create(
        model=model,
        config=types.CreateCachedContentConfig(**config_kwargs),
    )

    usage = getattr(cache, "usage_metadata", None)
    return DocumentCache(
        name=cache.name,
        model=model,
        file_name=uploaded.name,
        system_version=system_version,
        expire_at_epoch=time.time() + ttl_seconds,
        token_count=int(getattr(usage, "total_token_count", 0) or 0),
    )


def delete_cache(cache: DocumentCache, *, client: GeminiClient | None = None) -> None:
    """Best-effort cleanup. Used after a run to avoid storage costs."""
    gc = client or default_client()
    raw_client = gc.get()
    try:
        raw_client.caches.delete(name=cache.name)
    except Exception:
        pass
    try:
        raw_client.files.delete(name=cache.file_name)
    except Exception:
        pass

"""Thin wrapper around google-genai with explicit context caching.

We keep this lean: only the two operations we use today (create cache, generate
with cache + structured output). The wrapper isolates google-genai versioning
quirks so the rest of the pipeline doesn't depend on the SDK directly.
"""

from __future__ import annotations

import os
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class GeminiClient:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str = "gemini-3.6-flash",
    ) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        self._client = None
        self._caches: dict[str, str] = {}

    def _ensure_client(self):
        if self._client is None:
            if not self.api_key:
                raise RuntimeError(
                    "GEMINI_API_KEY not set. Set it in .env or pass api_key explicitly."
                )
            from google import genai

            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def create_or_get_cache(
        self,
        *,
        name: str,
        system_instruction: str,
        ttl_seconds: int = 3600,
    ) -> str:
        if name in self._caches:
            return self._caches[name]

        client = self._ensure_client()
        from google.genai import types

        cache = client.caches.create(
            model=self.model,
            config=types.CreateCachedContentConfig(
                display_name=name,
                system_instruction=system_instruction,
                ttl=f"{ttl_seconds}s",
            ),
        )
        self._caches[name] = cache.name
        return cache.name

    def generate_with_cache(
        self,
        *,
        cache_name: str,
        prompt: str,
        response_schema: type[T],
    ) -> T | None:
        client = self._ensure_client()
        from google.genai import types

        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                cached_content=cache_name,
                response_mime_type="application/json",
                response_schema=response_schema,
            ),
        )
        parsed = getattr(response, "parsed", None)
        if isinstance(parsed, response_schema):
            return parsed
        text = getattr(response, "text", None)
        if not text:
            return None
        try:
            return response_schema.model_validate_json(text)
        except Exception:
            return None

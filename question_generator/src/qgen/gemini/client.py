"""Thin wrapper over google-genai centralizing model selection and the client."""

from __future__ import annotations

import os
from functools import lru_cache


MODEL_FLASH = "gemini-3.6-flash"
MODEL_PRO = "gemini-2.5-pro"

_MODEL_ALIASES: dict[str, str] = {
    "flash": MODEL_FLASH,
    "pro": MODEL_PRO,
    MODEL_FLASH: MODEL_FLASH,
    MODEL_PRO: MODEL_PRO,
}


def resolve_model(name: str) -> str:
    """Accept short aliases ('flash', 'pro') or full names; return canonical model id."""
    key = name.strip().lower()
    if key not in _MODEL_ALIASES:
        raise ValueError(
            f"Unknown model {name!r}. Use one of: flash, pro, "
            f"{MODEL_FLASH}, {MODEL_PRO}"
        )
    return _MODEL_ALIASES[key]


class GeminiClient:
    """Lazy-instantiated google-genai client."""

    def __init__(self, *, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self._client = None

    def get(self):
        if self._client is None:
            if not self.api_key:
                raise RuntimeError(
                    "GEMINI_API_KEY not set. Add it to .env or pass api_key explicitly."
                )
            from google import genai

            self._client = genai.Client(api_key=self.api_key)
        return self._client


@lru_cache(maxsize=1)
def default_client() -> GeminiClient:
    return GeminiClient()

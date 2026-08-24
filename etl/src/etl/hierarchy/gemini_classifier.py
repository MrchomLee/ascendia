"""Gemini-based fallback classifier for ambiguous headings.

Used only when the regex classifier (`patterns.classify_heading`) cannot
decide whether a line is a heading. Batches candidates and sends them to
Gemini 2.5 Flash with structured output. The system prompt is wrapped in a
context cache to avoid paying token cost on every call.

This module is optional: the pipeline works without it (regex-only mode).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from etl.ai.gemini_client import GeminiClient


_SYSTEM_PROMPT = """You classify lines from Spanish military manuals into one of:
- PARTE (top-level division: "PRIMERA PARTE", "SEGUNDA PARTE", ...)
- CAPITULO (chapter: "Capítulo I", "Capítulo II", ...)
- SECCION (section: "Primera Sección", "Segunda Sección", "Sección Única")
- SUBSECCION (subsection: "Subsección (A)", "Subsección (B)", ...)
- ANEXO (annex: 'Anexo "A"', 'Anexo "B"', ...)
- NONE (not a structural heading: body text, titles of works, captions, etc.)

Return only the label string. Be conservative: when unsure, prefer NONE."""


class ClassifiedHeading(BaseModel):
    line: str
    label: str = Field(description="One of PARTE/CAPITULO/SECCION/SUBSECCION/ANEXO/NONE")


class HeadingClassificationBatch(BaseModel):
    classifications: list[ClassifiedHeading]


class GeminiHeadingClassifier:
    def __init__(self, client: GeminiClient | None = None) -> None:
        self.client = client or GeminiClient()
        self._cache_name: str | None = None

    def _ensure_cache(self) -> str:
        if self._cache_name is None:
            self._cache_name = self.client.create_or_get_cache(
                name="military-heading-classifier",
                system_instruction=_SYSTEM_PROMPT,
            )
        return self._cache_name

    def classify_batch(self, lines: list[str]) -> list[str]:
        if not lines:
            return []
        cache_name = self._ensure_cache()
        prompt = "\n".join(f"{i + 1}. {line}" for i, line in enumerate(lines))
        result = self.client.generate_with_cache(
            cache_name=cache_name,
            prompt=prompt,
            response_schema=HeadingClassificationBatch,
        )
        if not result or not result.classifications:
            return ["NONE"] * len(lines)
        return [c.label for c in result.classifications[: len(lines)]]

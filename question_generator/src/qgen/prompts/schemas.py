"""Structured-output schemas for Gemini/Ollama."""

from __future__ import annotations

from collections import Counter
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class OptionRole(StrEnum):
    CORRECT = "correct"
    CONFUSA = "confusa"
    DISTRACTOR = "distractor"


REQUIRED_ROLE_COUNTS: dict[str, int] = {
    OptionRole.CORRECT.value: 1,
    OptionRole.CONFUSA.value: 1,
    OptionRole.DISTRACTOR.value: 2,
}


class GeneratedOption(BaseModel):
    role: OptionRole
    text: str = Field(min_length=1, max_length=500)


class GeneratedQuestion(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    options: list[GeneratedOption] = Field(min_length=4, max_length=4)
    justification: str = Field(min_length=1, max_length=2000)

    @model_validator(mode="after")
    def _check_role_counts(self) -> "GeneratedQuestion":
        counts = Counter(o.role.value for o in self.options)
        for role, expected in REQUIRED_ROLE_COUNTS.items():
            actual = counts.get(role, 0)
            if actual != expected:
                raise ValueError(
                    f"Role mismatch for {role!r}: expected {expected}, got {actual}. "
                    f"Counts: {dict(counts)}"
                )
        # Reject duplicate option texts (case-insensitive)
        texts = [o.text.strip().lower() for o in self.options]
        if len(set(texts)) != len(texts):
            raise ValueError("Duplicate option texts in the same question")
        return self


class QuestionDraftList(BaseModel):
    questions: list[str] = Field(min_length=1, max_length=5)
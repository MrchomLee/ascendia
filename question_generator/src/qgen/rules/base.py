"""Per-archetype question-generation rules + per-document override mechanism.

The rules a generation run actually applies = `merge_rules(profile_default,
manual_override)` and that **merged result is frozen on `GenerationRun.rules_snapshot`**
so the run is reproducible later even if the profile defaults change.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

#: Familias de generación (spec §5): cambian el rol y el formato del prompt.
FAMILIAS = ("militar", "civil")
#: Tipos que un perfil puede permitir; "ejercicio" habilita ejercicio_libro y ejercicio_nuevo.
#: "ejercicio" solo se permite en libros de matemáticas (``matematicas=True``).
TIPOS = ("teoria", "ejercicio")


@dataclass(frozen=True)
class DocumentRules:
    """Knobs that shape question generation for a class of documents."""

    name: str
    forbidden_topics: tuple[str, ...] = field(default_factory=tuple)
    preferred_topics: tuple[str, ...] = field(default_factory=tuple)
    style_guide: str = ""
    extra_instructions: str = ""
    familia: str = "militar"
    tipos: tuple[str, ...] = ("teoria",)
    matematicas: bool = False

    def __post_init__(self) -> None:
        if self.familia not in FAMILIAS:
            raise ValueError(f"familia {self.familia!r} desconocida; debe ser una de {FAMILIAS}")
        if not self.tipos or any(t not in TIPOS for t in self.tipos):
            raise ValueError(f"tipos {self.tipos!r} inválidos; cada uno debe ser uno de {TIPOS}")
        if "ejercicio" in self.tipos and not self.matematicas:
            raise ValueError(
                f"{self.name}: los ejercicios solo aplican a libros de matemáticas; "
                "en un libro informativo usa tipos=('teoria',)"
            )

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "DocumentRules":
        tipos = tuple(d.get("tipos") or ("teoria",))
        return cls(
            name=d["name"],
            forbidden_topics=tuple(d.get("forbidden_topics") or ()),
            preferred_topics=tuple(d.get("preferred_topics") or ()),
            style_guide=d.get("style_guide", "") or "",
            extra_instructions=d.get("extra_instructions", "") or "",
            familia=d.get("familia") or "militar",
            tipos=tipos,
            # Las fotos anteriores a este campo solo tenían ejercicios en libros de matemáticas.
            matematicas=d.get("matematicas", "ejercicio" in tipos),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "forbidden_topics": list(self.forbidden_topics),
            "preferred_topics": list(self.preferred_topics),
            "style_guide": self.style_guide,
            "extra_instructions": self.extra_instructions,
            "familia": self.familia,
            "tipos": list(self.tipos),
            "matematicas": self.matematicas,
        }


@dataclass(frozen=True)
class RulesOverride:
    """Sparse overrides to layer over a profile default.

    Stored at ``Manual.metadata_json["question_rules"]``. ``None`` fields keep
    the default; non-None fields **replace** the default (no item-wise merge).
    Lists, when provided, replace wholesale — keeps semantics simple.
    """

    forbidden_topics: tuple[str, ...] | None = None
    preferred_topics: tuple[str, ...] | None = None
    style_guide: str | None = None
    extra_instructions: str | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> "RulesOverride":
        d = d or {}
        return cls(
            forbidden_topics=tuple(d["forbidden_topics"]) if "forbidden_topics" in d and d["forbidden_topics"] is not None else None,
            preferred_topics=tuple(d["preferred_topics"]) if "preferred_topics" in d and d["preferred_topics"] is not None else None,
            style_guide=d.get("style_guide"),
            extra_instructions=d.get("extra_instructions"),
        )


def merge_rules(default: DocumentRules, override: RulesOverride | None) -> DocumentRules:
    if override is None:
        return default
    return DocumentRules(
        name=default.name,
        forbidden_topics=override.forbidden_topics if override.forbidden_topics is not None else default.forbidden_topics,
        preferred_topics=override.preferred_topics if override.preferred_topics is not None else default.preferred_topics,
        style_guide=override.style_guide if override.style_guide is not None else default.style_guide,
        extra_instructions=override.extra_instructions if override.extra_instructions is not None else default.extra_instructions,
        familia=default.familia,
        tipos=default.tipos,
        matematicas=default.matematicas,
    )


def rules_to_dict(rules: DocumentRules) -> dict[str, Any]:
    return rules.to_dict()


def rules_from_dict(d: dict[str, Any]) -> DocumentRules:
    return DocumentRules.from_dict(d)

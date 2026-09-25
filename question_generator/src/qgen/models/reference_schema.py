"""Esquema SQLAlchemy para preguntas de referencia (banco de ejemplos/exemplars).

Permite registrar preguntas modelo con sus opciones de respuesta y justificaciones
para ser empleadas como Few-Shot Prompting en los prompts de generación.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from etl.models.schema import Base
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship


def _utcnow() -> datetime:
    """Retorna la fecha y hora actual en UTC."""
    return datetime.now(timezone.utc)


class ReferenceQuestion(Base):
    """Modelo de base de datos para una pregunta de referencia u oro."""

    __tablename__ = "reference_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    profile: Mapped[str] = mapped_column(String(32), default="global", index=True)
    manual_code: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    topic: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    source_tag: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    cognitive_level: Mapped[str | None] = mapped_column(String(16), nullable=True)

    question_text: Mapped[str] = mapped_column(Text)
    justification: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    options: Mapped[list[ReferenceOption]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="ReferenceOption.order_in_question",
    )


class ReferenceOption(Base):
    """Modelo de opción de respuesta para una pregunta de referencia."""

    __tablename__ = "reference_options"

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("reference_questions.id", ondelete="CASCADE"), index=True)

    role: Mapped[str] = mapped_column(String(32), index=True)  # correct, confusa, distractor
    order_in_question: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)

    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    question: Mapped[ReferenceQuestion] = relationship(back_populates="options")

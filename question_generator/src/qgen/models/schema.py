"""SQLAlchemy schema for generated questions.

Hereda del mismo `Base` que `etl.models.schema` para que las tres tablas
nuevas vivan en `data/manuals.sqlite` junto a Manual/Node/Chunk. Mismas FKs,
mismas migraciones, una sola BD.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from etl.models.schema import Base, Manual, Node
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class GenerationRun(Base):
    """Una corrida = N preguntas para un manual con un set de reglas y un modelo fijos.

    Inmutable post-completion: para regenerar se crea un nuevo GenerationRun.
    """

    __tablename__ = "generation_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    manual_id: Mapped[int] = mapped_column(ForeignKey("manuals.id", ondelete="CASCADE"), index=True)

    model: Mapped[str] = mapped_column(String(64))
    mode: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(16), default="running", index=True)

    profile_used: Mapped[str] = mapped_column(String(32))
    rules_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    cache_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    batch_job_id: Mapped[str | None] = mapped_column(String(256), nullable=True, index=True)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    nodes_total: Mapped[int] = mapped_column(Integer, default=0)
    nodes_completed: Mapped[int] = mapped_column(Integer, default=0)
    nodes_failed: Mapped[int] = mapped_column(Integer, default=0)

    cost_input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cost_output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cost_cached_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cost_estimate_usd: Mapped[float] = mapped_column(Float, default=0.0)

    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    manual: Mapped[Manual] = relationship()
    questions: Mapped[list[Question]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )


class Question(Base):
    __tablename__ = "questions"
    __table_args__ = (
        UniqueConstraint("run_id", "node_id", "generation_order", name="uq_questions_run_node_order"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("generation_runs.id", ondelete="CASCADE"), index=True)
    node_id: Mapped[int] = mapped_column(ForeignKey("nodes.id", ondelete="CASCADE"), index=True)
    manual_id: Mapped[int] = mapped_column(ForeignKey("manuals.id", ondelete="CASCADE"), index=True)

    generation_order: Mapped[int] = mapped_column(Integer)
    question_text: Mapped[str] = mapped_column(Text)
    justification: Mapped[str] = mapped_column(Text)
    raw_response_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    validation_status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    # qgen v2 (spec §8): tipo de pregunta, cita en que se apoya y ventana que la produjo.
    question_type: Mapped[str] = mapped_column(String(32), default="teoria", server_default="teoria")
    source_quote: Mapped[str] = mapped_column(Text, default="", server_default="")
    window_key: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    # Niveles cognitivos (spec de niveles §5): NULL = sin clasificar.
    cognitive_level: Mapped[str | None] = mapped_column(String(16), nullable=True)

    run: Mapped[GenerationRun] = relationship(back_populates="questions")
    node: Mapped[Node] = relationship()
    options: Mapped[list[QuestionOption]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="QuestionOption.order_in_question",
    )


class QuestionOption(Base):
    __tablename__ = "question_options"

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), index=True)

    role: Mapped[str] = mapped_column(String(32), index=True)
    order_in_question: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)

    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    question: Mapped[Question] = relationship(back_populates="options")

"""Mapea GeneratedQuestion de Pydantic + metadatos de corrida a filas del ORM."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from etl.models.schema import Manual
from sqlalchemy import select
from sqlalchemy.orm import Session

from qgen.models.schema import GenerationRun, Question, QuestionOption
from qgen.prompts.schemas import GeneratedQuestion, OptionRole


def create_run(
    session: Session,
    *,
    manual_id: int,
    model: str,
    mode: str,
    profile_used: str,
    rules_snapshot: dict,
    nodes_total: int,
    cache_name: str | None = None,
    batch_job_id: str | None = None,
    metadata_json: dict | None = None,
) -> GenerationRun:
    run = GenerationRun(
        manual_id=manual_id,
        model=model,
        mode=mode,
        status="running",
        profile_used=profile_used,
        rules_snapshot=rules_snapshot,
        cache_name=cache_name,
        batch_job_id=batch_job_id,
        nodes_total=nodes_total,
        metadata_json=metadata_json or {},
    )
    session.add(run)
    session.flush()
    return run


def persist_question(
    session: Session,
    *,
    run: GenerationRun,
    node_id: int,
    manual_id: int,
    generation_order: int,
    payload: GeneratedQuestion,
    raw_response: dict,
    metadata: dict[str, Any] | None = None,
    validation_status: str = "pending",
) -> Question:
    q = Question(
        run_id=run.id,
        node_id=node_id,
        manual_id=manual_id,
        generation_order=generation_order,
        question_text=payload.question,
        justification=payload.justification,
        raw_response_json=raw_response,
        validation_status=validation_status,
        metadata_json=metadata or {},
    )
    session.add(q)
    session.flush()

    for order, opt in enumerate(payload.options):
        session.add(
            QuestionOption(
                question_id=q.id,
                role=opt.role.value,
                order_in_question=order,
                text=opt.text,
                is_correct=(opt.role == OptionRole.CORRECT),
            )
        )
    return q


def remove_existing_questions_for_nodes(
    session: Session, *, manual_id: int, node_ids: list[int]
) -> int:
    """Usado por --regenerate. Eliminación en cascada mediante claves foráneas (FKs) run/question/options."""
    if not node_ids:
        return 0
    rows = (
        session.execute(
            select(Question)
            .where(Question.manual_id == manual_id)
            .where(Question.node_id.in_(node_ids))
        )
        .scalars()
        .all()
    )
    for q in rows:
        session.delete(q)
    return len(rows)


def finalize_run(
    session: Session,
    *,
    run: GenerationRun,
    nodes_completed: int,
    nodes_failed: int,
    cost_input_tokens: int,
    cost_output_tokens: int,
    cost_cached_tokens: int,
    cost_estimate_usd: float,
    status: str = "succeeded",
) -> None:
    run.nodes_completed = nodes_completed
    run.nodes_failed = nodes_failed
    run.cost_input_tokens = cost_input_tokens
    run.cost_output_tokens = cost_output_tokens
    run.cost_cached_tokens = cost_cached_tokens
    run.cost_estimate_usd = cost_estimate_usd
    run.status = status
    run.completed_at = datetime.now(timezone.utc)
    session.flush()


def load_manual(session: Session, manual_id: int) -> Manual:
    m = session.get(Manual, manual_id)
    if m is None:
        raise ValueError(f"Manual {manual_id} not found")
    return m

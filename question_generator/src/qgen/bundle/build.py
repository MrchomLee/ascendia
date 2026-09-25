"""Arma el bundle a partir del SQLite del pipeline.

Separado del CLI para poder probarlo sin invocar typer, y separado de
`spec.py` porque esto sí depende de SQLAlchemy y del esquema del pipeline —
mientras que `spec.py` tiene que poder importarse del lado de la webapp.
"""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from etl.models.schema import Chunk, Manual, Node
from sqlalchemy import select
from sqlalchemy.orm import Session

from qgen.bundle.spec import BUNDLE_VERSION, iso, run_ref
from qgen.models.schema import GenerationRun, Question, QuestionOption

#: Materia del catálogo sugerida según el código del manual. Es una pista, no
#: una decisión: quien importa puede ignorarla (ver `catalog_hint` en el contrato).
DEFAULT_GRADO_HINT = "SARG_2"


def _pipeline_commit() -> str | None:
    """Commit del repo de contenido, para poder reproducir una entrega vieja."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None


def _materia_hint(code: str) -> str:
    return "JUS_MIL" if code.upper().startswith("CJM") else "OPS_MIL"


def _qgen_version() -> str:
    try:
        from importlib.metadata import version

        return version("question_generator")
    except Exception:  # noqa: BLE001 — la versión es informativa, no vale fallar por ella
        return "0.0.0+unknown"


class DuplicateNodeRef(ValueError):
    """Dos nodos con el mismo `sort_key`: el bundle no tendría identidad."""


class DuplicateRunRef(ValueError):
    """Dos corridas que colapsan en el mismo `ref`."""


def build_bundle(
    session: Session,
    *,
    manual_id: int,
    run_ids: list[int] | None = None,
    include_raw: bool = False,
    source_sha256: str | None = None,
) -> dict[str, Any]:
    """Construye el bundle v2 de un manual.

    `run_ids` limita a esas corridas (y a sus preguntas); por defecto van todas
    las del manual.
    """
    manual = session.get(Manual, manual_id)
    if manual is None:
        raise ValueError(f"No hay ningún manual con id {manual_id}.")

    nodes = (
        session.execute(
            select(Node).where(Node.manual_id == manual_id).order_by(Node.sort_key, Node.id)
        )
        .scalars()
        .all()
    )

    # El `ref` de un nodo es su `sort_key`. El ensamblador lo construye con
    # contadores por nivel, así que es único por construcción — pero de eso
    # depende toda la identidad del bundle, así que se comprueba en vez de
    # confiar (ver el aviso del §4 del contrato).
    ref_by_id: dict[int, str] = {}
    seen_refs: dict[str, int] = {}
    for node in nodes:
        if node.sort_key in seen_refs:
            raise DuplicateNodeRef(
                f"Los nodos {seen_refs[node.sort_key]} y {node.id} comparten el sort_key "
                f"{node.sort_key!r}. Hay que arreglar la jerarquía (re-ingestar el manual) "
                f"antes de exportar: el bundle identifica los nodos por ese valor."
            )
        seen_refs[node.sort_key] = node.id
        ref_by_id[node.id] = node.sort_key

    chunks_by_node: dict[int, list[Chunk]] = {}
    for chunk in (
        session.execute(
            select(Chunk).where(Chunk.manual_id == manual_id).order_by(Chunk.node_id, Chunk.ordinal)
        )
        .scalars()
        .all()
    ):
        chunks_by_node.setdefault(chunk.node_id, []).append(chunk)

    runs_stmt = select(GenerationRun).where(GenerationRun.manual_id == manual_id)
    if run_ids:
        runs_stmt = runs_stmt.where(GenerationRun.id.in_(run_ids))
    runs = session.execute(runs_stmt.order_by(GenerationRun.id)).scalars().all()

    if run_ids:
        missing = set(run_ids) - {r.id for r in runs}
        if missing:
            raise ValueError(
                f"Las corridas {sorted(missing)} no existen o no son de este manual."
            )

    ref_by_run: dict[int, str] = {}
    seen_run_refs: dict[str, int] = {}
    for run in runs:
        ref = run_ref(run.model, run.mode, run.started_at)
        if ref in seen_run_refs:
            raise DuplicateRunRef(
                f"Las corridas {seen_run_refs[ref]} y {run.id} producen el mismo ref {ref!r} "
                f"(mismo modelo, modo y segundo de inicio). Exporta una sola con --run."
            )
        seen_run_refs[ref] = run.id
        ref_by_run[run.id] = ref

    questions: list[Question] = []
    if ref_by_run:
        questions = (
            session.execute(
                select(Question)
                .where(Question.run_id.in_(list(ref_by_run)))
                .order_by(Question.run_id, Question.generation_order, Question.id)
            )
            .scalars()
            .all()
        )

    options_by_question: dict[int, list[QuestionOption]] = {}
    if questions:
        for option in (
            session.execute(
                select(QuestionOption)
                .where(QuestionOption.question_id.in_([q.id for q in questions]))
                .order_by(QuestionOption.question_id, QuestionOption.order_in_question)
            )
            .scalars()
            .all()
        ):
            options_by_question.setdefault(option.question_id, []).append(option)

    return {
        "bundle_version": BUNDLE_VERSION,
        "generated_at": iso(datetime.now(timezone.utc)),
        "generator": {
            "tool": "qgen",
            "version": _qgen_version(),
            "pipeline_commit": _pipeline_commit(),
        },
        "manual": {
            "code": manual.code,
            "edition": manual.edition,
            "title": manual.title,
            "branch": manual.branch,
            "source_path": manual.source_path,
            "source_sha256": source_sha256,
            "page_count": manual.page_count,
            "extractor_used": manual.extractor_used,
            "ingested_at": iso(manual.ingested_at),
            "metadata": manual.metadata_json or {},
        },
        "catalog_hint": {
            "grado_code": DEFAULT_GRADO_HINT,
            "materia_code": _materia_hint(manual.code),
        },
        "nodes": [
            {
                "ref": ref_by_id[node.id],
                "parent_ref": ref_by_id.get(node.parent_id) if node.parent_id else None,
                "level": node.level,
                "level_label": node.level_label,
                "ordinal": node.ordinal,
                "title": node.title,
                "breadcrumb": node.breadcrumb,
                "page_start": node.page_start,
                "page_end": node.page_end,
                "is_anexo": bool(node.is_anexo),
                "metadata": node.metadata_json or {},
                "chunks": [
                    {
                        "ordinal": chunk.ordinal,
                        "text": chunk.text,
                        "char_count": chunk.char_count,
                        "page_start": chunk.page_start,
                        "page_end": chunk.page_end,
                        "has_table": bool(chunk.has_table),
                        "has_image_ref": bool(chunk.has_image_ref),
                        "metadata": chunk.metadata_json or {},
                    }
                    for chunk in chunks_by_node.get(node.id, [])
                ],
            }
            for node in nodes
        ],
        "runs": [
            {
                "ref": ref_by_run[run.id],
                "model": run.model,
                "mode": run.mode,
                "status": run.status,
                "profile_used": run.profile_used,
                "rules_snapshot": run.rules_snapshot or {},
                "started_at": iso(run.started_at),
                "completed_at": iso(run.completed_at),
                "nodes_total": run.nodes_total,
                "nodes_completed": run.nodes_completed,
                "nodes_failed": run.nodes_failed,
                "cost_input_tokens": run.cost_input_tokens,
                "cost_output_tokens": run.cost_output_tokens,
                "cost_cached_tokens": run.cost_cached_tokens,
                # numeric(12,6) del otro lado: más decimales se perderían igual.
                "cost_estimate_usd": round(float(run.cost_estimate_usd or 0.0), 6),
                "metadata": run.metadata_json or {},
            }
            for run in runs
        ],
        "questions": [
            {
                "run_ref": ref_by_run[question.run_id],
                "node_ref": ref_by_id[question.node_id],
                "generation_order": question.generation_order,
                "question_text": question.question_text,
                "justification": question.justification,
                "question_type": question.question_type,
                "source_quote": question.source_quote,
                "cognitive_level": question.cognitive_level,
                "validation_status": question.validation_status,
                "validated_at": iso(question.validated_at),
                "created_at": iso(question.created_at),
                "metadata": question.metadata_json or {},
                **(
                    {"raw_response": question.raw_response_json or {}}
                    if include_raw
                    else {}
                ),
                "options": [
                    {
                        "role": option.role,
                        "order_in_question": option.order_in_question,
                        "text": option.text,
                        "is_correct": bool(option.is_correct),
                        "metadata": option.metadata_json or {},
                    }
                    for option in options_by_question.get(question.id, [])
                ],
            }
            for question in questions
        ],
    }


def source_digest(manual_source_path: str) -> str | None:
    """SHA-256 del PDF de origen, si sigue estando donde dice el manual."""
    from qgen.bundle.spec import sha256_of

    path = Path(manual_source_path)
    return sha256_of(path) if path.is_file() else None

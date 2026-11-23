"""Acceso a las preguntas generadas (fase 2 del pipeline).

Aparte de `data_access.py` porque aquello solo sabe de la ETL —manuales, nodos,
chunks— y esto depende de `qgen`. Si un día se separan los dos paquetes, la
frontera ya está trazada.

Casi todo es de solo lectura y cacheado, como el resto del explorador. La única
excepción es `set_validation_status`: marcar una pregunta como revisada es el
motivo por el que se mira, y ese estado es justo lo que decide si la webapp se
la sirve a un alumno.
"""

from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st
from etl.db.session import get_engine, session_scope
from etl.models.schema import Chunk, Node
from pydantic import BaseModel, Field
from sqlalchemy import func, inspect, select, update

from explorer.data_access import NodeSummary, get_tree
from qgen.prompts.niveles import NIVEL_LABEL

#: Los cuatro estados que acepta la base de la webapp.
STATUSES: tuple[str, ...] = ("pending", "valid", "needs_review", "rejected")

#: Solo estos dos se le sirven a los alumnos.
SERVED_STATUSES: frozenset[str] = frozenset({"pending", "valid"})

STATUS_LABEL: dict[str, str] = {
    "pending": "⏳ sin revisar",
    "valid": "✅ aprobada",
    "needs_review": "🔎 a revisar",
    "rejected": "🚫 rechazada",
}

#: Color por rol de opción, para que se lean de un vistazo.
ROLE_COLOR: dict[str, str] = {
    "correct": "green",
    "confusa": "orange",
    "distractor": "blue",
}

ROLE_LABEL: dict[str, str] = {
    "correct": "correcta",
    "confusa": "confusa",
    "distractor": "distractor",
}

#: Tipo de pregunta (qgen v2).
TYPE_LABEL: dict[str, str] = {
    "teoria": "📘 Teoría",
    "ejercicio_libro": "✏️ Ejercicio del libro",
    "ejercicio_nuevo": "🆕 Ejercicio nuevo",
}

#: Valor del filtro para las preguntas sin nivel cognitivo (anteriores a los niveles).
SIN_NIVEL = "sin_nivel"


class OptionView(BaseModel):
    id: int
    role: str
    order_in_question: int
    text: str
    is_correct: bool


class QuestionView(BaseModel):
    id: int
    run_id: int
    node_id: int
    generation_order: int
    question_text: str
    justification: str
    validation_status: str
    created_at: datetime
    node_breadcrumb: str
    node_title: str
    node_label: str
    node_page_start: int
    question_type: str = "teoria"
    source_quote: str = ""
    motivos: list[str] = Field(default_factory=list)
    #: Veredicto de la revisión desde Claude Code (`qgen-claude importar-revision`).
    revision: dict | None = None
    cognitive_level: str | None = None
    #: El nivel que declaró la generación, si la revisión lo cambió.
    nivel_generado: str | None = None
    options: list[OptionView] = Field(default_factory=list)

    @property
    def served(self) -> bool:
        return self.validation_status in SERVED_STATUSES


class RunView(BaseModel):
    id: int
    model: str
    mode: str
    status: str
    profile_used: str
    started_at: datetime
    completed_at: datetime | None
    nodes_total: int
    nodes_completed: int
    nodes_failed: int
    cost_estimate_usd: float
    question_count: int


class QuestionKPIs(BaseModel):
    total: int
    by_status: dict[str, int] = Field(default_factory=dict)
    by_level: dict[str, int] = Field(default_factory=dict)
    nodes_with_text: int
    nodes_with_question: int
    cost_total_usd: float

    @property
    def served(self) -> int:
        return sum(self.by_status.get(s, 0) for s in SERVED_STATUSES)

    @property
    def coverage_pct(self) -> float:
        if not self.nodes_with_text:
            return 0.0
        return 100.0 * self.nodes_with_question / self.nodes_with_text


@st.cache_data(ttl=30, show_spinner=False)
def revision_label(revision: dict) -> str:
    """Una línea con el veredicto de la revisión desde Claude Code y sus motivos."""
    texto = f"Revisión de {revision.get('por', '?')}: {revision.get('veredicto', '?')} · {revision.get('calificacion', '?')}/5"
    if revision.get("nivel"):
        texto += f" · {NIVEL_LABEL.get(revision['nivel'], revision['nivel'])}"
    motivos = revision.get("motivos") or []
    return texto + (" — " + "; ".join(motivos) if motivos else "")


def level_label(question: QuestionView) -> str:
    """El nivel de la pregunta y, si la revisión lo cambió, el que declaró la generación."""
    if not question.cognitive_level:
        return "sin nivel"
    texto = NIVEL_LABEL.get(question.cognitive_level, question.cognitive_level)
    if question.nivel_generado:
        texto += f" (generada como {NIVEL_LABEL.get(question.nivel_generado, question.nivel_generado)})"
    return texto


def questions_available() -> bool:
    """¿Existen ya las tablas de la fase 2 en esta base?

    Un SQLite recién ingerido solo tiene las tablas de la ETL: las de preguntas
    las crea `qgen-generate` la primera vez. Preguntar es más barato que dejar
    que reviente una consulta. Si ya existen pero son de antes de una columna nueva
    (p. ej. el nivel cognitivo), la migración idempotente de qgen las pone al día.
    """
    if not inspect(get_engine()).has_table("questions"):
        return False
    from qgen.db.migration import init_question_tables

    init_question_tables()
    return True


@st.cache_data(ttl=30, show_spinner=False)
def get_question_kpis(manual_id: int) -> QuestionKPIs:
    from qgen.models.schema import GenerationRun, Question

    with session_scope() as session:
        by_status = dict(
            session.execute(
                select(Question.validation_status, func.count(Question.id))
                .where(Question.manual_id == manual_id)
                .group_by(Question.validation_status)
            ).all()
        )
        nodes_with_text = session.execute(
            select(func.count(func.distinct(Chunk.node_id))).where(Chunk.manual_id == manual_id)
        ).scalar_one()
        nodes_with_question = session.execute(
            select(func.count(func.distinct(Question.node_id))).where(
                Question.manual_id == manual_id
            )
        ).scalar_one()
        cost = session.execute(
            select(func.coalesce(func.sum(GenerationRun.cost_estimate_usd), 0.0)).where(
                GenerationRun.manual_id == manual_id
            )
        ).scalar_one()
        by_level = {
            nivel: n
            for nivel, n in session.execute(
                select(Question.cognitive_level, func.count(Question.id))
                .where(Question.manual_id == manual_id, Question.cognitive_level.is_not(None))
                .group_by(Question.cognitive_level)
            ).all()
        }

        return QuestionKPIs(
            total=sum(by_status.values()),
            by_status=by_status,
            by_level=by_level,
            nodes_with_text=nodes_with_text,
            nodes_with_question=nodes_with_question,
            cost_total_usd=float(cost or 0.0),
        )


@st.cache_data(ttl=30, show_spinner=False)
def list_runs(manual_id: int) -> list[RunView]:
    from qgen.models.schema import GenerationRun, Question

    with session_scope() as session:
        counts = dict(
            session.execute(
                select(Question.run_id, func.count(Question.id))
                .where(Question.manual_id == manual_id)
                .group_by(Question.run_id)
            ).all()
        )
        rows = (
            session.execute(
                select(GenerationRun)
                .where(GenerationRun.manual_id == manual_id)
                .order_by(GenerationRun.id.desc())
            )
            .scalars()
            .all()
        )
        return [
            RunView(
                id=r.id,
                model=r.model,
                mode=r.mode,
                status=r.status,
                profile_used=r.profile_used,
                started_at=r.started_at,
                completed_at=r.completed_at,
                nodes_total=r.nodes_total,
                nodes_completed=r.nodes_completed,
                nodes_failed=r.nodes_failed,
                cost_estimate_usd=float(r.cost_estimate_usd or 0.0),
                question_count=counts.get(r.id, 0),
            )
            for r in rows
        ]


@st.cache_data(ttl=30, show_spinner=False)
def list_questions(
    manual_id: int,
    *,
    statuses: tuple[str, ...] | None = None,
    levels: tuple[str, ...] | None = None,
    run_id: int | None = None,
    node_id: int | None = None,
    query: str | None = None,
    limit: int = 500,
) -> list[QuestionView]:
    """Preguntas de un manual, con su nodo y sus opciones ya resueltos."""
    from qgen.models.schema import Question, QuestionOption

    with session_scope() as session:
        stmt = (
            select(Question, Node)
            .join(Node, Node.id == Question.node_id)
            .where(Question.manual_id == manual_id)
        )
        if statuses:
            stmt = stmt.where(Question.validation_status.in_(statuses))
        if levels:
            nombrados = [n for n in levels if n != SIN_NIVEL]
            condicion = Question.cognitive_level.in_(nombrados) if nombrados else None
            if SIN_NIVEL in levels:
                nulos = Question.cognitive_level.is_(None)
                condicion = nulos if condicion is None else (condicion | nulos)
            stmt = stmt.where(condicion)
        if run_id is not None:
            stmt = stmt.where(Question.run_id == run_id)
        if node_id is not None:
            stmt = stmt.where(Question.node_id == node_id)
        if query:
            like = f"%{query.strip()}%"
            stmt = stmt.where(
                Question.question_text.ilike(like) | Question.justification.ilike(like)
            )

        rows = session.execute(
            stmt.order_by(Node.sort_key, Question.generation_order).limit(limit)
        ).all()
        if not rows:
            return []

        options_by_question: dict[int, list[OptionView]] = {}
        for option in (
            session.execute(
                select(QuestionOption)
                .where(QuestionOption.question_id.in_([q.id for q, _ in rows]))
                .order_by(QuestionOption.question_id, QuestionOption.order_in_question)
            )
            .scalars()
            .all()
        ):
            options_by_question.setdefault(option.question_id, []).append(
                OptionView(
                    id=option.id,
                    role=option.role,
                    order_in_question=option.order_in_question,
                    text=option.text,
                    is_correct=bool(option.is_correct),
                )
            )

        return [
            QuestionView(
                id=q.id,
                run_id=q.run_id,
                node_id=q.node_id,
                generation_order=q.generation_order,
                question_text=q.question_text,
                justification=q.justification,
                validation_status=q.validation_status,
                created_at=q.created_at,
                node_breadcrumb=node.breadcrumb,
                node_title=node.title,
                node_label=f"{node.level_label} {node.ordinal}".strip(),
                node_page_start=node.page_start,
                question_type=q.question_type,
                source_quote=q.source_quote,
                motivos=list((q.metadata_json or {}).get("motivos") or []),
                revision=(q.metadata_json or {}).get("revision"),
                cognitive_level=q.cognitive_level,
                nivel_generado=(q.metadata_json or {}).get("nivel_generado"),
                options=options_by_question.get(q.id, []),
            )
            for q, node in rows
        ]


@st.cache_data(ttl=30, show_spinner=False)
def status_by_node(manual_id: int) -> dict[int, list[str]]:
    """{node_id: [estados de sus preguntas]}, para pintar el árbol."""
    from qgen.models.schema import Question

    with session_scope() as session:
        rows = session.execute(
            select(Question.node_id, Question.validation_status).where(
                Question.manual_id == manual_id
            )
        ).all()
    out: dict[int, list[str]] = {}
    for node_id, status in rows:
        out.setdefault(node_id, []).append(status)
    return out


def nodes_missing_questions(manual_id: int) -> list[NodeSummary]:
    """Nodos con texto que se quedaron sin ninguna pregunta.

    Es la lista de trabajo pendiente de un manual: lo que falta por generar, o
    lo que falló en la última corrida.
    """
    covered = set(status_by_node(manual_id))
    return [n for n in get_tree(manual_id) if n.chunk_count and n.id not in covered]


def set_validation_status(question_id: int, status: str) -> None:
    """Marca una pregunta. **Escribe** en el SQLite local.

    Es lo único que este explorador cambia. No borra nada: una pregunta mala se
    marca `rejected` y sigue ahí, viaja en el bundle y queda constancia de que
    se revisó; simplemente la webapp no la mete en ningún examen.
    """
    if status not in STATUSES:
        raise ValueError(f"Estado desconocido: {status!r}. Debe ser uno de {STATUSES}.")

    from qgen.models.schema import Question

    with session_scope() as session:
        session.execute(
            update(Question)
            .where(Question.id == question_id)
            .values(validation_status=status, validated_at=datetime.now(timezone.utc))
        )
    st.cache_data.clear()

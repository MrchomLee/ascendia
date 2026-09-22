"""Orquestación de `qgen-generate` de principio a fin, con Gemini simulado.

Aquí no se prueba la calidad de las preguntas sino lo que rodea a las llamadas:
que la corrida siempre se cierre (también si se corta a medias), que lo
generado se guarde, que el cache se borre y que el costo cuente todo lo que se
pagó.
"""

from datetime import datetime, timezone

import pytest
from etl.db.session import session_scope
from etl.models.schema import Chunk, Manual, Node
from sqlalchemy import select

import qgen.pipeline as pipeline
from qgen.cli.generate import _progress_cb
from qgen.cost import actual_cost_usd
from qgen.db.migration import init_question_tables
from qgen.gemini.cache import DocumentCache
from qgen.gemini.client import MODEL_FLASH, MODEL_PRO
from qgen.gemini.generate import DraftOutcome, GenerationOutcome
from qgen.models.schema import GenerationRun, Question
from qgen.prompts.schemas import GeneratedOption, GeneratedQuestion, OptionRole

TEXT = "La guerra es un conflicto entre sociedades que luchan violentamente."


def _question(prefix: str = "T") -> GeneratedQuestion:
    return GeneratedQuestion(
        question=f"{prefix} — ¿qué es la guerra?",
        options=[
            GeneratedOption(role=OptionRole.CORRECT, text=TEXT),
            GeneratedOption(role=OptionRole.CONFUSA, text=f"{prefix} confusa"),
            GeneratedOption(role=OptionRole.DISTRACTOR, text=f"{prefix} fácil 1"),
            GeneratedOption(role=OptionRole.DISTRACTOR, text=f"{prefix} fácil 2"),
        ],
        justification="Párrafo 1.",
    )


def _seed(n_nodes: int = 2) -> int:
    init_question_tables()
    with session_scope() as session:
        manual = Manual(
            code="TST", title="Manual de prueba", source_path="no-existe.pdf",
            page_count=10, extractor_used="docling", ingested_at=datetime.now(timezone.utc),
            metadata_json={"profile": "manual"},
        )
        session.add(manual)
        session.flush()
        for i in range(n_nodes):
            node = Node(
                manual_id=manual.id, level=0, level_label="Capítulo", ordinal=str(i + 1),
                title=f"Capítulo {i + 1}", breadcrumb=f"Capítulo {i + 1}",
                page_start=i + 1, sort_key=f"{i + 1:02d}",
            )
            session.add(node)
            session.flush()
            session.add(Chunk(
                node_id=node.id, manual_id=manual.id, ordinal=0, text=TEXT,
                char_count=len(TEXT), page_start=i + 1, page_end=i + 1,
            ))
        return manual.id


class FakeGemini:
    """Sustituye cache, creador y generador de opciones del pipeline."""

    def __init__(self, monkeypatch, *, cache_tokens: int = 0) -> None:
        self.cache_models: list[str] = []
        self.deleted: list[str] = []
        self.cache_tokens = cache_tokens
        self.drafts = ["¿Qué es la guerra?"]
        self.one = lambda: GenerationOutcome(
            question=_question(), raw_response={}, input_tokens=100, output_tokens=50, cached_tokens=80,
        )
        monkeypatch.setattr(pipeline, "build_or_get_cache", self._build_cache)
        monkeypatch.setattr(pipeline, "delete_cache", lambda cache: self.deleted.append(cache.name))
        monkeypatch.setattr(pipeline, "generate_draft_questions", lambda **_: DraftOutcome(
            questions=list(self.drafts), input_tokens=10, output_tokens=5, cached_tokens=8,
        ))
        monkeypatch.setattr(pipeline, "generate_one", lambda **_: self.one())

    def _build_cache(self, *, model, **_):
        self.cache_models.append(model)
        return DocumentCache(
            name="cachedContents/test", model=model, file_name="files/test",
            system_version="test", expire_at_epoch=0.0, token_count=self.cache_tokens,
        )


def _runs():
    with session_scope() as session:
        return session.execute(select(GenerationRun)).scalars().all()


def _question_count() -> int:
    with session_scope() as session:
        return len(session.execute(select(Question)).scalars().all())


# ─── El callback del CLI ───────────────────────────────────────────────────


def test_cli_progress_callback_accepts_pipeline_jobs(monkeypatch):
    manual_id = _seed()
    fake = FakeGemini(monkeypatch)

    with session_scope() as session:
        summary = pipeline.run_generation(session, manual_id=manual_id, progress_cb=_progress_cb)

    assert summary.nodes_completed == 2
    assert [r.status for r in _runs()] == ["succeeded"]
    assert _question_count() == 2
    assert fake.deleted == ["cachedContents/test"]


# ─── La corrida siempre se cierra ──────────────────────────────────────────


def test_unexpected_error_marks_run_failed_and_deletes_cache(monkeypatch):
    manual_id = _seed()
    fake = FakeGemini(monkeypatch)

    def boom():
        raise RuntimeError("se cayó a medias")

    fake.one = boom

    with pytest.raises(RuntimeError, match="se cayó a medias"):
        with session_scope() as session:
            pipeline.run_generation(session, manual_id=manual_id)

    [run] = _runs()
    assert run.status == "failed"
    assert run.completed_at is not None
    assert fake.deleted == ["cachedContents/test"]


def test_ctrl_c_marks_run_cancelled_and_keeps_what_was_saved(monkeypatch):
    manual_id = _seed(n_nodes=1)
    fake = FakeGemini(monkeypatch)

    def interrupt(*_):
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        with session_scope() as session:
            pipeline.run_generation(session, manual_id=manual_id, progress_cb=interrupt)

    [run] = _runs()
    assert run.status == "cancelled"
    assert run.nodes_completed == 1
    # Se persiste antes de avisar al callback: lo ya pagado no se pierde.
    assert _question_count() == 1
    assert fake.deleted == ["cachedContents/test"]


# ─── Modelo ────────────────────────────────────────────────────────────────


def test_model_alias_is_resolved_before_calling_gemini(monkeypatch):
    manual_id = _seed(n_nodes=1)
    fake = FakeGemini(monkeypatch)

    with session_scope() as session:
        summary = pipeline.run_generation(session, manual_id=manual_id, model_name="pro")

    assert summary.model == MODEL_PRO
    assert fake.cache_models == [MODEL_PRO]
    assert summary.actual_cost_usd > 0


def test_unknown_model_is_rejected_before_creating_a_run(monkeypatch):
    manual_id = _seed(n_nodes=1)
    FakeGemini(monkeypatch)

    with pytest.raises(ValueError, match="Unknown model"):
        with session_scope() as session:
            pipeline.run_generation(session, manual_id=manual_id, model_name="deepseek-r1:8b")

    assert _runs() == []


# ─── Costo ─────────────────────────────────────────────────────────────────


def test_tokens_include_draft_calls_and_failed_answers(monkeypatch):
    manual_id = _seed(n_nodes=1)
    fake = FakeGemini(monkeypatch, cache_tokens=1_000)
    fake.drafts = ["¿Primera?", "¿Segunda?"]
    outcomes = iter([
        GenerationOutcome(question=_question("A"), raw_response={}, input_tokens=100, output_tokens=50, cached_tokens=80),
        # Respuesta que no valida: se pagó igual.
        GenerationOutcome(question=None, raw_response={}, error="validation error",
                          input_tokens=100, output_tokens=50, cached_tokens=80),
    ])
    fake.one = lambda: next(outcomes)

    with session_scope() as session:
        summary = pipeline.run_generation(session, manual_id=manual_id)

    [run] = _runs()
    assert run.status == "partial"
    # 1 draft (10/5/8) + 2 llamadas de opciones (100/50/80 cada una).
    assert (run.cost_input_tokens, run.cost_output_tokens, run.cost_cached_tokens) == (210, 105, 168)
    assert run.metadata_json["cache_tokens"] == 1_000

    without_cache = actual_cost_usd(
        model=MODEL_FLASH, mode="immediate", input_tokens=210, output_tokens=105, cached_tokens=168,
    )
    assert summary.actual_cost_usd > without_cache


# ─── Dry-run ───────────────────────────────────────────────────────────────


def test_dry_run_estimates_a_real_cost():
    manual_id = _seed(n_nodes=3)

    with session_scope() as session:
        estimate, n_nodes = pipeline.estimate_only(
            session, manual_id=manual_id, model_name="flash", mode="immediate",
            limit=None, only_node_id=None, regenerate=False,
        )

    assert n_nodes == 3
    assert estimate.model == MODEL_FLASH
    assert estimate.draft_calls == 3
    assert estimate.n_questions == 3 * pipeline.QUESTIONS_PER_NODE_ESTIMATE
    assert estimate.cache_tokens > 0
    assert estimate.total_usd > 0


def test_dry_run_with_nothing_to_generate_costs_nothing(monkeypatch):
    manual_id = _seed(n_nodes=1)
    FakeGemini(monkeypatch)
    with session_scope() as session:
        pipeline.run_generation(session, manual_id=manual_id)

    with session_scope() as session:
        estimate, n_nodes = pipeline.estimate_only(
            session, manual_id=manual_id, model_name="flash", mode="immediate",
            limit=None, only_node_id=None, regenerate=False,
        )

    assert n_nodes == 0
    assert estimate.total_usd == 0

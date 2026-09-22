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


# ─── Por qué falló ─────────────────────────────────────────────────────────


def _node_id(manual_id: int) -> int:
    with session_scope() as session:
        return session.execute(select(Node.id).where(Node.manual_id == manual_id)).scalar_one()


def test_el_motivo_de_una_opcion_fallida_queda_en_la_corrida_y_se_avisa(monkeypatch):
    manual_id = _seed(n_nodes=1)
    fake = FakeGemini(monkeypatch)
    fake.drafts = ["¿Primera?", "¿Segunda?"]
    outcomes = iter([
        GenerationOutcome(question=_question("A"), raw_response={}),
        GenerationOutcome(question=None, raw_response={}, error="validation error: Role mismatch for 'correct'"),
    ])
    fake.one = lambda: next(outcomes)
    avisos: list[str | None] = []

    with session_scope() as session:
        pipeline.run_generation(
            session, manual_id=manual_id,
            progress_cb=lambda idx, total, job, question, error: avisos.append(error),
        )

    [run] = _runs()
    assert run.metadata_json["failures"] == [
        {"node_id": _node_id(manual_id), "error": "validation error: Role mismatch for 'correct'"},
    ]
    assert "validation error: Role mismatch for 'correct'" in avisos


def test_el_motivo_de_un_creador_fallido_queda_en_la_corrida(monkeypatch):
    manual_id = _seed(n_nodes=1)
    FakeGemini(monkeypatch)
    monkeypatch.setattr(pipeline, "generate_draft_questions", lambda **_: DraftOutcome(
        questions=[], error="ClientError: 400 INVALID_ARGUMENT",
    ))

    with session_scope() as session:
        pipeline.run_generation(session, manual_id=manual_id)

    [run] = _runs()
    assert run.status == "partial"
    assert run.metadata_json["failures"] == [
        {"node_id": _node_id(manual_id), "error": "ClientError: 400 INVALID_ARGUMENT"},
    ]


class _FakeClient:
    """Cliente de Gemini mínimo: `generate_content` falla o devuelve `response`."""

    def __init__(self, *, raises: Exception | None = None, response=None) -> None:
        self.raises, self.response = raises, response
        self.models = self

    def get(self):
        return self

    def generate_content(self, **_):
        if self.raises:
            raise self.raises
        return self.response


def test_el_creador_devuelve_el_motivo_si_la_api_rechaza_la_llamada():
    from qgen.gemini.generate import generate_draft_questions

    client = _FakeClient(raises=RuntimeError("400 INVALID_ARGUMENT: request not supported"))
    draft = generate_draft_questions(
        model=MODEL_FLASH, variable_prompt="texto", system_instruction="instrucciones", client=client,
    )

    assert draft.questions == []
    assert "400 INVALID_ARGUMENT" in draft.error


def test_el_creador_devuelve_el_motivo_si_la_respuesta_no_es_json():
    from types import SimpleNamespace

    from qgen.gemini.generate import generate_draft_questions

    response = SimpleNamespace(text="esto no es json", usage_metadata=SimpleNamespace(
        prompt_token_count=12, candidates_token_count=3, cached_content_token_count=0,
    ))
    draft = generate_draft_questions(
        model=MODEL_FLASH, variable_prompt="texto", system_instruction="instrucciones",
        client=_FakeClient(response=response),
    )

    assert draft.questions == []
    assert draft.error is not None
    assert (draft.input_tokens, draft.output_tokens) == (12, 3)  # se pagaron igual


# ─── Respuestas reales de Gemini 3 ─────────────────────────────────────────


def test_una_respuesta_con_thought_signature_se_guarda(monkeypatch):
    """Gemini 3 firma sus partes con `thought_signature` (bytes no UTF-8). La
    respuesta cruda se guarda como JSON: en metadata y en raw_response_json."""
    import json

    from google.genai import types

    import qgen.gemini.generate as gemini_generate

    manual_id = _seed(n_nodes=1)
    FakeGemini(monkeypatch)
    monkeypatch.setattr(pipeline, "generate_one", gemini_generate.generate_one)
    response = types.GenerateContentResponse(
        candidates=[types.Candidate(content=types.Content(role="model", parts=[types.Part(
            text=_question("R").model_dump_json(),
            thought_signature=b"\x12\x8e'\n\x8b'\x01i\x14}\x13\xbe",  # tal cual en el log real
        )]))],
        usage_metadata=types.GenerateContentResponseUsageMetadata(
            prompt_token_count=100, candidates_token_count=50,
        ),
    )
    monkeypatch.setattr(gemini_generate, "default_client", lambda: _FakeClient(response=response))

    with session_scope() as session:
        pipeline.run_generation(session, manual_id=manual_id)

    [run] = _runs()
    assert run.status == "succeeded"
    with session_scope() as session:
        [question] = session.execute(select(Question)).scalars().all()
        stored = question.raw_response_json
    part = stored["candidates"][0]["content"]["parts"][0]
    assert isinstance(part["thought_signature"], str)
    json.dumps(stored)

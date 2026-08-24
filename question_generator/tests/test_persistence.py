from datetime import datetime, timezone
from pathlib import Path

from etl.db.session import session_scope
from etl.models.schema import Chunk, Manual, Node

from qgen.db.migration import init_question_tables
from qgen.db.persistence import (
    create_run,
    finalize_run,
    persist_question,
    remove_existing_questions_for_nodes,
)
from qgen.models.schema import GenerationRun, Question, QuestionOption
from qgen.prompts.schemas import GeneratedOption, GeneratedQuestion, OptionRole


def _seed_manual_and_node(session) -> tuple[int, int]:
    m = Manual(
        code="TEST-1", title="Test Manual", source_path="/tmp/test.pdf",
        page_count=10, extractor_used="docling", ingested_at=datetime.now(timezone.utc),
        metadata_json={"profile": "manual"},
    )
    session.add(m)
    session.flush()
    n = Node(
        manual_id=m.id, parent_id=None,
        level=2, level_label="Sección", ordinal="Primera",
        title="Generalidades", breadcrumb="PARTE I › Capítulo I › Primera Sección",
        page_start=1, page_end=2, sort_key="01.01.01", is_anexo=False,
        metadata_json={},
    )
    session.add(n)
    session.flush()
    session.add(Chunk(
        node_id=n.id, manual_id=m.id, ordinal=0, text="Texto de prueba.",
        char_count=16, page_start=1, page_end=1,
    ))
    session.flush()
    return m.id, n.id


def _make_question(text_prefix: str = "T"):
    return GeneratedQuestion(
        question=f"{text_prefix} - ¿Cuál es la respuesta?",
        options=[
            GeneratedOption(role=OptionRole.CORRECT, text=f"{text_prefix} correcta"),
            GeneratedOption(role=OptionRole.CONFUSA, text=f"{text_prefix} confusa"),
            GeneratedOption(role=OptionRole.DISTRACTOR, text=f"{text_prefix} fácil 1"),
            GeneratedOption(role=OptionRole.DISTRACTOR, text=f"{text_prefix} fácil 2"),
        ],
        justification="Justificación general.",
    )


def test_round_trip_run_and_question():
    init_question_tables()

    with session_scope() as s:
        manual_id, node_id = _seed_manual_and_node(s)
        run = create_run(
            s, manual_id=manual_id, model="gemini-3.6-flash", mode="immediate",
            profile_used="manual", rules_snapshot={"name": "manual"}, nodes_total=1,
        )
        persist_question(
            s, run=run, node_id=node_id, manual_id=manual_id,
            generation_order=0, payload=_make_question(), raw_response={"foo": "bar"},
        )
        finalize_run(
            s, run=run, nodes_completed=1, nodes_failed=0,
            cost_input_tokens=100, cost_output_tokens=200, cost_cached_tokens=50000,
            cost_estimate_usd=0.0123, status="succeeded",
        )

    with session_scope() as s:
        runs = s.query(GenerationRun).all()
        assert len(runs) == 1
        assert runs[0].nodes_completed == 1
        assert runs[0].status == "succeeded"

        questions = s.query(Question).all()
        assert len(questions) == 1
        q = questions[0]
        assert q.validation_status == "pending"
        assert q.raw_response_json == {"foo": "bar"}

        options = s.query(QuestionOption).filter_by(question_id=q.id).order_by(QuestionOption.order_in_question).all()
        assert len(options) == 4
        roles = [o.role for o in options]
        assert roles.count("correct") == 1
        assert roles.count("confusa") == 1
        assert roles.count("distractor") == 2
        correct = next(o for o in options if o.role == "correct")
        assert correct.is_correct is True


def test_two_runs_can_share_a_node():
    """Two different GenerationRuns for the same node are allowed (re-generation)."""
    init_question_tables()
    with session_scope() as s:
        manual_id, node_id = _seed_manual_and_node(s)
        run_a = create_run(
            s, manual_id=manual_id, model="gemini-3.6-flash", mode="immediate",
            profile_used="manual", rules_snapshot={}, nodes_total=1,
        )
        persist_question(
            s, run=run_a, node_id=node_id, manual_id=manual_id,
            generation_order=0, payload=_make_question("A"), raw_response={},
        )
        run_b = create_run(
            s, manual_id=manual_id, model="gemini-2.5-pro", mode="batch",
            profile_used="manual", rules_snapshot={}, nodes_total=1,
        )
        persist_question(
            s, run=run_b, node_id=node_id, manual_id=manual_id,
            generation_order=0, payload=_make_question("B"), raw_response={},
        )

    with session_scope() as s:
        assert s.query(Question).count() == 2
        assert s.query(QuestionOption).count() == 8  # 2 × 4


def test_remove_existing_for_nodes():
    init_question_tables()
    with session_scope() as s:
        manual_id, node_id = _seed_manual_and_node(s)
        run = create_run(
            s, manual_id=manual_id, model="gemini-3.6-flash", mode="immediate",
            profile_used="manual", rules_snapshot={}, nodes_total=1,
        )
        persist_question(
            s, run=run, node_id=node_id, manual_id=manual_id,
            generation_order=0, payload=_make_question("X"), raw_response={},
        )

    with session_scope() as s:
        n = remove_existing_questions_for_nodes(s, manual_id=1, node_ids=[1])
        assert n >= 1

    with session_scope() as s:
        assert s.query(Question).count() == 0

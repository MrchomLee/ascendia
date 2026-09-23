"""Qué ventanas procesa una corrida (spec §4): selección, reanudación y --limit."""

from datetime import datetime, timezone

from etl.db.session import session_scope
from etl.models.schema import Chunk, Manual, Node

from qgen.db.migration import init_question_tables
from qgen.db.persistence import create_run, persist_question
from qgen.pipeline import plan_windows
from qgen.prompts.schemas import GeneratedOption, GeneratedQuestion, OptionRole


def _seed(titles=("Capítulo 1", "Capítulo 2"), chunk_texts=("Texto del nodo.",)) -> tuple[int, list[int]]:
    init_question_tables()
    with session_scope() as session:
        manual = Manual(
            code="TST", title="Manual de prueba", source_path="no-existe.pdf", page_count=10,
            extractor_used="docling", ingested_at=datetime.now(timezone.utc), metadata_json={"profile": "manual"},
        )
        session.add(manual)
        session.flush()
        node_ids = []
        for i, title in enumerate(titles):
            node = Node(
                manual_id=manual.id, level=0, level_label="Capítulo", ordinal=str(i + 1), title=title,
                breadcrumb=title, page_start=i + 1, sort_key=f"{i + 1:02d}",
            )
            session.add(node)
            session.flush()
            node_ids.append(node.id)
            for j, text in enumerate(chunk_texts):
                session.add(Chunk(
                    node_id=node.id, manual_id=manual.id, ordinal=j, text=text,
                    char_count=len(text), page_start=i + 1, page_end=i + 1,
                ))
        return manual.id, node_ids


def _keys(manual_id: int, **kwargs) -> list[str]:
    with session_scope() as session:
        return [job.window.key for job in plan_windows(session, manual_id=manual_id, **kwargs)]


def _question() -> GeneratedQuestion:
    return GeneratedQuestion(
        question="¿Algo?",
        options=[
            GeneratedOption(role=OptionRole.CORRECT, text="a"),
            GeneratedOption(role=OptionRole.CONFUSA, text="b"),
            GeneratedOption(role=OptionRole.DISTRACTOR, text="c"),
            GeneratedOption(role=OptionRole.DISTRACTOR, text="d"),
        ],
        justification="…",
    )


def test_una_ventana_por_nodo_pequeno_en_orden():
    manual_id, (n1, n2) = _seed()

    with session_scope() as session:
        jobs = plan_windows(session, manual_id=manual_id)
        assert [job.window.key for job in jobs] == [f"{n1}:0-0", f"{n2}:0-0"]
        assert (jobs[0].node_label, jobs[0].node_title, jobs[0].node_breadcrumb) == ("Capítulo 1", "Capítulo 1", "Capítulo 1")


def test_las_introducciones_quedan_fuera():
    manual_id, (_, n2) = _seed(titles=("Introducción", "Capítulo 1"))
    assert _keys(manual_id) == [f"{n2}:0-0"]


def test_limit_cuenta_ventanas():
    manual_id, _ = _seed(chunk_texts=tuple(str(i) * 1500 for i in range(6)))  # 2 ventanas por nodo
    assert len(_keys(manual_id)) == 4
    assert len(_keys(manual_id, limit=3)) == 3


def test_solo_un_nodo():
    manual_id, (_, n2) = _seed()
    assert _keys(manual_id, only_node_id=n2) == [f"{n2}:0-0"]


def test_se_saltan_las_ventanas_ok_y_se_reintentan_las_fallidas():
    manual_id, (n1, n2) = _seed()
    with session_scope() as session:
        create_run(
            session, manual_id=manual_id, model="gemini-3.6-flash", mode="immediate", profile_used="manual",
            rules_snapshot={}, nodes_total=2, metadata_json={"ventanas": {f"{n1}:0-0": "ok", f"{n2}:0-0": "fallida"}},
        )
    assert _keys(manual_id) == [f"{n2}:0-0"]


def test_se_saltan_ventanas_con_preguntas_aunque_la_corrida_no_se_cerrara():
    manual_id, (n1, n2) = _seed()
    with session_scope() as session:
        run = create_run(
            session, manual_id=manual_id, model="gemini-3.6-flash", mode="immediate", profile_used="manual",
            rules_snapshot={}, nodes_total=2,
        )
        persist_question(
            session, run=run, node_id=n1, manual_id=manual_id, generation_order=0,
            payload=_question(), raw_response={}, window_key=f"{n1}:0-0",
        )
    assert _keys(manual_id) == [f"{n2}:0-0"]


def test_regenerate_ignora_el_historial():
    manual_id, (n1, n2) = _seed()
    with session_scope() as session:
        create_run(
            session, manual_id=manual_id, model="gemini-3.6-flash", mode="immediate", profile_used="manual",
            rules_snapshot={}, nodes_total=2, metadata_json={"ventanas": {f"{n1}:0-0": "ok"}},
        )
    assert _keys(manual_id, regenerate=True) == [f"{n1}:0-0", f"{n2}:0-0"]


def test_gana_el_ultimo_estado_de_cada_ventana():
    manual_id, (n1, n2) = _seed()
    with session_scope() as session:
        for estado in ("ok", "fallida"):
            create_run(
                session, manual_id=manual_id, model="gemini-3.6-flash", mode="immediate", profile_used="manual",
                rules_snapshot={}, nodes_total=2, metadata_json={"ventanas": {f"{n1}:0-0": estado, f"{n2}:0-0": "ok"}},
            )
    assert _keys(manual_id) == [f"{n1}:0-0"]

"""Pestaña "Exportar Bundle" de la página de preguntas, ejecutada con AppTest.

La descarga es la entrega a la webapp: solo se ofrece si el bundle cumple el
contrato, igual que `qgen-export`.
"""

from datetime import datetime, timezone
from pathlib import Path

from etl.db.init_db import init_db
from etl.db.session import session_scope
from etl.models.schema import Chunk, Manual, Node
from qgen.db.migration import init_question_tables
from qgen.db.persistence import create_run, finalize_run, persist_question
from qgen.prompts.schemas import GeneratedOption, GeneratedQuestion, OptionRole
from streamlit.testing.v1 import AppTest

PAGE = next((Path(__file__).parents[1] / "src" / "explorer" / "pages").glob("6_*_Preguntas.py"))


def _seed(*, run_status: str) -> int:
    init_db()
    init_question_tables()
    with session_scope() as session:
        manual = Manual(
            code="CJM", title="Código de Justicia Militar", source_path="no-existe.pdf",
            page_count=10, extractor_used="docling", ingested_at=datetime.now(timezone.utc),
            metadata_json={"profile": "codigo_legal"},
        )
        session.add(manual)
        session.flush()
        node = Node(
            manual_id=manual.id, level=0, level_label="Capítulo", ordinal="I",
            title="Disposiciones preliminares", breadcrumb="Capítulo I", page_start=1, sort_key="01",
        )
        session.add(node)
        session.flush()
        text = "La administración de la justicia militar corresponde al Supremo Tribunal Militar."
        session.add(Chunk(node_id=node.id, manual_id=manual.id, ordinal=0, text=text,
                          char_count=len(text), page_start=1, page_end=1))
        run = create_run(session, manual_id=manual.id, model="gemini-3.6-flash", mode="immediate",
                         profile_used="codigo_legal", rules_snapshot={}, nodes_total=1)
        persist_question(
            session, run=run, node_id=node.id, manual_id=manual.id, generation_order=0,
            source_quote=text,
            question_type="ejercicio_nuevo",
            metadata={
                "motivos": ["supera la dificultad del PDF"],
                "revision": {"por": "claude-opus-5-5", "veredicto": "dudosa", "calificacion": 3,
                             "motivos": ["depende de otra sección"], "fecha": "2026-09-24T00:00:00+00:00"},
            },
            payload=GeneratedQuestion(
                question="¿A quién corresponde la administración de la justicia militar?",
                options=[
                    GeneratedOption(role=OptionRole.CORRECT, text="Al Supremo Tribunal Militar."),
                    GeneratedOption(role=OptionRole.CONFUSA, text="A la Procuraduría de Justicia Militar."),
                    GeneratedOption(role=OptionRole.DISTRACTOR, text="A los consejos de honor."),
                    GeneratedOption(role=OptionRole.DISTRACTOR, text="A la Secretaría de la Defensa."),
                ],
                justification="Artículo 1o.",
            ),
            raw_response={},
        )
        if run_status != "running":
            finalize_run(session, run=run, nodes_completed=1, nodes_failed=0, cost_input_tokens=0,
                         cost_output_tokens=0, cost_cached_tokens=0, cost_estimate_usd=0.0,
                         status=run_status)
        return manual.id


def _open_page(manual_id: int) -> AppTest:
    at = AppTest.from_file(str(PAGE), default_timeout=60)
    at.query_params["manual_id"] = str(manual_id)
    at.run()
    assert not at.exception, at.exception
    return at


def test_un_bundle_que_cumple_el_contrato_se_puede_descargar():
    at = _open_page(_seed(run_status="succeeded"))

    assert [e.value for e in at.error] == []
    assert len(at.get("download_button")) == 1


def test_un_bundle_con_errores_no_se_ofrece_y_se_explica_por_que():
    # Una corrida en `running` es error duro del contrato (§5.6): el importador
    # de la webapp la rechazaría.
    at = _open_page(_seed(run_status="running"))

    assert at.get("download_button") == []
    assert any("running" in e.value for e in at.error)


def test_la_pregunta_muestra_su_tipo_y_sus_motivos():
    at = _open_page(_seed(run_status="succeeded"))

    assert any("Ejercicio nuevo" in c.value for c in at.caption)
    assert any("supera la dificultad del PDF" in w.value for w in at.warning)


def test_la_pregunta_muestra_la_revision_de_claude_con_su_calificacion():
    at = _open_page(_seed(run_status="succeeded"))

    assert any("dudosa · 3/5 — depende de otra sección" in i.value for i in at.info)


def test_la_cita_se_muestra_tal_cual():
    # Texto plano: en markdown, `>` citaría solo la primera línea y `*`, `_` o `$` de una
    # fórmula se interpretarían.
    at = _open_page(_seed(run_status="succeeded"))

    cita = "La administración de la justicia militar corresponde al Supremo Tribunal Militar."
    assert any(t.value == cita for t in at.text)

"""Pruebas unitarias para la capa de acceso a preguntas del explorador (questions_access.py)."""

from datetime import datetime, timezone
import streamlit as st

from etl.db.init_db import init_db
from etl.db.session import session_scope
from etl.models.schema import Chunk, Manual, Node
from qgen.db.migration import init_question_tables
from qgen.db.persistence import create_run, finalize_run, persist_question
from qgen.prompts.schemas import GeneratedOption, GeneratedQuestion, OptionRole

from explorer.questions_access import (
    SIN_NIVEL,
    get_question_kpis,
    level_label,
    list_questions,
    revision_label,
    list_runs,
    nodes_missing_questions,
    questions_available,
    set_validation_status,
)


def _seed_questions_data():
    """Siembra manual, nodo, corrida y preguntas para pruebas."""
    init_db()
    init_question_tables()

    with session_scope() as session:
        m = Manual(
            code="MAN-Q",
            title="Manual con Preguntas",
            source_path="/tmp/q.pdf",
            page_count=10,
            extractor_used="docling",
            ingested_at=datetime.now(timezone.utc),
            metadata_json={"profile": "manual"},
        )
        session.add(m)
        session.flush()

        n = Node(
            manual_id=m.id,
            parent_id=None,
            level=0,
            level_label="Capítulo",
            ordinal="I",
            title="Generalidades",
            breadcrumb="Capítulo I — Generalidades",
            page_start=1,
            page_end=3,
            sort_key="01",
            is_anexo=False,
        )
        session.add(n)
        session.flush()

        c = Chunk(
            manual_id=m.id,
            node_id=n.id,
            ordinal=1,
            text="Texto relevante del manual sobre disciplina.",
            char_count=44,
            page_start=1,
            page_end=2,
            has_table=False,
            has_image_ref=False,
        )
        session.add(c)
        session.flush()

        run = create_run(
            session,
            manual_id=m.id,
            model="test-model",
            mode="immediate",
            profile_used="manual",
            rules_snapshot={"rules": []},
            nodes_total=1,
        )

        gq = GeneratedQuestion(
            question="¿Cuál es la base de la disciplina militar?",
            justification="La disciplina es el principio rector.",
            options=[
                GeneratedOption(text="El cumplimiento estricto del deber", role=OptionRole.CORRECT),
                GeneratedOption(text="La fuerza física individual", role=OptionRole.CONFUSA),
                GeneratedOption(text="La ausencia de normas escritas", role=OptionRole.DISTRACTOR),
                GeneratedOption(text="El beneficio económico personal", role=OptionRole.DISTRACTOR),
            ],
        )
        q = persist_question(
            session,
            run=run,
            manual_id=m.id,
            node_id=n.id,
            generation_order=1,
            payload=gq,
            raw_response={},
            question_type="ejercicio_nuevo",
            source_quote="Texto relevante del manual sobre disciplina.",
            metadata={"motivos": ["la verificación eligió B; la clave es A"]},
        )
        finalize_run(
            session,
            run=run,
            nodes_completed=1,
            nodes_failed=0,
            cost_input_tokens=100,
            cost_output_tokens=50,
            cost_cached_tokens=0,
            cost_estimate_usd=0.001,
        )

        return m.id, n.id, run.id, q.id


def test_questions_available():
    """Verifica que detecta correctamente si las tablas de preguntas existen."""
    st.cache_data.clear()
    init_db()
    init_question_tables()
    assert questions_available() is True


def test_get_question_kpis_y_list_questions():
    """Verifica el cálculo de métricas y la consulta de preguntas."""
    st.cache_data.clear()
    manual_id, node_id, run_id, q_id = _seed_questions_data()

    kpis = get_question_kpis(manual_id)
    assert kpis.total == 1
    assert kpis.nodes_with_question == 1
    assert kpis.coverage_pct > 0
    assert kpis.by_status.get("pending") == 1

    questions = list_questions(manual_id)
    assert len(questions) == 1
    q = questions[0]
    assert q.id == q_id
    assert q.question_text == "¿Cuál es la base de la disciplina militar?"
    assert len(q.options) == 4
    assert q.served is True

    runs = list_runs(manual_id)
    assert len(runs) == 1
    assert runs[0].id == run_id

    # Como el único nodo tiene pregunta, la lista de nodos faltantes debe estar vacía
    faltantes = nodes_missing_questions(manual_id)
    assert len(faltantes) == 0


def test_set_validation_status():
    """Verifica la actualización de estado de validación (aprobación/rechazo)."""
    st.cache_data.clear()
    manual_id, _, _, q_id = _seed_questions_data()

    # Actualizamos a aprobado (valid)
    set_validation_status(q_id, "valid")
    st.cache_data.clear()

    q_actualizada = next(q for q in list_questions(manual_id) if q.id == q_id)
    assert q_actualizada.validation_status == "valid"

    # Actualizamos a rechazado (rejected)
    set_validation_status(q_id, "rejected")
    st.cache_data.clear()

    q_rechazada = next(q for q in list_questions(manual_id) if q.id == q_id)
    assert q_rechazada.validation_status == "rejected"
    assert q_rechazada.served is False


def test_la_pregunta_trae_su_tipo_su_cita_y_sus_motivos():
    st.cache_data.clear()
    manual_id, _, _, _ = _seed_questions_data()

    [q] = list_questions(manual_id)

    assert q.question_type == "ejercicio_nuevo"
    assert q.source_quote == "Texto relevante del manual sobre disciplina."
    assert q.motivos == ["la verificación eligió B; la clave es A"]


def test_la_etiqueta_de_la_revision_lleva_veredicto_calificacion_y_motivos():
    revision = {"por": "claude-opus-5-5", "veredicto": "rechazar", "calificacion": 1,
                "motivos": ["fuera de tema", "sin sentido"]}
    assert revision_label(revision) == (
        "Revisión de claude-opus-5-5: rechazar · 1/5 — fuera de tema; sin sentido"
    )
    assert revision_label({**revision, "veredicto": "aceptar", "calificacion": 5, "motivos": []}) == (
        "Revisión de claude-opus-5-5: aceptar · 5/5"
    )


def test_filtra_por_nivel_incluido_sin_clasificar():
    st.cache_data.clear()
    manual_id, _, _, qid = _seed_questions_data()
    assert list_questions(manual_id, levels=(SIN_NIVEL,))  # el seed no tiene nivel
    assert list_questions(manual_id, levels=("analisis",)) == []
    with session_scope() as session:
        from qgen.models.schema import Question
        q = session.get(Question, qid)
        q.cognitive_level = "analisis"
        q.metadata_json = {**(q.metadata_json or {}), "nivel_generado": "comprension"}
    st.cache_data.clear()
    [q] = list_questions(manual_id, levels=("analisis",))
    assert level_label(q) == "Análisis (generada como Comprensión)"
    assert get_question_kpis(manual_id).by_level == {"analisis": 1}


def test_la_etiqueta_de_revision_lleva_el_nivel_si_lo_hay():
    revision = {"por": "claude-opus-5-5", "veredicto": "aceptar", "calificacion": 5, "motivos": [], "nivel": "aplicacion"}
    assert revision_label(revision) == "Revisión de claude-opus-5-5: aceptar · 5/5 · Aplicación"

"""Construcción del bundle desde el SQLite del pipeline.

Lo que se comprueba aquí es que lo que sale de la base cumple el contrato y que
la identidad viaja en claves estables, no en los ids autoincrementales.
"""

from datetime import datetime, timezone

import pytest
from etl.db.session import session_scope
from etl.models.schema import Chunk, Manual, Node

from qgen.bundle.build import DuplicateNodeRef, build_bundle
from qgen.bundle.spec import validate
from qgen.db.migration import init_question_tables
from qgen.db.persistence import create_run, finalize_run, persist_question
from qgen.models.schema import GenerationRun
from qgen.prompts.schemas import GeneratedOption, GeneratedQuestion, OptionRole

CITA = "El fuero de guerra subsiste para los delitos del orden militar."


def _question(prefix: str = "T") -> GeneratedQuestion:
    return GeneratedQuestion(
        question=f"{prefix} — ¿cuál es la respuesta?",
        options=[
            GeneratedOption(role=OptionRole.CORRECT, text=f"{prefix} correcta"),
            GeneratedOption(role=OptionRole.CONFUSA, text=f"{prefix} confusa"),
            GeneratedOption(role=OptionRole.DISTRACTOR, text=f"{prefix} fácil 1"),
            GeneratedOption(role=OptionRole.DISTRACTOR, text=f"{prefix} fácil 2"),
        ],
        justification="Porque el artículo lo dice.",
    )


def _seed(session, *, sort_keys=("01", "01.01")) -> tuple[int, list[int]]:
    manual = Manual(
        code="CJM", title="Código de Justicia Militar", source_path="data/raw_pdfs/cjm.pdf",
        page_count=320, extractor_used="docling", ingested_at=datetime.now(timezone.utc),
        metadata_json={"profile": "codigo"},
    )
    session.add(manual)
    session.flush()

    node_ids: list[int] = []
    parent_id = None
    for level, sort_key in enumerate(sort_keys):
        node = Node(
            manual_id=manual.id, parent_id=parent_id, level=level,
            level_label="PARTE" if level == 0 else "Capítulo", ordinal=str(level + 1),
            title=f"Nodo {sort_key}", breadcrumb=f"› {sort_key}",
            page_start=level + 1, page_end=level + 5, sort_key=sort_key,
            is_anexo=False, metadata_json={},
        )
        session.add(node)
        session.flush()
        node_ids.append(node.id)
        parent_id = node.id

    session.add(Chunk(
        node_id=node_ids[-1], manual_id=manual.id, ordinal=0,
        text="El fuero de guerra subsiste para los delitos del orden militar.",
        char_count=62, page_start=2, page_end=2,
    ))
    session.flush()
    return manual.id, node_ids


def _seed_with_questions(session, **kwargs) -> tuple[int, list[int], int]:
    manual_id, node_ids = _seed(session, **kwargs)
    run = create_run(
        session, manual_id=manual_id, model="gemini-3.6-flash", mode="immediate",
        profile_used="codigo", rules_snapshot={"name": "codigo"}, nodes_total=1,
    )
    persist_question(
        session, run=run, node_id=node_ids[-1], manual_id=manual_id,
        question_type="teoria", source_quote=CITA,
        generation_order=0, payload=_question(), raw_response={"candidates": ["…"]},
    )
    finalize_run(
        session, run=run, nodes_completed=1, nodes_failed=0,
        cost_input_tokens=1000, cost_output_tokens=200, cost_cached_tokens=900,
        cost_estimate_usd=0.0123456789, status="succeeded",
    )
    return manual_id, node_ids, run.id


def test_el_bundle_exportado_cumple_el_contrato():
    init_question_tables()
    with session_scope() as session:
        manual_id, _, _ = _seed_with_questions(session)
        bundle = build_bundle(session, manual_id=manual_id)

    report = validate(bundle)
    assert report.ok, report.errors
    assert report.counts == {
        "nodes": 2, "chunks": 1, "runs": 1, "questions": 1,
        "questions_served": 1, "status_pending": 1,
    }


def test_la_identidad_va_en_refs_no_en_ids():
    init_question_tables()
    with session_scope() as session:
        manual_id, _, _ = _seed_with_questions(session)
        bundle = build_bundle(session, manual_id=manual_id)

    assert [n["ref"] for n in bundle["nodes"]] == ["01", "01.01"]
    assert bundle["nodes"][0]["parent_ref"] is None
    assert bundle["nodes"][1]["parent_ref"] == "01"

    assert bundle["runs"][0]["ref"].startswith("gemini-3.6-flash--immediate--")
    assert bundle["questions"][0]["node_ref"] == "01.01"
    assert bundle["questions"][0]["run_ref"] == bundle["runs"][0]["ref"]

    # Ni un solo id autoincremental en el fichero.
    from qgen.bundle.spec import dumps

    assert '"id"' not in dumps(bundle)


def test_dos_exportaciones_del_mismo_estado_son_identicas():
    init_question_tables()
    with session_scope() as session:
        manual_id, _, _ = _seed_with_questions(session)
        primero = build_bundle(session, manual_id=manual_id)
        segundo = build_bundle(session, manual_id=manual_id)

    for bundle in (primero, segundo):
        # `generated_at` es lo único que cambia entre dos corridas del exportador.
        bundle.pop("generated_at")
    assert primero == segundo


def test_la_respuesta_cruda_se_queda_fuera_salvo_que_se_pida():
    init_question_tables()
    with session_scope() as session:
        manual_id, _, _ = _seed_with_questions(session)
        sin_raw = build_bundle(session, manual_id=manual_id)
        con_raw = build_bundle(session, manual_id=manual_id, include_raw=True)

    assert "raw_response" not in sin_raw["questions"][0]
    assert con_raw["questions"][0]["raw_response"] == {"candidates": ["…"]}


def test_el_costo_se_redondea_a_lo_que_guarda_postgres():
    init_question_tables()
    with session_scope() as session:
        manual_id, _, _ = _seed_with_questions(session)
        bundle = build_bundle(session, manual_id=manual_id)

    # numeric(12,6) del otro lado: más decimales se perderían igual.
    assert bundle["runs"][0]["cost_estimate_usd"] == 0.012346


def test_sort_keys_repetidos_abortan_la_exportacion():
    init_question_tables()
    with session_scope() as session:
        manual_id, _ = _seed(session, sort_keys=("01", "01"))
        with pytest.raises(DuplicateNodeRef, match="sort_key"):
            build_bundle(session, manual_id=manual_id)


def test_se_puede_exportar_una_sola_corrida():
    init_question_tables()
    with session_scope() as session:
        manual_id, node_ids, run_id = _seed_with_questions(session)
        otra = create_run(
            session, manual_id=manual_id, model="gemini-2.5-pro", mode="batch",
            profile_used="codigo", rules_snapshot={}, nodes_total=1,
        )
        persist_question(
            session, run=otra, node_id=node_ids[-1], manual_id=manual_id,
            question_type="teoria", source_quote=CITA,
            generation_order=0, payload=_question("B"), raw_response={},
        )
        finalize_run(
            session, run=otra, nodes_completed=1, nodes_failed=0,
            cost_input_tokens=1, cost_output_tokens=1, cost_cached_tokens=0,
            cost_estimate_usd=0.001, status="succeeded",
        )

        completo = build_bundle(session, manual_id=manual_id)
        solo_una = build_bundle(session, manual_id=manual_id, run_ids=[run_id])

    assert len(completo["runs"]) == 2
    assert len(completo["questions"]) == 2
    assert validate(completo).ok

    assert len(solo_una["runs"]) == 1
    assert len(solo_una["questions"]) == 1
    assert solo_una["questions"][0]["run_ref"] == solo_una["runs"][0]["ref"]
    assert validate(solo_una).ok


def test_manual_inexistente():
    init_question_tables()
    with session_scope() as session:
        with pytest.raises(ValueError, match="ningún manual"):
            build_bundle(session, manual_id=999)


def test_corrida_que_no_es_del_manual():
    init_question_tables()
    with session_scope() as session:
        manual_id, _, _ = _seed_with_questions(session)
        with pytest.raises(ValueError, match="no existen o no son de este manual"):
            build_bundle(session, manual_id=manual_id, run_ids=[999])


def test_la_pregunta_viaja_con_su_tipo_y_su_cita():
    init_question_tables()
    with session_scope() as session:
        manual_id, _, _ = _seed_with_questions(session)
        bundle = build_bundle(session, manual_id=manual_id)

    assert bundle["bundle_version"] == 2
    q = bundle["questions"][0]
    assert (q["question_type"], q["source_quote"]) == ("teoria", CITA)


def test_varias_preguntas_del_mismo_nodo_se_exportan():
    init_question_tables()
    with session_scope() as session:
        manual_id, node_ids, run_id = _seed_with_questions(session)
        persist_question(
            session, run=session.get(GenerationRun, run_id), node_id=node_ids[-1], manual_id=manual_id,
            generation_order=1, payload=_question("B"), raw_response={},
            question_type="ejercicio_nuevo", source_quote=CITA,
        )
        bundle = build_bundle(session, manual_id=manual_id)

    report = validate(bundle)
    assert report.ok, report.errors
    assert [q["generation_order"] for q in bundle["questions"]] == [0, 1]

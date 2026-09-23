"""El contrato del bundle: lo que se acepta y, sobre todo, lo que no.

Cada caso de rechazo corresponde a una de las diez comprobaciones del contrato
(§5 de `CONTRATO-BUNDLE.md`).
"""

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

import pytest

from qgen.bundle.spec import (
    BUNDLE_VERSION,
    bundle_filename,
    dumps,
    iso,
    next_version,
    read_bundle,
    run_ref,
    validate,
    verify_checksum,
    write_bundle,
)


def _options(prefix: str = "o") -> list[dict]:
    return [
        {"role": "correct", "order_in_question": 0, "text": f"{prefix} correcta", "is_correct": True, "metadata": {}},
        {"role": "confusa", "order_in_question": 1, "text": f"{prefix} confusa", "is_correct": False, "metadata": {}},
        {"role": "distractor", "order_in_question": 2, "text": f"{prefix} fácil 1", "is_correct": False, "metadata": {}},
        {"role": "distractor", "order_in_question": 3, "text": f"{prefix} fácil 2", "is_correct": False, "metadata": {}},
    ]


def _bundle() -> dict:
    """Un bundle mínimo pero completo y válido."""
    return {
        "bundle_version": BUNDLE_VERSION,
        "generated_at": "2026-08-17T10:15:00Z",
        "generator": {"tool": "qgen", "version": "0.1.0", "pipeline_commit": "abc1234"},
        "manual": {
            "code": "CJM",
            "edition": None,
            "title": "Código de Justicia Militar",
            "branch": None,
            "source_path": "data/raw_pdfs/cjm.pdf",
            "source_sha256": None,
            "page_count": 320,
            "extractor_used": "docling",
            "ingested_at": "2026-08-16T22:04:11Z",
            "metadata": {},
        },
        "catalog_hint": {"grado_code": "SARG_2", "materia_code": "JUS_MIL"},
        "nodes": [
            {
                "ref": "01", "parent_ref": None, "level": 0, "level_label": "PARTE",
                "ordinal": "I", "title": "Disposiciones generales", "breadcrumb": "PARTE I",
                "page_start": 1, "page_end": 40, "is_anexo": False, "metadata": {},
                "chunks": [],
            },
            {
                "ref": "01.01", "parent_ref": "01", "level": 1, "level_label": "Capítulo",
                "ordinal": "1", "title": "Del fuero de guerra", "breadcrumb": "PARTE I › Capítulo 1",
                "page_start": 2, "page_end": 9, "is_anexo": False, "metadata": {},
                "chunks": [
                    {
                        "ordinal": 0, "text": "El fuero de guerra …", "char_count": 20,
                        "page_start": 2, "page_end": 3, "has_table": False,
                        "has_image_ref": False, "metadata": {},
                    }
                ],
            },
        ],
        "runs": [
            {
                "ref": "gemini-3.6-flash--immediate--20260817T093000Z",
                "model": "gemini-3.6-flash", "mode": "immediate", "status": "succeeded",
                "profile_used": "default", "rules_snapshot": {},
                "started_at": "2026-08-17T09:30:00Z", "completed_at": "2026-08-17T09:58:22Z",
                "nodes_total": 1, "nodes_completed": 1, "nodes_failed": 0,
                "cost_input_tokens": 1000, "cost_output_tokens": 200, "cost_cached_tokens": 900,
                "cost_estimate_usd": 0.0123, "metadata": {},
            }
        ],
        "questions": [
            {
                "run_ref": "gemini-3.6-flash--immediate--20260817T093000Z",
                "node_ref": "01.01",
                "generation_order": 0,
                "question_text": "¿Qué establece el artículo 1?",
                "justification": "Porque el artículo 1 dice …",
                "question_type": "teoria",
                "source_quote": "El fuero de guerra …",
                "validation_status": "valid",
                "validated_at": None,
                "created_at": "2026-08-17T09:41:07Z",
                "metadata": {},
                "options": _options(),
            }
        ],
    }


def _errors(mutate) -> list[str]:
    bundle = _bundle()
    mutate(bundle)
    return validate(bundle).errors


# ─── Camino feliz ──────────────────────────────────────────────────────────


def test_bundle_valido_pasa_sin_errores():
    report = validate(_bundle())
    assert report.ok, report.errors
    assert report.counts["nodes"] == 2
    assert report.counts["chunks"] == 1
    assert report.counts["questions"] == 1
    assert report.counts["questions_served"] == 1


def test_nodo_con_texto_sin_pregunta_avisa_pero_no_bloquea():
    bundle = _bundle()
    bundle["nodes"][0]["chunks"] = [{
        "ordinal": 0, "text": "algo", "char_count": 4, "page_start": 1, "page_end": 1,
        "has_table": False, "has_image_ref": False, "metadata": {},
    }]
    report = validate(bundle)
    assert report.ok
    assert any("sin pregunta" in w for w in report.warnings)


def test_preguntas_rechazadas_avisan():
    bundle = _bundle()
    bundle["questions"][0]["validation_status"] = "rejected"
    report = validate(bundle)
    assert report.ok
    assert report.counts["questions_served"] == 0
    assert any("rejected" in w for w in report.warnings)


# ─── (2) versión ───────────────────────────────────────────────────────────


def test_version_desconocida_se_rechaza_de_entrada():
    errors = _errors(lambda b: b.update(bundle_version=99))
    assert len(errors) == 1
    assert "bundle_version" in errors[0]


# ─── (3) campos requeridos y longitudes ────────────────────────────────────


def test_falta_un_campo_requerido():
    assert any("`title`" in e for e in _errors(lambda b: b["manual"].pop("title")))


def test_texto_mas_largo_que_la_columna():
    errors = _errors(lambda b: b["questions"][0].update(question_text="x" * 1001))
    assert any("máximo es 1000" in e for e in errors)


def test_fecha_que_no_es_iso_utc():
    errors = _errors(lambda b: b["questions"][0].update(created_at="17/08/2026"))
    assert any("ISO 8601" in e for e in errors)


# ─── (4) árbol ─────────────────────────────────────────────────────────────


def test_refs_de_nodo_repetidos():
    errors = _errors(lambda b: b["nodes"][1].update(ref="01", parent_ref=None))
    assert any("repetido" in e for e in errors)


def test_padre_que_no_esta_en_el_bundle():
    errors = _errors(lambda b: b["nodes"][1].update(parent_ref="99"))
    assert any("no está en el bundle" in e for e in errors)


def test_arbol_sin_raiz():
    errors = _errors(lambda b: b["nodes"][0].update(parent_ref="01.01"))
    assert any("no tiene raíz" in e or "ciclo" in e for e in errors)


def test_ciclo_en_el_arbol():
    def mutate(b):
        b["nodes"].append({
            "ref": "01.02", "parent_ref": "01.03", "level": 1, "level_label": "Capítulo",
            "ordinal": "2", "title": "A", "breadcrumb": "x", "page_start": 3, "page_end": 4,
            "is_anexo": False, "metadata": {}, "chunks": [],
        })
        b["nodes"].append({
            "ref": "01.03", "parent_ref": "01.02", "level": 1, "level_label": "Capítulo",
            "ordinal": "3", "title": "B", "breadcrumb": "y", "page_start": 5, "page_end": 6,
            "is_anexo": False, "metadata": {}, "chunks": [],
        })

    assert any("ciclo" in e for e in _errors(mutate))


# ─── (6) corridas ──────────────────────────────────────────────────────────


def test_corrida_a_medias_no_se_entrega():
    errors = _errors(lambda b: b["runs"][0].update(status="running"))
    assert any("running" in e for e in errors)


def test_modo_de_corrida_invalido():
    assert any("`mode`" in e for e in _errors(lambda b: b["runs"][0].update(mode="turbo")))


def test_corrida_con_nodos_fallidos_avisa():
    bundle = _bundle()
    bundle["runs"][0]["nodes_failed"] = 3
    report = validate(bundle)
    assert report.ok
    assert any("sin pregunta" in w for w in report.warnings)


# ─── (5) referencias cruzadas ──────────────────────────────────────────────


def test_pregunta_que_apunta_a_un_nodo_inexistente():
    errors = _errors(lambda b: b["questions"][0].update(node_ref="99.99"))
    assert any("no está en `nodes`" in e for e in errors)


def test_pregunta_que_apunta_a_una_corrida_inexistente():
    errors = _errors(lambda b: b["questions"][0].update(run_ref="otra"))
    assert any("no está en `runs`" in e for e in errors)


def _v1(b):
    b["bundle_version"] = 1
    for q in b["questions"]:
        q.pop("question_type")
        q.pop("source_quote")


def test_v2_admite_varias_preguntas_por_nodo():
    def mutate(b):
        otra = deepcopy(b["questions"][0])
        otra.update(generation_order=1, options=_options("z"))
        b["questions"].append(otra)

    assert _errors(mutate) == []


def test_v2_rechaza_el_mismo_orden_dos_veces_en_una_corrida():
    def mutate(b):
        otra = deepcopy(b["questions"][0])
        otra["options"] = _options("z")
        b["questions"].append(otra)

    assert any("`generation_order` 0" in e and "índice único" in e for e in _errors(mutate))


def test_v2_exige_un_tipo_de_pregunta_conocido():
    assert any("`question_type`" in e for e in _errors(lambda b: b["questions"][0].update(question_type="examen")))
    assert any("`question_type`" in e for e in _errors(lambda b: b["questions"][0].pop("question_type")))


def test_v2_exige_la_cita():
    assert any("`source_quote`" in e for e in _errors(lambda b: b["questions"][0].pop("source_quote")))
    assert any("máximo es 2000" in e for e in _errors(lambda b: b["questions"][0].update(source_quote="x" * 2001)))


def test_v1_sigue_siendo_valido_sin_los_campos_nuevos():
    assert _errors(_v1) == []


def test_v1_mantiene_una_pregunta_por_corrida_y_nodo():
    def mutate(b):
        _v1(b)
        otra = deepcopy(b["questions"][0])
        otra.update(generation_order=1, options=_options("z"))
        b["questions"].append(otra)

    assert any("índice único" in e for e in _errors(mutate))


# ─── (7, 8) opciones ───────────────────────────────────────────────────────


def test_numero_de_opciones_distinto_de_cuatro():
    errors = _errors(lambda b: b["questions"][0]["options"].pop())
    assert any("deben ser 4" in e for e in errors)


def test_reparto_de_roles_incorrecto():
    errors = _errors(lambda b: b["questions"][0]["options"][2].update(role="correct"))
    assert any("distractor" in e for e in errors)


def test_sin_opcion_correcta():
    errors = _errors(lambda b: b["questions"][0]["options"][0].update(is_correct=False))
    assert any("is_correct" in e for e in errors)


def test_la_correcta_marcada_no_es_la_del_rol_correct():
    def mutate(b):
        b["questions"][0]["options"][0]["is_correct"] = False
        b["questions"][0]["options"][1]["is_correct"] = True

    assert any("no es la de rol `correct`" in e for e in _errors(mutate))


def test_opciones_con_el_mismo_texto():
    def mutate(b):
        texto = b["questions"][0]["options"][0]["text"]
        # Mismo texto con otra caja y espacios de más: sigue siendo el mismo.
        b["questions"][0]["options"][3]["text"] = f"  {texto.upper()}  "

    assert any("mismo texto" in e for e in _errors(mutate))


# ─── (9) estado de validación ──────────────────────────────────────────────


def test_estado_de_validacion_desconocido():
    errors = _errors(lambda b: b["questions"][0].update(validation_status="aprobada"))
    assert any("validation_status" in e for e in errors)


# ─── Secretos ──────────────────────────────────────────────────────────────


def test_api_key_en_metadata_bloquea_la_entrega():
    errors = _errors(
        lambda b: b["runs"][0]["metadata"].update(api_key="AIzaSyD-1234567890abcdefghijklmnop")
    )
    assert any("secreto" in e for e in errors)


def test_cadena_de_conexion_en_metadata_bloquea_la_entrega():
    errors = _errors(
        lambda b: b["manual"]["metadata"].update(origen="postgres://usuario:secreta@servidor:5432/base")
    )
    assert any("secreto" in e for e in errors)


def test_los_contadores_de_tokens_no_son_un_secreto():
    """`cost_input_tokens` contiene 'token': el detector no debe morder ahí."""
    assert validate(_bundle()).ok


# ─── Serialización, checksum y nombres ─────────────────────────────────────


def test_ida_y_vuelta_por_disco_con_checksum(tmp_path: Path):
    bundle = _bundle()
    target = tmp_path / bundle_filename("CJM", datetime(2026, 8, 17).date(), 1)
    written, checksum = write_bundle(target, bundle)

    assert written.name == "cjm--20260817--v1.json"
    assert written.with_name(written.name + ".sha256").exists()
    verify_checksum(written)
    assert read_bundle(written) == bundle
    assert len(checksum) == 64


def test_checksum_que_no_cuadra_se_detecta(tmp_path: Path):
    target = tmp_path / "cjm--20260817--v1.json"
    written, _ = write_bundle(target, _bundle())
    written.write_text(written.read_text(encoding="utf-8").replace("Justicia", "Injusticia"),
                       encoding="utf-8")
    with pytest.raises(ValueError, match="no cuadra"):
        verify_checksum(written)


def test_falta_el_checksum(tmp_path: Path):
    target = tmp_path / "cjm--20260817--v1.json"
    written, _ = write_bundle(target, _bundle())
    written.with_name(written.name + ".sha256").unlink()
    with pytest.raises(FileNotFoundError, match="Falta el checksum"):
        verify_checksum(written)


def test_los_acentos_no_se_escapan():
    assert "Código" in dumps(_bundle())


def test_siguiente_version_cuenta_por_manual(tmp_path: Path):
    assert next_version(tmp_path, "CJM") == 1
    (tmp_path / "cjm--20260817--v1.json").touch()
    (tmp_path / "cjm--20260901--v2.json").touch()
    (tmp_path / "dn-m-1455--20260901--v7.json").touch()
    assert next_version(tmp_path, "CJM") == 3
    assert next_version(tmp_path, "DN M 1455") == 8


def test_fecha_ingenua_se_lee_como_utc():
    assert iso(datetime(2026, 8, 17, 9, 30, 0)) == "2026-08-17T09:30:00Z"
    assert iso(datetime(2026, 8, 17, 9, 30, 0, tzinfo=timezone.utc)) == "2026-08-17T09:30:00Z"
    assert iso(None) is None


def test_ref_de_corrida_es_estable():
    started = datetime(2026, 8, 17, 9, 30, 0, tzinfo=timezone.utc)
    assert run_ref("gemini-3.6-flash", "immediate", started) == (
        "gemini-3.6-flash--immediate--20260817T093000Z"
    )

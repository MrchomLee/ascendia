"""Generación sin API desde Claude Code: exportar ventanas, responder, importar.

Lo que se prueba es el intercambio de archivos y que la importación pase por
las mismas revisiones que una corrida con Gemini, sin llamar a Gemini.
"""

import json
from datetime import datetime, timezone

import pytest
from etl.db.session import session_scope
from etl.models.schema import Chunk, Manual, Node
from sqlalchemy import select
from typer.testing import CliRunner

import qgen.pipeline as pipeline
from qgen.claude_code import MODEL_CLAUDE_CODE, exportar, importar, leer_respuesta, nombre_de
from qgen.cli.claude_code import app
from qgen.db.migration import init_question_tables
from qgen.models.schema import GenerationRun, Question

TEXTO = "La guerra es un conflicto entre sociedades que luchan violentamente."
EJEMPLO = "EJEMPLO 1 Derivar f(x) = x^2. Solución: f'(x) = 2x."


def _item(pregunta="¿Qué es la guerra?", *, tipo="teoria", nivel="conocimiento", correcta="un conflicto entre sociedades",
          cita=TEXTO, prefijo="T") -> dict:
    return {
        "tipo": tipo,
        "nivel": nivel,
        "pregunta": pregunta,
        "opciones": [
            {"rol": "correct", "texto": correcta},
            {"rol": "confusa", "texto": f"{prefijo} confusa"},
            {"rol": "distractor", "texto": f"{prefijo} distractor 1"},
            {"rol": "distractor", "texto": f"{prefijo} distractor 2"},
        ],
        "cita": cita,
        "justificacion": "Lo dice el texto.",
    }


def _seed(n_nodes: int = 2, *, profile: str = "historia_universal", texto: str = TEXTO) -> int:
    init_question_tables()
    with session_scope() as session:
        manual = Manual(
            code="TST", title="Manual de prueba", source_path="no-existe.pdf", page_count=10,
            extractor_used="docling", ingested_at=datetime.now(timezone.utc), metadata_json={"profile": profile},
        )
        session.add(manual)
        session.flush()
        for i in range(n_nodes):
            node = Node(
                manual_id=manual.id, level=0, level_label="Capítulo", ordinal=str(i + 1),
                title=f"Capítulo {i + 1}", breadcrumb=f"Capítulo {i + 1}", page_start=i + 1, sort_key=f"{i + 1:02d}",
            )
            session.add(node)
            session.flush()
            session.add(Chunk(
                node_id=node.id, manual_id=manual.id, ordinal=0, text=texto,
                char_count=len(texto), page_start=i + 1, page_end=i + 1,
            ))
        return manual.id


@pytest.fixture(autouse=True)
def _sin_gemini(monkeypatch):
    """Importar respuestas nunca llama a Gemini: ni cache, ni ventana, ni verificación."""
    def prohibido(*_, **__):
        raise AssertionError("la importación no debe llamar a Gemini")
    for nombre in ("build_or_get_cache", "generate_window", "verify_exercise"):
        monkeypatch.setattr(pipeline, nombre, prohibido)


def _exportar(manual_id: int, carpeta):
    with session_scope() as session:
        return exportar(session, manual_id=manual_id, carpeta=carpeta)


def _importar(manual_id: int, carpeta):
    with session_scope() as session:
        return importar(session, manual_id=manual_id, carpeta=carpeta)


def _responder(carpeta, nombre: str, preguntas) -> None:
    contenido = preguntas if isinstance(preguntas, str) else json.dumps({"preguntas": preguntas}, ensure_ascii=False)
    (carpeta / "respuestas" / f"{nombre}.json").write_text(contenido, encoding="utf-8")


def _ventanas(carpeta) -> list[str]:
    return sorted(p.stem for p in (carpeta / "ventanas").glob("*.md"))


def _pendientes(manual_id: int) -> list[str]:
    with session_scope() as session:
        return [job.window.key for job in pipeline.plan_windows(session, manual_id=manual_id)]


def _questions() -> list[dict]:
    with session_scope() as session:
        return [
            {
                "tipo": q.question_type, "estado": q.validation_status, "ventana": q.window_key,
                "motivos": (q.metadata_json or {}).get("motivos"),
                "provider": (q.metadata_json or {}).get("provider"),
            }
            for q in session.execute(select(Question).order_by(Question.id)).scalars().all()
        ]


def _runs():
    with session_scope() as session:
        return session.execute(select(GenerationRun).order_by(GenerationRun.id)).scalars().all()


# ─── Exportar ──────────────────────────────────────────────────────────────


def test_la_clave_de_la_ventana_se_vuelve_un_nombre_de_archivo_valido_en_windows():
    assert nombre_de("12:0-3") == "12_0-3"


def test_exportar_deja_la_instruccion_y_un_archivo_por_ventana(tmp_path):
    manual_id = _seed()
    carpeta = tmp_path / "TST"

    exportacion = _exportar(manual_id, carpeta)

    assert exportacion.ventanas == 2
    assert _ventanas(carpeta) == sorted(nombre_de(key) for key in _pendientes(manual_id))
    for archivo in (carpeta / "ventanas").glob("*.md"):
        assert TEXTO in archivo.read_text(encoding="utf-8")
    instruccion = (carpeta / "instruccion.md").read_text(encoding="utf-8")
    assert '"preguntas"' in instruccion and "respuestas/" in instruccion and "cita" in instruccion
    assert list((carpeta / "respuestas").iterdir()) == []


def test_volver_a_exportar_solo_deja_las_pendientes_y_conserva_las_respuestas(tmp_path):
    manual_id = _seed()
    carpeta = tmp_path / "TST"
    _exportar(manual_id, carpeta)
    primera, segunda = _ventanas(carpeta)
    _responder(carpeta, primera, [_item()])
    _importar(manual_id, carpeta)

    exportacion = _exportar(manual_id, carpeta)

    assert exportacion.ventanas == 1
    assert _ventanas(carpeta) == [segunda]
    assert (carpeta / "respuestas" / f"{primera}.json").exists()


# ─── Importar ──────────────────────────────────────────────────────────────


def test_importar_guarda_una_corrida_de_claude_code_sin_tocar_el_contrato(tmp_path):
    manual_id = _seed()
    carpeta = tmp_path / "TST"
    _exportar(manual_id, carpeta)
    for nombre in _ventanas(carpeta):
        _responder(carpeta, nombre, [_item()])

    summary = _importar(manual_id, carpeta)

    assert (summary.windows_total, summary.windows_failed, summary.questions_saved) == (2, 0, 2)
    (run,) = _runs()
    assert (run.model, run.mode, run.status) == (MODEL_CLAUDE_CODE, "immediate", "succeeded")
    assert run.metadata_json["provider"] == "claude-code"
    assert run.cost_estimate_usd == 0.0
    assert [(q["tipo"], q["estado"], q["provider"]) for q in _questions()] == [("teoria", "pending", "claude-code")] * 2
    assert _pendientes(manual_id) == []


def test_solo_se_importan_las_ventanas_con_respuesta_y_las_demas_siguen_pendientes(tmp_path):
    manual_id = _seed()
    carpeta = tmp_path / "TST"
    _exportar(manual_id, carpeta)
    primera, segunda = _ventanas(carpeta)
    _responder(carpeta, primera, [_item()])

    summary = _importar(manual_id, carpeta)

    assert summary.windows_total == 1
    assert [nombre_de(key) for key in _pendientes(manual_id)] == [segunda]


def test_las_respuestas_pasan_por_las_mismas_revisiones(tmp_path):
    manual_id = _seed(1)
    carpeta = tmp_path / "TST"
    _exportar(manual_id, carpeta)
    (nombre,) = _ventanas(carpeta)
    _responder(carpeta, nombre, [
        _item(),
        _item(),  # duplicada
        _item("¿Qué hacen las sociedades?", correcta="negocian en paz", prefijo="N"),  # no literal
        _item("Deriva x^3.", tipo="ejercicio_nuevo", correcta="3x^2", cita=EJEMPLO, prefijo="E"),  # tipo no permitido
        {"tipo": "teoria", "pregunta": "¿Rota?"},  # estructura inválida
    ])

    summary = _importar(manual_id, carpeta)

    assert summary.questions_saved == 2
    literal, no_literal = _questions()
    assert literal["estado"] == "pending"
    assert no_literal["estado"] == "needs_review" and no_literal["motivos"]
    motivos = [d["motivo"] for d in _runs()[0].metadata_json["descartes"]]
    assert "duplicada" in motivos
    assert any("no permitido" in m for m in motivos)
    assert any("estructura inválida" in m for m in motivos)


def test_un_ejercicio_nuevo_entra_a_revisar_por_no_tener_verificacion(tmp_path):
    manual_id = _seed(1, profile="calculo_una_variable", texto=EJEMPLO)
    carpeta = tmp_path / "TST"
    _exportar(manual_id, carpeta)
    (nombre,) = _ventanas(carpeta)
    _responder(carpeta, nombre, [
        _item("Deriva f(x) = x^3.", tipo="ejercicio_nuevo", correcta="3x^2", cita=EJEMPLO, prefijo="E"),
    ])

    _importar(manual_id, carpeta)

    (pregunta,) = _questions()
    assert pregunta["estado"] == "needs_review"
    assert pipeline.SIN_VERIFICACION in pregunta["motivos"]


def test_una_respuesta_ilegible_deja_la_ventana_fallida_y_se_retoma(tmp_path):
    manual_id = _seed(1)
    carpeta = tmp_path / "TST"
    _exportar(manual_id, carpeta)
    (nombre,) = _ventanas(carpeta)
    _responder(carpeta, nombre, "esto no es JSON")

    summary = _importar(manual_id, carpeta)

    assert (summary.windows_failed, summary.questions_saved) == (1, 0)
    (run,) = _runs()
    assert run.status == "partial"
    assert "ilegible" in run.metadata_json["failures"][0]["error"]
    assert [nombre_de(key) for key in _pendientes(manual_id)] == [nombre]


def test_una_respuesta_sin_la_lista_de_preguntas_es_ilegible(tmp_path):
    archivo = tmp_path / "r.json"
    archivo.write_text(json.dumps([_item()]), encoding="utf-8")
    assert "ilegible" in leer_respuesta(archivo).error


def test_sin_respuestas_no_se_crea_ninguna_corrida(tmp_path):
    manual_id = _seed()
    carpeta = tmp_path / "TST"
    _exportar(manual_id, carpeta)

    assert _importar(manual_id, carpeta) is None
    assert _runs() == []


# ─── CLI ───────────────────────────────────────────────────────────────────


def test_el_cli_exporta_e_importa(tmp_path):
    manual_id = _seed(1)
    carpeta = tmp_path / "TST"
    runner = CliRunner()

    salida = runner.invoke(app, ["exportar", str(manual_id), "--carpeta", str(carpeta)])
    assert salida.exit_code == 0, salida.output
    (nombre,) = _ventanas(carpeta)
    _responder(carpeta, nombre, [_item()])

    salida = runner.invoke(app, ["importar", str(manual_id), "--carpeta", str(carpeta)])
    assert salida.exit_code == 0, salida.output
    assert len(_questions()) == 1

"""Orquestación de `qgen-generate` por ventanas (spec §4–§8), con Gemini simulado.

No se prueba la calidad de las preguntas sino lo que rodea a las llamadas: una
llamada por ventana, qué se guarda y con qué estado, qué se descarta, que la
corrida siempre se cierre, que se pueda reanudar y que el costo cuente todo.
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
from qgen.gemini.generate import VerificationOutcome, WindowOutcome
from qgen.models.schema import GenerationRun, Question
from qgen.prompts.schemas import VerificationResult

TEXTO = "La guerra es un conflicto entre sociedades que luchan violentamente."
EJEMPLO = "EJEMPLO 1 Derivar f(x) = x^2. Solución: f'(x) = 2x."


def _item(pregunta="¿Qué es la guerra?", *, tipo="teoria", correcta="un conflicto entre sociedades",
          cita=TEXTO, prefijo="T") -> dict:
    return {
        "tipo": tipo,
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


def _ejercicio_nuevo() -> dict:
    return _item("Deriva f(x) = x^3.", tipo="ejercicio_nuevo", correcta="3x^2", cita=EJEMPLO, prefijo="E")


def _seed(n_nodes: int = 2, *, profile: str = "manual", texto: str = TEXTO) -> int:
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


def _letra(message: str, texto: str) -> str:
    """La letra con que la verificación presenta la opción `texto`."""
    for line in message.splitlines():
        if line[1:3] == ") " and line[3:] == texto:
            return line[0]
    raise AssertionError(f"{texto!r} no está en las opciones de la verificación")


class FakeGemini:
    """Sustituye cache, llamada por ventana y verificación del pipeline."""

    def __init__(self, monkeypatch, *, cache_tokens: int = 0) -> None:
        self.cache_models: list[str] = []
        self.deleted: list[str] = []
        self.messages: list[str] = []
        self.cache_tokens = cache_tokens
        self.window = lambda message: WindowOutcome(items=[_item()], input_tokens=100, output_tokens=50, cached_tokens=80)
        self.verify = lambda message: VerificationOutcome(
            result=VerificationResult(razonamiento="…", opcion=_letra(message, "3x^2"), dificultad="igual"),
        )
        monkeypatch.setattr(pipeline, "build_or_get_cache", self._build_cache)
        monkeypatch.setattr(pipeline, "delete_cache", lambda cache: self.deleted.append(cache.name))
        monkeypatch.setattr(pipeline, "generate_window", self._generate_window)
        monkeypatch.setattr(pipeline, "verify_exercise", lambda *, message, **_: self.verify(message))

    def _generate_window(self, *, message, **_):
        self.messages.append(message)
        return self.window(message)

    def _build_cache(self, *, model, **_):
        self.cache_models.append(model)
        return DocumentCache(
            name="cachedContents/test", model=model, file_name="files/test",
            system_version="test", expire_at_epoch=0.0, token_count=self.cache_tokens,
        )


def _run(manual_id: int, **kwargs):
    with session_scope() as session:
        return pipeline.run_generation(session, manual_id=manual_id, **kwargs)


def _runs():
    with session_scope() as session:
        return session.execute(select(GenerationRun).order_by(GenerationRun.id)).scalars().all()


def _questions() -> list[dict]:
    with session_scope() as session:
        return [
            {
                "tipo": q.question_type, "estado": q.validation_status, "ventana": q.window_key,
                "cita": q.source_quote, "motivos": (q.metadata_json or {}).get("motivos"),
            }
            for q in session.execute(select(Question).order_by(Question.id)).scalars().all()
        ]


# ─── Una llamada por ventana ───────────────────────────────────────────────


def test_una_llamada_por_ventana_y_sus_preguntas_se_guardan(monkeypatch):
    manual_id = _seed()
    fake = FakeGemini(monkeypatch)

    summary = _run(manual_id)

    assert len(fake.messages) == 2
    assert (summary.windows_total, summary.windows_failed, summary.questions_saved) == (2, 0, 2)
    [run] = _runs()
    assert run.status == "succeeded"
    assert (run.nodes_total, run.nodes_completed, run.nodes_failed) == (2, 2, 0)
    assert sorted(run.metadata_json["ventanas"].values()) == ["ok", "ok"]
    assert run.metadata_json["preguntas"] == {"teoria/pending": 2}
    preguntas = _questions()
    assert [(q["tipo"], q["estado"], q["cita"]) for q in preguntas] == [("teoria", "pending", TEXTO)] * 2
    assert {q["ventana"] for q in preguntas} == set(run.metadata_json["ventanas"])
    assert fake.deleted == ["cachedContents/test"]


def test_el_mensaje_lleva_el_titulo_del_manual_la_ruta_y_el_texto(monkeypatch):
    manual_id = _seed(n_nodes=1)
    fake = FakeGemini(monkeypatch)

    _run(manual_id)

    [message] = fake.messages
    assert "Manual de prueba" in message and "Capítulo 1" in message and TEXTO in message


# ─── Descartes y revisión ──────────────────────────────────────────────────


def test_una_pregunta_mal_formada_no_tumba_la_ventana(monkeypatch):
    manual_id = _seed(n_nodes=1)
    fake = FakeGemini(monkeypatch)
    fake.window = lambda message: WindowOutcome(items=[_item(), {"tipo": "teoria"}])

    _run(manual_id)

    [run] = _runs()
    assert run.status == "succeeded"
    assert len(_questions()) == 1
    assert run.metadata_json["descartes"][0]["motivo"].startswith("pregunta 2: estructura inválida")


def test_un_tipo_que_el_perfil_no_permite_se_descarta(monkeypatch):
    manual_id = _seed(n_nodes=1, profile="manual")  # militar: solo teoría
    fake = FakeGemini(monkeypatch)
    fake.window = lambda message: WindowOutcome(items=[_item(), _ejercicio_nuevo()])

    _run(manual_id)

    assert [q["tipo"] for q in _questions()] == ["teoria"]
    [run] = _runs()
    assert run.metadata_json["descartes"][0]["motivo"] == "tipo ejercicio_nuevo no permitido en manual"


def test_una_respuesta_parafraseada_queda_en_revision_con_su_motivo(monkeypatch):
    manual_id = _seed(n_nodes=1)
    fake = FakeGemini(monkeypatch)
    fake.window = lambda message: WindowOutcome(items=[_item(correcta="una pelea violenta")])

    _run(manual_id)

    [q] = _questions()
    assert (q["estado"], q["motivos"]) == ("needs_review", ["respuesta parafraseada"])


def test_las_duplicadas_se_descartan(monkeypatch):
    manual_id = _seed(n_nodes=1)
    fake = FakeGemini(monkeypatch)
    fake.window = lambda message: WindowOutcome(items=[_item(), _item(prefijo="U")])

    _run(manual_id)

    [q] = _questions()
    [run] = _runs()
    assert run.metadata_json["descartes"] == [{"window_key": q["ventana"], "motivo": "duplicada"}]


# ─── Ejercicios nuevos ─────────────────────────────────────────────────────


def test_el_ejercicio_nuevo_verificado_queda_pendiente(monkeypatch):
    manual_id = _seed(n_nodes=1, profile="calculo_una_variable", texto=EJEMPLO)
    fake = FakeGemini(monkeypatch)
    fake.window = lambda message: WindowOutcome(items=[_ejercicio_nuevo()])

    _run(manual_id)

    [q] = _questions()
    assert (q["tipo"], q["estado"]) == ("ejercicio_nuevo", "pending")


@pytest.mark.parametrize("opcion, dificultad, motivo", [
    ("otra", "igual", "la verificación eligió"),
    ("ninguna", "igual", "ninguna"),
    ("clave", "mayor", "supera la dificultad del PDF"),
])
def test_la_verificacion_manda_a_revision(monkeypatch, opcion, dificultad, motivo):
    manual_id = _seed(n_nodes=1, profile="calculo_una_variable", texto=EJEMPLO)
    fake = FakeGemini(monkeypatch)
    fake.window = lambda message: WindowOutcome(items=[_ejercicio_nuevo()])

    def verify(message):
        clave = _letra(message, "3x^2")
        elegida = {"clave": clave, "otra": "A" if clave != "A" else "B"}.get(opcion, opcion)
        return VerificationOutcome(result=VerificationResult(razonamiento="…", opcion=elegida, dificultad=dificultad))

    fake.verify = verify

    _run(manual_id)

    [q] = _questions()
    assert q["estado"] == "needs_review"
    assert any(motivo in m for m in q["motivos"])


def test_si_la_verificacion_falla_la_pregunta_queda_en_revision(monkeypatch):
    manual_id = _seed(n_nodes=1, profile="calculo_una_variable", texto=EJEMPLO)
    fake = FakeGemini(monkeypatch)
    fake.window = lambda message: WindowOutcome(items=[_ejercicio_nuevo()])
    fake.verify = lambda message: VerificationOutcome(result=None, error="RuntimeError: 500 INTERNAL")

    _run(manual_id)

    [q] = _questions()
    assert (q["estado"], q["motivos"]) == ("needs_review", ["verificación fallida"])


# ─── Reanudar ──────────────────────────────────────────────────────────────


def test_una_ventana_fallida_se_retoma_en_la_siguiente_corrida(monkeypatch):
    manual_id = _seed(n_nodes=1)
    fake = FakeGemini(monkeypatch)
    fake.window = lambda message: WindowOutcome(items=[], error="respuesta ilegible: JSONDecodeError", input_tokens=10)

    _run(manual_id)

    [primera] = _runs()
    assert primera.status == "partial"
    assert (primera.nodes_completed, primera.nodes_failed) == (0, 1)
    assert list(primera.metadata_json["ventanas"].values()) == ["fallida"]
    assert primera.metadata_json["failures"][0]["error"].startswith("respuesta ilegible")

    fake.window = lambda message: WindowOutcome(items=[_item()])
    _run(manual_id)

    assert len(fake.messages) == 2
    assert _runs()[1].status == "succeeded"
    assert len(_questions()) == 1


def test_las_ventanas_ya_hechas_no_se_repiten(monkeypatch):
    manual_id = _seed(n_nodes=1)
    fake = FakeGemini(monkeypatch)

    _run(manual_id)
    segunda = _run(manual_id)

    assert len(fake.messages) == 1
    assert (segunda.nodes_total, segunda.windows_total) == (0, 0)
    assert len(_questions()) == 1


def test_regenerate_rehace_las_ventanas(monkeypatch):
    manual_id = _seed(n_nodes=1)
    fake = FakeGemini(monkeypatch)

    _run(manual_id)
    _run(manual_id, regenerate=True)

    assert len(fake.messages) == 2
    assert len(_questions()) == 1  # la primera se borró antes de rehacer la ventana


# ─── La corrida siempre se cierra ──────────────────────────────────────────


def test_un_error_inesperado_marca_la_corrida_failed_y_borra_el_cache(monkeypatch):
    manual_id = _seed()
    fake = FakeGemini(monkeypatch)

    def boom(message):
        raise RuntimeError("se cayó a medias")

    fake.window = boom

    with pytest.raises(RuntimeError, match="se cayó a medias"):
        _run(manual_id)

    [run] = _runs()
    assert run.status == "failed"
    assert run.completed_at is not None
    assert fake.deleted == ["cachedContents/test"]


def test_ctrl_c_marca_la_corrida_cancelled_y_conserva_lo_guardado(monkeypatch):
    manual_id = _seed(n_nodes=1)
    fake = FakeGemini(monkeypatch)

    def interrupt(*_):
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        _run(manual_id, progress_cb=interrupt)

    [run] = _runs()
    assert run.status == "cancelled"
    assert run.nodes_completed == 1
    # Se guarda antes de avisar al callback: lo ya pagado no se pierde.
    assert len(_questions()) == 1
    assert fake.deleted == ["cachedContents/test"]


def test_el_callback_del_cli_acepta_ventanas_buenas_y_fallidas(monkeypatch):
    manual_id = _seed()
    fake = FakeGemini(monkeypatch)
    # `list.pop` es atómico: las dos ventanas se piden desde dos hilos.
    respuestas = [WindowOutcome(items=[_item()]), WindowOutcome(items=[], error="respuesta ilegible")]
    fake.window = lambda message: respuestas.pop(0)

    summary = _run(manual_id, progress_cb=_progress_cb)

    assert (summary.windows_total, summary.windows_failed) == (2, 1)


# ─── Modelo ────────────────────────────────────────────────────────────────


def test_el_alias_del_modelo_se_resuelve_antes_de_llamar(monkeypatch):
    manual_id = _seed(n_nodes=1)
    fake = FakeGemini(monkeypatch)

    summary = _run(manual_id, model_name="pro")

    assert summary.model == MODEL_PRO
    assert fake.cache_models == [MODEL_PRO]
    assert summary.actual_cost_usd > 0


def test_un_modelo_desconocido_se_rechaza_antes_de_crear_la_corrida(monkeypatch):
    manual_id = _seed(n_nodes=1)
    FakeGemini(monkeypatch)

    with pytest.raises(ValueError, match="Unknown model"):
        _run(manual_id, model_name="deepseek-r1:8b")

    assert _runs() == []


# ─── Costo ─────────────────────────────────────────────────────────────────


def test_el_costo_cuenta_la_ventana_la_verificacion_y_el_cache(monkeypatch):
    manual_id = _seed(n_nodes=1, profile="calculo_una_variable", texto=EJEMPLO)
    fake = FakeGemini(monkeypatch, cache_tokens=1_000)
    fake.window = lambda message: WindowOutcome(items=[_ejercicio_nuevo()], input_tokens=100, output_tokens=50, cached_tokens=80)
    fake.verify = lambda message: VerificationOutcome(
        result=VerificationResult(razonamiento="…", opcion=_letra(message, "3x^2"), dificultad="igual"),
        input_tokens=30, output_tokens=20,
    )

    summary = _run(manual_id)

    [run] = _runs()
    assert (run.cost_input_tokens, run.cost_output_tokens, run.cost_cached_tokens) == (130, 70, 80)
    assert run.metadata_json["cache_tokens"] == 1_000
    sin_cache = actual_cost_usd(model=MODEL_FLASH, mode="immediate", input_tokens=130, output_tokens=70, cached_tokens=80)
    assert summary.actual_cost_usd > sin_cache


# ─── Dry-run ───────────────────────────────────────────────────────────────


def _estimate(manual_id: int):
    with session_scope() as session:
        return pipeline.estimate_only(
            session, manual_id=manual_id, model_name="flash", mode="immediate",
            limit=None, only_node_id=None, regenerate=False,
        )


def test_el_dry_run_estima_por_ventanas():
    manual_id = _seed(n_nodes=3)

    estimate, n_windows = _estimate(manual_id)

    assert n_windows == 3 and estimate.windows == 3
    assert estimate.model == MODEL_FLASH
    assert estimate.verifications == 0  # manual militar: sin ejercicios
    assert estimate.cache_tokens > 0 and estimate.total_usd > 0


def test_el_dry_run_sin_nada_que_generar_no_cuesta(monkeypatch):
    manual_id = _seed(n_nodes=1)
    FakeGemini(monkeypatch)
    _run(manual_id)

    estimate, n_windows = _estimate(manual_id)

    assert n_windows == 0 and estimate.total_usd == 0


# ─── Arreglos de la revisión final ─────────────────────────────────────────


def test_un_regenerate_que_falla_no_pierde_la_ventana(monkeypatch):
    manual_id = _seed(n_nodes=1)
    fake = FakeGemini(monkeypatch)
    _run(manual_id)

    fake.window = lambda message: WindowOutcome(items=[], error="respuesta ilegible")
    _run(manual_id, regenerate=True)
    assert _questions() == []

    fake.window = lambda message: WindowOutcome(items=[_item()])
    _run(manual_id)

    assert len(fake.messages) == 3
    assert len(_questions()) == 1


def test_un_regenerate_cortado_retoma_las_ventanas_que_faltan(monkeypatch):
    manual_id = _seed(n_nodes=3)
    FakeGemini(monkeypatch)
    _run(manual_id)

    def interrupt(*_):
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        _run(manual_id, regenerate=True, progress_cb=interrupt)
    _run(manual_id)

    assert len(_questions()) == 3


def test_lo_generado_se_exporta_como_bundle_v2_valido(monkeypatch):
    from qgen.bundle.build import build_bundle
    from qgen.bundle.spec import validate

    manual_id = _seed(n_nodes=2)
    fake = FakeGemini(monkeypatch)
    fake.window = lambda message: WindowOutcome(items=[
        _item(), _item("¿Cómo luchan las sociedades?", correcta="luchan violentamente", prefijo="V"),
    ])

    _run(manual_id)
    with session_scope() as session:
        bundle = build_bundle(session, manual_id=manual_id)

    report = validate(bundle)
    assert report.ok, report.errors
    assert report.counts["questions"] == 4  # dos por nodo: el contrato v1 lo habría rechazado
    assert {q["question_type"] for q in bundle["questions"]} == {"teoria"}

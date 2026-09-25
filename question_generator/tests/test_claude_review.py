"""Revisión de calidad desde Claude Code: exportar lotes, calificar, importar veredictos.

Se prueba el intercambio de archivos y cómo se aplican los veredictos: qué
estado queda, qué se registra y qué no se toca (lo que ya decidió una persona).
"""

import json
from datetime import datetime, timezone

from etl.db.session import session_scope
from etl.models.schema import Chunk, Manual, Node
from sqlalchemy import select
from typer.testing import CliRunner

from qgen.claude_code import MODEL_CLAUDE_CODE, exportar, importar
from qgen.claude_review import exportar_revision, importar_revision
from qgen.cli.claude_code import app
from qgen.db.migration import init_question_tables
from qgen.models.schema import Question

TEXTO = "La guerra es un conflicto entre sociedades que luchan violentamente."


def _item(pregunta: str, correcta: str = "un conflicto entre sociedades", prefijo: str = "T") -> dict:
    return {
        "tipo": "teoria",
        "nivel": "conocimiento",
        "pregunta": pregunta,
        "opciones": [
            {"rol": "correct", "texto": correcta},
            {"rol": "confusa", "texto": f"{prefijo} confusa"},
            {"rol": "distractor", "texto": f"{prefijo} distractor 1"},
            {"rol": "distractor", "texto": f"{prefijo} distractor 2"},
        ],
        "cita": TEXTO,
        "justificacion": "Lo dice el texto.",
    }


def _seed(code: str = "TST") -> int:
    """Un manual de un nodo con una ventana (perfil civil de solo teoría)."""
    init_question_tables()
    with session_scope() as session:
        manual = Manual(
            code=code, title=f"Manual {code}", source_path="no-existe.pdf", page_count=10,
            extractor_used="docling", ingested_at=datetime.now(timezone.utc),
            metadata_json={"profile": "historia_universal"},
        )
        session.add(manual)
        session.flush()
        node = Node(
            manual_id=manual.id, level=0, level_label="Capítulo", ordinal="1",
            title="Capítulo 1", breadcrumb="Bloque 1 › Capítulo 1", page_start=1, sort_key="01",
        )
        session.add(node)
        session.flush()
        session.add(Chunk(
            node_id=node.id, manual_id=manual.id, ordinal=0, text=TEXTO,
            char_count=len(TEXTO), page_start=1, page_end=1,
        ))
        manual_id = manual.id
    return manual_id


def _generar(manual_id: int, carpeta, n: int = 3) -> list[int]:
    with session_scope() as session:
        exportar(session, manual_id=manual_id, carpeta=carpeta)
    (ventana,) = [p.stem for p in (carpeta / "ventanas").glob("*.md")]
    distintas = [
        ("¿Qué es la guerra?", "un conflicto entre sociedades"),
        ("¿Cómo luchan las sociedades en guerra?", "violentamente"),
        ("¿Entre quiénes ocurre el conflicto armado?", "entre sociedades"),
    ]
    preguntas = [_item(p, c, prefijo=f"P{i}") for i, (p, c) in enumerate(distintas[:n])]
    (carpeta / "respuestas" / f"{ventana}.json").write_text(json.dumps({"preguntas": preguntas}), encoding="utf-8")
    with session_scope() as session:
        importar(session, manual_id=manual_id, carpeta=carpeta)
        return list(session.execute(
            select(Question.id).where(Question.manual_id == manual_id).order_by(Question.id)
        ).scalars())


def _exportar_revision(manual_id: int, carpeta):
    with session_scope() as session:
        return exportar_revision(session, manual_id=manual_id, carpeta=carpeta)


def _importar_revision(manual_id: int, carpeta):
    with session_scope() as session:
        return importar_revision(session, manual_id=manual_id, carpeta=carpeta)


def _veredictos(carpeta, nombre: str, veredictos) -> None:
    contenido = veredictos if isinstance(veredictos, str) else json.dumps({"veredictos": veredictos}, ensure_ascii=False)
    destino = carpeta / "revision" / "veredictos"
    destino.mkdir(parents=True, exist_ok=True)
    (destino / f"{nombre}.json").write_text(contenido, encoding="utf-8")


def _lotes(carpeta) -> list[str]:
    return sorted(p.stem for p in (carpeta / "revision" / "lotes").glob("*.md"))


def _estado(qid: int) -> tuple[str, dict]:
    with session_scope() as session:
        q = session.get(Question, qid)
        return q.validation_status, dict(q.metadata_json or {})


def _marcar(qid: int, estado: str) -> None:
    with session_scope() as session:
        session.get(Question, qid).validation_status = estado


# ─── Exportar ──────────────────────────────────────────────────────────────


def test_exportar_revision_deja_la_rubrica_y_un_lote_por_ventana(tmp_path):
    manual_id = _seed()
    carpeta = tmp_path / "TST"
    ids = _generar(manual_id, carpeta)

    exportacion = _exportar_revision(manual_id, carpeta)

    assert (exportacion.lotes, exportacion.preguntas) == (1, 3)
    (lote,) = _lotes(carpeta)
    contenido = (carpeta / "revision" / "lotes" / f"{lote}.md").read_text(encoding="utf-8")
    assert TEXTO in contenido and "Bloque 1 › Capítulo 1" in contenido
    for qid in ids:
        assert f"Pregunta {qid}" in contenido
    assert "[correct] un conflicto entre sociedades" in contenido
    rubrica = (carpeta / "revision" / "instruccion.md").read_text(encoding="utf-8")
    assert "rechazar" in rubrica and "dudosa" in rubrica and "fuera de tema" in rubrica.lower()
    assert "Guerra Fría" in rubrica  # temas del perfil, para juzgar si está fuera de tema


def test_solo_se_exportan_las_preguntas_sin_decidir_y_sin_revision_previa(tmp_path):
    manual_id = _seed()
    carpeta = tmp_path / "TST"
    aprobada, rechazada, libre = _generar(manual_id, carpeta)
    _marcar(aprobada, "valid")
    _marcar(rechazada, "rejected")

    exportacion = _exportar_revision(manual_id, carpeta)
    assert exportacion.preguntas == 1

    _veredictos(carpeta, _lotes(carpeta)[0], [
        {"id": libre, "nivel": "conocimiento", "veredicto": "dudosa", "calificacion": 3, "motivos": ["no se puede decidir con el texto"]},
    ])
    _importar_revision(manual_id, carpeta)
    assert _exportar_revision(manual_id, carpeta).preguntas == 0


# ─── Importar ──────────────────────────────────────────────────────────────


def test_cada_veredicto_deja_su_estado_y_queda_registrado(tmp_path):
    manual_id = _seed()
    carpeta = tmp_path / "TST"
    aceptada, rechazada, dudosa = _generar(manual_id, carpeta)
    _exportar_revision(manual_id, carpeta)
    _veredictos(carpeta, _lotes(carpeta)[0], [
        {"id": aceptada, "nivel": "conocimiento", "veredicto": "aceptar", "calificacion": 5, "motivos": []},
        {"id": rechazada, "nivel": "conocimiento", "veredicto": "rechazar", "calificacion": 1, "motivos": ["fuera de tema"]},
        {"id": dudosa, "nivel": "conocimiento", "veredicto": "dudosa", "calificacion": 3, "motivos": ["depende de otra ventana"]},
    ])

    resumen = _importar_revision(manual_id, carpeta)

    assert (resumen.aceptadas, resumen.rechazadas, resumen.dudosas) == (1, 1, 1)
    estado, meta = _estado(aceptada)
    assert estado == "valid"
    assert meta["revision"] == {
        "por": MODEL_CLAUDE_CODE, "veredicto": "aceptar", "calificacion": 5, "motivos": [],
        "nivel": "conocimiento", "fecha": meta["revision"]["fecha"],
    }
    estado, meta = _estado(rechazada)
    assert estado == "rejected" and meta["revision"]["motivos"] == ["fuera de tema"]
    assert not meta.get("motivos")  # los de la revisión automática quedan aparte
    estado, meta = _estado(dudosa)
    assert estado == "needs_review" and meta["revision"]["motivos"] == ["depende de otra ventana"]
    with session_scope() as session:
        assert all(session.get(Question, qid).validated_at for qid in (aceptada, rechazada, dudosa))


def test_no_se_tocan_las_preguntas_que_ya_decidio_una_persona_ni_las_de_otro_manual(tmp_path):
    manual_id = _seed()
    carpeta = tmp_path / "TST"
    aprobada, libre, _ = _generar(manual_id, carpeta)
    otro_manual = _seed("OTRO")
    (ajena, *_) = _generar(otro_manual, tmp_path / "OTRO")
    _exportar_revision(manual_id, carpeta)
    _marcar(aprobada, "valid")
    _veredictos(carpeta, _lotes(carpeta)[0], [
        {"id": aprobada, "nivel": "conocimiento", "veredicto": "rechazar", "calificacion": 1, "motivos": ["x"]},
        {"id": ajena, "nivel": "conocimiento", "veredicto": "rechazar", "calificacion": 1, "motivos": ["x"]},
        {"id": 99999, "nivel": "conocimiento", "veredicto": "rechazar", "calificacion": 1, "motivos": ["x"]},
        {"id": libre, "nivel": "conocimiento", "veredicto": "aceptar", "calificacion": 4, "motivos": []},
    ])

    resumen = _importar_revision(manual_id, carpeta)

    assert resumen.aceptadas == 1 and resumen.rechazadas == 0
    assert sorted(qid for qid, _ in resumen.omitidas) == sorted([aprobada, ajena, 99999])
    assert _estado(aprobada)[0] == "valid"
    assert _estado(ajena)[0] == "pending"


def test_un_lote_invalido_no_aplica_nada_y_se_reporta(tmp_path):
    manual_id = _seed()
    carpeta = tmp_path / "TST"
    primera, segunda, _ = _generar(manual_id, carpeta)
    _exportar_revision(manual_id, carpeta)
    _veredictos(carpeta, "roto", "esto no es JSON")
    _veredictos(carpeta, "sin_motivos", [
        {"id": primera, "nivel": "conocimiento", "veredicto": "aceptar", "calificacion": 5, "motivos": []},
        {"id": segunda, "nivel": "conocimiento", "veredicto": "rechazar", "calificacion": 1, "motivos": []},  # rechazar exige motivos
    ])

    resumen = _importar_revision(manual_id, carpeta)

    assert sorted(nombre for nombre, _ in resumen.lotes_invalidos) == ["roto", "sin_motivos"]
    assert _estado(primera)[0] == "pending"
    assert _estado(segunda)[0] == "pending"


# ─── CLI ───────────────────────────────────────────────────────────────────


def test_el_cli_exporta_e_importa_la_revision(tmp_path):
    manual_id = _seed()
    carpeta = tmp_path / "TST"
    (primera, *_) = _generar(manual_id, carpeta)
    runner = CliRunner()

    salida = runner.invoke(app, ["exportar-revision", str(manual_id), "--carpeta", str(carpeta)])
    assert salida.exit_code == 0, salida.output
    _veredictos(carpeta, _lotes(carpeta)[0], [{"id": primera, "nivel": "conocimiento", "veredicto": "aceptar", "calificacion": 5, "motivos": []}])

    salida = runner.invoke(app, ["importar-revision", str(manual_id), "--carpeta", str(carpeta)])
    assert salida.exit_code == 0, salida.output
    assert _estado(primera)[0] == "valid"


def _sin_nivel(qid: int) -> None:
    with session_scope() as session:
        session.get(Question, qid).cognitive_level = None


def _nivel(qid: int) -> str | None:
    with session_scope() as session:
        return session.get(Question, qid).cognitive_level


def test_la_rubrica_trae_los_niveles_y_sus_criterios(tmp_path):
    manual_id = _seed()
    carpeta = tmp_path / "TST"
    _generar(manual_id, carpeta)
    _exportar_revision(manual_id, carpeta)
    rubrica = (carpeta / "revision" / "instruccion.md").read_text(encoding="utf-8")
    for marca in ("CONCLUSIÓN INFERIDA", "Paráfrasis infiel", "lógicamente innegable",
                  "no se resuelve con la regla citada", "solo clasificar"):
        assert marca in rubrica
    (lote,) = _lotes(carpeta)
    assert "nivel declarado: conocimiento" in (carpeta / "revision" / "lotes" / f"{lote}.md").read_text(encoding="utf-8")


def test_si_el_nivel_revisado_difiere_la_pregunta_se_reclasifica(tmp_path):
    manual_id = _seed()
    carpeta = tmp_path / "TST"
    primera, *_ = _generar(manual_id, carpeta)
    _exportar_revision(manual_id, carpeta)
    _veredictos(carpeta, _lotes(carpeta)[0], [
        {"id": primera, "nivel": "analisis", "veredicto": "aceptar", "calificacion": 4, "motivos": []},
    ])

    resumen = _importar_revision(manual_id, carpeta)

    estado, meta = _estado(primera)
    assert (estado, _nivel(primera), meta["nivel_generado"], meta["revision"]["nivel"]) == (
        "valid", "analisis", "conocimiento", "analisis",
    )
    assert resumen.reclasificadas == 1


def test_las_decididas_sin_nivel_solo_se_clasifican_sin_tocar_su_estado(tmp_path):
    manual_id = _seed()
    carpeta = tmp_path / "TST"
    aprobada, _, _ = _generar(manual_id, carpeta)
    _marcar(aprobada, "valid")
    _sin_nivel(aprobada)

    exportacion = _exportar_revision(manual_id, carpeta)
    contenido = (carpeta / "revision" / "lotes" / f"{_lotes(carpeta)[0]}.md").read_text(encoding="utf-8")
    assert exportacion.solo_clasificar == 1 and "SOLO CLASIFICAR" in contenido

    _veredictos(carpeta, _lotes(carpeta)[0], [
        {"id": aprobada, "nivel": "comprension", "veredicto": "rechazar", "calificacion": 1, "motivos": ["x"]},
    ])
    resumen = _importar_revision(manual_id, carpeta)

    estado, meta = _estado(aprobada)
    assert (estado, _nivel(aprobada), meta["clasificacion"]["nivel"]) == ("valid", "comprension", "comprension")
    assert resumen.solo_clasificadas == 1 and resumen.rechazadas == 0
    assert (aprobada, "ya decidida (valid): solo se clasificó") in resumen.omitidas


def test_una_sin_decidir_sin_veredicto_se_omite(tmp_path):
    manual_id = _seed()
    carpeta = tmp_path / "TST"
    primera, *_ = _generar(manual_id, carpeta)
    _exportar_revision(manual_id, carpeta)
    _veredictos(carpeta, _lotes(carpeta)[0], [{"id": primera, "nivel": "conocimiento"}])

    resumen = _importar_revision(manual_id, carpeta)

    assert (primera, "falta el veredicto") in resumen.omitidas
    assert _estado(primera)[0] == "pending"


def test_un_lote_de_la_ronda_anterior_sin_nivel_no_aplica_nada(tmp_path):
    manual_id = _seed()
    carpeta = tmp_path / "TST"
    primera, *_ = _generar(manual_id, carpeta)
    _exportar_revision(manual_id, carpeta)
    _veredictos(carpeta, "viejo", [{"id": primera, "veredicto": "aceptar", "calificacion": 5, "motivos": []}])

    resumen = _importar_revision(manual_id, carpeta)

    assert [nombre for nombre, _ in resumen.lotes_invalidos] == ["viejo"]
    assert _estado(primera)[0] == "pending"

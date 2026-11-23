"""Corrección de preguntas desde Claude Code con las observaciones del usuario.

Se prueba el intercambio de archivos y cómo se aplican las decisiones: qué texto queda, qué
se guarda de la versión original y qué no se toca (lo que ya decidió una persona).
"""

import json

from etl.db.session import session_scope
from sqlalchemy import select
from typer.testing import CliRunner

from qgen.claude_correccion import exportar_correccion, importar_correccion
from qgen.cli.claude_code import app
from qgen.models.schema import Question
from tests.test_claude_review import _generar, _seed

EJEMPLO = {
    "nivel": "conocimiento", "articulo": "Artículo 222",
    "antes": {"pregunta": "¿De qué no serán responsables los rebeldes?", "opciones": ["de las muertes en combate", "b", "c", "d"]},
    "observacion_pregunta": "Evitar enunciados en negativo.",
    "observacion_opciones": "Cambiar los «ni» por «y».",
    "despues": {"pregunta": "¿De qué actos quedan exentos los rebeldes?", "opciones": ["De las muertes en combate.", "B.", "C.", "D."]},
}


def _exportar(manual_id, carpeta, **kw):
    with session_scope() as session:
        return exportar_correccion(session, manual_id=manual_id, carpeta=carpeta, **kw)


def _importar(manual_id, carpeta, **kw):
    with session_scope() as session:
        return importar_correccion(session, manual_id=manual_id, carpeta=carpeta, **kw)


def _escribir(carpeta, decisiones) -> None:
    (lote,) = [p.stem for p in (carpeta / "correccion" / "lotes").glob("*.md")]
    (carpeta / "correccion" / "decisiones" / f"{lote}.json").write_text(
        json.dumps({"decisiones": decisiones}, ensure_ascii=False), encoding="utf-8")


def _pregunta(qid):
    with session_scope() as session:
        q = session.get(Question, qid)
        return {
            "texto": q.question_text, "estado": q.validation_status, "nivel": q.cognitive_level,
            "opciones": sorted((o.role, o.text) for o in q.options), "meta": dict(q.metadata_json or {}),
        }


def test_exportar_deja_reglas_ejemplos_y_un_lote_por_ventana(tmp_path):
    manual_id = _seed()
    ids = _generar(manual_id, tmp_path)

    exp = _exportar(manual_id, tmp_path, ejemplos=[EJEMPLO])

    assert (exp.lotes, exp.preguntas, exp.ejemplos) == (1, len(ids), 1)
    instruccion = (tmp_path / "correccion" / "instruccion.md").read_text(encoding="utf-8")
    assert "todas y cada una" in instruccion and "Paralelismo absoluto" in instruccion
    assert "OBSERVACIÓN AL ENUNCIADO: Evitar enunciados en negativo." in instruccion
    assert "¿De qué actos quedan exentos los rebeldes?" in instruccion
    (lote,) = (tmp_path / "correccion" / "lotes").glob("*.md")
    texto = lote.read_text(encoding="utf-8")
    assert all(f"## Pregunta {i} " in texto for i in ids) and "TEXTO:" in texto


def test_corregir_cambia_el_texto_y_guarda_la_version_original(tmp_path):
    manual_id = _seed()
    a, b, c = _generar(manual_id, tmp_path)
    antes = _pregunta(a)
    _exportar(manual_id, tmp_path)
    _escribir(tmp_path, [
        {"id": a, "accion": "corregir", "nivel": "comprension", "pregunta": "¿Cómo se describe la guerra?",
         "opciones": {"correct": "Un conflicto entre sociedades.", "confusa": "Un acuerdo entre sociedades.",
                      "distractores": ["Una tregua.", "Un armisticio."]},
         "motivos": ["regla 12: sin punto final"]},
        {"id": b, "accion": "sin_cambios"},
        {"id": c, "accion": "descartar", "motivos": ["repetida con la primera"]},
    ])

    r = _importar(manual_id, tmp_path, model_name="claude-opus-5-5")

    assert (r.corregidas, r.sin_cambios, r.descartadas, r.reclasificadas) == (1, 1, 1, 1)
    despues = _pregunta(a)
    assert despues["texto"] == "¿Cómo se describe la guerra?" and despues["nivel"] == "comprension"
    assert ("correct", "Un conflicto entre sociedades.") in despues["opciones"]
    assert despues["meta"]["original"]["pregunta"] == antes["texto"]
    assert despues["meta"]["correccion"]["por"] == "claude-opus-5-5"
    assert despues["meta"]["nivel_generado"] == "conocimiento"
    assert _pregunta(b)["meta"]["correccion"]["accion"] == "sin_cambios"
    assert _pregunta(c)["estado"] == "rejected"


def test_no_se_corrige_dos_veces_ni_lo_que_decidio_una_persona(tmp_path):
    manual_id = _seed()
    a, b, _ = _generar(manual_id, tmp_path)
    with session_scope() as session:
        session.get(Question, b).validation_status = "valid"
    _exportar(manual_id, tmp_path)
    _escribir(tmp_path, [{"id": a, "accion": "sin_cambios"}, {"id": b, "accion": "sin_cambios"}])
    r = _importar(manual_id, tmp_path)
    assert r.sin_cambios == 1 and (b, "ya decidida (valid)") in r.omitidas

    exp = _exportar(manual_id, tmp_path)
    assert exp.preguntas == 1  # solo la que falta: ni la corregida ni la decidida
    r = _importar(manual_id, tmp_path)
    assert (a, "ya corregida") in r.omitidas


def test_un_lote_invalido_no_aplica_nada(tmp_path):
    manual_id = _seed()
    a, *_ = _generar(manual_id, tmp_path)
    _exportar(manual_id, tmp_path)
    _escribir(tmp_path, [{"id": a, "accion": "corregir", "pregunta": "¿Otra?"}])  # sin motivos

    r = _importar(manual_id, tmp_path)

    assert r.corregidas == 0 and r.lotes_invalidos
    assert "correccion" not in _pregunta(a)["meta"]


def test_los_comandos_exportan_e_importan(tmp_path):
    manual_id = _seed()
    ids = _generar(manual_id, tmp_path)
    ejemplos = tmp_path / "ejemplos.json"
    ejemplos.write_text(json.dumps({"ejemplos": [EJEMPLO]}), encoding="utf-8")
    salida = CliRunner().invoke(app, ["exportar-correccion", str(manual_id), "--carpeta", str(tmp_path), "--ejemplos", str(ejemplos)])
    assert salida.exit_code == 0 and f"{len(ids)} preguntas en 1 lotes (1 ejemplos)" in salida.output
    _escribir(tmp_path, [{"id": i, "accion": "sin_cambios"} for i in ids])
    salida = CliRunner().invoke(app, ["importar-correccion", str(manual_id), "--carpeta", str(tmp_path)])
    assert salida.exit_code == 0 and f"{len(ids)} sin cambios" in salida.output

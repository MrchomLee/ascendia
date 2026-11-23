"""Pruebas unitarias para la importación y consulta de preguntas de referencia (importer.py y repository.py)."""

import json

import openpyxl
import pytest
from etl.db.init_db import init_db
from etl.db.session import session_scope
from qgen.db.migration import init_question_tables
from qgen.models.reference_schema import ReferenceQuestion
from qgen.reference.importer import import_reference_questions, limpiar_ejemplo, load_reference_file
from qgen.reference.repository import get_level_exemplars, get_reference_exemplars


def test_import_reference_questions_json(tmp_path):
    """Verifica la carga e importación de preguntas desde un archivo JSON."""
    init_db()
    init_question_tables()

    sample_data = [
        {
            "question": "¿Cuál es la ley de los signos para la multiplicación?",
            "profile": "algebra_baldor",
            "topic": "leyes de signos",
            "justification": "Signos iguales dan positivo, signos diferentes dan negativo.",
            "options": [
                {"text": "Signos iguales dan positivo (+)", "role": "correct"},
                {"text": "Signos iguales dan negativo (-)", "role": "confusa"},
                {"text": "El resultado siempre es cero", "role": "distractor"},
                {"text": "Depende de la suma de los valores", "role": "distractor"},
            ],
        }
    ]

    json_file = tmp_path / "sample.json"
    json_file.write_text(json.dumps(sample_data), encoding="utf-8")

    loaded_data = load_reference_file(json_file)
    assert len(loaded_data) == 1

    with session_scope() as session:
        created = import_reference_questions(session, loaded_data, default_profile="algebra_baldor")
        assert len(created) == 1
        ref_q = created[0]
        assert ref_q.profile == "algebra_baldor"
        assert len(ref_q.options) == 4
        assert any(o.role == "correct" for o in ref_q.options)

        exemplars = get_reference_exemplars(session, profile="algebra_baldor", limit=5)
        assert len(exemplars) >= 1
        ex = exemplars[0]
        assert ex["question_text"] == "¿Cuál es la ley de los signos para la multiplicación?"
        assert len(ex["options"]) == 4


def _xlsx(tmp_path, hojas: dict[str, list[list]]):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    for nombre, filas in hojas.items():
        ws = wb.create_sheet(nombre)
        for fila in filas:
            ws.append(fila)
    ruta = tmp_path / "ejemplos.xlsx"
    wb.save(ruta)
    return ruta


ENCABEZADO = ["Pregunta", "Respuesta correcta", "Respuesta similar", "Respuesta incorrecta", "Respuesta incorrecta"]


def test_el_xlsx_da_un_ejemplo_por_fila_con_el_nivel_de_su_hoja(tmp_path):
    ruta = _xlsx(tmp_path, {
        "Conocimiento": [[None, *ENCABEZADO], [None, "Según el texto, ¿qué es A?", "A1", "A2", "A3", "A4"]],
        "Aplicacion": [ENCABEZADO, ["Un equipo mide X[cite: 1]. ¿Qué hace?", "B1 [cite: 1]", "B2", "B3", "B4"], [None] * 5],
    })

    items = load_reference_file(ruta)

    assert [(i["nivel"], i["question"]) for i in items] == [
        ("conocimiento", "¿Qué es A?"),
        ("aplicacion", "Un equipo mide X. ¿Qué hace?"),
    ]
    assert [o["role"] for o in items[1]["options"]] == ["correct", "confusa", "distractor", "distractor"]
    assert items[1]["options"][0]["text"] == "B1"


def test_una_hoja_que_no_es_un_nivel_se_rechaza(tmp_path):
    ruta = _xlsx(tmp_path, {"Resumen": [ENCABEZADO]})
    with pytest.raises(ValueError, match="Resumen"):
        load_reference_file(ruta)


def test_una_fila_con_menos_de_cuatro_respuestas_se_rechaza_con_hoja_y_fila(tmp_path):
    ruta = _xlsx(tmp_path, {"Analisis": [ENCABEZADO, ["¿Qué se deduce?", "C1", "C2"]]})
    with pytest.raises(ValueError, match="Analisis.*fila 2"):
        load_reference_file(ruta)


@pytest.mark.parametrize("sucio, limpio", [
    ("De acuerdo con la información del texto, ¿cuáles son las coordenadas?", "¿Cuáles son las coordenadas?"),
    ("A partir del texto, ¿cómo se explica el avance?", "¿Cómo se explica el avance?"),
    ("¿Cómo se establecieron los límites tras 1848, según el texto?", "¿Cómo se establecieron los límites tras 1848?"),
    ("Trazar la línea media del río[cite: 1].", "Trazar la línea media del río."),
    ("A partir de las proporciones mencionadas en el texto respecto a Canadá, ¿qué se deduce?",
     "A partir de las proporciones mencionadas respecto a Canadá, ¿qué se deduce?"),
    ("A partir de las características descritas en el texto, ¿qué implicación se infiere?",
     "A partir de las características descritas, ¿qué implicación se infiere?"),
])
def test_limpiar_ejemplo(sucio, limpio):
    assert limpiar_ejemplo(sucio) == limpio


def test_el_ejemplo_importado_guarda_su_nivel_y_se_elige_uno_por_nivel_con_prioridad():
    init_db()
    init_question_tables()

    def ej(pregunta, nivel, **extra):
        return {"question": pregunta, "nivel": nivel, **extra,
                "options": [{"text": f"{pregunta} {i}", "role": r} for i, r in
                            enumerate(("correct", "confusa", "distractor", "distractor"))]}

    with session_scope() as session:
        import_reference_questions(session, [
            ej("global conocimiento", "conocimiento"),
            ej("global análisis", "analisis"),
            ej("perfil conocimiento", "conocimiento", profile="historia_universal"),
            ej("manual conocimiento", "conocimiento", manual_code="HU"),
        ])
        elegidos = get_level_exemplars(session, profile="historia_universal", manual_code="HU")
    assert [(e["nivel"], e["question_text"]) for e in elegidos] == [
        ("conocimiento", "manual conocimiento"),
        ("analisis", "global análisis"),
    ]

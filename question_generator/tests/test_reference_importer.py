"""Pruebas unitarias para la importación y consulta de preguntas de referencia (importer.py y repository.py)."""

import json
from etl.db.init_db import init_db
from etl.db.session import session_scope
from qgen.db.migration import init_question_tables
from qgen.models.reference_schema import ReferenceQuestion
from qgen.reference.importer import import_reference_questions, load_reference_file
from qgen.reference.repository import get_reference_exemplars


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

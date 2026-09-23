"""Idempotent creation of the question-generation tables.

Importing :mod:`qgen.models.schema` registers the ORM mappings against the
same `Base.metadata` used by `etl.models.schema`. ``Base.metadata.create_all``
issues `CREATE TABLE IF NOT EXISTS` for *all* tables, but it never touches a
table that already exists: the columns added later are added here, one by one.
"""

from __future__ import annotations

from sqlalchemy import inspect, text

from etl.db.session import get_engine
from etl.models.schema import Base

# noqa: F401 — los imports son requeridos para que SQLAlchemy registre las nuevas tablas
import qgen.models.schema  # noqa: F401
import qgen.models.reference_schema  # noqa: F401

# Columnas de `questions` que llegaron después de crear la tabla (qgen v2, spec §8).
_QUESTION_COLUMNS: dict[str, str] = {
    "question_type": "VARCHAR(32) NOT NULL DEFAULT 'teoria'",
    "source_quote": "TEXT NOT NULL DEFAULT ''",
    "window_key": "VARCHAR(64)",
}


def init_question_tables(db_url: str | None = None) -> None:
    engine = get_engine(db_url)
    Base.metadata.create_all(engine)
    _add_missing_columns(engine)


def _add_missing_columns(engine) -> None:
    existing = {c["name"] for c in inspect(engine).get_columns("questions")}
    with engine.begin() as conn:
        for name, ddl in _QUESTION_COLUMNS.items():
            if name not in existing:
                conn.execute(text(f"ALTER TABLE questions ADD COLUMN {name} {ddl}"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_questions_window_key ON questions (window_key)"))

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

# Columnas que llegaron después de crear cada tabla (qgen v2 y niveles cognitivos).
_NEW_COLUMNS: dict[str, dict[str, str]] = {
    "questions": {
        "question_type": "VARCHAR(32) NOT NULL DEFAULT 'teoria'",
        "source_quote": "TEXT NOT NULL DEFAULT ''",
        "window_key": "VARCHAR(64)",
        "cognitive_level": "VARCHAR(16)",
    },
    "reference_questions": {
        "cognitive_level": "VARCHAR(16)",
    },
}


def init_question_tables(db_url: str | None = None) -> None:
    engine = get_engine(db_url)
    Base.metadata.create_all(engine)
    _add_missing_columns(engine)


def _add_missing_columns(engine) -> None:
    inspector = inspect(engine)
    with engine.begin() as conn:
        for table, columns in _NEW_COLUMNS.items():
            existing = {c["name"] for c in inspector.get_columns(table)}
            for name, ddl in columns.items():
                if name not in existing:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_questions_window_key ON questions (window_key)"))

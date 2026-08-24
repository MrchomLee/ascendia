"""Idempotent creation of the question-generation tables.

Importing :mod:`qgen.models.schema` registers the three new ORM mappings
against the same `Base.metadata` used by `etl.models.schema`. Calling
``Base.metadata.create_all`` then issues `CREATE TABLE IF NOT EXISTS` for
*all* tables — but is safe to run because existing tables are not touched.
"""

from __future__ import annotations

from etl.db.session import get_engine
from etl.models.schema import Base

# noqa: F401 — the import is required so SQLAlchemy registers the new tables
import qgen.models.schema  # noqa: F401


def init_question_tables(db_url: str | None = None) -> None:
    engine = get_engine(db_url)
    Base.metadata.create_all(engine)

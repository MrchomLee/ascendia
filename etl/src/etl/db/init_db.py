from __future__ import annotations

from etl.db.session import get_engine
from etl.models.schema import Base


def init_db(db_url: str | None = None) -> None:
    """Create all tables. Idempotent — safe to run on existing DBs."""
    engine = get_engine(db_url)
    Base.metadata.create_all(engine)

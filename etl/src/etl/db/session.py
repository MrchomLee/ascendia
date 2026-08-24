from __future__ import annotations

import os
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from typing import Iterator

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker


def _default_db_url() -> str:
    url = os.getenv("DB_URL")
    if url:
        return url
    data_dir = Path(os.getenv("DATA_DIR", "./data")).resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{(data_dir / 'manuals.sqlite').as_posix()}"


@lru_cache(maxsize=4)
def get_engine(db_url: str | None = None) -> Engine:
    url = db_url or _default_db_url()
    engine = create_engine(url, echo=False, future=True)
    if url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def _enable_fk(dbapi_connection, _) -> None:  # type: ignore[no-untyped-def]
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.close()
    return engine


@lru_cache(maxsize=4)
def get_session_factory(db_url: str | None = None) -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(db_url), expire_on_commit=False, future=True)


@contextmanager
def session_scope(db_url: str | None = None) -> Iterator[Session]:
    factory = get_session_factory(db_url)
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

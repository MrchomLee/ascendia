import pytest


@pytest.fixture(autouse=True)
def _isolate_data_dir(tmp_path, monkeypatch):
    """Each test gets a fresh DB. Clear etl's lru_cache so a new engine binds to it."""
    from etl.db import session as etl_session

    etl_session.get_engine.cache_clear()
    etl_session.get_session_factory.cache_clear()

    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("DB_URL", f"sqlite:///{tmp_path}/test.sqlite")
    monkeypatch.setenv("GEMINI_API_KEY", "fake-test-key")

    yield

    etl_session.get_engine.cache_clear()
    etl_session.get_session_factory.cache_clear()

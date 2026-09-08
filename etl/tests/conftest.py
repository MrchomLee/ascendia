import pytest


@pytest.fixture(autouse=True)
def _isolate_data_dir(tmp_path, monkeypatch):
    """Cada test obtiene un directorio de datos limpio y un SQLite aislado."""
    from etl.db import session as etl_session

    # Limpiar lru_cache para que cada test vincule un engine nuevo
    etl_session.get_engine.cache_clear()
    etl_session.get_session_factory.cache_clear()

    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("DB_URL", f"sqlite:///{tmp_path}/test.sqlite")
    yield

    etl_session.get_engine.cache_clear()
    etl_session.get_session_factory.cache_clear()

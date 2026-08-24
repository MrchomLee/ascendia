import os

import pytest


@pytest.fixture(autouse=True)
def _isolate_data_dir(tmp_path, monkeypatch):
    """Each test gets a clean data dir + in-memory-equivalent SQLite file."""
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("DB_URL", f"sqlite:///{tmp_path}/test.sqlite")
    yield

import os

import pytest


@pytest.fixture(scope="session", autouse=True)
def _session_database(tmp_path_factory):
    """Point DATABASE_URL at a temporary file for the whole session."""
    path = tmp_path_factory.mktemp("session-db") / "radar.db"
    old = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = f"sqlite:///{path}"
    yield
    if old is None:
        os.environ.pop("DATABASE_URL", None)
    else:
        os.environ["DATABASE_URL"] = old


@pytest.fixture
def db_url(tmp_path):
    """A fresh temporary SQLite URL (the file does not exist yet)."""
    return f"sqlite:///{tmp_path / 'radar.db'}"

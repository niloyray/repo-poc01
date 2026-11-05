import sqlite3

from fastapi.testclient import TestClient

from app.main import app


def test_lifespan_seeds_once(db_url, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", db_url)
    path = db_url.removeprefix("sqlite:///")
    for _ in range(2):
        with TestClient(app):
            pass
        with sqlite3.connect(path) as conn:
            assert conn.execute("SELECT COUNT(*) FROM topics").fetchone() == (7,)

import os
import sqlite3
from pathlib import Path

from app.db import init_database


def dump(path):
    with sqlite3.connect(path) as conn:
        names = [
            r[0]
            for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY 1")
        ]
        return {n: conn.execute(f"SELECT * FROM {n}").fetchall() for n in names}


def test_restart_changes_no_data(tmp_path):
    path = tmp_path / "radar.db"
    url = f"sqlite:///{path}"
    init_database(url)
    with sqlite3.connect(path) as conn:
        conn.execute("INSERT INTO sources (name, kind, address) VALUES ('s', 'rss', 'u')")
        conn.execute("INSERT INTO topics (name) VALUES ('llm')")
        conn.execute(
            "INSERT INTO items (title, canonical_url, source_id, kind, fetched_at)"
            " VALUES ('t', 'https://e.com/1', 1, 'paper', '2026-01-01 00:00:00')"
        )
    before = dump(path)
    init_database(url)
    assert dump(path) == before


def test_empty_file_is_upgraded(tmp_path):
    path = tmp_path / "radar.db"
    path.touch()
    init_database(f"sqlite:///{path}")
    assert {"sources", "items", "digests"} <= set(dump(path))


def test_partial_file_keeps_rows_and_gets_missing_tables(tmp_path):
    path = tmp_path / "radar.db"
    with sqlite3.connect(path) as conn:
        conn.execute(
            "CREATE TABLE topics (id INTEGER NOT NULL, name TEXT NOT NULL UNIQUE,"
            " CONSTRAINT pk_topics PRIMARY KEY (id))"
        )
        conn.execute("INSERT INTO topics (name) VALUES ('keep me')")
    init_database(f"sqlite:///{path}")
    data = dump(path)
    assert data["topics"] == [(1, "keep me", "", "[]", "[]")]
    assert {"sources", "items", "item_topics", "runs", "digests"} <= set(data)


def test_default_database_is_not_created():
    assert not Path("data/radar.db").exists()
    assert "data/radar.db" not in os.environ["DATABASE_URL"]


def _downgrade_to_0001(path, drop_columns):
    with sqlite3.connect(path) as conn:
        for column in drop_columns:
            conn.execute(f"ALTER TABLE topics DROP COLUMN {column}")
        conn.execute("UPDATE alembic_version SET version_num = '0001'")


def test_0002_keeps_topic_rows_and_links(tmp_path):
    path = tmp_path / "radar.db"
    url = f"sqlite:///{path}"
    init_database(url)
    _downgrade_to_0001(path, ["description", "keywords", "exclusion_keywords"])
    with sqlite3.connect(path) as conn:
        conn.execute("INSERT INTO sources (name, kind, address) VALUES ('s', 'rss', 'u')")
        conn.execute("INSERT INTO topics (name) VALUES ('old')")
        conn.execute(
            "INSERT INTO items (title, canonical_url, source_id, kind, fetched_at)"
            " VALUES ('t', 'https://e.com/1', 1, 'paper', '2026-01-01 00:00:00')"
        )
        conn.execute("INSERT INTO item_topics VALUES (1, 1)")
    init_database(url)
    data = dump(path)
    assert data["topics"] == [(1, "old", "", "[]", "[]")]
    assert data["item_topics"] == [(1, 1)]
    init_database(url)
    assert dump(path) == data


def test_0002_with_one_column_already_present(tmp_path):
    path = tmp_path / "radar.db"
    url = f"sqlite:///{path}"
    init_database(url)
    _downgrade_to_0001(path, ["keywords", "exclusion_keywords"])
    with sqlite3.connect(path) as conn:
        conn.execute("INSERT INTO topics (name, description) VALUES ('x', 'desc')")
    init_database(url)
    assert dump(path)["topics"] == [(1, "x", "desc", "[]", "[]")]

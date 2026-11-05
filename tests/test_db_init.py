import sqlite3

from app.db import init_database

TABLES = {"sources", "topics", "items", "item_topics", "runs", "digests"}


def table_names(path):
    with sqlite3.connect(path) as conn:
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    return {r[0] for r in rows}


def test_first_start_creates_file_folder_and_tables(tmp_path):
    path = tmp_path / "a" / "b" / "radar.db"
    init_database(f"sqlite:///{path}")
    assert path.is_file()
    assert TABLES <= table_names(path)


def test_existing_folder(tmp_path):
    init_database(f"sqlite:///{tmp_path / 'x.db'}")
    assert TABLES <= table_names(tmp_path / "x.db")


def test_bare_file_name(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    init_database("sqlite:///radar.db")
    assert TABLES <= table_names(tmp_path / "radar.db")


def test_wal_is_on(db_url, tmp_path):
    init_database(db_url)
    with sqlite3.connect(tmp_path / "radar.db") as conn:
        assert conn.execute("PRAGMA journal_mode").fetchone()[0] == "wal"


def test_works_from_another_cwd(tmp_path, monkeypatch):
    other = tmp_path / "other"
    other.mkdir()
    monkeypatch.chdir(other)
    init_database(f"sqlite:///{tmp_path / 'radar.db'}")
    assert TABLES <= table_names(tmp_path / "radar.db")

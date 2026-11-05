import json
import sqlite3

from app.db import init_database
from app.seed import load_seed

COLUMNS = "id, name, description, keywords, exclusion_keywords"


def rows(url):
    path = url.removeprefix("sqlite:///")
    with sqlite3.connect(path) as conn:
        return conn.execute(f"SELECT {COLUMNS} FROM topics ORDER BY id").fetchall()


def write_seed(path, topics):
    path.write_text(json.dumps({"topics": topics}), encoding="utf-8")
    return path


def topic(name, keywords=("k",), description="d", exclusions=()):
    return {
        "name": name,
        "description": description,
        "keywords": list(keywords),
        "exclusion_keywords": list(exclusions),
    }


def test_first_load_gives_seven_topics_with_all_fields(db_url):
    init_database(db_url)
    assert load_seed(db_url) == 7
    data = rows(db_url)
    assert len(data) == 7
    for _id, name, description, keywords, exclusions in data:
        assert name and description
        assert json.loads(keywords)
        assert isinstance(json.loads(exclusions), list)


def test_second_load_changes_nothing(db_url):
    init_database(db_url)
    load_seed(db_url)
    before = rows(db_url)
    assert load_seed(db_url) == 0
    assert rows(db_url) == before


def test_existing_name_is_not_overwritten(db_url, tmp_path):
    init_database(db_url)
    load_seed(db_url, write_seed(tmp_path / "a.json", [topic("A", ["one"], "first")]))
    before = rows(db_url)
    changed = write_seed(tmp_path / "b.json", [topic("A", ["two"], "second", ["x"])])
    assert load_seed(db_url, changed) == 0
    assert rows(db_url) == before


def test_new_name_is_added(db_url, tmp_path):
    init_database(db_url)
    load_seed(db_url, write_seed(tmp_path / "a.json", [topic("A")]))
    assert load_seed(db_url, write_seed(tmp_path / "b.json", [topic("A"), topic("B")])) == 1
    assert [r[1] for r in rows(db_url)] == ["A", "B"]


def test_default_file_found_from_another_cwd(db_url, tmp_path, monkeypatch):
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    init_database(db_url)
    assert load_seed(db_url) == 7

import json
import sqlite3

import pytest

from app.db import init_database
from app.seed import SeedError, load_seed, parse_seed


def good(name="Good"):
    return {"name": name, "description": "d", "keywords": ["k"], "exclusion_keywords": []}


def seed(tmp_path, topics):
    path = tmp_path / "seed.json"
    path.write_text(json.dumps({"topics": topics}), encoding="utf-8")
    return path


def fails(path, *fragments):
    with pytest.raises(SeedError) as exc:
        parse_seed(path)
    message = str(exc.value)
    assert str(path) in message
    for fragment in fragments:
        assert fragment in message


def test_missing_name(tmp_path):
    entry = good()
    del entry["name"]
    fails(seed(tmp_path, [good("A"), entry]), "entry 2 (no name)")


def test_blank_name(tmp_path):
    fails(seed(tmp_path, [{**good(), "name": "   "}]), "entry 1 (no name)")


def test_empty_keywords(tmp_path):
    fails(seed(tmp_path, [{**good("Empty"), "keywords": []}]), 'entry 1 ("Empty")', "keywords")


def test_blank_only_keywords(tmp_path):
    fails(seed(tmp_path, [{**good("Blank"), "keywords": [" ", ""]}]), 'entry 1 ("Blank")')


def test_duplicate_name_names_second_entry(tmp_path):
    fails(seed(tmp_path, [good("Dup"), good(" dup ")]), 'entry 2 ("dup")', "duplicate")


def test_wrong_types(tmp_path):
    fails(seed(tmp_path, [{**good("T"), "keywords": "abc"}]), 'entry 1 ("T")')
    fails(seed(tmp_path, [{**good("T"), "exclusion_keywords": [1]}]), 'entry 1 ("T")')
    fails(seed(tmp_path, ["nope"]), "entry 1")
    fails(seed(tmp_path, [{**good("T"), "name": 5}]), "entry 1 (no name)")


def test_missing_file(tmp_path):
    fails(tmp_path / "absent.json")


def test_invalid_json(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not json", encoding="utf-8")
    fails(path, "not valid JSON")


def test_no_topics_list(tmp_path):
    path = tmp_path / "x.json"
    path.write_text("[]", encoding="utf-8")
    fails(path, "topics")


def test_empty_exclusions_accepted_and_text_stripped(tmp_path):
    entry = {"name": " A ", "keywords": [" k ", ""]}
    assert parse_seed(seed(tmp_path, [entry])) == [
        {"name": "A", "description": "", "keywords": ["k"], "exclusion_keywords": []}
    ]


def test_one_bad_entry_writes_nothing(db_url, tmp_path):
    init_database(db_url)
    path = seed(tmp_path, [good("A"), {**good("B"), "keywords": []}, good("C")])
    with pytest.raises(SeedError):
        load_seed(db_url, path)
    with sqlite3.connect(db_url.removeprefix("sqlite:///")) as conn:
        assert conn.execute("SELECT COUNT(*) FROM topics").fetchone() == (0,)

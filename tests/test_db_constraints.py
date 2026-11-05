from datetime import UTC, datetime

import pytest
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError

from app.db import init_database
from app.db.engine import prepare_engine
from app.db.schema import item_topics, items, sources

NOW = datetime(2026, 1, 1, tzinfo=UTC)


@pytest.fixture
def engine(db_url):
    init_database(db_url)
    eng = prepare_engine(db_url)
    yield eng
    eng.dispose()


def new_source(conn):
    result = conn.execute(sa.insert(sources).values(name="s", kind="rss", address="u"))
    return result.inserted_primary_key[0]


def item(source_id, url="https://example.com/a"):
    return {
        "title": "t",
        "canonical_url": url,
        "source_id": source_id,
        "kind": "paper",
        "fetched_at": NOW,
    }


def test_duplicate_canonical_url_rejected(engine):
    with engine.begin() as conn:
        sid = new_source(conn)
        conn.execute(sa.insert(items).values(item(sid)))
    with pytest.raises(IntegrityError), engine.begin() as conn:
        conn.execute(sa.insert(items).values(item(sid)))


def test_optional_fields_may_be_missing(engine):
    with engine.begin() as conn:
        sid = new_source(conn)
        conn.execute(sa.insert(items).values(item(sid)))
        row = conn.execute(sa.select(items)).one()
    assert row.published_at is None
    assert row.summary is None
    assert row.score is None


def test_foreign_keys_enforced(engine):
    with pytest.raises(IntegrityError), engine.begin() as conn:
        conn.execute(sa.insert(items).values(item(999)))
    with pytest.raises(IntegrityError), engine.begin() as conn:
        conn.execute(sa.insert(item_topics).values(item_id=1, topic_id=1))

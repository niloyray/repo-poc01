"""Database URL validation and engine creation (SQLite file, WAL, foreign keys)."""

import sqlite3
from pathlib import Path

import sqlalchemy as sa
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import ArgumentError, SQLAlchemyError


class DatabaseConfigError(RuntimeError):
    """The database cannot be set up. The message starts with ``DATABASE_URL: ``."""


def _fail(problem: str) -> DatabaseConfigError:
    return DatabaseConfigError(f"DATABASE_URL: {problem}")


def parse_url(database_url: str) -> tuple[URL, Path]:
    """Return the parsed URL and the database file path; reject non-file-SQLite."""
    try:
        url = make_url(database_url)
    except (ArgumentError, ValueError):
        raise _fail(
            f'expected a SQLite URL such as sqlite:///data/radar.db, got "{database_url}"'
        ) from None
    if url.drivername not in ("sqlite", "sqlite+pysqlite"):
        raise _fail(f'only SQLite is supported, got "{database_url}"')
    if not url.database or url.database == ":memory:" or url.database.startswith("file:"):
        raise _fail(f'expected a SQLite database file path, got "{database_url}"')
    return url, Path(url.database)


def create_db_engine(url: URL) -> sa.Engine:
    engine = sa.create_engine(url)

    @sa.event.listens_for(engine, "connect")
    def _pragmas(dbapi_connection, _record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def prepare_engine(database_url: str) -> sa.Engine:
    """Validate the URL, create the folder and file, and return a working engine."""
    url, path = parse_url(database_url)
    try:
        if path.parent != Path("."):
            path.parent.mkdir(parents=True, exist_ok=True)
        engine = create_db_engine(url)
        try:
            with engine.connect() as conn:
                conn.execute(sa.text("SELECT 1"))
        except BaseException:
            engine.dispose()
            raise
    except (OSError, sqlite3.Error, SQLAlchemyError) as exc:
        raise _fail(f'cannot create or open "{database_url}": {exc}') from exc
    return engine

"""Bring the database to the current schema with Alembic, run programmatically."""

import sqlite3
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy.exc import SQLAlchemyError

from app.db.engine import DatabaseConfigError, prepare_engine

MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"


def make_config(engine) -> Config:
    config = Config()
    config.set_main_option("script_location", str(MIGRATIONS_DIR))
    config.attributes["engine"] = engine
    return config


def init_database(database_url: str) -> None:
    """Create the file and folder if missing and upgrade to the latest schema.

    Safe to call on every start: an up-to-date database is left untouched.
    """
    engine = prepare_engine(database_url)
    try:
        command.upgrade(make_config(engine), "head")
    except (OSError, sqlite3.Error, SQLAlchemyError) as exc:
        raise DatabaseConfigError(f"DATABASE_URL: cannot migrate the database: {exc}") from exc
    finally:
        engine.dispose()

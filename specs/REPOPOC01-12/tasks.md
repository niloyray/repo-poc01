# Tasks: Create the SQLite schema and migration path

**Spec**: `specs/REPOPOC01-12/spec.md` | **Plan**: `specs/REPOPOC01-12/plan.md`
Run `uv run pytest` and `uvx ruff check .` before finishing.

## Setup

- [x] T001 Add `sqlalchemy` and `alembic` to dependencies and refresh the lock file: `pyproject.toml`, `uv.lock`
- [x] T002 Add `data/` to `.gitignore`: `.gitignore`
- [x] T003 Create the package skeleton `app/db/__init__.py` (empty exports for now) and `tests/conftest.py` with a fixture giving a temporary `sqlite:///` URL under `tmp_path` and setting `DATABASE_URL` to it for the whole test session

## Schema and engine

- [x] T004 [P] Define the `MetaData` (with naming convention) and the six tables `sources`, `topics`, `items`, `item_topics`, `runs`, `digests` as in the plan: `app/db/schema.py`
- [x] T005 [P] Implement `DatabaseConfigError`, URL validation (SQLite file only), parent-folder creation (skipped for a bare file name), engine creation with `PRAGMA journal_mode=WAL` and `PRAGMA foreign_keys=ON` on connect, and wrapping of OS/SQLite errors in messages starting `DATABASE_URL: `: `app/db/engine.py`

## Migrations

- [x] T006 Create the Alembic environment (no ini file, `render_as_batch=True`, target metadata from `schema.py`, no logging reconfiguration): `app/db/migrations/env.py`, `app/db/migrations/script.py.mako`
- [x] T007 Write the initial migration that creates only the missing tables among the six, in one transaction: `app/db/migrations/versions/0001_initial_schema.py`
- [x] T008 Implement `init_database(database_url)` that validates, creates folder/file, runs Alembic `upgrade head` programmatically with an absolute `script_location`, and disposes the engine; export it and `DatabaseConfigError`: `app/db/migrate.py`, `app/db/__init__.py`
- [x] T009 Add the developer helper `python -m app.db upgrade|revision "message"` (revision uses autogenerate): `app/db/__main__.py`

## Start-up wiring

- [x] T010 Add a FastAPI `lifespan` that calls `init_database(get_settings().database_url)`: `app/main.py`
- [x] T011 Call `init_database` before `uvicorn.run`; on `DatabaseConfigError` print `Invalid configuration: <message>` to stderr and exit 2: `app/__main__.py`

## Tests (temporary database only, no network)

- [x] T012 [P] First start creates file and missing folder, works with an existing folder and with a bare file name, and all six tables exist; WAL is on from a fresh connection: `tests/test_db_init.py`
- [x] T013 [P] A second item with the same canonical URL is rejected; an item with only required fields (no published time, summary, score) is stored; foreign keys are enforced: `tests/test_db_constraints.py`
- [x] T014 [P] Restarting on an existing database leaves all rows unchanged; an empty file and a file with only some tables are brought to the current schema with existing rows kept; `init_database` works from a different working directory; the default `data/radar.db` is never created: `tests/test_db_migrations.py`
- [x] T015 [P] A non-SQLite URL, `:memory:`, and an uncreatable/unwritable path fail with a message naming `DATABASE_URL`: `tests/test_db_errors.py`
- [x] T016 Extend entry-point tests: a database error exits with code 2 and the message on stderr, and `uvicorn.run` is not called; the success path calls `init_database` first: `tests/test_main_entry.py`

## Documentation and finish

- [x] T017 Add a "Database and migrations" README section: where the file lives, automatic creation on start, how to add and apply a schema change (edit `schema.py`, `python -m app.db revision`, review, `python -m app.db upgrade` or restart), and the warning that the file (plus its `-wal`/`-shm` files while running) is the only copy and is not backed up: `README.md`
- [x] T018 Run `uv run pytest` and `uvx ruff check .`, fix any failures, and confirm `git status` shows no `data/` or `.db` files: no new files

# Implementation Plan: Create the SQLite schema and migration path

**Branch**: `REPOPOC01-12-create-the-sqlite-schema-and-migration-p` | **Date**: 2026-11-05 | **Spec**: `specs/REPOPOC01-12/spec.md`

## Summary

Add a small `app/db/` package that owns the SQLite database: it resolves the file path from `DATABASE_URL` (REPOPOC01-11 settings), creates the folder and file, switches on WAL and foreign keys, and brings the schema to the current version by running Alembic migrations programmatically. The initial migration creates the six tables. `init_database()` runs at start-up (in `python -m app` before uvicorn, so failures stop with a clear message, and again in the FastAPI lifespan for plain `uvicorn app.main:app`). It is idempotent: on an up-to-date file it changes nothing. The README documents how a later story adds a migration. No endpoints or pages.

## Technical Context

**Language/Version**: Python 3.12 (existing)
**Primary Dependencies**: add `sqlalchemy` (Core, no ORM sessions needed yet) and `alembic`. Existing `fastapi`, `uvicorn`. SQLite via stdlib `sqlite3`.
**Storage**: one SQLite file, path from `DATABASE_URL` (default `sqlite:///data/radar.db`)
**Testing**: pytest with `tmp_path` databases; no network; the default file is never touched
**Project Type**: web-service (single project)
**Constraints**: fail fast naming `DATABASE_URL`; no edits to `.github/`, `.specify/`, `.claude/`, `CLAUDE.md`; no secrets

## Constitution Check

`.specify/memory/constitution.md` is still the unfilled template and sets no gates. `CLAUDE.md` rules are followed: code in `app/`, tests in `tests/`, ruff as a tool only, configuration from environment. No violations.

## Design Decisions

Open questions of the spec are resolved here (spec text is not changed):

- **Q1 migrations**: versioned Alembic scripts run automatically at start-up, configured in code (`alembic.config.Config` with `script_location` set to `app/db/migrations` and the URL passed through `config.attributes`/`set_main_option`), so no `alembic.ini` and no cwd dependence. No `alembic` command line is needed. The README gives: edit `app/db/schema.py`, run a documented helper `uv run python -m app.db revision "message"` (wraps `alembic revision --autogenerate`), review the script, then start the service (or `python -m app.db upgrade`) to apply it.
- **Q2 outside signals**: one nullable JSON column `outside_signals` on `items`.
- **Q3 kind / scoring method**: plain nullable/required text, no CHECK constraint; later stories define values.
- **Q4 deletes**: `PRAGMA foreign_keys=ON` on every connection; no `ON DELETE` rules are added now (deletion is decided in a later story). The link table uses a composite primary key `(item_id, topic_id)`.
- **Path handling**: parse `DATABASE_URL` with `sqlalchemy.engine.make_url`. Accept only drivername `sqlite` / `sqlite+pysqlite` with a file database (reject `:memory:`, empty path, other databases) with `DatabaseError("DATABASE_URL: ...")`. Create the parent folder with `mkdir(parents=True, exist_ok=True)` only when the path has a folder part. Relative paths resolve against the current working directory, as `sqlite3` does.
- **Errors**: `DatabaseConfigError(RuntimeError)` whose message starts with `DATABASE_URL: `. `OSError` and `sqlite3.DatabaseError`/`sqlalchemy.exc.SQLAlchemyError` raised while creating/opening/migrating are wrapped in it. `app/__main__.py` prints `Invalid configuration: <message>` to stderr and exits 2 (same as settings errors).
- **WAL**: an engine `connect` event sets `PRAGMA journal_mode=WAL` and `PRAGMA foreign_keys=ON`. WAL is persistent in the file; the test reads `PRAGMA journal_mode` from a fresh connection.
- **Existing / partial files**: Alembic tracks `alembic_version`. A new or empty file is upgraded from base. A file that has some of the six tables but no `alembic_version` (hand-made partial schema) is handled by the initial migration using `CREATE TABLE IF NOT EXISTS` semantics (inspect existing tables, create only the missing ones), then stamped. Existing rows are never touched. Columns missing in a partially existing table are out of reach of this story and not repaired (documented as a limit).
- **Idempotent start**: if the current revision equals head, `upgrade` does nothing; a test snapshots all rows before/after a second `init_database()` and asserts equality.
- **Timestamps**: stored as timezone-aware UTC ISO text via SQLAlchemy `DateTime(timezone=True)`; `fetched_at` is required, `published_at` is nullable.
- **Schema** (module `app/db/schema.py`, SQLAlchemy `MetaData` + `Table`s, naming convention set so constraint names are stable):
  - `sources(id PK, name NOT NULL, kind NOT NULL, address NOT NULL)`
  - `topics(id PK, name NOT NULL UNIQUE)`
  - `items(id PK, title NOT NULL, canonical_url NOT NULL UNIQUE, source_id FK sources NOT NULL, kind NOT NULL, published_at NULL, fetched_at NOT NULL, excerpt NULL, score NULL, score_reason NULL, scoring_method NULL, summary NULL, outside_signals JSON NULL)`
  - `item_topics(item_id FK items, topic_id FK topics, PK(item_id, topic_id))`
  - `runs(id PK, started_at NOT NULL, finished_at NULL, outcome NULL)`
  - `digests(id PK, run_id FK runs NOT NULL, created_at NOT NULL, content NOT NULL)`
  "Every item keeps the link to its original source" is met by `canonical_url` NOT NULL plus `source_id`.
- **Start-up wiring**: `app/main.py` gets a `lifespan` that calls `init_database(get_settings().database_url)`. `TestClient` used without `with` does not run lifespan, so existing tests never create `data/radar.db`. Tests that use lifespan override `DATABASE_URL`/pass a tmp path.
- **Git**: add `data/` to `.gitignore`.
- **Packaging**: migration scripts live inside the `app` package so the hatch wheel includes them.

## Project Structure

```text
specs/REPOPOC01-12/            # spec.md, plan.md, tasks.md
app/
├── db/
│   ├── __init__.py            # NEW: exports init_database, DatabaseConfigError
│   ├── __main__.py            # NEW: `python -m app.db upgrade|revision`
│   ├── schema.py              # NEW: MetaData and the six tables
│   ├── engine.py              # NEW: URL/path validation, engine, WAL + FK pragmas
│   ├── migrate.py             # NEW: init_database(), programmatic Alembic upgrade
│   └── migrations/
│       ├── env.py             # NEW: Alembic env (uses schema.metadata)
│       ├── script.py.mako     # NEW
│       └── versions/0001_initial_schema.py   # NEW
├── main.py                    # lifespan calls init_database
└── __main__.py                # init_database before uvicorn.run, exit 2 on error
tests/
├── conftest.py                # NEW: tmp database URL fixture
├── test_db_init.py            # NEW: create file/folder, tables, WAL, bare filename, existing folder
├── test_db_constraints.py     # NEW: unique URL, optional fields, foreign keys
├── test_db_migrations.py      # NEW: idempotent restart, partial file, empty file, upgrade keeps rows
├── test_db_errors.py          # NEW: non-SQLite URL, unwritable path, message names DATABASE_URL
└── test_main_entry.py         # extend: DB failure exits 2
README.md                      # "Database and migrations" section, backup warning
.gitignore                     # data/
pyproject.toml, uv.lock        # sqlalchemy, alembic
```

**Structure Decision**: A sub-package `app/db/` because schema, engine and migrations are several modules; the rest of `app/` stays flat.

## Risks

1. **Alembic run inside the app process**: Alembic's `env.py` normally configures logging and reads `alembic.ini`; with programmatic use it can reset logging or fail to find scripts when run from another cwd or when packaged. Mitigation: `script_location` as an absolute path from `__file__`, skip `fileConfig`, a test that runs `init_database` from a different cwd.
2. **Partial or hand-made files**: a file with some tables but no version row can make the initial migration fail with "table already exists", or leave a half-built schema. Mitigation: create only missing tables in the first migration, run it in one transaction, and test empty, partial and full files.
3. **Unintended data change on restart / data loss in later migrations**: SQLite `ALTER TABLE` is limited; autogenerate may drop and recreate tables. Mitigation: idempotency test comparing rows, `render_as_batch=True` in `env.py`, README tells the developer to review generated scripts.
4. **WAL and file handling**: WAL creates `-wal`/`-shm` side files, so copying only `radar.db` while running can lose data; temp-dir cleanup on Windows can fail with open connections. Mitigation: dispose engines after use, README notes it, ignore `data/` wholesale.
5. **Tests touching the default file**: an app lifespan or `get_settings()` cache could create `data/radar.db` during tests. Mitigation: conftest sets `DATABASE_URL` to a tmp path for the whole session and a test asserts `data/radar.db` is not created.

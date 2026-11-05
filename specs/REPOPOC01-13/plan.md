# Implementation Plan: Load the watched topics as seed data

**Branch**: `REPOPOC01-13-load-the-watched-topics-as-seed-data` | **Date**: 2026-11-05 | **Spec**: `specs/REPOPOC01-13/spec.md`

## Summary

Add a JSON seed file `app/seed/topics.json` with the seven topics, a migration that adds `description`, `keywords` and `exclusion_keywords` to `topics`, and a small module `app/seed.py` that validates the whole file and inserts only the topic names that are not yet in the table, in one transaction. The loader runs at start-up right after `init_database()`, in `python -m app` (fail fast, exit 2) and in the FastAPI lifespan. Loading is idempotent: existing rows are never touched. No endpoints, pages or new environment variables.

## Technical Context

**Language/Version**: Python 3.12 (existing)
**Primary Dependencies**: none new. JSON is read with stdlib `json`; SQLAlchemy Core and Alembic from REPOPOC01-12.
**Storage**: existing SQLite file; `topics` gains three columns.
**Testing**: pytest with `tmp_path` databases and temporary seed files; no network, no Claude Code CLI.
**Constraints**: no edits to `.github/`, `.specify/`, `.claude/`, `CLAUDE.md`; no secrets; ruff only as a tool.

## Constitution Check

`.specify/memory/constitution.md` is the unfilled template and sets no gates. `CLAUDE.md` rules are followed (code in `app/`, tests in `tests/`). No violations.

## Design Decisions

Open questions of the spec are resolved here (the spec text is not changed):

- **Q1 storage**: new Alembic migration `0002_topic_seed_columns` adds `description` (Text, NOT NULL, server default `''`), `keywords` (JSON, NOT NULL, server default `'[]'`) and `exclusion_keywords` (JSON, NOT NULL, server default `'[]'`). Defaults let existing rows survive. The migration inspects existing columns and adds only missing ones (same defensive style as 0001), uses `batch_alter_table` (already `render_as_batch`). `app/db/schema.py` is updated to match.
- **Q2 existing names**: insert-if-missing only. Existing rows are never updated, so later edits (F2-S3) are kept. Implemented with the SQLite `INSERT ... ON CONFLICT (name) DO NOTHING`, safe if two processes start together.
- **Q3 format and place**: JSON at `app/seed/topics.json` (stdlib, no new dependency, ships inside the wheel; add `app/seed/` as package data — hatch includes non-Python files inside the `app` package already). Shape: `{"topics": [{"name", "description", "keywords": [...], "exclusion_keywords": [...]}, ...]}`. The path is a constant `DEFAULT_SEED_PATH` in `app/seed.py`; the loader takes an optional path argument for tests.
- **Q4 rejection**: validate every entry first; if any problem exists, raise one `SeedError` listing all of them and write nothing.
- **Validation** (`parse_seed`): top level must be an object with a `topics` list; each entry must be an object. Name must be a non-blank string; `keywords` must be a list of strings with at least one non-blank item; `exclusion_keywords` may be missing or empty but if present must be a list of strings; `description` is a string (may be missing, stored as `''`). Names and keywords are stripped; blank keyword strings are dropped. Duplicate names (compared after strip, case-insensitive) are rejected naming the second entry. Messages name the entry as `entry 3 ("Algorithms")`, or `entry 3 (no name)`, with 1-based position, and the file path.
- **File errors**: missing, unreadable or invalid JSON → `SeedError("Seed file <path>: ...")`.
- **Error type**: `SeedError(RuntimeError)` in `app/seed.py`. `app/__main__.py` catches it with the other config errors, prints `Invalid configuration: <message>`, exits 2.
- **Start-up wiring**: keep `init_database()` schema-only, so the existing migration tests that expect untouched `topics` rows stay valid. Add `load_seed(database_url, seed_path=DEFAULT_SEED_PATH)` which opens an engine through `app.db.engine.prepare_engine`, writes in one `engine.begin()` transaction and disposes the engine. Call it after `init_database` in `app/__main__.py` and in `lifespan` in `app/main.py`.
- **Topic 4 (Lean)**: description states "Lean theorem prover / Lean 4, not Lean process improvement"; exclusion keywords include `lean manufacturing`, `lean startup`, `six sigma`, `lean six sigma`, `lean management`.
- **Seed content**: the seven names exactly as in the spec table; keywords derived from the "examples" column.

## Project Structure

```text
specs/REPOPOC01-13/            # spec.md, plan.md, tasks.md
app/
├── seed/
│   └── topics.json            # NEW: the seven topics
├── seed.py                    # NEW: SeedError, parse_seed, load_seed
├── db/
│   ├── schema.py              # topics gets three columns
│   └── migrations/versions/0002_topic_seed_columns.py   # NEW
├── main.py                    # lifespan also calls load_seed
└── __main__.py                # load_seed after init_database; SeedError -> exit 2
tests/
├── test_seed_load.py          # NEW: first load, repeat load, keeps edited rows, new name added
├── test_seed_validation.py    # NEW: rejected entries, duplicates, blanks, bad file, nothing written
├── test_seed_file.py          # NEW: shipped file has seven valid topics, Lean exclusions
├── test_db_migrations.py      # extend: 0002 keeps existing topic rows, partial columns
└── test_main_entry.py         # extend: bad seed exits 2
README.md                      # short "Seed topics" section
```

**Structure Decision**: one flat module `app/seed.py` plus a data folder; the DB package stays focused on schema and migrations.

## Risks

1. **Migration on a populated or hand-made `topics` table**: adding NOT NULL columns in SQLite through batch mode copies the table; a mistake can lose rows or break foreign keys from `item_topics`. Mitigation: server defaults, column inspection, tests that upgrade a 0001 database with existing topics and linked `item_topics` rows and compare rows afterwards.
2. **Idempotency drift**: re-running must change nothing, including JSON column text. Mitigation: insert-only with `ON CONFLICT DO NOTHING`, and a test snapshotting every column before and after a second load, and a test where the file differs for an existing name.
3. **All-or-nothing validation**: partial writes if validation is interleaved with inserts. Mitigation: parse fully first, then one transaction; test that a file with one bad entry leaves the table empty.
4. **Existing tests and the default DB**: wiring the loader into the lifespan must not create `data/radar.db` or break tests that use `TestClient` without `with`. Mitigation: conftest already points `DATABASE_URL` at a temp file; keep the loader out of `init_database`.
5. **Seed file packaging and path**: the file must be found independent of cwd and inside the wheel. Mitigation: path built from `Path(__file__).parent`, test run from another cwd.

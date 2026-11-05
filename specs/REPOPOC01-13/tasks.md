# Tasks: Load the watched topics as seed data

**Spec**: `specs/REPOPOC01-13/spec.md` | **Plan**: `specs/REPOPOC01-13/plan.md`
Run `uv run pytest` and `uvx ruff check .` after each phase. `[P]` = can run in parallel with other `[P]` tasks.

## Phase 1: Storage

- [x] T001 Add `description` (Text, not null, server default `''`), `keywords` (JSON, not null, server default `'[]'`) and `exclusion_keywords` (JSON, not null, server default `'[]'`) to the `topics` table in `app/db/schema.py`.
- [x] T002 Create migration `app/db/migrations/versions/0002_topic_seed_columns.py` (revision `0002`, down `0001`): inspect `topics` columns, add only missing ones with `batch_alter_table`; downgrade drops them.
- [x] T003 Extend `tests/test_db_migrations.py`: a 0001 database with an existing topic and a linked `item_topics` row upgrades to head with rows and link intact and the new defaults; a table that already has one of the columns still upgrades; a second start changes nothing.

## Phase 2: Seed file and loader

- [x] T004 [P] Create `app/seed/topics.json` with the seven topics from the spec table (name, description, keywords, exclusion_keywords). Topic 4 description says Lean means the Lean theorem prover, and its exclusions include `lean manufacturing`, `lean startup`, `six sigma`.
- [x] T005 Create `app/seed.py` with `SeedError`, `DEFAULT_SEED_PATH` (built from `__file__`), and `parse_seed(path)` that reads the JSON and validates every entry (missing/blank name, empty or all-blank keywords, wrong types, duplicate names), collecting all problems in one `SeedError` whose messages name the file and the entry as `entry N ("Name")` or `entry N (no name)`. Missing, unreadable or invalid-JSON file also raises `SeedError` naming the file.
- [x] T006 In `app/seed.py` add `load_seed(database_url, seed_path=DEFAULT_SEED_PATH)`: parse first, then in one `engine.begin()` transaction insert each topic with SQLite `ON CONFLICT (name) DO NOTHING`; use `prepare_engine` and dispose the engine in `finally`. Never update existing rows. Return the number of rows added.

## Phase 3: Start-up wiring

- [x] T007 In `app/__main__.py` call `load_seed(settings.database_url)` after `init_database` and add `SeedError` to the caught errors (prints `Invalid configuration: ...`, exit 2).
- [x] T008 In `app/main.py` call `load_seed(get_settings().database_url)` after `init_database` inside `lifespan`.

## Phase 4: Tests (temporary database, no network, no Claude Code CLI)

- [x] T009 [P] Create `tests/test_seed_load.py`: first load gives seven topics with all fields; a second load adds nothing and every column is identical (snapshot); an existing name with different values in the file is not overwritten; a new name in the file is added; loading works when the default cwd differs (`monkeypatch.chdir`).
- [x] T010 [P] Create `tests/test_seed_validation.py` using temporary seed files: missing name, blank name, empty keywords, keywords of only blanks, duplicate name, wrong types, missing file, invalid JSON each raise `SeedError` naming the file and the entry; empty `exclusion_keywords` is accepted; a file with one bad entry among valid ones writes nothing.
- [x] T011 [P] Create `tests/test_seed_file.py`: the shipped `app/seed/topics.json` parses, has exactly the seven spec names in order, each with non-empty keywords, and topic 4 has the Lean exclusions and a description that mentions the theorem prover.
- [x] T012 Extend `tests/test_main_entry.py`: with a broken seed (patched `DEFAULT_SEED_PATH` or `load_seed` raising `SeedError`) `main()` exits 2 and writes `Invalid configuration` to stderr without starting uvicorn. Add a lifespan test (`with TestClient(app)`) on a temporary database showing seven topics after start and still seven after a second start.

## Phase 5: Docs and final checks

- [x] T013 Add a short "Seed topics" section to `README.md`: file location and shape, insert-only rule (existing rows are not overwritten), whole-file rejection, how to add a topic.
- [x] T014 Run `uv run pytest` and `uvx ruff check .`; confirm `data/radar.db` was not created by the tests and nothing under `.github/`, `.specify/`, `.claude/` or `CLAUDE.md` changed.

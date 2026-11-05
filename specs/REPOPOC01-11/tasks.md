# Tasks: Read all settings from environment variables

**Input**: `specs/REPOPOC01-11/spec.md`, `specs/REPOPOC01-11/plan.md`

**Format**: `[ID] [P?] Description (files)`. `[P]` means it can run in parallel with other `[P]` tasks (different files).

## Phase 1: Setup

- [x] T001 Add the `tzdata; sys_platform == 'win32'` dependency, run `uv sync` to refresh the lock, and add `.env` to `.gitignore`. Do not add ruff. Files: `pyproject.toml`, `uv.lock`, `.gitignore`

## Phase 2: Tests first

- [x] T002 [P] Write `tests/test_settings.py` using `load_settings(mapping)` (no network, no real environment): defaults with an empty mapping (host `127.0.0.1`, port 8000, `sqlite:///data/radar.db`, `06:00`, `Asia/Kolkata`, `llm_model` and `github_token` None); one overridden value (`HOST`, `PORT`); table-driven invalid values (`PORT=abc`, `0`, `65536`, `" 80"`, `SCAN_TIME=6:00`/`24:00`/`06:60`, `SCAN_TIMEZONE=Nowhere/Land`, empty `HOST`) asserting `SettingsError` whose message names the variable; `GITHUB_TOKEN=""` is None; a sample token never appears in `repr(settings)`. Files: `tests/test_settings.py`
- [x] T003 [P] Write `tests/test_main_entry.py`: with `uvicorn.run` monkeypatched, `app.__main__.main()` passes host and port from `HOST`/`PORT` and the defaults `127.0.0.1`/8000 when unset; with `PORT=abc` it exits with code 2, writes a message naming `PORT` to stderr and does not call `uvicorn.run`. Files: `tests/test_main_entry.py`

## Phase 3: Implementation

- [x] T004 Create `app/settings.py`: frozen dataclass `Settings` (token field `repr=False`), `SettingsError(ValueError)`, `load_settings(env=None)` with strict parsers per the plan (port range, `HH:MM` regex, `ZoneInfo` check, empty-string rules), error format `NAME: expected <what>, got "<value>"`, and cached `get_settings()`. This is the only file that reads `os.environ`. Files: `app/settings.py`
- [x] T005 Create `app/__main__.py` with `main()`: call `load_settings()`, on `SettingsError` print the message to stderr and `sys.exit(2)`; otherwise `uvicorn.run("app.main:app", host=s.host, port=s.port)`; guard with `if __name__ == "__main__"`. Leave `app/main.py` unchanged. Files: `app/__main__.py`
- [x] T006 Run `uv run pytest` and make T002 and T003 pass; fix only `app/settings.py`, `app/__main__.py` or the tests as needed. Files: `app/settings.py`, `app/__main__.py`, `tests/test_settings.py`, `tests/test_main_entry.py`

## Phase 4: Documentation

- [x] T007 [P] Create `.env.example` listing `DATABASE_URL`, `HOST`, `PORT`, `SCAN_TIME`, `SCAN_TIMEZONE`, `LLM_MODEL`, `GITHUB_TOKEN`, each with its default and a one-line comment; `GITHUB_TOKEN=` left empty; no real secret. Files: `.env.example`
- [x] T008 [P] Add a "Configuration" section to the README: copy `.env.example`, export variables in the shell (no auto-loading), start with `uv run python -m app`, and show the bad-`PORT` error. Do not touch existing text otherwise. Files: `README.md`

## Phase 5: Verification

- [x] T009 Run `uv run pytest` and `uvx ruff check .`; fix findings. Confirm `grep -rn "environ\|getenv" app/` matches only `app/settings.py`, `.env.example` has no secret, and nothing changed under `.github/`, `.specify/`, `.claude/` or `CLAUDE.md`. Files: `app/`, `tests/`
- [ ] T010 Manually check: `uv run python -m app` listens on 127.0.0.1:8000 with no variables; `PORT=8123` changes the port; `PORT=abc` exits with code 2 and a message naming `PORT`. Stop the service afterwards. Files: none (verification only)

## Dependencies

T001 → T004 → T005 → T006 → T009 → T010. T002 and T003 can be written in parallel after T001 and must exist before T006. T007 and T008 can run any time after T001 and must be finished before T009.

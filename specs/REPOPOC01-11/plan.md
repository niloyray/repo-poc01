# Implementation Plan: Read all settings from environment variables

**Branch**: `REPOPOC01-11-read-all-settings-from-environment-varia` | **Date**: 2026-11-05 | **Spec**: `specs/REPOPOC01-11/spec.md`

## Summary

Add one settings module, `app/settings.py`, that is the only code reading `os.environ`. It parses and validates the seven variables of the spec into an immutable `Settings` object, using only the standard library (no new runtime dependency). Invalid values raise `SettingsError` naming the variable. A new entry point `app/__main__.py` (`uv run python -m app`) loads the settings, prints a clear error and exits non-zero on failure, and otherwise starts uvicorn on `settings.host` and `settings.port`. `.env.example` documents every variable.

## Technical Context

**Language/Version**: Python 3.12 (existing)
**Primary Dependencies**: existing `fastapi`, `uvicorn`; stdlib `os`, `dataclasses`, `zoneinfo`, `datetime`. No pydantic-settings, no python-dotenv.
**Storage**: N/A (only the `DATABASE_URL` string is parsed, not used)
**Testing**: pytest with `monkeypatch`/explicit env mappings; no network
**Project Type**: web-service (single project)
**Constraints**: fail fast on bad values; never print `GITHUB_TOKEN`; no `.github/`, `.specify/`, `.claude/`, `CLAUDE.md` edits

## Constitution Check

`.specify/memory/constitution.md` sets no gates; `CLAUDE.md` rules are followed: code in `app/`, tests in `tests/`, no secrets (`.env.example` has an empty `GITHUB_TOKEN`), ruff as a tool only. No violations.

## Design Decisions

Open questions of the spec are resolved here (spec text is not changed):

- **PORT default `8000`** (Q1).
- **`LLM_MODEL` is optional, default `None`** (unset or empty allowed at start-up); the later LLM story decides a value or makes it required (Q2).
- **No `.env` auto-loading**; `.env.example` is documentation only, variables are exported by the shell (Q3). Add `.env` to `.gitignore` if not already ignored.
- **API**: `load_settings(env: Mapping[str, str] | None = None) -> Settings` parses a mapping (defaults to `os.environ`), which makes tests network- and process-state-free. `get_settings()` is a cached wrapper (`functools.cache`) for application code. `os.environ` is read only inside `app/settings.py`.
- **Fields**: `database_url: str` (default `sqlite:///data/radar.db`), `host: str` (`127.0.0.1`), `port: int` (1-65535), `scan_time: datetime.time` (strict `HH:MM`, 24h, regex `^([01]\d|2[0-3]):[0-5]\d$`), `scan_timezone: str` validated with `zoneinfo.ZoneInfo` (`Asia/Kolkata`), `llm_model: str | None`, `github_token: str | None` (empty string treated as unset).
- **Empty values**: an empty string for an optional variable (`GITHUB_TOKEN`, `LLM_MODEL`) is unset; for variables with defaults (`DATABASE_URL`, `HOST`, `PORT`, `SCAN_TIME`, `SCAN_TIMEZONE`) an empty string is invalid, to avoid guessing. A variable that is not set at all uses its default.
- **Errors**: `SettingsError(ValueError)` with message `NAME: expected <what>, got "<value>"`, matching the spec example. The token is never parsed with validation, so its value cannot appear in any message; `Settings.__repr__` masks it (`field(repr=False)`).
- **Collecting errors**: report the first invalid variable only (simple, matches the spec example).
- **Start-up**: `app/__main__.py` calls `load_settings()`; on `SettingsError` it writes the message to stderr and exits with code 2; otherwise `uvicorn.run("app.main:app", host=..., port=...)`. `app/main.py` stays unchanged and does not read the environment.
- **Time zones**: `zoneinfo` needs the IANA database; on Windows add `tzdata; sys_platform == 'win32'` to dependencies.

## Project Structure

```text
specs/REPOPOC01-11/        # spec.md, plan.md, tasks.md
app/
├── settings.py            # NEW: Settings, SettingsError, load_settings, get_settings
└── __main__.py            # NEW: python -m app entry point
tests/
├── test_settings.py       # NEW: defaults, override, invalid values, edge cases
└── test_main_entry.py     # NEW: entry point passes host/port, exits on bad value
.env.example               # NEW: every variable, default, one-line explanation
README.md                  # add "Configuration" section
pyproject.toml, uv.lock    # tzdata marker dependency (Windows only)
.gitignore                 # ignore .env
```

**Structure Decision**: Keep the flat `app/` package; no sub-package until later stories add many settings.

## Risks

1. **Entry point wiring**: HOST/PORT only take effect when the service is started through `python -m app`; starting with plain `uvicorn ... --port` bypasses settings. Mitigation: README documents `python -m app` as the start command, and a test mocks `uvicorn.run` to check arguments.
2. **Strict validation gaps**: `int()` accepts `" 8000 "`, `"+80"`, `"8_000"`; `time.fromisoformat` accepts more than `HH:MM`. Mitigation: explicit regexes plus table-driven tests of invalid inputs.
3. **Secret leakage** via `repr`, error messages or logs. Mitigation: `repr=False` on the token and a test asserting a sample token never appears in `repr(settings)` or any error.
4. **Time zone data missing** on some platforms makes the default `Asia/Kolkata` invalid. Mitigation: `tzdata` marker dependency and a defaults test.

# Implementation Plan: Source adapter interface and shared HTTP client

**Branch**: `REPOPOC01-15-define-the-source-adapter-interface-and` | **Date**: 2026-11-05 | **Spec**: `specs/REPOPOC01-15/spec.md`

## Summary

Add a package `app/sources/` with: the common `Item` shape and the `SourceAdapter` contract (`base.py`), a shared synchronous HTTP client built on httpx with timeout, retry/back-off on 429 and 5xx, and a descriptive User-Agent (`http.py`), and a runner that executes many adapters and isolates failures (`runner.py`). Three new settings (timeout, retry count, User-Agent) are added to `app/settings.py` and `.env.example`. No concrete adapters, no database writes, no endpoints.

## Technical Context

**Language/Version**: Python 3.12 (existing)
**Primary Dependencies**: `httpx` (confirmed; moved from the dev group to runtime dependencies in `pyproject.toml`). Stdlib `dataclasses`, `logging`, `time`.
**Storage**: none.
**Testing**: pytest with `httpx.MockTransport` as the fake transport and an injected `sleep`; no network, no Claude Code CLI.
**Constraints**: no edits to `.github/`, `.specify/`, `.claude/`, `CLAUDE.md`; no secrets; ruff only as a tool; `app/settings.py` stays the only module reading the environment.

## Constitution Check

`.specify/memory/constitution.md` sets no gates. `CLAUDE.md` rules followed (code in `app/`, tests in `tests/`). No violations.

## Design Decisions

Open questions of the spec are resolved here (spec text unchanged):

- **Q1 Retry-After**: honoured on 429 (and 503) when it is a whole number of seconds; the wait is `min(value, MAX_BACKOFF_SECONDS)` with a cap of 30 s. HTTP-date form is ignored (falls back to own back-off). Own schedule: `base * 2**attempt` with base 0.5 s, capped at 30 s.
- **Q2 failure record**: `SourceFailure(source_name, error)` frozen dataclass; `run_sources` returns `ScanResult(items, failures)` and also logs one `logging` warning per failure. Nothing is persisted (database story comes later).
- **Q3 partial items**: a failed adapter contributes nothing; its items are discarded.
- **Item shape**: frozen dataclass `Item(title, url, source_name, kind, published_at, excerpt, signals)`. `title` and `url` must be non-blank (`ValueError` in `__post_init__`); `published_at: datetime | None`, `excerpt: str = ""`, `signals: Mapping[str, float | int | str] | None = None`. `kind` is a `str` (values such as `paper`, `release`, `blog`, `news` documented, matching `sources.kind`).
- **Source record**: `SourceRecord` is a small frozen dataclass `(id, name, kind, address)` mirroring the `sources` table columns; adapters read only those fields. (A Protocol was considered; a dataclass is simpler to build in tests.)
- **Adapter contract**: `SourceAdapter` is a `typing.Protocol` with `fetch(source: SourceRecord, since: datetime | None) -> list[Item]`. `since` is the last successful fetch, `None` on first fetch. Adapters receive the `HttpClient` through their own constructor.
- **HTTP client**: `HttpClient(settings-derived values, transport=None, sleep=time.sleep)`; wraps one `httpx.Client(timeout=..., headers={"User-Agent": ...}, transport=transport)`. `get(url, params=None, headers=None) -> httpx.Response`. Retries on 429 and 500-599 up to `max_retries` (so up to `max_retries + 1` attempts), also on `httpx.TransportError` (timeouts, connection errors). Other statuses (e.g. 404) are returned-as-error immediately: after the final attempt, or at once for non-retryable, the client raises `HttpError(url, status, message)`; there is no silent return of an error response. Has `close()` and context-manager support.
- **Settings**: `HTTP_TIMEOUT_SECONDS` (float, > 0, default 10), `HTTP_MAX_RETRIES` (int, 0–10, default 3), `HTTP_USER_AGENT` (non-empty, default `AIRadar/<app.__version__>`). Fields `http_timeout`, `http_max_retries`, `http_user_agent` on `Settings`; same error style as existing settings (`SettingsError` naming the variable). The User-Agent default carries no email; a value containing `@` is not rejected (the operator's choice) but the default has none.
- **Runner**: `run_sources(jobs, *, since_for=None)` where a job is `(SourceRecord, SourceAdapter)`; for each, calls `adapter.fetch(source, since)` inside `try/except Exception`, so one failure is recorded and the loop continues. Order of items follows the order of jobs. `BaseException` (KeyboardInterrupt) is not caught.

## Project Structure

```text
specs/REPOPOC01-15/            # spec.md, plan.md, tasks.md
app/
├── settings.py                # three new HTTP settings
└── sources/
    ├── __init__.py            # NEW: re-exports public names
    ├── base.py                # NEW: Item, SourceRecord, SourceAdapter
    ├── http.py                # NEW: HttpClient, HttpError
    └── runner.py              # NEW: SourceFailure, ScanResult, run_sources
tests/
├── test_settings.py           # extend: new defaults, overrides, invalid values
├── test_source_item.py        # NEW: Item validation
├── test_http_client.py        # NEW: success, retry then success, give up, 404 no retry, User-Agent, Retry-After
└── test_source_runner.py      # NEW: one failing source among several
pyproject.toml                 # httpx to runtime dependencies
uv.lock                        # refreshed by uv
.env.example                   # three new variables
README.md                      # short "Source adapters" section
```

**Structure Decision**: a new `app/sources/` package keeps adapters and the client together and separate from the DB layer.

## Risks

1. **Retry logic correctness**: off-by-one attempts, retrying non-retryable statuses, or sleeping for real in tests. Mitigation: injected `sleep`, a MockTransport that counts calls, tests for exact attempt counts (retries=3 gives 4 calls), 404 gives 1 call.
2. **Retry-After abuse / long waits**: a server could stall a scan. Mitigation: cap at 30 s, ignore non-numeric or negative values.
3. **Failure isolation too narrow or too wide**: catching too little lets one source stop the scan; catching `BaseException` would swallow Ctrl-C. Mitigation: catch `Exception` only; tests with several raising types.
4. **Settings validation changes**: existing `Settings(...)` constructions in tests break when fields are added. Mitigation: new fields get defaults placed after existing ones; extend tests.
5. **Dependency change**: moving httpx to runtime changes `uv.lock`; must stay consistent with `uv run`. Mitigation: run `uv lock` and the full test command.
6. **User-Agent privacy**: default must not leak personal data. Mitigation: test asserts the default is `AIRadar/<version>` and contains no `@`.

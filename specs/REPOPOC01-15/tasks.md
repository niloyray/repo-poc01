# Tasks: Source adapter interface and shared HTTP client

**Spec**: `specs/REPOPOC01-15/spec.md` | **Plan**: `specs/REPOPOC01-15/plan.md`
Run `uv run pytest` and `uvx ruff check .` after each phase. `[P]` = can run in parallel with other `[P]` tasks.

## Phase 1: Settings and dependency

- [ ] T001 Move `httpx` from the dev group to `dependencies` in `pyproject.toml` and refresh `uv.lock` with `uv lock`.
- [ ] T002 Add `http_timeout` (float > 0, default 10, `HTTP_TIMEOUT_SECONDS`), `http_max_retries` (int 0–10, default 3, `HTTP_MAX_RETRIES`) and `http_user_agent` (non-empty, default `AIRadar/<__version__>`, `HTTP_USER_AGENT`) to `Settings` and `load_settings` in `app/settings.py`, with `SettingsError` messages naming the variable.
- [ ] T003 [P] Add the three variables with their defaults and one-line comments to `.env.example`.
- [ ] T004 Extend `tests/test_settings.py`: defaults (including User-Agent without `@`), overrides, and invalid values (zero or non-numeric timeout, negative or too large retries, empty User-Agent) naming the variable.

## Phase 2: Common contract

- [ ] T005 Create `app/sources/base.py` with `SourceRecord` (id, name, kind, address), `Item` (title, url, source_name, kind, published_at, excerpt, signals; blank title or url raises `ValueError`) and the `SourceAdapter` Protocol `fetch(source, since) -> list[Item]`. Create `app/sources/__init__.py` re-exporting public names.
- [ ] T006 [P] Create `tests/test_source_item.py`: valid item with and without signals, URL required, blank title rejected, item is immutable, a fake adapter satisfies the Protocol.

## Phase 3: Shared HTTP client

- [ ] T007 Create `app/sources/http.py` with `HttpError` and `HttpClient(timeout, max_retries, user_agent, transport=None, sleep=time.sleep)` wrapping `httpx.Client`; `get(url, params=None, headers=None)` sends the User-Agent and timeout, returns the response on 2xx/3xx-followed success, raises `HttpError` for other statuses without retry (404 and similar), and has `close()` plus context-manager support. Add `HttpClient.from_settings(settings, ...)`.
- [ ] T008 In `app/sources/http.py` add retry with back-off: retry 429, 500–599 and `httpx.TransportError` up to `max_retries` extra attempts, wait `base * 2**attempt` (base 0.5 s, cap 30 s), honour a numeric `Retry-After` capped at 30 s, raise `HttpError` with the final status or error after the last attempt.
- [ ] T009 Create `tests/test_http_client.py` with `httpx.MockTransport` and a recording `sleep`: successful fetch; 503 then 200 succeeds with one wait; 429 with `Retry-After` uses it (and caps it); retries exhausted gives `HttpError` after `max_retries + 1` calls; 404 gives one call and `HttpError`; transport timeout is retried; User-Agent header equals the configured value; no real sleeping.

## Phase 4: Runner

- [ ] T010 Create `app/sources/runner.py` with `SourceFailure(source_name, error)`, `ScanResult(items, failures)` and `run_sources(jobs, since_for=None)`: call each adapter's `fetch(source, since)` in `try/except Exception`, log a warning per failure, discard a failed source's items, keep job order. Re-export from `app/sources/__init__.py`.
- [ ] T011 Create `tests/test_source_runner.py`: three sources where the middle one raises — items from the other two are returned, one failure names the source and error; a source that yields then raises contributes nothing; all-fail and empty-job-list cases; `since` is `None` on first fetch and passed through when given; a log line is emitted (`caplog`).

## Phase 5: Docs and final checks

- [ ] T012 [P] Add a short "Source adapters" section to `README.md`: the adapter contract, the three environment variables, and that tests use a fake transport.
- [ ] T013 Run `uv run pytest` and `uvx ruff check .`; fix failures; confirm no changes under `.github/`, `.specify/`, `.claude/` or `CLAUDE.md`.

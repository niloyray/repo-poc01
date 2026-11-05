# Tasks: FastAPI project skeleton with a health endpoint

**Input**: `specs/REPOPOC01-10/spec.md`, `specs/REPOPOC01-10/plan.md`

**Format**: `[ID] [P?] [Story] Description (files)`. `[P]` means it can run in parallel with other `[P]` tasks (different files).

## Phase 1: Setup

- [ ] T001 Create `pyproject.toml` and `.python-version`: project name `ai-radar`, `requires-python = ">=3.12,<3.13"`, `dynamic = ["version"]`, dependencies `fastapi` and `uvicorn`, dev dependency group with `pytest` and `httpx` (no ruff), hatchling build backend with `[tool.hatch.version] path = "app/__init__.py"` and wheel `packages = ["app"]`, `[tool.pytest.ini_options] testpaths = ["tests"]`, and a minimal `[tool.ruff]` section. Files: `pyproject.toml`, `.python-version`
- [ ] T002 Create the package with the single version source: `__version__ = "0.1.0"`. Files: `app/__init__.py`
- [ ] T003 Run `uv sync` to install and generate the lock file; confirm it succeeds on Python 3.12 with no ruff in the lock. Files: `uv.lock`

## Phase 2: User Story 1 - Health endpoint (P1)

- [ ] T004 [US1] Write the tests first: `GET /health` returns 200 and JSON with `status == "ok"` and `version`; `version` equals `app.__version__` and `importlib.metadata.version("ai-radar")`; `POST /health` returns 405; `GET /unknown` returns 404. Use `TestClient`, no network. Files: `tests/test_health.py`
- [ ] T005 [US1] Implement the FastAPI app with a Pydantic `HealthResponse` model and `GET /health` returning `{"status": "ok", "version": __version__}`; register no other routes. Files: `app/main.py`
- [ ] T006 [US1] Run `uv run pytest` and make T004 pass. Files: `app/main.py`, `tests/test_health.py` (fix only if needed)

## Phase 3: User Story 2 - README (P2)

- [ ] T007 [US2] Add a short "Develop locally" section to the README: `uv sync`, `uv run pytest`, `uvx ruff check .`, and `uv run uvicorn app.main:app --host 127.0.0.1 --port 8000` with a `curl http://127.0.0.1:8000/health` check and sample output. Do not touch the existing workflow text. Files: `README.md`

## Phase 4: Polish and verification

- [ ] T008 Run `uv run pytest` and `uvx ruff check .`; fix any findings. Confirm no secrets, no `0.0.0.0`, no ruff in `pyproject.toml`, and no changes under `.github/`, `.specify/`, `.claude/` or `CLAUDE.md`. Files: `app/`, `tests/`, `pyproject.toml`
- [ ] T009 Start the service on 127.0.0.1 and confirm `GET /health` answers locally (as the README says); stop the service afterwards. Files: none (verification only)

## Dependencies

T001 → T002 → T003 → T004 → T005 → T006 → T008 → T009. T007 can run any time after T001 (`[P]` with T004-T006) but must be finished before T008.

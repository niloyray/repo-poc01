# repo-poc01

Onboarded to the AINS AI-native SDLC platform (niloyray/ains-platform). Stories: Jira project `REPOPOC01`.

How a story flows: Jira story with label `ai-native` moved to **Ready** → the orchestrator claims it → spec agent (gate G1 in Jira: move to **Planning**) → plan agent (gate G2: move to **Implementing**) → implement agent → PR ready → CI (`ci` check) → review agent posts a review → a human approves the PR (gate G3) → squash merge → release: image to GHCR, **staging** (G4) and **production** (G5) environment approvals → Jira **Done**.

Human lane: branch `<JIRA-KEY>-<slug>`, open a PR, add the label `ai-review` for an agent review, same CI and gates.

Conventions: see `CLAUDE.md`. Specs per story: `specs/<JIRA-KEY>/`.

## Develop locally

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12.

```bash
uv sync                      # install dependencies
uv run pytest                # run the tests
uvx ruff check .             # lint (ruff runs as a tool, not a dependency)
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000   # start the service
```

Check it:

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok","version":"0.1.0"}
```

## Configuration

All settings are read from environment variables, and every one has a safe default, so the service runs with no configuration. `.env.example` lists each variable with its default and meaning. The file is not loaded automatically: copy it for reference and export the variables in your shell.

```bash
export PORT=8123
uv run python -m app         # start the service using HOST and PORT
```

A bad value stops start-up with a message naming the variable, and exit code 2:

```bash
PORT=abc uv run python -m app
# Invalid configuration: PORT: expected a whole number from 1 to 65535, got "abc"
```

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

## Database and migrations

Everything is stored in one SQLite file, at the path in `DATABASE_URL` (default `sqlite:///data/radar.db`, relative to the folder you start the service from). On start the service creates the file and any missing folder, then brings it to the current schema. No manual step is needed, and starting on an up-to-date file changes no data. `data/` is ignored by git.

If `DATABASE_URL` is not a SQLite file URL, or the path cannot be created or written, start-up stops with a message beginning `DATABASE_URL:` and exit code 2.

To change the schema in a later story:

1. Edit the tables in `app/db/schema.py`.
2. Run `uv run python -m app.db revision "what changed"`. This writes a new script in `app/db/migrations/versions/`.
3. Review the script. SQLite cannot alter every table in place, so check that it does not drop and re-create a table holding data.
4. Apply it with `uv run python -m app.db upgrade`, or just restart the service.

Limit: the first migration adds only missing tables. It does not repair missing columns in a table that already exists.

**Backup:** the database file is the only copy of the data and is not backed up. While the service runs, SQLite (WAL mode) also keeps `radar.db-wal` and `radar.db-shm` next to it; copy all three, or stop the service first.

## Seed topics

The watched topics live in `app/seed/topics.json`: a `topics` list of entries with `name`, `description`, `keywords` and `exclusion_keywords`. On start (after the migration) the service loads the file into the `topics` table. No manual step is needed.

- **Insert-only:** a name already in the table is never changed, so edits made later are kept. Starting again adds nothing.
- **Whole file or nothing:** a missing or blank name, an empty keyword list, a duplicate name or an unreadable file stops start-up with a message beginning `Invalid configuration: Seed file <path>:` that names the entry, and exit code 2. Nothing is written.
- **Add a topic:** add an entry with a unique name and at least one keyword (`exclusion_keywords` may be empty), then restart.

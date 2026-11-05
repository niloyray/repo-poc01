# Feature Specification: Create the SQLite schema and migration path

**Story**: REPOPOC01-12 (idea F1-S3, MVP) | **Branch**: `REPOPOC01-12-create-the-sqlite-schema-and-migration-p` | **Status**: Draft
**Depends on**: REPOPOC01-11 (settings from environment variables, provides `DATABASE_URL`)

## Goal

As a developer, I want the SQLite schema and a migration path, so that AI Radar's data survives upgrades. The service keeps everything in one database file; when the schema changes in a later story, an existing file is upgraded without losing data.

## User-visible behaviour

- On first start the service creates the database file at the path in `DATABASE_URL` (default `data/radar.db`), including any missing folder, and creates all tables. No manual step is needed.
- On every later start the existing file is opened as is. Rows are not changed, removed or re-created.
- When a later story changes the schema, the developer follows the README steps to apply the change to an existing file, with the data kept.
- The database file is not tracked by git: `data/` is listed in `.gitignore`.
- There are no new pages or endpoints.

### Data to store

| Table | Holds |
|-------|-------|
| sources | Places the radar watches (name, kind, address) |
| topics | Watched topics |
| items | Papers, releases, blog posts and news found by a scan |
| item-topic links | Which topics an item matches (many-to-many) |
| runs | One record per daily scan run (start, end, outcome) |
| digests | The daily briefing built from a run |

Item fields: title, canonical URL (unique), source, kind, published time, fetched time, excerpt, score, score reason, scoring method, summary, outside signals. Every item keeps the link to its original source.

## Acceptance criteria

- [ ] On first start the database file is created at the path from `DATABASE_URL` (default `data/radar.db`), including its folder.
- [ ] Tables exist for sources, topics, items, item-topic links, runs and digests.
- [ ] The canonical URL of an item is unique: storing a second item with the same canonical URL is rejected.
- [ ] WAL journal mode is on for the database.
- [ ] `data/` is listed in `.gitignore`.
- [ ] Starting the service on an existing database changes no data.
- [ ] The README documents how a schema change is applied to an existing file.
- [ ] Tests use a temporary database and never the default file; they use no network.

## Edge cases

- The folder of the database path already exists, or the path is just a file name with no folder: start-up still works.
- `DATABASE_URL` points to something that is not SQLite, or to a path that cannot be created or written: start-up stops with a clear message naming `DATABASE_URL` (same fail-fast rule as REPOPOC01-11).
- The file exists but is empty or has only some of the tables: start-up brings it to the current schema without touching existing rows.
- An item with a missing optional field (for example no published time, no summary, not yet scored) can still be stored.

## Out of scope

- Seed data for topics and sources.
- API endpoints and pages that read or write the data.
- Backup of the database. The file is the only copy; the README should say so.

## Open questions

1. How should schema changes be applied? Proposed: versioned migration scripts run automatically at start-up (Alembic alongside the proposed SQLAlchemy), so an upgrade needs no manual step. The alternative is a documented manual command. The story only requires the README steps.
2. Should "outside signals" be one text/JSON column on the item, or its own table? Proposed: one JSON column, since its shape is not yet defined.
3. Which values are allowed for `kind` (paper, release, blog post, news) and `scoring method`? Proposed: store as plain text now, and let the stories that produce them define the values.
4. What happens to an item's links and rows when a topic or source is deleted? Proposed: not needed yet because nothing deletes them in this story; foreign keys are enforced and deletion is decided later.

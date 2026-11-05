# Feature Specification: Read all settings from environment variables

**Story**: REPOPOC01-11 (idea F1-S2, MVP) | **Branch**: `REPOPOC01-11-read-all-settings-from-environment-varia` | **Status**: Draft
**Depends on**: REPOPOC01-10 (FastAPI skeleton with health endpoint)

## Goal

As an operator, I want every setting of AI Radar read from environment variables, so that nothing is hard-coded and the service can be reconfigured without editing code. The service must run with zero configuration, using safe local defaults.

## User-visible behaviour

- Starting the service with no environment variables set works. It uses the defaults below and listens on `127.0.0.1`.
- Setting `HOST` or `PORT` changes where the service listens.
- A bad value (for example `PORT=abc`) stops start-up with a clear message that names the variable (for example `PORT: expected a whole number, got "abc"`). The service does not start with a guessed value.
- An operator copies `.env.example` to learn every available variable, its default and what it does.

### Settings

| Variable | Default | Meaning |
|----------|---------|---------|
| `DATABASE_URL` | SQLite file `data/radar.db` | Where the single data file lives |
| `HOST` | `127.0.0.1` | Address the service listens on |
| `PORT` | see open questions | Port the service listens on |
| `SCAN_TIME` | `06:00` | Time of day for the daily scan (24h `HH:MM`) |
| `SCAN_TIMEZONE` | `Asia/Kolkata` | Time zone for `SCAN_TIME` |
| `LLM_MODEL` | see open questions | Name of the model used for ranking and summaries |
| `GITHUB_TOKEN` | unset (optional) | Optional token for higher GitHub rate limits; the only secret |

Later stories add their own settings to the same module and to `.env.example`.

## Acceptance criteria

- [ ] One settings module is the only place that reads environment variables; all other code imports settings from it.
- [ ] With no environment variables set, the service starts using the defaults and listens on `127.0.0.1`.
- [ ] `HOST` and `PORT` can be changed with environment variables and the service listens accordingly.
- [ ] `.env.example` lists every variable with its default and a one-line explanation, and contains no real secret (`GITHUB_TOKEN` is left empty).
- [ ] An invalid value (for example a non-numeric `PORT`) stops start-up with a message that names the variable.
- [ ] Tests cover the defaults, one overridden value and one invalid value, without using the network.

## Edge cases

- Empty string for an optional variable (`GITHUB_TOKEN=`) is treated as unset.
- `SCAN_TIME` not in `HH:MM` form, an unknown `SCAN_TIMEZONE`, or a `PORT` outside 1-65535 are invalid values and follow the same fail-fast rule.
- The token value is never printed in error messages or logs.

## Out of scope

- Using the settings for the database, the scheduler or the LLM; those come in later stories.
- An Anthropic API key: the service never needs one.
- Config files, command-line flags, or reloading settings while running.

## Open questions

1. What is the default `PORT`? Proposed: `8000` (the usual FastAPI/uvicorn default); the story lists no default.
2. What is the default `LLM_MODEL`? The story lists none. Proposed: no built-in model name (required later only when the LLM story needs it), or a Claude model alias chosen by that story. Should an unset `LLM_MODEL` be allowed at start-up now?
3. Should a `.env` file be loaded automatically, or is `.env.example` documentation only (variables exported by the shell)? Proposed: documentation only, no new dependency.

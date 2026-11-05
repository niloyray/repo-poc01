# Feature Specification: Source adapter interface and shared HTTP client

**Story**: REPOPOC01-15 (F3-S1, MVP) · **Needs first**: REPOPOC01-11 (settings from environment variables, already merged)

## Goal

Give AI Radar one common contract for every kind of source (papers, releases, blog posts, news) so later source adapters all return items in the same shape. Provide one shared way to fetch over HTTP, so timeouts, retries and identification are handled once, and a helper that runs many sources so one broken source never stops the daily scan.

## User-visible behaviour

There is no screen change. The behaviour is for developers writing and running source adapters:

- A developer writes an adapter that, given a source record and the time of the last successful fetch (or none for a first fetch), returns a list of items.
- Every item has: title, URL (the link to the original source), source name, kind, published time, excerpt, and optional outside signals (for example votes or stars). Adapters of any kind return this same shape.
- Adapters fetch through the shared HTTP client. It applies a timeout, retries with back-off on HTTP 429 and 5xx responses, and sends a User-Agent that names the application and its version. The User-Agent contains no personal email address.
- A helper runs a list of adapters. If one fails, the failure is recorded (which source, what error) and the remaining sources still run. The caller gets the items from the sources that worked plus the recorded failures.
- Timeout, retry count and User-Agent are configured through environment variables, listed with defaults in `.env.example`. None needs an API key.

## Acceptance criteria

- [ ] One adapter interface exists: given a source record and the time of its last successful fetch, an adapter returns a list of items in the common shape.
- [ ] The common item shape has title, URL, source name, kind, published time, excerpt and optional outside signals; URL is required so every item keeps its link to the original source.
- [ ] A shared HTTP client applies a timeout, retries with back-off on HTTP 429 and 5xx responses, and sends a descriptive User-Agent (application name and version, no personal email).
- [ ] The client gives up after the configured retry count and reports the final error to the caller; other statuses (such as 404) are not retried.
- [ ] A helper runs a list of adapters; an error in one source is recorded and does not stop the others.
- [ ] Timeout, retry count and User-Agent are settings read from environment variables, each listed in `.env.example` with a default.
- [ ] Tests use a fake transport (no network, no Claude Code CLI) and cover: a successful fetch, a retry that succeeds, and one failing source among several.
- [ ] `uv run pytest` and `uvx ruff check .` pass.

## Out of scope

- Any concrete source adapter (arXiv, GitHub, RSS and so on).
- Storing items in the database.
- Ranking, de-duplication, scheduling the daily scan.

## Assumptions

- The HTTP library is httpx, as proposed in the story; the plan may confirm it.
- Back-off waits are short in tests (injectable or zero) so tests stay fast.
- A "source record" is the existing watched-source data; this story only needs the fields an adapter reads from it.
- The default User-Agent looks like `AIRadar/<version>` with no contact details.

## Open questions

1. Should the client honour a `Retry-After` header on 429 responses, or use only its own back-off schedule? (Default assumed: honour it when present, capped.)
2. What should the failure record contain and where does it live until the database story exists? (Default assumed: a returned result object listing source name and error message, plus a log line.)
3. Should a failing adapter that returned some items before erroring keep those items? (Default assumed: no, a failed source contributes nothing.)

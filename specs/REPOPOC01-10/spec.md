# Feature Specification: FastAPI project skeleton with a health endpoint

**Story**: REPOPOC01-10 (idea F1-S1, priority MVP, release 1 of 49)

**Created**: 2026-11-05

**Status**: Draft

**Input**: "Create the FastAPI project skeleton with a health endpoint"

## Goal

AI Radar is a local, single-reader FastAPI website. This repository has no application code yet. This story gives later stories a working place to land: a runnable service, a test setup and a short README. It has one visible behaviour, a health check.

## User Scenarios & Testing

### User Story 1 - Check that the service is alive (Priority: P1)

A developer starts the service on their machine and asks `GET /health`. They get a small JSON answer saying the service is up and which version it is.

**Why this priority**: It is the only behaviour in this story. It proves the skeleton runs end to end.

**Independent Test**: Call `GET /health` through the FastAPI test client. No network is used.

**Acceptance Scenarios**:

1. **Given** the service is running, **When** a client sends `GET /health`, **Then** it receives HTTP 200 and a JSON body.
2. **Given** that response, **When** the body is read, **Then** it has a `status` field and a `version` field holding the application version.

### User Story 2 - Set up, test and start from the README (Priority: P2)

A developer who has just cloned the repository follows the README to install dependencies, run the tests and start the service locally.

**Why this priority**: Later stories depend on every developer and agent being able to run the project the same way.

**Independent Test**: Follow the README steps on a clean clone. Install succeeds, the tests pass and `/health` answers locally.

**Acceptance Scenarios**:

1. **Given** a clean clone with uv installed, **When** the developer follows the README, **Then** they can install dependencies, run the tests and start the service without other instructions.

### Edge Cases

- A request to `/health` with a method other than GET is rejected with the framework's standard "method not allowed" response.
- A request to an unknown path returns the framework's standard 404. No other routes exist yet.
- The service listens on 127.0.0.1 only, never on all interfaces.

## Requirements

### Functional Requirements

- **FR-001**: `GET /health` MUST return HTTP 200 with a JSON body containing `status` (the value `ok`) and `version` (the application version).
- **FR-002**: The application version MUST be defined in one place and MUST be the same value in the project metadata and in the `/health` response.
- **FR-003**: The project MUST be managed with uv for Python 3.12, with application code under `app/` and tests under `tests/`.
- **FR-004**: At least one test MUST call `/health` through the FastAPI test client, without the network or the Claude Code CLI.
- **FR-005**: `uv run pytest` and `uvx ruff check .` MUST both pass. ruff MUST run as a tool and MUST NOT be a project dependency.
- **FR-006**: The README MUST have a short section on installing dependencies, running the tests and starting the service locally on 127.0.0.1.
- **FR-007**: The skeleton MUST NOT contain secrets and MUST NOT need an API key.

## Acceptance Criteria

- [ ] `uv run pytest` passes with at least one test that calls the health endpoint through the FastAPI test client.
- [ ] `uvx ruff check .` passes.
- [ ] `GET /health` returns HTTP 200 with a JSON body that has a `status` field and the application version.
- [ ] Application code is under `app/` and tests are under `tests/`.
- [ ] The README has a short section on how to install dependencies, run the tests and start the service locally.

## Out of Scope

- Database, settings module, web pages and scheduler.
- A Dockerfile.
- Login, deployment to a server and any call to the network.

## Assumptions

- The reader is one developer on one machine; the service is local only.
- uv is already installed on the developer's machine.
- The `/health` JSON field for the version is named `version`. The story says only "the application version".
- The `status` value is the string `ok`.
- The health check does not look at the database or other parts, because none exist yet.
- The first version number is `0.1.0`.

## Open Questions

- None blocking. If the version field should have a different name, say so before planning. A later story may add `.env.example` entries once there are settings.

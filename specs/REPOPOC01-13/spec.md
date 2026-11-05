# Feature Specification: Load the watched topics as seed data

**Story**: REPOPOC01-13 (idea F2-S1, MVP) | **Branch**: `REPOPOC01-13-load-the-watched-topics-as-seed-data` | **Status**: Draft
**Depends on**: REPOPOC01-12 (SQLite schema and migration path)

## Goal

As a reader, I want the watched topics loaded as seed data, so that the first run already knows what to look for. The seven topics live in a seed file in the repository and are put into the `topics` table when the service starts, with no manual step.

## User-visible behaviour

- A seed file in the repository defines seven topics. Each has a name, a description, a list of keywords and a list of exclusion keywords.
- On start-up the service loads the seed file into the topics table. After the first start the seven topics are present.
- Starting again (or loading the same file twice) creates no duplicates and changes nothing: no row is added, and no value is altered.
- If a topic entry has a missing name or an empty keyword list, it is rejected. The message names the entry (its position in the file, and its name if it has one). The service does not load a partly valid file silently.
- There are no new pages or endpoints. Topics are not shown or edited here.

### The seven topics

| # | Name | Examples of what to catch |
|---|------|---------------------------|
| 1 | Knowledge graphs | GraphRAG, knowledge graph construction with LLMs, ontologies, graph databases, graph reasoning |
| 2 | AI-native SDLC | Coding agents, spec-driven development, agentic code review and testing, software engineering benchmarks |
| 3 | Business process modeling with agentic AI | BPMN and LLMs, process mining, agentic process automation, multi-agent orchestration of business workflows |
| 4 | Problem solving | Lean 4 and mathlib, automated theorem proving, OpenEvolve, AlphaEvolve-style evolutionary program search, reasoning methods |
| 5 | Algorithms | New algorithms and complexity results, algorithm discovery by AI, optimization and search methods |
| 6 | AI news of high importance | Major model launches, significant papers, policy and safety events, large industry moves |
| 7 | New releases | New versions of models, frameworks, SDKs and tools tracked by name |

For topic 4, "Lean" means the Lean theorem prover, not Lean process improvement. Its description and exclusion keywords must say so (for example, exclusions such as "lean manufacturing", "lean startup", "six sigma").

## Acceptance criteria

- [ ] A seed file in the repository defines the seven topics, each with name, description, keywords and exclusion keywords.
- [ ] On start-up the topics are loaded into the topics table.
- [ ] Loading the same file twice creates no duplicate and changes nothing.
- [ ] A topic with a missing name or an empty keyword list is rejected with a message that names the entry.
- [ ] Tests cover a first load, a repeated load and a rejected entry.
- [ ] Tests use a temporary database, no network and no Claude Code CLI.

## Edge cases

- Seed file missing or not readable, or not valid in its format: start-up stops with a clear message naming the file (same fail-fast rule as the settings story).
- Two entries in the file with the same name: rejected, naming the entry.
- A blank (whitespace-only) name or a keyword list holding only blank strings counts as missing / empty.
- An empty exclusion keyword list is allowed; only keywords are required.
- A name already in the table with different description or keywords in the file: see open question 2.

## Out of scope

- Editing topics on a page (F2-S3).
- Assigning items to topics (F4-S2).
- Showing topics anywhere in the UI.

## Open questions

1. The current topics table holds only `id` and `name`. Description, keywords and exclusion keywords need somewhere to be stored. Proposed: add the columns through a new migration in this story (keywords as a JSON list, since the schema story left the shape open).
2. When a name already exists but the file's description or keywords differ, should the file win or the database win? The story says "changes nothing" for the same file. Proposed: existing rows are never overwritten, so later edits (F2-S3) are not lost; a changed seed file only adds new topic names.
3. Seed file format and location. Proposed: a JSON or YAML file under `app/` (for example `app/seed/topics.json`); the format is the plan's decision, and no new environment variable is needed.
4. Should a rejected entry stop the whole load, or should valid entries still load? Proposed: reject the whole file (load nothing) so the table never holds a half-applied seed.

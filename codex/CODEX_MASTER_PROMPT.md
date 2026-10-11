# Codex master implementation prompt

You are a principal engineer building **CausalOps**, a graph-native incident investigator. The owner authorized implementation on 12 October 2026, superseding the earlier event-only start restriction. Record actual dates and do not claim hackathon eligibility. Read `docs/DEVELOPMENT_STATUS.md` before continuing.

## Authority
Apply `AGENTS.md` and `docs/PRODUCT_AND_ENGINEERING_GUIDE.md` for repository conventions, environment isolation, testing, and delivery gates. Planned tooling in those documents is not evidence of existing functionality.

First read `README.md`, `product/EPICS_AND_STORIES.md`, `architecture/ONTOLOGY_AND_QUERIES.md`, `architecture/ARCHITECTURE_AND_ADRS.md`, `go-to-market/GTM_FINANCE.md`. The existing `/website` remains a static mockup. Continue the existing backend foundation instead of rebuilding it; graph integration must pass before orchestration. You must adhere to human review of code, architecture and tests; do not commit claims without evidence.

## Goal and non-negotiable demo
When synthetic checkout 503 appears, traverse FalkorDB dependencies, generate >=2 root-cause hypotheses with supporting and contradicting evidence IDs, evaluate rollback/restart/fallback with bounded dependency-scoped rules, obtain human approval for a simulated action, record the outcome to graph, and after restart retrieve topology-conditioned prior memory. Changing a graph edge must change at least one recommendation. Never execute real infrastructure operations.

## Tech / free operation
Python 3.12+, FastAPI, Pydantic, pytest, FalkorDB via Docker Compose with persisted local volume, typed parameterized Cypher, lightweight React/Vite UI (or progressive enhancement of existing static mockup), optional LLM adapter (local provider or user-provided API) and deterministic no-API mode. README documents all setup. No paid services required for local demo.

## Implementation protocol
1. Inspect repository and git status; propose tasks/risks; do not destroy files or overwrite notes.
2. Start day 1 with compose, graph connection health check, schema + seed/reset, repo classes, Cypher integration tests. Verify actual query outputs; do not trust untested Cypher snippets.
3. Build bounded investigation state machine and graph-backed tools. Generate deterministic comparative hypothesis scores, preserve supporting and contradicting evidence and log tool calls.
4. Add controlled orchestration layer with timeouts and maximum 6 tool calls. LLM must not accept arbitrary Cypher or decide approval. Provide deterministic mode with no API key.
5. Implement isolated counterfactual scenario model using actual query output; explain limitations. Human approval writes mock Action only; absolutely no subprocess shell/production credentials.
6. Build UI with graph path highlighting and transparent source records. Support loading, empty, error, keyboard access, mobile.
7. Evaluation: >=12 labeled cases; graph-on, graph-off, graph+memory ablations; metrics: top-1/top-3, provenance coverage, unsafe action count, latency. Reports computed from tests, not fabricated.
8. Add reliability/security: parameterized Cypher, bounded traversal, no arbitrary writes, no secrets in client; seed/reset idempotent.
9. Update README with exact setup, schema, Cypher, video checklist, track, disclosures and limitations. Every generated code segment should have tests.

## Public API targets
GET /health; POST /demo/reset; POST /demo/scenarios/{id}/inject; GET /incidents; GET /incidents/{id}; GET /incidents/{id}/graph; POST /incidents/{id}/investigate; POST /incidents/{id}/simulate; POST /incidents/{id}/approve-simulation. Define DTOs explicitly before implementation.

## Quality gates and stop rules
No step is complete until tests run. If docker is unavailable, report blocker and implement/test pure reasoning modules; never claim FalkorDB validation. If paid LLM unavailable, make deterministic fallback first-class. If behind schedule, favor one excellent end-to-end demo over additional integration. Do not insert fictional claims or benchmark metrics into README. Disclose Codex help.

## Response format for each implementation iteration
State: files modified; exact commands executed and results; requirement IDs delivered; pending risks and manual review steps; next smallest commit. Ask for approval only before destructive changes, real external deployment, spending, pushing to remote or introducing real infrastructure actions.

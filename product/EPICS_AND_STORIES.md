# CausalOps — epics, stories and delivery contract

**Original release target:** Hackathon MVP, 15–18 October 2026 IST. **Status:** E1 foundation in progress, started Oct 12 by owner instruction; real graph validation blocked by unavailable Docker. Later epics remain planned. See [development status](../docs/DEVELOPMENT_STATUS.md). **Legend:** P0 must, P1 should, P2 future. Every acceptance test uses synthetic data.

## E1. Seeded operational graph (P0, day 1)
- **US-01 — Load topology:** As an operator I can load a reproducible microservice fixture. **AC:** 12 services, >=4 resources, >=18 typed dependency edges; two seed runs have no duplicates; source IDs stable.
- **US-02 — Query blast radius:** As an investigator I can find critical upstream callers of a failed service. **AC:** bounded <=4-hop traversal returns ordered unique service IDs and full paths; a fixture test checks expected affected and unaffected nodes.
- **US-03 — Graph change:** As an investigator I can update a simulated dependency and see downstream recommendations change. **AC:** query outputs change with graph mutation and reset restores original fixture.
- **US-04 — Data provenance:** As an auditor I can inspect timestamps and sources for evidence. **AC:** every claim references one or more evidence IDs or is tagged unverified.

## E2. Investigation engine (P0, day 2)
- **US-05 — Generate hypotheses:** As an on-call engineer I see multiple plausible causes. **AC:** >=2 hypotheses per nontrivial incident; conflicting evidence visible; none labeled confirmed without confirmation logic.
- **US-06 — Correlate changes:** As on-call I can find deployments before the incident. **AC:** bounded time window, no future deployments, no false assertion of causality from temporal correlation alone.
- **US-07 — Tool orchestration:** As operator I receive an actionable synthesis. **AC:** max 6 calls and max 2 evidence-search cycles; tool-call log visible; handles graph failure with safe error; free deterministic fallback mode works without paid API.
- **US-08 — Graph explanations:** As engineer I can open paths underlying any finding. **AC:** each suspected dependency returns node IDs, edge types, evidence sources and uncertainty.

## E3. Simulation and human controls (P0, day 3)
- **US-09 — Compare responses:** As incident commander I can compare rollback, restart and fallback. **AC:** results derived from scoped dependency subgraph + policy rules, not invented by LLM; risks and limitations shown.
- **US-10 — Approval:** As operator I explicitly approve mock actions. **AC:** no real infrastructure actions; disabled by default; simulator writes an auditable Action record, with approver, timestamp and outcome.
- **US-11 — Outcome verification:** As operator I can inspect simulated after-state. **AC:** expected vs actual fixture conditions reported; unexplained failures remain unresolved.

## E4. Experience and observability (P0, day 3)
- **US-12 — Dashboard:** As on-call I can navigate incidents, topology, evidence and recommended actions. **AC:** responsive at 375/768/1440px; proper empty/loading/error states; keyboard access and labels.
- **US-13 — Graph interaction:** As investigator I can select a node, inspect metadata, and highlight paths. **AC:** clicking hypothesis highlights relevant exact traversals; node details from API; no fabricated edges.
- **US-14 — Investigation timeline:** As auditor I can follow a decision chronologically. **AC:** event ordering, source attribution, tool results and action state appear in sequence.

## E5. Memory & evaluation (P0, day 4)
- **US-15 — Persistent incidents:** As on-call I can retrieve prior similar incidents after restart. **AC:** persistent graph volume; retrieval conditioned on topology and failure modes; incident IDs never collide.
- **US-16 — Benchmark:** As judge I can run graph-on and graph-off scenarios. **AC:** at least 12 seeded incidents, frozen fixture labels, accuracy and evidence coverage measured, run commands in README.
- **US-17 — Reproducibility:** As judge I can reproduce demo without secrets. **AC:** Docker startup, seed/reset, test command, demo script, environment example; no hard-coded secret or confidential data.

## E6. Security, operations, commercialization (P1 / post-hackathon)
- **US-18 (P1) — Workspaces:** scoped per-tenant graph and access policy; cross-tenant negative tests.
- **US-19 (P1) — Read-only connectors:** ingest synthetic OTEL/GitHub change events; explicit permissions and dedupe.
- **US-20 (P1) — Durable control plane:** bounded retries, backpressure, audit retention, health checks.
- **US-21 (P2) — Real actions:** require threat modeling, approval, least privilege, staged rollout and rollback plan before enabling.
- **US-22 (P2) — Product analytics:** track activated workspaces, time-to-first-investigation, scenario completion, evidence coverage, retention; no surveillance-like employee metrics.

## Definition of ready
Story has owner, fixture, API contract, acceptance criteria, failure mode and test case. No story may require paid services to demonstrate locally.

## Definition of done
Code + unit/integration tests + reproducible fixture + accessible UI + no secret leakage + documented known limitations + reviewer verification. Generated code must be understood and manually reviewed.

## Sprint gates
- **Day 1 (hard stop):** graph tests pass before building orchestration.
- **Day 2:** if LLM unreliable, keep deterministic ranking and make LLM optional explanation only.
- **Day 3:** if interface delayed, ship a single strong incident screen instead of multiple thin tabs.
- **Day 4:** no new major features; run benchmark and record reproducible demo.

## Ownership / RACI (solo founder)
Founder acts as PM + backend + front-end + QA + security + release owner; Codex is an assistant not an accountable actor. External reviewers may challenge architecture/UX but cannot approve production risk on founder's behalf.

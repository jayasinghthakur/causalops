# CausalOps Owner and AI Engineer Interview Guide

This is the owner’s end-to-end explanation of CausalOps. Use it to prepare for product, architecture, AI engineering, security, and operations interviews. It distinguishes the current graph foundation from the planned incident investigator so that no planned behavior is presented as shipped.

## The 60-second explanation

CausalOps is an incident investigation system for small SaaS engineering teams. When an alert says that checkout is failing, the operator needs more than a list of symptoms: they need the affected dependency paths, competing explanations, evidence for and against each explanation, the risks of possible responses, and a record of what was decided. CausalOps models services, resources, deployments, incidents, evidence, hypotheses, and actions as a graph in FalkorDB. Deterministic graph tools establish facts; an optional bounded AI layer explains and coordinates those tools; a human approves simulated responses. The system never treats a dependency path or a time correlation as proof of causality.

The current implementation is the graph foundation: FastAPI, a validated synthetic topology, parameterized bounded queries, CLI seed/reset, evidence references, and tests. The incident engine, LLM layer, action simulator, persistence workflow, frontend integration, and production controls are still planned.

## The problem and why it matters

During an incident, information is split across alerts, service ownership, dependency diagrams, deployment records, logs, runbooks, and prior incident notes. Flat search produces plausible but weak answers. A topology-aware investigator can narrow the search space and show exactly why a finding was returned. The buyer is not purchasing an “AI that fixes production”; the value hypothesis is reduced investigation effort and better evidence coverage for teams without a dedicated SRE platform.

The initial customer profile is a SaaS team with roughly 5–30 engineers and 5–20 services. The first user is an on-call engineer, the champion is a staff or lead engineer, and the economic buyer is a founder or VP Engineering. The first discovery questions are about the last real incident, how topology is maintained, where false leads came from, which actions require approval, and what data can be accessed safely.

Why this scope: it tests whether graph structure improves investigation quality before expensive connectors or production automation are built. Why not start with real customer telemetry: it introduces privacy, security, integration, and support obligations before the core reasoning value is proven. Why synthetic data: it gives reproducible ground truth and makes unsafe action impossible.

## Product flow from alert to memory

The target workflow is:

```text
Alert or scenario
  → identify affected service
  → traverse bounded dependency paths
  → gather deployments, alerts, and evidence
  → generate competing hypotheses
  → attach supporting and contradicting evidence
  → rank hypotheses deterministically
  → compare scoped simulated responses
  → await explicit human approval
  → record simulated outcome and audit event
  → retrieve topology-conditioned incident memory
```

The first demonstration is a synthetic checkout 503 incident. A payment deployment and Redis timeout are temporally correlated. The system should show a likely regression hypothesis, a transient dependency-failure hypothesis, and a weak symptom-only hypothesis. It should explain that the deployment is a candidate cause, not proof. It should compare rollback, restart, and fallback using the affected subgraph and policy rules, then record a mock approval without executing infrastructure commands.

## Why the architecture is graph-first

The authoritative relationships are multi-hop and typed: `Service CALLS Service`, `Service DEPENDS_ON Resource`, `Deployment DEPLOYED_TO Service`, `Incident HAS_ALERT Alert`, and `Hypothesis SUPPORTED_BY Evidence`. A graph makes path traversal and provenance explicit. FalkorDB is selected because the project requires a graph database and the MVP needs local, open-source operation.

The API is a modular FastAPI application. Routes validate input and return stable DTOs. Services coordinate workflows. Pure domain code ranks and applies policy without importing FastAPI, FalkorDB, or an LLM SDK. The graph repository is the only layer that executes Cypher. This keeps query safety and test responsibility in one place.

The current foundation exposes read-only `GET /health`, `GET /topology`, `GET /services/{service_id}/impact`, and `GET /evidence/{evidence_id}` routes. Seed, reset, and dependency mutation are CLI-only. The target API later adds incident injection, investigation, simulation, approval, incident retrieval, and graph views. The existing website is intentionally separate until real graph integration passes.

Why one application: the MVP needs reviewability more than independent service scaling. Why one orchestrator: a bounded coordinator is easier to debug and evaluate than a multi-agent swarm. Why not a relational database as a second source of truth: duplicating topology would create synchronization and provenance problems. Why not a frontend rewrite now: it would test presentation before the graph contract is proven.

## Graph model and query reasoning

The fixture currently contains 12 services, four resources, six endpoints, six journeys, one evidence record, and 32 typed edges. IDs are stable. Every relationship points to a synthetic evidence record. The impact query starts at a failed service and searches incoming critical `CALLS` paths from one to four hops. It excludes cyclic paths, returns at most 50 paths, and reads one extra row internally to report truncation.

The result is classified as `potential_impact`. It includes ordered unique caller IDs, full node paths, relationship types, evidence IDs, hop counts, and a caveat. The query never returns “root cause.” A path answers “what may be affected if this service is unhealthy,” not “what caused the incident.”

Parameterization is required because it prevents Cypher injection and lets FalkorDB reuse execution plans. Traversal, result, evidence-window, and timeout limits are product safety controls as well as performance controls. Query failures return an explicit unavailable error; they do not produce a fabricated answer.

## AI engineering design

The deterministic layer is the source of truth. It performs graph traversal, time-window filtering, evidence joins, rule-based ranking, policy checks, and simulation calculations. An optional model may select from an allowlisted set of tools and turn verified results into a concise explanation. It may not invent nodes, edges, evidence IDs, scores, approvals, or actions.

The proposed investigation state machine is `intake → gather → hypotheses → contradictions → rank → response options → await human → record`. It has a maximum of six tool calls and two evidence-search cycles. Each tool call is logged with inputs, outputs, timing, and errors. The model is given evidence as data, so log text or a runbook cannot override system policy through prompt injection.

Why deterministic-first: it works without a paid model, provides a benchmarkable baseline, and makes safety failures visible. Why an LLM at all: explanation, tool selection, and summarization are language-heavy tasks after the facts are known. Why not let the LLM write Cypher: arbitrary queries create injection, cost, data exposure, and unbounded traversal risks. Why not call a confidence score a probability: fixture scores are comparative ranking signals without calibration data.

The model evaluation must compare the same frozen incidents in graph-on, graph-off, and graph-plus-memory modes. Report top-1/top-3 hypothesis accuracy where labels exist, provenance coverage, unsafe-action count, failures, and latency. Keep labels outside the model-visible input. Real-provider evaluations are separate from deterministic CI and must record model, prompt, provider, budget, and version.

## Safety and security position

MVP actions are simulations only. There is no shell execution, restart, rollback, or production write. Approval is an explicit server-side state transition with an authenticated approver in hosted environments, an idempotency rule, a timestamp, and an audit record. A browser-supplied name is not an approver identity.

Treat telemetry, logs, runbooks, and model output as untrusted input. Use parameterized allowlisted queries, bounded hops and rows, strict IDs, timeouts, output encoding, origin controls, and deny-by-default action policy. Do not expose graph credentials to the browser. Keep local, test, preview, staging, and production databases, credentials, volumes, and permissions separate; an environment variable alone is not isolation.

The main threats are arbitrary Cypher, prompt injection, cross-tenant leakage, malicious action requests, secrets in logs, SSRF through source references, deep traversal denial of service, and uncontrolled model cost. Interviewers should hear the control paired with each threat, not a generic “we added security.”

## Testing strategy

Unit tests cover pure ranking, evidence handling, policy decisions, timestamps, and state transitions. Graph integration tests run real FalkorDB and verify Cypher syntax, edge direction, idempotent seeding, affected and unaffected services, cycles, hop limits, truncation, mutation/reset, and restart persistence. API contract tests validate DTOs, stable errors, request IDs, and unavailable-database behavior. Browser tests later use Playwright to cover the actual alert-to-approval journey at mobile and desktop widths.

Fixtures use stable IDs, fixed UTC timestamps, expected paths, contradictory evidence, permitted responses, and outcome labels. Each test run uses a disposable graph or unique test namespace. It must fail clearly when Docker is unavailable rather than silently using an in-memory substitute. The current foundation has 33 unit and contract tests; real graph integration remains blocked until Docker is available.

Testing questions to answer in an interview:

- How do you know the seed is idempotent? Run it twice and compare node/edge state and stable IDs.
- How do you test a graph query without trusting a mock? Execute it against a pinned FalkorDB image.
- How do you stop a path from becoming a causal claim? Return potential impact, provenance, uncertainty, and contradictory evidence as separate fields.
- How do you test model safety? Feed malformed tool output, invented IDs, prompt-injection text, timeouts, and tool-limit exhaustion through a deterministic adapter.
- What does coverage mean here? Domain branch coverage is useful, but safety invariants, integration behavior, and frozen evaluation cases matter more than a single percentage.

## Delivery and ownership model

The owner is accountable for product priority, architecture, security, release, and customer promises. AI assistance can generate code and suggestions but cannot approve production access or claim a passing test it did not run. Each story needs a user problem, fixture, API contract, acceptance examples, failure mode, owner, reviewer, and rollback impact.

Work moves through `Backlog → Ready → In progress → Review → Verified → Done`, with a blocked state that names the unblock condition. The delivery order is graph foundation, deterministic investigation, connected experience and simulation, then memory and evaluation. Do not add real connectors or production actions while an earlier gate is failing. A strong single incident workflow is more valuable than several disconnected screens.

Release promotion uses the same immutable artifact from CI to staging to production. Before a pilot, prove authentication, read-only scopes, workspace isolation, deletion, backup restore, support ownership, and consent. Before production, prove capacity, recovery objectives, migration rollback, monitoring, alert ownership, and incident response. A successful demo is not production readiness.

## Current implementation interview answer

“I started with E1 because the product’s central claim depends on graph evidence. I implemented a Python 3.12/FastAPI boundary, an official FalkorDB client repository, a versioned synthetic fixture, parameterized four-hop critical-call traversal, provenance, local/test environment guards, CLI administration, and unit/API tests. Ruff and mypy pass, and 33 unit/contract tests pass. Docker is not available in the current machine, so I explicitly mark real FalkorDB integration, container startup, persistence, and E1 acceptance as pending. I will not add an LLM or claim the graph works until the real integration suite passes.”

This answer demonstrates judgment: build the riskiest product assumption first, separate verified facts from plans, and make blockers visible instead of hiding them.

## Likely interview questions and strong answers

**What is the product’s unique value?** Graph-backed evidence paths, topology-conditioned memory, graph-change sensitivity, and human-controlled simulated responses. It is an investigative reasoning layer, not an observability replacement or autonomous remediation bot.

**Why can’t a dependency path identify the root cause?** Dependency expresses potential propagation. Causality also requires temporal, operational, and contradictory evidence. The system labels hypotheses and uncertainty instead of asserting proof.

**Why not use embeddings alone?** Similar wording does not guarantee structural similarity. Retrieval can supplement memory, but incident memory must include topology and failure mode conditions.

**Why use an LLM if deterministic rules exist?** Rules establish and constrain facts. The model helps choose a bounded investigation sequence and explain verified evidence. It never becomes the authority for graph truth or approval.

**What happens if FalkorDB is down?** The API returns a structured 503 with a request ID. It does not return a cached or invented investigation result. Later, resilience can add bounded retries and a clearly labeled degraded mode.

**How would you add customer integrations?** Start read-only, define explicit scopes, validate and deduplicate events, namespace data, test tenant isolation, and obtain consent. Do not connect production telemetry before the local synthetic workflow and security boundary are proven.

**When would you enable real actions?** Only after a separate threat model, least-privilege credentials, policy engine, staged rollout, approval protocol, audit integrity, rollback strategy, and production recovery evidence. It is outside the MVP.

**What would make you stop or pivot?** If interviews do not show repeated investigation pain, if two design partners will not repeat a pilot, or if graph-on does not improve evidence quality over a flat-data baseline. A narrower blast-radius or incident-memory product may then be more valuable.

## Owner checklist before claiming readiness

- [ ] I can explain one complete incident flow and its failure cases.
- [ ] I can identify which behavior is implemented, tested, planned, or blocked.
- [ ] I can show the exact evidence ID behind every graph finding.
- [ ] I can explain why a model is bounded and what it is forbidden to do.
- [ ] I can run unit, contract, integration, browser, security, and benchmark checks at the appropriate milestone.
- [ ] I can describe local/test/staging/production differences without treating configuration names as isolation.
- [ ] I can explain approval, audit, backup, restore, rollback, and incident ownership.
- [ ] I can state what the latest measured result is and what remains an assumption.

Keep this guide synchronized with [development status](DEVELOPMENT_STATUS.md), [architecture decisions](../architecture/ARCHITECTURE_AND_ADRS.md), [the product backlog](../product/EPICS_AND_STORIES.md), and the [engineering guide](PRODUCT_AND_ENGINEERING_GUIDE.md). When an implementation decision changes, update the interview answer and the relevant ADR together.

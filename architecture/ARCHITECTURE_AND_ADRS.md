# CausalOps architecture and decision records

## Context / boundaries
Static prototype is viewable in `/website`. A local FastAPI/FalkorDB foundation is under development in `/backend`; real database validation and frontend integration remain pending. Target architecture: browser → FastAPI → validated tools → FalkorDB; optional LLM for bounded explanation; simulator for synthetic events and mock remediations. No real production actions or customer data.

## ADR-006: Local graph foundation first

**Accepted for implementation, 12 October 2026.** The owner instructed development to begin now; record actual dates rather than treating the earlier event plan as completed history. Use Python 3.12, uv lockfiles, FastAPI, and the official FalkorDB client. Keep the existing static frontend separate until graph integration passes. Alternatives were a frontend rewrite or immediate LLM integration; neither validates the graph-first product assumption. Review this choice after E1 acceptance.

Foundation HTTP routes are read-only: `/health`, `/topology`, `/services/{service_id}/impact`, and `/evidence/{evidence_id}`. Seed, reset, and dependency mutation are CLI-only. The unauthenticated foundation accepts only local/test configuration and must not be deployed publicly. Integration tests use a separate database service and unique graph names. The pinned container and query behavior require real-database validation before E1 is marked complete.

## Components
1. **Web application:** command center, interactive graph, evidence panel, remediation comparison, incident history. Accessibility and responsive requirements apply.
2. **REST/SSE API:** `GET /health`, `POST /demo/reset`, `POST /demo/scenarios/{id}/inject`, `GET /incidents`, `GET /incidents/{id}`, `GET /incidents/{id}/graph`, `POST /incidents/{id}/investigate`, `POST /incidents/{id}/simulate`, `POST /incidents/{id}/approve-simulation`. Distinguish future planned APIs from implemented website.
3. **Graph repository:** explicit Cypher query registry, Pydantic request/response DTOs, parameter validation, bounded hops, namespaced seeded graphs.
4. **Investigation service:** bounded state machine: intake → gather → hypotheses → contradictions → rank → response options → await human → record.
5. **Policy engine:** allowlist action kinds, deny real commands, require explicit approval, audit every state change.
6. **Simulator:** reproducible fixed incident scenarios with fixture ground truth and reset capability.
7. **Evaluation:** graph-on, graph-off and graph-plus-memory comparison with fixed labels.

## ADR-001: FalkorDB as primary graph store
**Accepted.** Incident reasoning requires typed multi-hop topology and provenance. Avoid parallel authoritative relational graph representation in MVP. Trade-off: operational deployment and Cypher testing complexity.

## ADR-002: Single orchestrator over multi-agent swarm
**Accepted.** One bounded coordinator with deterministic graph tools reduces debugging, latency and cost. Stretch multi-agent only if objective benchmark improves.

## ADR-003: Zero-cost local-first
**Accepted.** Docker + Python + frontend + synthetic fixtures; optional local LLM. Do not require paid LLM/hosting; static site may be published separately on a free tier. Trade-off: limited always-on multi-user availability.

## ADR-004: Simulation-only execution
**Accepted.** Real remediation can disrupt services. Mock actions only in MVP. All approvals auditable and no shell execution.

## ADR-005: Evidence before language
**Accepted.** Deterministic ranking with source IDs; LLM summarizes and selects bounded tools but cannot invent nodes, edges, evidence or numeric confidence.

## Security / privacy / reliability
Threats: prompt injection from logs/runbooks; arbitrary Cypher execution; cross-tenant leakage; malicious action requests; secrets leakage; SSRF in source refs; denial of service via deep traversal; uncontrolled costs. Controls: treat evidence as data; parameterized allowlisted graph queries; bounded hop/window/row/iterations; per-tenant isolation later; sample fixtures only; no secret in browser; action deny-by-default; rate limits for deployment; backups and retention later. A failure to reach DB returns a clear error instead of a fabricated answer.

## Operational requirements
- Local health endpoint, predictable seed reset, docker compose setup, environment example, deterministic tests.
- For production: TLS, auth, RBAC, tenant isolation, backups, SLO definition, audit integrity, observability, tracing, retention policy, incident response runbook, abuse protection, secret vault, legal review.

## Performance and SLO hypotheses
Hackathon target: <3 seconds for graph-only local query chain on seeded dataset (measure; not guaranteed); bounded 4-hop graph exploration; 50 max paths; no specific LLM response-time promises. Commercial SLOs must be based on pilot load tests.

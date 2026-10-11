# CausalOps · From alerts to evidence-backed action

**Status: graph foundation under development; static concept website available.** The repository now includes a FastAPI graph API, synthetic fixtures, Docker configuration, and automated tests. Real FalkorDB integration and container startup are not yet verified on the development machine because Docker is unavailable. Investigation, action workflows, benchmarks, and frontend integration are still planned. See [development status](docs/DEVELOPMENT_STATUS.md).

Implementation began on 12 October 2026 following the owner's instruction to start now, superseding the earlier planned start date. Do not present this work as having begun during the hackathon window or assume submission eligibility.

![License: MIT](https://img.shields.io/badge/license-MIT-blue) ![Stage: Foundation](https://img.shields.io/badge/stage-foundation-orange)

## Backend foundation

Use Python 3.12 and uv 0.13.0 for host development. `make bootstrap` installs locked dependencies and downloads Python if needed. This workspace already has uv in `.bootstrap/bin/uv`; on a fresh checkout install uv first, or create the same isolated bootstrap:

```bash
python3 -m venv .bootstrap
.bootstrap/bin/python -m pip install uv==0.13.0
make bootstrap
make check
make test-unit
```

With Docker Engine/Desktop and Compose v2 installed and running:

```bash
make up                 # Build API and start persistent local FalkorDB
make seed               # Load 12 services, 4 resources, and 6 journeys
make test-integration   # Separate disposable test database on port 6380
```

Open `http://localhost:8001/docs` for the read-only API. Routes: `GET /health`, `GET /topology`, `GET /services/payment/impact`, and `GET /evidence/evidence-topology-v1`. Health checks the FalkorDB module; it does not imply the fixture has been seeded. Graph failures return HTTP 503, not mocked results.

`make reset` replaces only the local synthetic dataset. `make down` stops services and retains the local volume. `make api` runs the API on the host for development after starting the graph. Run `make test` for all mandatory checks; it fails when Docker/integration infrastructure is missing. Current validation and remaining gaps are recorded in [development status](docs/DEVELOPMENT_STATUS.md).

The frontend below remains a standalone mockup and is not yet connected to this API. Production/staging configuration is deliberately rejected by the foundation backend.

## Interactive website — run now

```bash
cd website
python3 -m http.server 8000
# open http://localhost:8000
```

The website shows an interactive **synthetic** incident scenario, dependency illustration, hypothesis explanations, a non-executing response comparison, incident history mockup and roadmap. It has no backend or LLM, and does not persist data.

## Product mission

An incident investigator that traverses service and infrastructure dependencies in FalkorDB, compares competing hypotheses against observed evidence, identifies likely blast radius, evaluates simulated corrective actions and records reproducible incident memory.

## Planned architecture

Browser (React or equivalent) → FastAPI → bounded LLM orchestrator → validated graph tools → FalkorDB. Separately: seeded event simulator and safety-gated mock action executor. The LLM proposes; deterministic graph logic returns evidence; a person approves actions.

## Read the planning package

- `docs/PRODUCT_AND_ENGINEERING_GUIDE.md` — end-to-end product delivery, decision rationale, coding standards, environment separation, testing setup, project management, and production readiness gates.
- `docs/OWNER_AI_ENGINEER_INTERVIEW_GUIDE.md` — owner-level product, architecture, AI engineering, safety, testing, operations, tradeoff, and interview notes.
- `docs/CausalOps_PRD.docx` — complete product requirements, scenarios, success criteria, roles, security, finance, GTM.
- `docs/CausalOps_Pitch_Deck.pptx` — 12-slide presentation.
- `product/EPICS_AND_STORIES.md` — testable backlog, milestones and definitions of done.
- `architecture/ONTOLOGY_AND_QUERIES.md` — planned graph model and Cypher designs.
- `architecture/ARCHITECTURE_AND_ADRS.md` — architecture decisions and threat model.
- `codex/CODEX_MASTER_PROMPT.md` — implementation prompt to use once event opens.
- `codex/BUILD_WITH_CODEX.md` — reproducible development workflow.
- `go-to-market/GTM_FINANCE.md` — customer discovery, free-cost model, pricing hypotheses.

## Four-day execution

1. Oct 15: build live FalkorDB graph, schema, validated tools and deterministic fixtures.
2. Oct 16: bounded agent with evidence/contradiction checks and explainable hypotheses.
3. Oct 17: frontend live graph results, action simulations, approvals and persistent history.
4. Oct 18: benchmark graph-on vs graph-off, security review, record demo, document setup and submit.

## Zero-budget approach

Use local Docker, Python, FalkorDB Community/open source, synthetic data, local/static website and optional local LLM. Free-to-start does **not** imply free production hosting, free third-party APIs, or reliable 24/7 availability. The website can be hosted as a static site on Cloudflare Pages free tier subject to plan limits. Keep API + graph database local for hackathon judging if no cost-free persistent service is available.

## Hackathon rules / responsibility

Official rules: https://www.wemakedevs.org/hackathons/falkordb/rules
Main coding and design must start after Oct 15 at 00:01 IST. Pre-event brainstorming/notes/sketches allowed. Disclose coding assistants. Do not claim simulated metrics as measured. Use only authorized data. Submit public source, queries, schema, demo video, deployment or complete local setup, and chosen track. Explain and verify every generated component.

## Security guardrails

No prod credentials; no real rollback/restart command in MVP; deny arbitrary shell/graph writes from the LLM; validate IDs, parameterize Cypher; approval before stateful actions; secrets in environment; no real customer telemetry in sample dataset.

## License

MIT (see LICENSE). Proposed submission track: **01, Agents That Act on Connected Data**.

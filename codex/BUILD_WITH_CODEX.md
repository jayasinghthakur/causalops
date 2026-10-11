# End-to-end Codex playbook (zero-budget local-first)

Use the [Product and Engineering Guide](../docs/PRODUCT_AND_ENGINEERING_GUIDE.md) for coding standards, decision rationale, environment separation, test setup, project management, and pilot/production gates. The day-by-day workflow below covers the hackathon subset; proposed commands must be implemented and verified before use.

## Before Oct 15 — allowed preparation only
Original event plan: preparation only before Oct 15. The owner subsequently authorized implementation on Oct 12; this supersedes the repository's start restriction, not external eligibility rules. Keep actual dates in [development status](../docs/DEVELOPMENT_STATUS.md). Read docs and stories, choose fixtures, and verify applicable submission rules before claiming eligibility.

## Tools needed
Git, Python 3.12+, Docker Desktop/Engine, editor/terminal, Node.js LTS for React if chosen, Codex installed or accessible in ChatGPT/IDE. Optional local LLM runtime; no API subscription required for deterministic baseline. Do not paste keys or prod logs into prompts.

## Day-by-day Codex workflow
### 15 October: graph first
Prompt Codex: `Implement E1/US-01–04 only. Set up FalkorDB Docker Compose, graph health, idempotent seed fixtures, parameterized query functions, bounded 4-hop impact traversal and integration tests. Do not build AI or UI yet. Run tests and show exact output.`
Review generated graph types, variable-length Cypher support, relationship directions, edge counts and fixture expected paths. Commit only after testing.

### 16 October: safe diagnosis
Prompt Codex: `Implement E2/US-05–08 with evidence provenance, conflicting evidence, rule-based ranking, optional bounded LLM tool selection, deterministic mode. Max six tool calls; no arbitrary Cypher; test false-correlation scenarios.`
Review hypothesis justification and negative cases. Do not call scores calibrated probabilities.

### 17 October: demo experience
Prompt Codex: `Implement E3+E4 against the actual backend: interactive topology, hypothesis path highlights, simulated action approval, scenario reset and incident history persisted in FalkorDB. No real commands. Add loading/error states and smoke tests.`
Review API mapping and whether selecting graph entities shows exact evidence IDs.

### 18 October: evaluation and ship
Prompt Codex: `Freeze feature set. Implement labeled benchmark of >=12 incidents, graph-on vs graph-off ablation, unit/integration/e2e smoke tests, security review, README and demo checklist. Print actual results; don't invent metrics. Prepare 3-minute script and blog outline.`
Manually demonstrate from empty local environment. Record video. Submit before 23:59 IST.

## Operator guide: local concept site (available now)
```bash
cd website && python3 -m http.server 8000
```
Visit http://localhost:8000; click **Inject incident**; inspect graph/hypotheses; use **Response simulator**; click **Approve simulated action**; reset. These are all client-side interactions, not a running backend.

## Operator guide: planned hackathon backend
The foundation now defines `make up`, `make seed`, `make reset`, `make check`, `make test-unit`, `make test-integration`, and `make test`. Container/graph validation is pending Docker availability. `make demo` and `make benchmark` remain unimplemented. Follow the README for current setup; incident simulation and action audit workflows are later milestones.

## GitHub publication
Create a new public repo on github.com, upload the project only after reviewing rules and commit history. Do not publish secrets. Name it `causalops` (or unique available variant). Add screenshots/demo gif after there is an eligible working build. GitHub Actions can run Python unit tests and static lint once code exists. Prefer public reproducible local setup over unstable free backend hosting.

## Deploy marketing website for free
Cloudflare Pages → connect GitHub → select repo → build command **none** → output directory `website` (if project root is repo root). Consult current UI docs; deploy limits apply. This static deployment shows the product concept, not a live incident engine. For hackathon submission provide reproducible local Docker setup if backend not hosted.

## Troubleshooting guide
- Graph connection refused: inspect container status/port/auth and startup wait.
- Duplicate seeds: use MERGE by stable IDs and rerun idempotency test.
- Empty paths: inspect relationship direction and critical flag.
- Cypher unsupported: use simpler tested queries; retain contract tests.
- LLM hallucinates edges: restrict tool outputs; validate evidence IDs server-side; use deterministic fallback.
- Container costs: avoid cloud instance; keep local. Track memory/CPU usage.
- Frontend shows false results: mark static prototype explicitly; backend mode should display API status and data source.
- LLM expenses: no API key means deterministic baseline, not failure.

## Verification checklist
[ ] all required graph tools use actual FalkorDB; [ ] first-run and second-run seed stable; [ ] no unsupported query syntax; [ ] visible provenance; [ ] adversarial contradictory evidence case; [ ] mock-only action; [ ] restart persistence; [ ] tests pass; [ ] demo video reproducible; [ ] Codex usage disclosed; [ ] commit timestamps honest.

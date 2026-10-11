# CausalOps Product and Engineering Guide

Planning baseline: 12 October 2026. This guide covers discovery, implementation, testing, delivery, and operation. Foundation implementation has started; consult [development status](DEVELOPMENT_STATUS.md) and the README for implemented commands and validation evidence. Later-stage tooling below remains a requirement until implemented and verified.

Build one reproducible investigation first: inject a synthetic checkout failure, query dependencies, compare hypotheses with evidence, compare simulated responses, record human approval, and retrieve the investigation after restart. Expand only when that workflow is reliable and useful to target users.

## 1. How to use this guide

Start with [repository instructions](../AGENTS.md), the [backlog](../product/EPICS_AND_STORIES.md), [architecture decisions](../architecture/ARCHITECTURE_AND_ADRS.md), and [ontology](../architecture/ONTOLOGY_AND_QUERIES.md). This guide supplies delivery practices; those documents define the product and existing architectural commitments. Resolve contradictions explicitly and update affected documents together.

The repository records a hackathon implementation window of 15–18 October 2026 IST. Preserve that planning boundary unless the owner explicitly changes the project scope. Before implementation, finalize scenarios, contracts, and expected results. Treat event eligibility as requiring verification against official rules before submission; these dates are repository planning assumptions, not a new verification of event rules.

## 2. Product discovery and scope

The initial user is an on-call engineer at a SaaS team with 5–30 engineers and 5–20 services. The job is to reduce investigation effort by exposing dependencies, evidence, uncertainty, and response risks. The product must not imply that a dependency path proves causation.

Follow the [discovery plan](../go-to-market/GTM_FINANCE.md): interview 10 engineers and 5 leaders about recent incidents, current investigation workflows, false leads, topology maintenance, and approval constraints. Record observations separately from assumptions. Do not request production credentials during discovery.

For every proposed feature, record:

- User and concrete problem, with interview or incident evidence.
- Desired outcome and how it will be measured.
- Smallest workflow that tests the hypothesis.
- Explicit exclusions, dependencies, risks, and acceptance examples.
- Decision date, owner, and evidence needed to continue or stop.

MVP scope is synthetic incidents, graph-backed evidence, deterministic diagnosis, mock responses, and persistent history. Customer connectors, tenancy, billing, and real remediation are separate milestones. Validate the product before investing in broad integration coverage.

Continue toward pilots when at least three independent teams describe the unmet need, two agree to repeat pilots, and graph-based investigation improves evidence quality against the baseline. These are decision gates from the GTM plan, not achieved results. Track time to first investigation, repeat usage, and usefulness of findings; synthetic accuracy is not a production MTTR claim.

## 3. Build sequence and completion gates

Dates below are targets from the repository plan. If a gate fails, reduce scope or move the milestone; a date does not override a failing gate.

| Stage | When | Deliverable | Exit evidence |
| --- | --- | --- | --- |
| Preparation | Before implementation window | Three scenario specifications, API contracts, expected graph paths, task ownership | Each first-stage story meets definition of ready |
| Graph foundation | Day 1, Oct 15; US-01–04 | Local FalkorDB, health checks, seed/reset, provenance, bounded queries | Real-database tests pass; two seeds create no duplicates; graph mutation changes results |
| Investigation | Day 2, Oct 16; US-05–08 | Deterministic ranking, conflicting evidence, bounded orchestration | At least two hypotheses for nontrivial incidents; evidence IDs verified; failure fallback tested |
| Complete workflow | Day 3, Oct 17; US-09–14 | API-connected UI, simulation, approval, timeline | Browser workflow passes; approval is recorded once; no infrastructure action executes |
| Evaluation and delivery | Day 4, Oct 18; US-15–17 | Persistent history, benchmark, setup instructions, demo | Restart persistence; at least 12 labeled cases; clean-machine reproduction |
| Design-partner pilot | After demo and discovery gate | Authorized read-only ingestion and authenticated access | Isolation, deletion, restore, support ownership, and pilot consent verified |
| Production | After operational readiness review | Supported deployment with measured capacity and service objectives | Release, security, recovery, monitoring, and incident-response gates met |

First implementation tasks: define fixture truth; pin compatible dependencies; establish a health-checked local graph; implement repeatable seed/reset; implement impact queries; test affected and unaffected services; expose the validated result through FastAPI. Do not start orchestration until graph tests pass.

## 4. Architecture choices and when to revisit them

Existing ADR-001–005 remain accepted planning decisions. Additional choices below are proposed implementation defaults. Record acceptance dates when actually accepted; do not invent historical decisions.

| Choice | Why | Adopt when | Revisit when |
| --- | --- | --- | --- |
| FalkorDB as authoritative graph | Dependency traversal and evidence relationships are central to the product; required by current project scope | Foundation; existing ADR-001 | A measured query, reliability, or deployment limitation blocks requirements |
| One modular Python/FastAPI application | Keeps API, graph access, and reasoning reviewable without distributed-service overhead | Foundation; proposed | Independent scaling or ownership is demonstrated by measurements |
| Deterministic reasoning before optional LLM | Provides a repeatable baseline, explainable evidence, and no-key operation | Investigation; ADR-005 | An evaluated LLM improves a defined task without bypassing policy |
| One bounded orchestrator | Limits tool calls, cost, and debugging complexity | Investigation; ADR-002 | A controlled benchmark justifies additional coordination |
| Retain and connect the existing website initially | Shortens the path to testing the full workflow | UI integration; proposed | Interaction complexity justifies a documented React/Vite migration |
| Docker Compose for local services | Makes database version and lifecycle reproducible | Foundation; ADR-003 | Hosted operation has separate reliability and capacity requirements |
| Simulation-only actions | Allows workflow validation without production disruption | Every MVP milestone; ADR-004 | A separately reviewed real-action product has scoped credentials, policy, and recovery controls |
| Promote immutable release artifacts | Ensures staging validates the code actually deployed | First hosted release; proposed | Never replace traceable promotion with ad hoc production edits |

Create an ADR before changing a database, framework, public contract, trust boundary, deployment model, or material dependency. Include status, date, owner, context, alternatives, choice, consequences, evidence, rollout, reversal plan, and review trigger. Supersede old ADRs rather than silently rewriting their rationale.

## 5. Repository and module boundaries

Proposed layout; create each part as its milestone needs it:

```text
backend/
  pyproject.toml          # Dependencies and Python tool configuration
  app/
    api/                 # HTTP routes, DTOs, authentication boundary
    domain/              # Pure scoring, policies, and state transitions
    graph/               # Parameterized query registry and repository
    services/            # Investigation and simulation coordination
    adapters/            # Optional LLM and future connector adapters
    config.py            # Validated environment settings
  tests/
    unit/
    integration/
    contract/
    security/
    conftest.py
fixtures/                # Versioned synthetic topology and scenario truth
tests/e2e/               # Browser workflows
tests/performance/       # Repeatable bounded-load experiments
evaluation/              # Benchmark runner and frozen case definitions
website/                 # Existing static frontend
ops/                     # Release, backup, recovery, and incident runbooks
compose.yaml             # Local services; not a production readiness claim
Makefile                 # Documented developer command interface
.github/workflows/       # CI checks once implemented
```

Routes validate requests and call services. Services coordinate domain logic and repositories. Domain functions do not import web frameworks, graph clients, or LLM SDKs. Only graph repositories execute Cypher. Browser code never accesses graph credentials. Adapters translate external data into validated internal records.

## 6. Coding and API guidelines

- Python: four-space indentation, snake_case functions/modules, PascalCase classes, uppercase constants. Add types to public functions and explicit DTOs at boundaries. Adopt Ruff formatting/linting and mypy during foundation setup; commit their configuration.
- JavaScript and CSS: two-space indentation for new multiline code, camelCase functions, kebab-case CSS and DOM IDs. Preserve existing navigation hooks. Adopt ESLint and Prettier with configuration in a dedicated change; avoid mixing wholesale formatting with feature work.
- Keep functions focused on one domain responsibility. Prefer explicit inputs and outputs over global mutable state. Comment why a policy exists; do not narrate obvious syntax.
- Represent timestamps in UTC with timezone information; convert only for display. Validate IDs, time windows, enums, limits, and missing values. Never conflate missing evidence with evidence of health.
- Parameterize query values and allowlist query shapes. Bound traversal to four hops, output to 50 paths, and orchestration to six tool calls and two evidence-search cycles as specified in the plan. Test limits server-side.
- Keep ranking rules versioned and deterministic. Return supporting and contradicting evidence IDs, source timestamps, and explicit unknowns. Comparative scores are not calibrated probabilities.
- Use structured errors with stable codes and request IDs. Distinguish invalid input, missing entities, forbidden access, dependency failure, and timeout. Do not return synthetic success when the graph fails.
- Use text-safe DOM rendering for untrusted values. Existing fixture-only HTML construction must be reviewed before rendering API, log, or model content.
- Add explicit timeouts and bounded retries at network boundaries. Retry reads or operations with proven idempotency; never duplicate an approval or action on retry.
- Pin a tested dependency set and commit the selected lockfiles. Update dependencies through a reviewed change with relevant regression checks. Do not copy unverified version numbers into setup instructions.

Specify request/response examples before implementing each API. Include error cases, pagination or result bounds, authentication requirements, and idempotency behavior. Keep the target endpoints in the architecture document synchronized with generated OpenAPI output. Introduce explicit API versioning before external clients depend on it.

Approval identity must come from authenticated server context in hosted environments, not a browser-supplied name. Local synthetic identity must be visibly marked. Enforce action transitions server-side, use an idempotency key or equivalent uniqueness rule, and test simultaneous approval requests. Approval and its audit event must not diverge on partial failure; verify atomicity or implement a recoverable state transition protocol against the selected database version.

## 7. Environment separation

An environment variable is not an isolation boundary. Separate credentials, database instances, network access, volumes, and deployment permissions as appropriate. Namespaced graphs help organize tests but do not replace security isolation.

| Environment | Purpose and data | Lifecycle | Access and action policy |
| --- | --- | --- | --- |
| Local | Developer iteration with synthetic fixtures | Persistent developer volume; explicit reset | Bind services to loopback; mock actions only |
| Automated test | Deterministic unit, integration, and browser checks | Disposable instance and unique graph per run/worker | Test credentials only; no route or credentials to production |
| Preview | Optional review of a branch | Temporary isolated synthetic data; expire after review | Authenticated if hosted; no customer connectors |
| Staging | Validate a release candidate and operational procedures | Production-like configuration with separate secrets and storage | Restricted access; synthetic or explicitly approved sanitized data |
| Production | Authorized customer workloads | Durable storage, backups, retention, monitored migrations | Authenticated users, tenant enforcement, least privilege; real actions remain disabled |

Use the same application artifact across staging and production, with validated environment configuration. Local developer reload and test overrides must be unavailable in production. Keep the public static concept website separate from any claim of a live service.

Define a configuration contract for `APP_ENV`, graph endpoint/name, allowed origins, log level, LLM mode, and feature flags. Proposed values are `local`, `test`, `preview`, `staging`, and `production`. Fail startup on unknown environments or unsafe combinations. Production must reject demo/reset routes, synthetic authentication, debug mode, and missing required secrets. A flag alone must never authorize real actions.

Commit `.env.example` with placeholders and safe local defaults. Keep `.env` files ignored, inject CI secrets through the CI secret store, and use a managed secret mechanism for hosted environments. Never place secrets in frontend build variables, screenshots, logs, or test artifacts. Use separate secrets per environment and rotate exposed credentials.

Reset and test setup must verify the environment, an allowlisted test endpoint, and an owned graph identifier before destructive operations. Refuse ambiguous targets. Clean up only resources created by that run; never use broad database deletion as teardown.

## 8. Local setup and command contract

Available today, from repository root:

```bash
python3 -m http.server 8000 --directory website
# Visit http://localhost:8000
node --check website/app.js  # Optional: requires Node.js; syntax only
```

During foundation implementation, select and record tested Python, Node, Docker, and FalkorDB versions. Create a Python virtual environment, install locked development dependencies, and keep browser-test dependencies in a locked Node manifest. Run the API on a documented separate port, for example 8001, while the website uses 8000. Configure an exact local origin allowlist or a same-origin development proxy.

Implement these root commands before advertising them as available:

| Proposed command | Required behavior |
| --- | --- |
| `make bootstrap` | Check prerequisites; install locked development dependencies; never overwrite existing secrets |
| `make up` | Start local graph and API; wait for readiness with a deadline |
| `make seed` | Load the versioned synthetic fixture idempotently |
| `make dev` | Start documented frontend development serving |
| `make check` | Check formatting, lint, types, and configuration without modifying files |
| `make test-unit` | Run pure unit tests without Docker or paid APIs |
| `make test-integration` | Provision isolated real FalkorDB; test queries, persistence, and API integration |
| `make test-contract` | Validate API schemas and adapter input/output contracts |
| `make test-security` | Run authorization, input, injection, and environment-guard regression tests |
| `make test-e2e` | Start an isolated full application and run browser workflows |
| `make test` | Run checks and mandatory deterministic test suites; fail on missing required infrastructure |
| `make benchmark` | Evaluate frozen cases and produce machine-readable results |
| `make test-performance` | Run a bounded synthetic load profile outside production |
| `make demo` | Prepare the documented synthetic demonstration without silently erasing other data |
| `make reset` | Reset only the explicitly selected local demo dataset |
| `make down` | Stop local services while preserving data volumes |

Document ports, readiness failures, volume locations, resource requirements, and recovery steps. Verify setup on a clean machine or clean CI runner. Commands should return nonzero on failure; a skipped database suite cannot be reported as passing integration validation.

## 9. Testing setup and coverage

Use pytest for Python tests and Playwright for browser workflows. Choose test cases by risk and acceptance criteria, not by implementation line count. Adopt a proposed minimum of 80% branch coverage for domain and policy modules once instrumentation exists; any exception needs an owner and explanation. Critical safety invariants need explicit negative tests regardless of coverage percentage.

| Layer | Required examples | Run when |
| --- | --- | --- |
| Unit | Ranking ties, missing evidence, timestamp boundaries, policy denial, state transitions | Every relevant change and PR |
| Graph integration | Real Cypher syntax, direction, cycles, deduplication, four-hop boundary, 50-path cap, mutation/reset | Every PR affecting backend or fixtures; full release suite |
| API contract | Valid and invalid DTOs, stable errors, unknown IDs, timeouts, bounded output | API/adapter changes and releases |
| Persistence | Restart graph/API and retrieve incident, evidence, approval, memory | Persistence changes and releases |
| Concurrency | Duplicate inject requests, repeated approval, conflicting updates, partial write failure | Stateful workflow changes and releases |
| Browser | Injection through history, exact path highlighting, options, approval, reset, backend outage | UI/API changes and releases |
| Accessibility | Keyboard navigation, focus, labels, contrast, 375/768/1440px layouts | UI changes; manual review before release |
| Security | Arbitrary Cypher denial, prompt injection, XSS payloads, origin/auth rules, cross-tenant denial when tenancy exists | Relevant changes and releases |
| Evaluation | Frozen labels, graph-on/off/memory comparison, false correlation and contradictory evidence | Reasoning/fixture changes and releases |
| Performance | Representative graph sizes, concurrent requests, timeout behavior, p50/p95 latency | Query changes and release candidates |
| Operations | Configuration rejection, startup, migration, backup restore, rollback, dependency outage | Deployment changes and hosted releases |

### Fixture and database setup

Use `conftest.py` fixtures for clocks, IDs, domain objects, API clients, and graph lifecycle. A session fixture may start a pinned test database; each mutating test gets its own graph or clean namespace, including a worker suffix for parallel execution. Register strict pytest markers such as `integration`, `contract`, and `security`. Teardown must execute after failures and only remove owned test resources. Pytest fixtures support reusable setup and teardown; use them to prevent order-dependent tests. See [pytest fixture guidance](https://docs.pytest.org/en/stable/how-to/fixtures.html).

Name tests by behavior: `test_impact_excludes_noncritical_caller`, `test_approval_replay_creates_one_action`, and `test_future_deployment_is_not_candidate`. Mock external LLM/network behavior for unit tests, but use actual FalkorDB for repository and query tests. Test missing Docker as a reported blocker, not a silent mock substitution.

Version fixtures with stable IDs, fixed UTC timestamps, expected affected and unaffected services, supporting and contradicting evidence, permitted responses, and expected outcomes. Implement the planned 12 services, at least four resources, at least 18 typed dependency edges, and six journeys. Freeze at least 12 evaluation cases covering outage, healthy siblings, fallback saturation, overlapping incidents, missing telemetry, stale memory, conflicting evidence, forbidden remediation, absent ownership, duplicate alerts, and false deployment correlation.

### Browser setup

Create `playwright.config.ts`, a locked development dependency, and `tests/e2e/*.spec.ts`. Configure an isolated base URL, app readiness, fresh browser context per test, stable accessible locators, failure screenshots, and traces. Begin with Chromium on PRs; run the declared supported-browser matrix before hosted releases. Wait for UI state rather than arbitrary sleeps.

After the manifest exists, CI installs dependencies with `npm ci`, installs the matching browsers with `npx playwright install --with-deps`, and runs `npx playwright test`. Provision the backend and graph before browser tests. Retain failure artifacts without secrets or customer data. See [Playwright CI setup](https://playwright.dev/docs/ci).

### LLM and benchmark checks

The default suite runs without model credentials. Use deterministic adapter doubles for malformed output, invented IDs, timeout, tool-limit exhaustion, and prompt injection carried in evidence. Validate model-selected tools and IDs server-side. Optional real-provider evaluations use explicit budgets and report provider/model/prompt versions; they are separate from deterministic CI.

Keep labels outside inputs available to the investigator. Freeze evaluation fixtures separately from tuning scenarios; reset memory between cases unless testing memory deliberately. Report case count, top-1/top-3 accuracy on eligible labeled cases, provenance coverage, unsafe-action count, failures, and latency with hardware and version details. Compare the same cases across modes. Do not silently discard errors or reinterpret labels after seeing results.

Every test report records commit ID when available, fixture version, environment, command, pass/fail/skip counts, and artifacts. Fix flaky tests rather than hiding them behind retries. A quarantined noncritical test needs a tracked issue and expiry; approval and isolation tests cannot be waived by quarantine.

## 10. Project management and review

Maintain one backlog with `Backlog → Ready → In progress → Review → Verified → Done`, plus an explicit blocked state with owner and unblock condition. Keep one implementation story active per developer where practical. Split work into changes that can be reviewed independently; avoid a single PR containing infrastructure, reasoning, and a frontend rewrite.

Use this issue template:

```text
Story ID and title:
User problem and evidence:
Owner and reviewer:
Outcome, scope, and exclusions:
Dependencies and decision records:
Acceptance examples, including failure cases:
Environment and data impact:
Test plan and release/rollback impact:
Estimate, risks, and target milestone:
Evidence links and final validation:
```

Ready means the fixture, contract, acceptance criteria, failure cases, and dependencies are understood. Done means implementation, relevant tests, documentation, review, and milestone acceptance are complete. Code merged and code deployed are distinct statuses.

At the start of each day, select the next smallest dependency-ready story. At day's end, record demonstrated behavior, actual checks, blockers, and next steps. Weekly after the hackathon, review customer evidence, product metrics, technical risks, operating costs, and scope. Maintain a risk register with probability, impact, owner, mitigation, and review date.

The founder owns product priorities, release decisions, and operational accountability until roles are assigned. Automated assistants can implement and review but do not approve customer access or production readiness. For a solo workflow, record a deliberate self-review; seek independent review before handling customer data or changing access boundaries.

Recommended branches: `feat/US-02-impact-query`, `fix/approval-idempotency`, and `docs/environment-guide`. Use concise imperative commits, such as `feat: bound impact traversal to four hops`. This checkout has no Git history, so these are proposed conventions. Initialize and configure version control before implementation tracking begins; do not fabricate historical commits.

PRs must explain the problem, resulting behavior, linked story/ADR, checks actually run, data/config changes, known limits, and rollout/rollback impact. Include screenshots for UI changes. If scope changes, update the acceptance criteria and estimates explicitly. Keep speculative refactoring separate.

## 11. CI and release management

Implement PR checks in this order: locked dependency installation; formatting/lint/types; unit tests; isolated graph and contract tests; security regressions; browser smoke tests; fixture validation and benchmark checks for reasoning changes. Always run the full mandatory suite on release candidates. Later add dependency, secret, and container scanning with reviewed findings and explicit exception expiry.

Do not provide production secrets to PR jobs, especially untrusted contributions. Use minimal CI permissions and reviewed action versions. Configure required checks on the protected main branch once a remote exists.

For a hosted release:

1. Select a reviewed commit and assign a release version. Capture dependency locks, fixture/schema versions, and an immutable artifact identifier.
2. Run the release suite and build once. Record results and unresolved issues.
3. Back up affected state and rehearse migration and restoration in staging. Prefer backward-compatible additions before removing old fields or edges.
4. Deploy the artifact to staging; verify investigation, authentication, audit, persistence, and operational checks.
5. The named release owner reviews evidence and authorizes production deployment. Record the release time, owner, artifact, migration, and rollback target.
6. Promote the same artifact to production, run nondestructive smoke checks, and observe errors, latency, and dependency health against agreed thresholds.
7. Roll back or disable the affected feature if thresholds fail. Record customer impact and follow-up work.

Schema changes require a migration ledger, repeatability checks, interrupted-migration handling, and compatibility tests. An application rollback cannot undo an incompatible graph migration. Define whether recovery uses a forward fix, compatible old artifact, or validated restore before deployment. Never use fixture reset as production migration tooling.

## 12. Production operations and security gates

Local success does not establish hosted readiness. Before customer traffic, assign owners for deployment, incident response, security, backups, and support. Define expected workload, latency/availability objectives, acceptable data loss (RPO), and acceptable restore time (RTO) with stakeholders. Test recovery against those objectives before promising them.

Hosted deployment must explicitly cover HTTPS, startup, restart, replication strategy, and resource consumption. Choose process and container settings after measuring the workload; a container alone does not provide these operating guarantees. See [FastAPI deployment concepts](https://fastapi.tiangolo.com/deployment/concepts/).

Required pilot/production controls:

- Authenticate users; authorize every incident, evidence, and action access. Before multiple customer workspaces, test tenant separation across queries, memory retrieval, exports, and background work.
- Start connectors read-only with explicit scopes. Validate webhook signatures where applicable, deduplicate events, bound retries, and make revocation work. Treat logs/runbooks as untrusted data.
- Keep the graph private, restrict network egress where practical, and use least-privilege service credentials. Do not expose arbitrary URL fetches or Cypher from user/model input.
- Define data retention, deletion, export, and backup expiry. Avoid storing raw sensitive telemetry unless needed and authorized. Test deletion without destroying another workspace's records.
- Collect structured logs with request/incident IDs, query duration, investigation outcome, and dependency errors. Redact secrets and avoid high-cardinality or personal data in metric labels.
- Alert on user-impacting failures, graph unavailability, sustained latency, storage pressure, failed backups, and approval/audit failures. Every alert needs an owner and action.
- Keep audit records attributable and access-restricted. Test backup restoration into an isolated environment and verify recovered incidents, evidence links, and approvals.
- Monitor model usage, compute, storage, and support costs per investigation/workspace. Set budgets before optional paid providers are enabled.

Create runbooks for deploy/rollback, graph outage, corrupt or missing data, failed migration, secret exposure, provider outage, and backup restoration. During an incident: assess impact, assign an incident owner, contain harm, preserve evidence, communicate status, recover, and verify. Afterwards, document causes, contributing conditions, and owned corrective actions.

## 13. Milestone acceptance checklists

### Local MVP

- [ ] Fresh setup works using documented commands and no paid API.
- [ ] Real graph queries, idempotent seeding, bounds, and provenance tests pass.
- [ ] Full incident-to-simulated-outcome workflow works with visible uncertainty.
- [ ] Approval replay is safe and history survives restart.
- [ ] Frozen benchmark and graph-off comparison produce actual recorded results.
- [ ] Synthetic disclosures, limitations, and assistant contributions are documented.

### Customer pilot

- [ ] Discovery gate met and pilot objectives agreed with participants.
- [ ] Authorized read-only ingestion, authentication, isolation, deletion, and revocation tested.
- [ ] Staging, backups, restore procedure, support owner, and incident channel ready.
- [ ] Data handling, costs, and success/stop criteria agreed before access.

### Production release

- [ ] Required checks pass for the exact release artifact.
- [ ] Operational objectives, capacity, restore, and rollback are verified.
- [ ] Security findings have dispositions and accountable owners.
- [ ] Monitoring, release ownership, support, and customer communication are ready.
- [ ] Production seed/reset and debug paths are disabled; real remediation remains outside scope.

These gates are intentionally separate. A convincing demo validates a workflow; pilot and production readiness require additional evidence about customer value, access boundaries, and reliable operation.

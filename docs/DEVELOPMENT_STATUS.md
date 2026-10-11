# CausalOps Development Status

## Foundation iteration on 12 October 2026

The owner instructed implementation to begin now. This supersedes the earlier repository start restriction, not external hackathon rules. Codex generated and locally reviewed this foundation. No Git history or remote exists in this checkout; no commit, hosted CI run, or deployment is claimed.

## Implemented scope

- Python 3.12/FastAPI application with read-only health, topology, service impact, and evidence routes; generated OpenAPI documentation.
- Official FalkorDB client repository with parameterized queries, four-hop critical CALLS traversal, cyclic-path exclusion, a 50-path response cap, and truncation signaling.
- Versioned synthetic topology: 12 services, four resources, six endpoints, six journeys, one evidence record, 20 dependency edges, and 12 journey/endpoint edges.
- CLI seed, reset, health, and dependency-criticality mutation. Writes are limited to local/test targets; no mutation HTTP endpoints or arbitrary query API.
- Separate local/test Compose services, a persistent local volume, loopback-only exposed ports, and a non-root API container definition.
- Locked Python dependencies, Ruff, mypy, pytest, coverage enforcement for the small domain module, and a CI workflow including real graph integration and restart persistence.

These are implementation artifacts. Database query correctness, container startup, and persistence are not yet validated locally.

## Validation evidence

| Check | Actual result |
| --- | --- |
| Runtime/dependency setup | Python 3.12.15 and uv 0.13.0 installed in repository-local environments; dependencies resolved into `backend/uv.lock` |
| `make check` | Passed: Ruff lint and formatting; mypy checked 12 application source files |
| `make test-unit` | 33 unit/API-contract tests passed |
| Domain coverage | 100% of the current 12-statement domain module; this is not whole-backend or integration coverage |
| `node --check website/app.js` | Passed; existing website was not changed |
| Live API startup | Started successfully on localhost:8001 |
| Live `/health` without database | HTTP 503 with `graph_unavailable` and matching request ID header/body |
| Live `/openapi.json` | HTTP 200 |
| `make test-integration` | Blocked: `docker: No such file or directory`; no integration pass claimed |
| Image build, graph seed/query, restart persistence, hosted CI | Not run; require a running Docker/Compose installation |

The installed Starlette test client emits one deprecation warning about its httpx compatibility path. It does not fail the tests; review the test transport dependency during the next dependency update.

## Story acceptance state

| Story | State | Remaining gate |
| --- | --- | --- |
| US-01 topology | Implemented, awaiting integration | Confirm real graph counts and duplicate-free repeated seed |
| US-02 impact | Implemented, awaiting integration | Confirm exact paths, healthy siblings, noncritical exclusion, hop limit, cycles, and truncation |
| US-03 graph change | CLI implemented, awaiting integration | Confirm changed query results and reset restoration; recommendations come in E2 |
| US-04 provenance | Topology provenance implemented, awaiting integration | Resolve every returned evidence ID; later incident claims need equivalent provenance |
| E2–E6 | Not started | E1 real-database gate first |

## Next execution sequence

1. Install/start Docker with Compose v2 on the development machine.
2. Run `make test-integration`; fix any query/image compatibility failures before claiming E1 acceptance.
3. Run `make up`, `make seed`, and inspect `http://localhost:8001/docs`.
4. Seed again and compare topology; restart graph/API and verify identical stored state. The CI workflow defines this check but has not executed yet.
5. Complete E1 acceptance review; then implement deterministic investigation and incident evidence before optional LLM behavior.

For a host API with a containerized graph, run `docker compose up -d --wait falkordb`, then `make api`. Do not also run the container API on port 8001. Run `make down` to stop the Compose services without deleting the local volume.

To demonstrate the dependency mutation after seeding:

```bash
curl --fail http://localhost:8001/services/payment/impact
docker compose exec -T api .venv/bin/python -m app.cli set-critical checkout payment false
curl --fail http://localhost:8001/services/payment/impact
make reset
```

The direct checkout-to-payment path should disappear after mutation. Checkout can still be potentially affected through orders and billing; multiple valid paths are deliberately retained.

## Boundaries and known limitations

The existing website is still an independent static demonstration. Impact currently starts from a Service and follows incoming CALLS edges only; it does not diagnose resource failures or prove causality. There is no LLM, incident orchestrator, authentication, customer data, real remediation, benchmark runner, or production deployment.

This foundation rejects staging/production settings. Reset is a local destructive operation followed by seeding, not an atomic production migration. Queries have deadlines, but concurrency and full failure recovery remain later work. Docker images are version-tagged rather than digest-pinned; image promotion and production hardening remain pending.

## Implementation references

The official [FalkorDB client API](https://falkordb-py.readthedocs.io/en/stable/falkordb.html) supplies parameterized query and read-only query methods. [FalkorDB query documentation](https://docs.falkordb.com/commands/graph.query) describes query parameters and timeouts. The pinned image's [startup script](https://github.com/FalkorDB/FalkorDB/blob/v4.22.0/build/docker/run.sh) sets its data directory explicitly; the Compose volume targets that directory. These references informed implementation, not a claim that local integration passed.

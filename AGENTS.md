# Repository Guidelines

## Project Structure & Module Organization

CausalOps contains a graph foundation under development, planning materials, and a static concept website. The full incident engine is not implemented.

- `website/`: `index.html` defines views, `styles.css` provides responsive styling, and `app.js` handles synthetic scenarios and inline SVG graphs. There is no separate asset directory.
- `architecture/`: planned architecture, decision records, graph ontology, and query designs.
- `product/`: epics, user stories, and acceptance criteria.
- `codex/`: implementation prompts and development playbook.
- `go-to-market/`: commercial assumptions and financial planning.
- `docs/`: Word PRD and PowerPoint pitch deck.
- `docs/OWNER_AI_ENGINEER_INTERVIEW_GUIDE.md`: owner-level product, architecture, AI, safety, testing, and interview notes.
- `backend/`: FastAPI application, graph repository, pytest suites, and locked dependencies.
- `fixtures/`: validated synthetic topology; `compose.yaml` separates local and test databases.

Follow [Product and Engineering Guide](docs/PRODUCT_AND_ENGINEERING_GUIDE.md) for delivery, decisions, environment isolation, testing, and releases. Proposed tooling requires implementation before use.

## Build, Test, and Development Commands

Run from the repository root:

```bash
python3 -m http.server 8000 --directory website
```

Open `http://localhost:8000` for the standalone demo.

Backend commands: `make bootstrap` installs locked dependencies with uv; `make check` runs Ruff and mypy; `make test-unit` runs unit/contract tests. With Docker running, `make up`, `make seed`, and `make test-integration` start and verify the graph stack. `make test` includes all mandatory checks. See README for prerequisites.

## Coding Style & Naming Conventions

Use typed Python, four-space indentation, snake_case functions, and Ruff formatting in the backend. Keep domain logic independent of database and HTTP frameworks. Preserve camelCase JavaScript, kebab-case CSS/DOM IDs, and navigation hooks in the website; use two-space indentation for new multiline code. Planning documents use uppercase descriptive filenames.

## Testing Guidelines

Pytest tests use `test_*.py`. Domain branch coverage must reach 80%. Integration tests require actual FalkorDB at localhost:6380 and unique test graphs; never substitute mocks or silently skip missing infrastructure. For website changes, manually check navigation, injection, graph highlights, response options, approval, reset, and responsive layouts. Record actual results in `docs/DEVELOPMENT_STATUS.md`.

## Commit & Pull Request Guidelines

This checkout has no `.git` history, so existing commit conventions cannot be verified. Use concise imperative subjects, for example `docs: clarify simulation boundaries`. Describe the change, link applicable story IDs such as `US-01`, report validation, and include screenshots for visual changes.

## Scope & Safety

Preserve synthetic-data disclosures. Never add production credentials, customer telemetry, or real remediation commands. Distinguish planned features from verified behavior. Record actual implementation dates and assistant contributions per `README.md`.

UV := $(if $(wildcard .bootstrap/bin/uv),$(CURDIR)/.bootstrap/bin/uv,uv)
export UV_CACHE_DIR := $(CURDIR)/.cache/uv
export UV_PYTHON_INSTALL_DIR := $(CURDIR)/.tools/python
RUN = $(UV) run --directory backend --frozen

.PHONY: help bootstrap check test test-unit test-integration up seed reset down dev api
help:
	@echo "bootstrap check test-unit test-integration test up seed reset down dev api"

bootstrap:
	$(UV) sync --project backend --frozen

check:
	$(RUN) ruff check app tests
	$(RUN) ruff format --check app tests
	$(RUN) mypy app

test-unit:
	$(RUN) pytest tests/unit tests/contract --cov=app.domain --cov-branch --cov-fail-under=80

test-integration:
	docker compose --profile test up -d --wait --wait-timeout 90 falkordb-test
	$(RUN) pytest tests/integration

test: check test-unit test-integration

up:
	docker compose up -d --build --wait --wait-timeout 120 falkordb api

seed:
	docker compose exec -T api .venv/bin/python -m app.cli seed

reset:
	docker compose exec -T api .venv/bin/python -m app.cli reset

down:
	docker compose --profile test down

dev:
	python3 -m http.server 8000 --bind 127.0.0.1 --directory website

api:
	$(RUN) uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload

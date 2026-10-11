FROM ghcr.io/astral-sh/uv:0.13.0 AS uv
FROM python:3.12-slim
COPY --from=uv /uv /usr/local/bin/uv
WORKDIR /workspace/backend
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev
COPY backend/app ./app
COPY fixtures /workspace/fixtures
RUN useradd --uid 10001 --create-home causalops
USER causalops
EXPOSE 8001
CMD [".venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]

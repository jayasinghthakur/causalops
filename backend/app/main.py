"""Read-only foundation API. Local mutations are CLI-only."""

from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.responses import Response

from app.api.models import EntityId, EvidenceResult, HealthResult, ImpactResult, TopologyResult
from app.config import Settings
from app.graph.repository import (
    EntityNotFound,
    GraphLimitExceeded,
    GraphRepository,
    GraphUnavailable,
)


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings()
    repository = GraphRepository(config)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        yield
        repository.close()

    app = FastAPI(
        title="CausalOps Graph Foundation",
        version="0.1.0",
        description="Local synthetic topology and potential impact. No live incident engine.",
        lifespan=lifespan,
    )
    app.state.repository = repository

    @app.middleware("http")
    async def request_id(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request.state.request_id = str(uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response

    def error(request: Request, status: int, code: str, message: str) -> JSONResponse:
        return JSONResponse(
            status_code=status,
            content={
                "error": {"code": code, "message": message, "request_id": request.state.request_id}
            },
        )

    @app.exception_handler(GraphUnavailable)
    async def graph_error(request: Request, exc: GraphUnavailable) -> JSONResponse:
        return error(
            request, 503, "graph_unavailable", "FalkorDB is unavailable or the query failed."
        )

    @app.exception_handler(EntityNotFound)
    async def missing_entity(request: Request, exc: EntityNotFound) -> JSONResponse:
        return error(request, 404, "not_found", str(exc))

    @app.exception_handler(GraphLimitExceeded)
    async def limit_error(request: Request, exc: GraphLimitExceeded) -> JSONResponse:
        return error(request, 409, "graph_limit_exceeded", str(exc))

    @app.exception_handler(RequestValidationError)
    async def invalid_input(request: Request, exc: RequestValidationError) -> JSONResponse:
        return error(request, 422, "invalid_input", "Request parameters failed validation.")

    @app.get("/health", response_model=HealthResult)
    def health() -> dict[str, str]:
        if not app.state.repository.healthy():
            raise GraphUnavailable()
        return {"status": "ok", "mode": config.app_env, "graph": "connected"}

    @app.get("/topology", response_model=TopologyResult)
    def topology() -> dict[str, Any]:
        return dict(app.state.repository.topology())

    @app.get("/services/{service_id}/impact", response_model=ImpactResult)
    def impact(service_id: EntityId) -> dict[str, Any]:
        return dict(app.state.repository.impact(service_id))

    @app.get("/evidence/{evidence_id}", response_model=EvidenceResult)
    def evidence(evidence_id: EntityId) -> dict[str, Any]:
        return dict(app.state.repository.evidence(evidence_id))

    return app


app = create_app()

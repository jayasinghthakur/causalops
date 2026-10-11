from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.graph.repository import EntityNotFound, GraphUnavailable
from app.main import create_app


@pytest.fixture
def client():
    app = create_app(Settings(_env_file=None))
    # Contract double only; query correctness is tested exclusively against real FalkorDB.
    app.state.repository = Mock()
    with TestClient(app) as client:
        yield client, app.state.repository


def test_health_requires_database(client):
    browser, repository = client
    repository.healthy.side_effect = GraphUnavailable("sensitive internal details")
    response = browser.get("/health")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "graph_unavailable"
    assert "sensitive" not in response.text
    assert response.headers["x-request-id"] == response.json()["error"]["request_id"]


def test_health_success(client):
    browser, repository = client
    repository.healthy.return_value = True
    assert browser.get("/health").json() == {"status": "ok", "mode": "local", "graph": "connected"}


def test_unknown_service_is_404(client):
    browser, repository = client
    repository.impact.side_effect = EntityNotFound("Service not found")
    assert browser.get("/services/unknown/impact").status_code == 404


def test_invalid_id_rejected_before_query(client):
    browser, repository = client
    assert browser.get("/services/MATCH%20(n)/impact").status_code == 422
    repository.impact.assert_not_called()


def test_impact_contract(client):
    browser, repository = client
    repository.impact.return_value = {
        "service_id": "payment",
        "classification": "potential_impact",
        "max_hops": 4,
        "truncated": False,
        "affected_service_ids": ["checkout"],
        "paths": [
            {
                "node_ids": ["checkout", "payment"],
                "relationship_types": ["CALLS"],
                "evidence_ids": ["evidence-topology-v1"],
                "hops": 1,
            }
        ],
        "caveat": "Potential impact only.",
    }
    response = browser.get("/services/payment/impact")
    assert response.status_code == 200
    assert response.json()["paths"][0]["evidence_ids"] == ["evidence-topology-v1"]


def test_mutation_and_arbitrary_query_routes_are_absent(client):
    browser, repository = client
    for path in ["/demo/reset", "/query", "/seed", "/approve"]:
        assert browser.post(path, json={"query": "MATCH (n) DETACH DELETE n"}).status_code == 404

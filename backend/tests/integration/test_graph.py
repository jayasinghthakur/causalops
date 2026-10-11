import pytest
from fastapi.testclient import TestClient

from app.fixtures import load_fixture
from app.graph.repository import EntityNotFound, GraphRepository
from app.main import create_app

pytestmark = pytest.mark.integration


def test_real_api_resolves_topology_paths_and_evidence(repository):
    with TestClient(create_app(repository.settings)) as client:
        assert client.get("/health").status_code == 200
        assert len(client.get("/topology").json()["nodes"]) == 29
        response = client.get("/services/payment/impact")
        assert response.status_code == 200
        for path in response.json()["paths"]:
            for evidence_id in path["evidence_ids"]:
                assert client.get(f"/evidence/{evidence_id}").status_code == 200


def test_two_seeds_have_no_duplicates(repository):
    before = repository.topology()
    repository.seed(load_fixture())
    assert repository.topology() == before
    assert len(before["nodes"]) == 29
    assert len(before["edges"]) == 32


def test_impact_returns_expected_paths_and_healthy_siblings(repository):
    impact = repository.impact("payment")
    assert impact["affected_service_ids"] == ["billing", "checkout", "gateway", "orders"]
    assert {tuple(p["node_ids"]) for p in impact["paths"]} == {
        ("billing", "payment"),
        ("checkout", "payment"),
        ("orders", "billing", "payment"),
        ("gateway", "checkout", "payment"),
        ("checkout", "orders", "billing", "payment"),
        ("gateway", "checkout", "orders", "billing", "payment"),
    }
    assert "identity" not in impact["affected_service_ids"]
    assert "catalog" not in impact["affected_service_ids"]


def test_noncritical_calls_do_not_propagate(repository):
    assert repository.impact("analytics")["paths"] == []
    assert repository.impact("notification")["paths"] == []


def test_mutation_changes_impact_and_reset_restores(repository):
    before = repository.impact("payment")
    repository.set_critical("checkout", "payment", False)
    assert repository.impact("payment") != before
    assert ["checkout", "payment"] not in [
        list(p["node_ids"]) for p in repository.impact("payment")["paths"]
    ]
    repository.reset(load_fixture())
    assert repository.impact("payment") == before


def test_unknown_service_and_parameter_injection(repository):
    for value in ["unknown", "payment'}) MATCH (n) DETACH DELETE n //"]:
        with pytest.raises(EntityNotFound):
            repository.impact(value)
    assert len(repository.topology()["nodes"]) == 29


def test_every_path_resolves_source_evidence(repository):
    for path in repository.impact("payment")["paths"]:
        for evidence_id in path["evidence_ids"]:
            evidence = repository.evidence(evidence_id)
            assert evidence["source_ref"] == "fixtures/topology-v1.json"
            assert evidence["occurred_at"].endswith("Z")
            assert evidence["verification_status"] == "synthetic"


def test_new_connection_sees_seeded_state(repository):
    before = repository.topology()
    other = GraphRepository(repository.settings)
    try:
        assert other.topology() == before
    finally:
        other.close()


def test_hop_bound_cycles_and_result_cap(repository):
    # Test-owned graph only. Build a chain beyond the boundary, a cycle, and broad fan-in.
    repository._run(
        """
        UNWIND range(0, 5) AS i
        MERGE (:Entity:Service {id: 'chain-' + toString(i)})
        WITH count(*) AS ignored
        UNWIND range(0, 4) AS i
        MATCH (a:Service {id: 'chain-' + toString(i)}),
              (b:Service {id: 'chain-' + toString(i + 1)})
        MERGE (a)-[:CALLS {critical: true, evidence_id: 'evidence-topology-v1'}]->(b)
        RETURN count(*)
    """,
        write=True,
    )
    impact = repository.impact("chain-5")
    assert "chain-0" not in impact["affected_service_ids"]
    assert "chain-1" in impact["affected_service_ids"]
    repository._run(
        """
        MATCH (a:Service {id: 'chain-5'}), (b:Service {id: 'chain-3'})
        MERGE (a)-[:CALLS {critical: true, evidence_id: 'evidence-topology-v1'}]->(b)
        RETURN count(*)
    """,
        write=True,
    )
    assert all(
        len(p["node_ids"]) == len(set(p["node_ids"])) for p in repository.impact("chain-5")["paths"]
    )
    repository._run(
        """
        UNWIND range(0, 54) AS i
        MERGE (a:Entity:Service {id: 'fan-' + toString(i)})
        WITH a
        MATCH (b:Service {id: 'payment'})
        MERGE (a)-[:CALLS {critical: true, evidence_id: 'evidence-topology-v1'}]->(b)
        RETURN count(*)
    """,
        write=True,
    )
    impact = repository.impact("payment")
    assert impact["truncated"] is True
    assert len(impact["paths"]) == 50

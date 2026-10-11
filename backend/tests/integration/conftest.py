from uuid import uuid4

import pytest

from app.config import Settings
from app.fixtures import load_fixture
from app.graph.repository import GraphRepository, GraphUnavailable


@pytest.fixture
def repository():
    config = Settings(
        _env_file=None,
        app_env="test",
        graph_host="127.0.0.1",
        graph_port=6380,
        graph_name=f"causalops_test_{uuid4().hex}",
    )
    repo = GraphRepository(config)
    try:
        if not repo.healthy():
            pytest.fail("FalkorDB health query failed")
    except GraphUnavailable:
        repo.close()
        pytest.fail(
            "Real FalkorDB required at localhost:6380; run make test-integration. No mock fallback."
        )
    try:
        repo.seed(load_fixture())
        yield repo
    finally:
        try:
            repo.delete_test_graph()
        finally:
            repo.close()

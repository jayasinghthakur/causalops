from unittest.mock import Mock

import pytest
from redis.exceptions import ConnectionError

from app.config import Settings
from app.fixtures import load_fixture
from app.graph.repository import GraphRepository, GraphUnavailable


def test_reset_refuses_changed_target_before_connecting():
    settings = Settings(_env_file=None)
    repository = GraphRepository(settings)
    repository._connection = Mock()
    settings.graph_name = "production"
    with pytest.raises(ValueError):
        repository.reset(load_fixture())
    repository._connection.assert_not_called()


def test_local_graph_cannot_be_deleted_by_test_teardown():
    repository = GraphRepository(Settings(_env_file=None))
    repository._connection = Mock()
    with pytest.raises(ValueError, match="Only owned test graphs"):
        repository.delete_test_graph()
    repository._connection.assert_not_called()


def test_connection_failure_becomes_explicit_unavailability():
    repository = GraphRepository(Settings(_env_file=None))
    repository._connection = Mock(side_effect=ConnectionError("private database details"))
    with pytest.raises(GraphUnavailable):
        repository.impact("payment")
    with pytest.raises(GraphUnavailable):
        repository.healthy()

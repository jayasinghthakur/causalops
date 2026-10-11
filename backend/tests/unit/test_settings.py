import pytest
from pydantic import ValidationError

from app.config import Settings


@pytest.mark.parametrize("environment", ["production", "staging", "preview", "unknown"])
def test_hosted_environment_rejected(environment):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, app_env=environment)


@pytest.mark.parametrize(
    "values",
    [
        {"app_env": "test"},
        {"app_env": "test", "graph_name": "causalops_test_a", "graph_port": 6379},
        {"graph_name": "customer_data"},
        {"graph_host": "production.example.com"},
        {"graph_name": "causalops_test_a"},
        {"graph_timeout_ms": 10000},
        {"graph_host": "falkordb-test"},
    ],
)
def test_unsafe_targets_rejected(values):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **values)


def test_isolated_test_target_accepted():
    config = Settings(
        _env_file=None, app_env="test", graph_name="causalops_test_a", graph_port=6380
    )
    config.require_mutation_target()


def test_write_guard_rechecks_changed_target():
    config = Settings(_env_file=None)
    config.graph_name = "customer_data"
    with pytest.raises(ValueError):
        config.require_mutation_target()

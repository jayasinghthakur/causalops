import pytest


@pytest.fixture(autouse=True)
def clear_environment(monkeypatch):
    """Developer settings must not silently change automated test targets."""
    for key in ["APP_ENV", "GRAPH_HOST", "GRAPH_PORT", "GRAPH_NAME", "GRAPH_TIMEOUT_MS"]:
        monkeypatch.delenv(key, raising=False)

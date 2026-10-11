from app.domain.impact import ImpactPath, ordered_callers


def test_callers_are_unique_and_ordered_by_nearest_path():
    def path(*nodes):
        return ImpactPath(nodes, ("CALLS",) * (len(nodes) - 1), ("evidence",) * (len(nodes) - 1))

    paths = [
        path("gateway", "checkout", "payment"),
        path("checkout", "payment"),
        path("gateway", "orders", "billing", "payment"),
        path("billing", "payment"),
    ]
    assert ordered_callers(paths) == ["billing", "checkout", "gateway"]
    assert len(paths) == 4


def test_empty_impact_is_empty():
    assert ordered_callers([]) == []

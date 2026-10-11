from collections import Counter

import pytest
from pydantic import ValidationError

from app.fixtures import TopologyFixture, load_fixture


def test_fixture_meets_foundation_contract():
    fixture = load_fixture()
    labels = Counter(node.label for node in fixture.nodes)
    assert labels["Service"] == 12
    assert labels["Resource"] == 4
    assert labels["Journey"] == 6
    assert sum(edge.type in {"CALLS", "DEPENDS_ON"} for edge in fixture.edges) >= 18
    assert load_fixture() == fixture


@pytest.mark.parametrize(
    "defect",
    [
        "duplicate",
        "dangling",
        "wrong_type",
        "missing_evidence",
        "id_override",
        "timestamp",
        "duplicate_edge",
        "arbitrary_label",
    ],
)
def test_bad_fixture_rejected_before_writes(defect):
    raw = load_fixture().model_dump()
    if defect == "duplicate":
        raw["nodes"].append(raw["nodes"][0])
    elif defect == "dangling":
        raw["edges"][0]["target"] = "unknown"
    elif defect == "wrong_type":
        raw["edges"][0]["target"] = "redis"
    elif defect == "missing_evidence":
        raw["edges"][0]["evidence_id"] = "unknown"
    elif defect == "id_override":
        raw["nodes"][0]["properties"]["id"] = "overridden"
    elif defect == "timestamp":
        next(n for n in raw["nodes"] if n["label"] == "Evidence")["properties"]["occurred_at"] = (
            "2026-10-12T00:00:00"
        )
    elif defect == "duplicate_edge":
        raw["edges"].append(raw["edges"][0])
    else:
        raw["nodes"][0]["label"] = "Service) DELETE n"
    with pytest.raises(ValidationError):
        TopologyFixture.model_validate(raw)

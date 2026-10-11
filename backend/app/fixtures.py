"""Validate synthetic graph data before any database writes."""

from datetime import datetime
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.config import ROOT

NodeLabel = Literal["Service", "Resource", "Endpoint", "Journey", "Evidence"]
EdgeType = Literal["CALLS", "DEPENDS_ON", "EXPOSES", "USES"]


class FixtureNode(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(pattern=r"^[a-z][a-z0-9-]{0,79}$")
    label: NodeLabel
    properties: dict[str, str | bool | int]


class FixtureEdge(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source: str
    target: str
    type: EdgeType
    critical: bool
    evidence_id: str


class TopologyFixture(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: str
    nodes: list[FixtureNode] = Field(min_length=1, max_length=500)
    edges: list[FixtureEdge] = Field(max_length=1000)

    @model_validator(mode="after")
    def validate_references(self) -> Self:
        by_id = {node.id: node for node in self.nodes}
        if len(by_id) != len(self.nodes):
            raise ValueError("Fixture node IDs must be globally unique")
        allowed = {
            "CALLS": ("Service", "Service"),
            "DEPENDS_ON": ("Service", "Resource"),
            "EXPOSES": ("Service", "Endpoint"),
            "USES": ("Journey", "Endpoint"),
        }
        seen = set()
        for node in self.nodes:
            if "id" in node.properties:
                raise ValueError("Properties must not override node identity")
            if node.label == "Evidence":
                timestamp = node.properties.get("occurred_at")
                if not isinstance(timestamp, str):
                    raise ValueError("Evidence needs a timestamp")
                parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                offset = parsed.utcoffset()
                if offset is None or offset.total_seconds() != 0:
                    raise ValueError("Evidence timestamp must be UTC")
                if not node.properties.get("source_ref"):
                    raise ValueError("Evidence needs a source reference")
        for edge in self.edges:
            if edge.source not in by_id or edge.target not in by_id:
                raise ValueError("Edge references an unknown node")
            if (by_id[edge.source].label, by_id[edge.target].label) != allowed[edge.type]:
                raise ValueError("Edge type has invalid endpoint labels")
            evidence = by_id.get(edge.evidence_id)
            if evidence is None or evidence.label != "Evidence":
                raise ValueError("Every edge must reference known evidence")
            identity = (edge.source, edge.type, edge.target)
            if identity in seen:
                raise ValueError("Duplicate fixture edge")
            seen.add(identity)
        return self


def load_fixture() -> TopologyFixture:
    return TopologyFixture.model_validate_json((ROOT / "fixtures/topology-v1.json").read_text())

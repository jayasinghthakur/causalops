from typing import Annotated, Literal

from pydantic import BaseModel, Field

EntityId = Annotated[str, Field(pattern=r"^[a-z][a-z0-9-]{0,79}$")]


class PathResult(BaseModel):
    node_ids: list[str]
    relationship_types: list[str]
    evidence_ids: list[str]
    hops: int = Field(ge=1, le=4)


class ImpactResult(BaseModel):
    service_id: str
    classification: Literal["potential_impact"]
    max_hops: Literal[4]
    truncated: bool
    affected_service_ids: list[str]
    paths: list[PathResult] = Field(max_length=50)
    caveat: str


class TopologyNode(BaseModel):
    id: str
    labels: list[str]
    properties: dict[str, str | int | bool]


class TopologyEdge(BaseModel):
    source: str
    target: str
    type: str
    critical: bool
    evidence_id: str


class TopologyResult(BaseModel):
    synthetic: Literal[True]
    nodes: list[TopologyNode]
    edges: list[TopologyEdge]


class EvidenceResult(BaseModel):
    id: str
    name: str
    occurred_at: str
    source_type: str
    source_ref: str
    summary: str
    verification_status: str


class HealthResult(BaseModel):
    status: Literal["ok"]
    mode: Literal["local", "test"]
    graph: Literal["connected"]

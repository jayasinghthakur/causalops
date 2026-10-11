"""Real database operations; no in-memory graph fallback."""

from typing import Any

from falkordb import FalkorDB
from redis.exceptions import RedisError

from app.config import Settings
from app.domain.impact import ImpactPath, ordered_callers
from app.fixtures import TopologyFixture
from app.graph import queries


class GraphUnavailable(Exception):
    pass


class EntityNotFound(Exception):
    pass


class GraphLimitExceeded(Exception):
    pass


class GraphRepository:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._db: Any = None

    def _connection(self) -> Any:
        if self._db is None:
            self._db = FalkorDB(
                host=self.settings.graph_host,
                port=self.settings.graph_port,
                socket_timeout=5,
                socket_connect_timeout=2,
                max_connections=16,
            )
        return self._db

    def _run(
        self, query: str, params: dict[str, Any] | None = None, *, write: bool = False
    ) -> list[list[Any]]:
        if write:
            self.settings.require_mutation_target()
        try:
            graph = self._connection().select_graph(self.settings.graph_name)
            execute = graph.query if write else graph.ro_query
            result = execute(query, params=params or {}, timeout=self.settings.graph_timeout_ms)
            return list(result.result_set)
        except RedisError as exc:
            # Do not leak connection strings or raw queries to API clients.
            raise GraphUnavailable("FalkorDB query failed or database is unavailable") from exc

    def close(self) -> None:
        if self._db is not None:
            self._db.close()
            self._db = None

    def healthy(self) -> bool:
        # GRAPH.LIST checks the module before seeding without creating an empty graph.
        try:
            self._connection().list_graphs()
            return True
        except RedisError as exc:
            raise GraphUnavailable("FalkorDB is unavailable") from exc

    def seed(self, fixture: TopologyFixture) -> dict[str, Any]:
        """One repeatable query; fixture validation precedes all writes."""
        parts: list[str] = []
        params: dict[str, Any] = {}
        for label in sorted({node.label for node in fixture.nodes}):
            key = f"nodes_{label}"
            params[key] = [
                {"id": n.id, "properties": n.properties} for n in fixture.nodes if n.label == label
            ]
            # Labels/types originate only from fixture Literal allowlists, never request values.
            parts.append(
                f"UNWIND ${key} AS row MERGE (n:Entity:{label} {{id: row.id}}) "
                "SET n += row.properties WITH count(*) AS ignored"
            )
        for edge_type in sorted({edge.type for edge in fixture.edges}):
            key = f"edges_{edge_type}"
            params[key] = [edge.model_dump() for edge in fixture.edges if edge.type == edge_type]
            parts.append(
                f"UNWIND ${key} AS row "
                "MATCH (a:Entity {id: row.source}), (b:Entity {id: row.target}) "
                f"MERGE (a)-[r:{edge_type}]->(b) "
                "SET r.critical = row.critical, r.evidence_id = row.evidence_id "
                "WITH count(*) AS ignored"
            )
        self._run("\n".join(parts) + "\nRETURN 1", params, write=True)
        return {
            "fixture_version": fixture.version,
            "nodes": len(fixture.nodes),
            "edges": len(fixture.edges),
        }

    def reset(self, fixture: TopologyFixture) -> dict[str, Any]:
        # Two operations, explicitly local-only; a failed seed leaves an empty graph, not success.
        self._run("MATCH (n) DETACH DELETE n", write=True)
        return self.seed(fixture)

    def delete_test_graph(self) -> None:
        self.settings.require_mutation_target()
        if self.settings.app_env != "test":
            raise ValueError("Only owned test graphs may be deleted")
        if self.settings.graph_name in self._connection().list_graphs():
            self._connection().select_graph(self.settings.graph_name).delete()

    def topology(self) -> dict[str, Any]:
        nodes = self._run(queries.NODES)
        edges = self._run(queries.EDGES)
        if len(nodes) > 500 or len(edges) > 1000:
            raise GraphLimitExceeded("Topology exceeds the local foundation display limit")
        return {
            "synthetic": True,
            "nodes": [
                {"id": row[0], "labels": [x for x in row[1] if x != "Entity"], "properties": row[2]}
                for row in nodes
            ],
            "edges": [
                {
                    "source": r[0],
                    "target": r[1],
                    "type": r[2],
                    "critical": r[3],
                    "evidence_id": r[4],
                }
                for r in edges
            ],
        }

    def impact(self, service_id: str) -> dict[str, Any]:
        if not self._run(queries.SERVICE_EXISTS, {"service_id": service_id}):
            raise EntityNotFound("Service not found")
        rows = self._run(queries.IMPACT, {"service_id": service_id})
        paths = [ImpactPath(tuple(r[0]), tuple(r[1]), tuple(r[2])) for r in rows[:50]]
        return {
            "service_id": service_id,
            "classification": "potential_impact",
            "max_hops": 4,
            "truncated": len(rows) > 50,
            "affected_service_ids": ordered_callers(paths),
            "paths": [
                {
                    "node_ids": p.node_ids,
                    "relationship_types": p.relationship_types,
                    "evidence_ids": p.evidence_ids,
                    "hops": p.hops,
                }
                for p in paths
            ],
            "caveat": "Dependency paths describe potential impact, not proven causation.",
        }

    def evidence(self, evidence_id: str) -> dict[str, Any]:
        rows = self._run(queries.EVIDENCE, {"evidence_id": evidence_id})
        if not rows:
            raise EntityNotFound("Evidence not found")
        return dict(rows[0][0])

    def set_critical(self, source: str, target: str, critical: bool) -> None:
        rows = self._run(
            queries.SET_CRITICAL,
            {"source": source, "target": target, "critical": critical},
            write=True,
        )
        if not rows or rows[0][0] == 0:
            raise EntityNotFound("CALLS dependency not found")

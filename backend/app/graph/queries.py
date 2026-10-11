"""Reviewed Cypher shapes. User values are always parameters."""

SERVICE_EXISTS = "MATCH (n:Service {id: $service_id}) RETURN n.id LIMIT 1"
IMPACT = """
MATCH p=(caller:Service)-[:CALLS*1..4]->(root:Service {id: $service_id})
WHERE caller.id <> root.id
  AND all(e IN relationships(p) WHERE e.critical = true)
  AND all(n IN nodes(p) WHERE single(m IN nodes(p) WHERE m.id = n.id))
RETURN DISTINCT [n IN nodes(p) | n.id] AS path,
       [e IN relationships(p) | type(e)] AS edge_types,
       [e IN relationships(p) | e.evidence_id] AS evidence_ids,
       length(p) AS hops
ORDER BY hops, path
LIMIT 51
"""
# Read one extra row to report truncation; never expose more than 50 paths.
NODES = """
MATCH (n:Entity)
RETURN n.id, labels(n), properties(n)
ORDER BY n.id LIMIT 501
"""
EDGES = """
MATCH (a:Entity)-[r]->(b:Entity)
RETURN a.id, b.id, type(r), r.critical, r.evidence_id
ORDER BY a.id, b.id, type(r) LIMIT 1001
"""
EVIDENCE = "MATCH (n:Evidence {id: $evidence_id}) RETURN properties(n) LIMIT 1"
SET_CRITICAL = """
MATCH (a:Service {id: $source})-[r:CALLS]->(b:Service {id: $target})
SET r.critical = $critical
RETURN count(r)
"""

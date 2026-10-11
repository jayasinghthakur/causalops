# Graph ontology, query plans and evaluation

**Target schema; foundation subset implemented but database validation pending.** The current fixture includes Service, Resource, Endpoint, Journey, and Evidence nodes, with a shared Entity label and globally unique fixture IDs. Incident and action types below are still planned. FalkorDB is the required primary graph database. Target node identity follows `(type,id)`; incident references are immutable. Use parameterized Cypher; validate every query against the pinned FalkorDB version.

Current impact queries traverse critical Service-to-Service CALLS edges only. Resource impact, deployment correlation, and hypothesis queries remain planned. The implementation in `backend/app/graph/queries.py` excludes cyclic paths, returns at most 50 paths, and uses an extra internal row to detect truncation; the sample below is a design illustration.

## Nodes
- `Service(id,name,criticality,team_id,environment)`
- `Resource(id,name,kind,environment,criticality)`
- `Endpoint(id,route,method,service_id)`
- `Journey(id,name,priority)`
- `Deployment(id,version,occurred_at,change_ref)`
- `Incident(id,status,severity,started_at,resolved_at)`
- `Alert(id,occurred_at,kind,severity)`
- `Evidence(id,occurred_at,source_type,source_ref,summary,verification_status)`
- `Hypothesis(id,label,score,version,status)`
- `Action(id,type,state,created_at,approved_at,approver,outcome)`
- `Runbook(id,name,version)`

## Edges and orientation
```
(Service)-[:CALLS {critical,protocol}]->(Service)
(Service)-[:DEPENDS_ON {critical,fallback_available}]->(Resource)
(Service)-[:EXPOSES]->(Endpoint)
(Journey)-[:USES]->(Endpoint)
(Deployment)-[:DEPLOYED_TO]->(Service)
(Deployment)-[:CHANGED]->(Resource)
(Incident)-[:HAS_ALERT]->(Alert)-[:TRIGGERED_ON]->(Service)
(Incident)-[:HAS_HYPOTHESIS]->(Hypothesis)
(Hypothesis)-[:SUPPORTED_BY|CONTRADICTED_BY]->(Evidence)
(Hypothesis)-[:SUSPECTS]->(Deployment)
(Incident)-[:HAS_ACTION]->(Action)-[:TARGETS]->(Service)
(Action)-[:BASED_ON]->(Runbook)
(Incident)-[:SIMILAR_TO {score,method}]->(Incident)
```

## Core Cypher (test and amend before use)

### Impact from critical callers
```cypher
MATCH (root:Service {id:$service_id})
MATCH p=(caller:Service)-[:CALLS*1..4]->(root)
WHERE all(e IN relationships(p) WHERE e.critical = true)
RETURN DISTINCT caller.id AS caller_id,
       [n IN nodes(p) | n.id] AS path,
       length(p) AS hop_count
ORDER BY hop_count ASC LIMIT 50
```

### Evidence for hypothesis
```cypher
MATCH (:Incident {id:$incident_id})-[:HAS_HYPOTHESIS]->(h:Hypothesis)
OPTIONAL MATCH (h)-[r:SUPPORTED_BY|CONTRADICTED_BY]->(e:Evidence)
RETURN h.id,h.label,h.score,
       collect({kind:type(r),evidence_id:e.id,source:e.source_ref}) AS provenance
```

### Previous successful response
```cypher
MATCH (i:Incident {id:$incident_id})-[s:SIMILAR_TO]->(prior:Incident)-[:HAS_ACTION]->(a:Action)
WHERE s.score >= $threshold AND a.state = 'verified_success'
RETURN prior.id, s.score, a.type, a.id
ORDER BY s.score DESC LIMIT 5
```

### Candidate deployments (query plan)
Find services within bounded two-hop dependency neighborhood; join deployment edges to affected service/resource; filter deployment timestamps from time window before incident. Separate structural traversal from evidence timeline query if union variable-length Cypher is unsupported in tested version.

## Causal reasoning safeguards
- Architecture path != proven fault propagation. Mark impact as *potential*.
- Deployment time != proof of regression. Include contradictory evidence and explicit unknowns.
- Confidence scores are comparative deterministic ranking signals, not calibrated probabilities.
- Never mutate the production topology during counterfactual analysis; use an isolated clone or scenario model.
- Incident memory retrieval must include topology condition and incident type, not only embedding similarity.

## Test fixture plan
12 services, 4 resources, 6 journeys, 3 demo stories, >=12 evaluation cases. Cases: new deployment causing timeout, dependency outage, healthy sibling, fallback saturation, multiple overlapping incidents, missing telemetry, stale memory, conflicting evidence, remediation not allowed, service owner missing, duplicate alerts, false correlated deployment. Record ground truth and allowed actions per fixture.

## Query performance controls
Cap hops at 4, rows at 50, evidence window at bounded time, use stable IDs and indices as supported, hide arbitrary Cypher from UI and LLM, measure query latency, optimize only observed bottlenecks.

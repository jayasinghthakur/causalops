# Synthetic Topology Fixture

`topology-v1.json` contains 29 nodes and 32 edges: 12 services, four resources, six endpoints, six journeys, one evidence record, 20 CALLS/DEPENDS_ON edges, and 12 EXPOSES/USES edges. All identities and timestamps are fixed; no production telemetry is included.

The shared `evidence-topology-v1` record identifies the hand-authored topology snapshot. Its timestamp is fixture metadata, not an observed incident time. Every relationship references that source record. The loader rejects dangling references, duplicates, invalid node/edge types, missing provenance, and non-UTC evidence timestamps before writing.

For the `payment` service, expected unique potential callers, ordered by nearest hop and ID, are `billing`, `checkout`, `gateway`, and `orders`. There are six paths, including `gateway → checkout → orders → billing → payment`. Identity and catalog remain unaffected. The noncritical analytics and notification calls do not propagate impact.

Changing `checkout → payment` to noncritical removes that direct path but leaves the alternative through orders/billing. Reset restores the fixture. Tests construct additional isolated chain, cycle, and fan-in cases to validate traversal bounds and truncation.

These expected results are tested in `backend/tests/integration/test_graph.py`; database validation is pending. Incident ground truth and the planned three scenario stories/12-case benchmark will be added during later milestones, separately from inputs visible to the investigator.

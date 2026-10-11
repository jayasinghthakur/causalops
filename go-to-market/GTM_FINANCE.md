# GTM and finance — zero-budget plan

## ICP and buyer map
Start with 5–30-engineer SaaS teams, 5–20 services, one on-call rotation, basic metrics and logs, no dedicated SRE platform. User: on-call backend engineer. Champion: lead/staff engineer. Buyer: VP engineering / founder. Economic case: reduce *investigation effort*, not promise automatic incident resolution.

## Jobs to be done
When production services exhibit cascading alerts, show me an evidence-backed dependency path, the likely initiating issue, risks of candidate actions and an auditable investigation record so I can make an informed recovery decision.

## Positioning
Not an observability replacement. A **graph-based investigative reasoning layer** above existing logs, incidents and topology. Competitors include observability suites, incident management platforms, AIOps copilots and custom scripts. Differentiate on provenance, topology-conditioned memory, graph-change sensitivity and human-approved remediation.

## Pricing hypotheses — not validated
- Open-source Community: self-host, synthetic demo, core graph engine and local actions.
- Pilot: free for up to 3 design partners with read-only integrations and feedback agreement.
- Paid Team (future): possible per-workspace monthly subscription; determine value and cost only after willingness-to-pay interviews. Do not publish arbitrary dollar amounts as committed prices.

## Finance: estimated cost drivers
- **Local MVP cash cost:** potentially ₹0 if hardware, power and internet already available, and using open-source/FOSS stack. Existing resources still have opportunity costs.
- **Optional LLM API:** metered tokens; costs depend on model, volume and provider; local model fallback avoids API billing but consumes hardware resources.
- **Static marketing/demo site:** Cloudflare Pages free tier subject to build/files/usage limits; not a guarantee of free persistent backend hosting.
- **Persistent online graph + API:** no zero-cost SLA assumed. Prefer Docker-hosted local demo, later pay for hosted infrastructure if customers require uptime.
- **Commercial unit economics:** gross margin = revenue − (compute + model tokens + storage + monitoring + support + payment fees). Instrument before promising pricing.

## Customer discovery sequence
Interview 10 engineers and 5 leaders. Ask last incident timeline, how service topology is maintained, false root-cause guesses, approval rules, data access, budgets. Show 3-minute scenario, measure understanding and willingness to pilot. Never request access to private production data at initial discovery.

## Acquisition / messaging
Public GitHub with setup instructions, architecture write-up, Graph Hacks demo, technical blog on dependency traversal and counterfactual analysis; technical LinkedIn posts / communities with educational content, not spam. CTA: request design-partner interview.

## KPIs
Activation: first reproducible incident investigation. Quality: root-cause top-1/top-3 accuracy on labeled fixtures, evidence coverage, number of unsafe actions, graph-on vs graph-off lift. Product: time-to-first-value, repeat investigations, weekly engineering team usage, pilot conversion. Do not call synthetic benchmark gains production MTTR improvements.

## Go / no-go decision criteria
Continue if 3+ independent teams articulate unmet need, 2 agree to repeat pilots, and graph approach demonstrably improves evidence quality over flat-data baseline. Otherwise pivot to narrower code-change blast radius or incident knowledge retention.

## Responsible scope
Do not ingest or publish third-party restricted data; default mock actions; product disclaimers that causal claims are hypotheses; require enterprise security before production integrations.

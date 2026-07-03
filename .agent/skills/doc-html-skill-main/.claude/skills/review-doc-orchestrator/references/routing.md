# Routing heuristics

Map an incoming request to exactly one artifact type. When signals are mixed,
prefer the type matching the **primary audience need**, and confirm with the
user if still ambiguous.

## Signals by type

### user-story-review
- Keywords: user story, "as a / I want / so that", acceptance criteria, scope gap,
  persona, journey, backlog refinement.
- Primary audience: Product, Design, Engineering.
- Produce when the request is about *what a user needs and whether the story is ready*.

### architecture-review
- Keywords: architecture, topology, components, interfaces, sequence, data flow,
  ADR, trade-off, deployment, scalability, coupling.
- Primary audience: Architects, Engineering leads.
- Produce when the request is about *how the system is structured and why*.

### prd-review
- Keywords: PRD, product requirements, goals, success metrics, out of scope,
  requirement coverage, readiness, stakeholders.
- Primary audience: Product, Delivery.
- Produce when the request is about *requirement completeness and readiness*.

### risk-analysis
- Keywords: risk, likelihood, impact, mitigation, control, residual risk,
  trigger, incident, register, blast radius.
- Primary audience: QA, Product, Operations.
- Produce when the request is about *what could go wrong and how it's mitigated*.

### test-charter
- Keywords: exploratory testing, charter, mission, heuristic, coverage boundary,
  session-based testing, exit criteria.
- Primary audience: QA.
- Produce when the request is about *how to explore/test an area*.

## Disambiguation rules

- **Architecture vs risk:** if the deliverable is a risk register/matrix → risk;
  if it's the structural design with risks as one section → architecture.
- **PRD vs user-story:** PRD covers the whole feature's requirements; user-story
  covers a single story's readiness.
- **Spanning requests** (e.g. "architecture + risks"): produce the primary
  artifact and offer a second artifact rather than mixing types in one document.

## When to ask

Ask the user to confirm the type only when two types score equally on the signals
above. Otherwise pick the best match and state which type you chose.

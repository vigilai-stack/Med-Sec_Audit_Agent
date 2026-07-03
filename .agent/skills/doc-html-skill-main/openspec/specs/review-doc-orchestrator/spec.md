# review-doc-orchestrator Specification

## Purpose
Define the orchestrator skill that classifies review requests, routes them to the correct artifact specialist, gathers evidence scope, assembles validated canonical source, and keeps a thin skill footprint.

## Requirements

### Requirement: Request routing to artifact type
The orchestrator skill SHALL classify an incoming request and route it to the correct artifact specialist (user-story, architecture, PRD, risk-analysis, or test-charter) based on the request intent and audience.

#### Scenario: Architecture request routed
- **WHEN** a user asks for a review of a service's topology and design trade-offs
- **THEN** the orchestrator selects the architecture-review artifact type

#### Scenario: Ambiguous request clarified
- **WHEN** the request does not clearly map to a single artifact type
- **THEN** the orchestrator asks the user to confirm the artifact type before producing source

### Requirement: Canonical source assembly
The orchestrator SHALL assemble validated canonical source by delegating content authoring to the selected artifact skill and selecting the appropriate template and theme token set. It MUST NOT hand-author final HTML.

#### Scenario: Validated source produced
- **WHEN** the orchestrator finishes assembling an artifact
- **THEN** it emits canonical YAML/JSON that passes schema validation and references the chosen template

### Requirement: Evidence scope gathering
The orchestrator SHALL collect the evidence scope (links to code, ADRs, docs) for inclusion in the artifact's `evidence` list before rendering.

#### Scenario: Evidence attached
- **WHEN** the user references supporting documents or code paths
- **THEN** the orchestrator records them as `{label, href}` evidence entries in the source

### Requirement: Thin skill footprint
The orchestrator `SKILL.md` SHALL stay within Anthropic's 500-line guidance, deferring routing tables and artifact-type detail to support reference files loaded only when needed.

#### Scenario: Reference offloading
- **WHEN** detailed routing rules are needed
- **THEN** they are read from a support reference file rather than inlined in `SKILL.md`

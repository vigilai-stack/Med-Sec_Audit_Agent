## ADDED Requirements

### Requirement: Five artifact specialist skills
The system SHALL provide five thin artifact skills — user-story review, architecture review, PRD review, risk-analysis review, and test-charter review — each authoring compact canonical source that validates against the base schema plus its overlay.

#### Scenario: Each skill emits valid source
- **WHEN** any artifact skill produces canonical source
- **THEN** that source validates against the base schema and the skill's overlay schema

### Requirement: Content-not-chrome authoring
Each artifact skill SHALL author only review content — summaries, findings, evidence references, table rows, and Mermaid source — and MUST NOT emit HTML, CSS, or JavaScript boilerplate.

#### Scenario: No boilerplate emitted
- **WHEN** an artifact skill generates output
- **THEN** the output contains zero HTML/CSS/JS chrome and only canonical content fields

### Requirement: Artifact-appropriate sections
Each artifact skill SHALL populate the overlay fields and section primitives appropriate to its type (e.g. user-story emits acceptance criteria and journey states; risk-analysis emits a risk matrix table; architecture emits sequence/topology diagrams and decisions).

#### Scenario: Risk artifact includes matrix
- **WHEN** the risk-analysis skill produces source
- **THEN** it includes a risk-matrix table section with likelihood, impact, and mitigation columns

#### Scenario: User-story artifact includes acceptance criteria
- **WHEN** the user-story skill produces source
- **THEN** it includes `acceptance_criteria` and at least one journey or section conveying scope

### Requirement: Scoped diagram defaults
Each artifact skill SHALL default to one primary diagram per core section and keep Mermaid blocks small (target under 40 lines), offering larger or ELK-layout diagrams only on explicit request.

#### Scenario: Default single diagram
- **WHEN** a skill generates a section that warrants a diagram
- **THEN** it emits one focused Mermaid block under the size target by default

### Requirement: Token-efficient output
Each artifact skill SHALL target canonical source between 2 KB and 12 KB and SHALL support section-level regeneration rather than re-emitting the whole document.

#### Scenario: Section regeneration
- **WHEN** a user requests a change to one section
- **THEN** the skill regenerates only that section's source rather than the entire artifact

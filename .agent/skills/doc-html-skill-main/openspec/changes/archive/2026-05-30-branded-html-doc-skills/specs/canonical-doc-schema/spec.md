## ADDED Requirements

### Requirement: Shared base document schema
The system SHALL define a single shared base schema for all review artifacts, expressed as JSON Schema (Draft 2020-12). The base schema MUST require `schema_version`, `artifact_type`, and `title`, and MUST support `subtitle`, `audience`, `status`, `owner`, `updated_at`, `theme`, `summary`, `sections`, `evidence`, and `export`.

#### Scenario: Minimal valid source
- **WHEN** a canonical source supplies `schema_version`, `artifact_type`, and `title`
- **THEN** the schema validator accepts it as structurally valid

#### Scenario: Missing required field rejected
- **WHEN** a canonical source omits `artifact_type`
- **THEN** the schema validator reports a validation error identifying the missing field

### Requirement: Section block types
The base schema SHALL support a `sections` array where each section has an `id`, `title`, and `kind`. The supported `kind` values MUST include `prose`, `mermaid`, and `table`. A `mermaid` section MUST carry a `diagram_type` and `source`; a `table` section MUST carry `columns` and `rows`.

#### Scenario: Mermaid section validates
- **WHEN** a section declares `kind: mermaid` with `diagram_type` and `source`
- **THEN** the validator accepts the section

#### Scenario: Table section missing columns rejected
- **WHEN** a section declares `kind: table` with `rows` but no `columns`
- **THEN** the validator reports a validation error

### Requirement: Artifact-specific overlays
The system SHALL provide overlay schemas that extend the base for each artifact type without replacing base fields: user-story (`as_a`, `i_want`, `so_that`, `acceptance_criteria`, `personas`, `journey_states`, `dependencies`), architecture (`decisions`, `constraints`, `interfaces`, `deployment_context`, `alternatives`), PRD (`business_goals`, `out_of_scope`, `requirement_coverage`, `stakeholders`), risk-analysis (`triggers`, `controls`, `residual_risk`, `owners`, `review_cadence`), and test-charter (`missions`, `heuristics`, `coverage_boundaries`, `exit_criteria`).

#### Scenario: Overlay extends base
- **WHEN** an `architecture-review` source includes base fields plus `decisions` and `constraints`
- **THEN** the architecture overlay schema validates it successfully

#### Scenario: Overlay does not drop base requirements
- **WHEN** an overlay-typed source omits a base-required field
- **THEN** validation still fails on the missing base field

### Requirement: Evidence and export metadata
The base schema SHALL support an `evidence` list of `{label, href}` references and an `export` object with at least `pdf` (boolean) and `freeze_diagrams` (boolean) flags.

#### Scenario: Evidence links captured
- **WHEN** a source lists evidence entries with `label` and `href`
- **THEN** the validator accepts them and the renderer can surface them as links

### Requirement: Dual canonical formats
The schema SHALL be authorable as either YAML or JSON, and both forms MUST validate against the same JSON Schema.

#### Scenario: YAML and JSON parity
- **WHEN** the same artifact is expressed once in YAML and once in JSON
- **THEN** both validate against the identical schema with equivalent results

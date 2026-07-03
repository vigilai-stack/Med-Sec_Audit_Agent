# canonical-doc-schema Specification

## Purpose
Define the shared canonical document schema for branded review artifacts, including the base schema, artifact-specific overlays, evidence/export metadata, and dual YAML/JSON authoring.

## Requirements

### Requirement: Shared base document schema
The system SHALL define a single shared base schema for all review artifacts, expressed as JSON Schema (Draft 2020-12). The base schema MUST require `schema_version`, `artifact_type`, and `title`, and MUST support `subtitle`, `audience`, `status`, `owner`, `updated_at`, `theme`, `summary`, `sections`, `evidence`, and `export`.

#### Scenario: Minimal valid source
- **WHEN** a canonical source supplies `schema_version`, `artifact_type`, and `title`
- **THEN** the schema validator accepts it as structurally valid

#### Scenario: Missing required field rejected
- **WHEN** a canonical source omits `artifact_type`
- **THEN** the schema validator reports a validation error identifying the missing field

### Requirement: Section block types
The base schema SHALL support a `sections` array where each section has an `id`, `title`, and `kind`. The supported `kind` values MUST include `prose`, `mermaid`, `table`, `callout`, `stats`, `steps`, `cards`, `keyvalue`, `code`, `tabs`, `details`, `timeline`, `heatmap`, and `meters`. Each kind MUST enforce its content contract:
- `mermaid` MUST carry `diagram_type` and `source`, and MAY carry `caption`.
- `table` MUST carry `columns` and `rows`.
- `callout` MUST carry `intent` (one of `note`, `tip`, `warning`, `danger`) and `body`.
- `stats` MUST carry `items[]` of `{value, label}` with optional `delta`.
- `steps` MUST carry `items[]` of `{title, body}`.
- `cards` MUST carry `items[]` of `{title, body}` with optional `tag`, `ref`, and `variant` (`generic`, `decision`, `rejected`, `persona`).
- `keyvalue` MUST carry `items[]` of `{key, value}`.
- `code` MUST carry `source` with optional `language` and `filename`.
- `tabs` MUST carry `items[]` of `{label, body}`.
- `details` MUST carry `summary` and `body`.
- `timeline` MUST carry `items[]` of `{label, body}` with optional `date`.
- `heatmap` MUST carry `x_labels`, `y_labels`, and `cells[]` of `{x, y, level}` with optional `label`.
- `meters` MUST carry `items[]` of `{label, value}` (0–100) with optional `note`.

Each section MAY carry an optional `width` hint (`full` or `half`).

#### Scenario: Mermaid section validates
- **WHEN** a section declares `kind: mermaid` with `diagram_type` and `source`
- **THEN** the validator accepts the section

#### Scenario: Table section missing columns rejected
- **WHEN** a section declares `kind: table` with `rows` but no `columns`
- **THEN** the validator reports a validation error

#### Scenario: Callout section validates
- **WHEN** a section declares `kind: callout` with `intent: warning` and a `body`
- **THEN** the validator accepts the section

#### Scenario: Invalid callout intent rejected
- **WHEN** a section declares `kind: callout` with `intent: shouting`
- **THEN** the validator reports an invalid enum value

#### Scenario: Stats section missing items rejected
- **WHEN** a section declares `kind: stats` without `items`
- **THEN** the validator reports a validation error

#### Scenario: Width hint accepted
- **WHEN** a section declares `width: half`
- **THEN** the validator accepts the section

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

### Requirement: Layout selection field
The base schema's `theme` object SHALL support an optional `layout` field with enum values `docs-site`, `editorial`, and `brief`. Sources omitting `theme.layout` MUST remain valid (the renderer applies the artifact type's default skin).

#### Scenario: Layout override validates
- **WHEN** a source sets `theme.layout: editorial`
- **THEN** the validator accepts it

#### Scenario: Omitted layout still valid
- **WHEN** a source provides a `theme` object without `layout`
- **THEN** validation succeeds

### Requirement: Constraint severity vocabulary
The architecture overlay SHALL allow `constraints` entries to be either a plain string (severity defaults to `info`) or an object `{text, severity}` with severity one of `high`, `medium`, `low`, `info`. Existing string-only sources MUST remain valid.

#### Scenario: Plain string constraint still valid
- **WHEN** an architecture source lists a constraint as a plain string
- **THEN** validation succeeds and the renderer treats it as `info` severity

#### Scenario: Severity-tagged constraint validates
- **WHEN** a constraint is `{text: "...", severity: high}`
- **THEN** the validator accepts it

# canonical-doc-schema Specification (delta)

## MODIFIED Requirements

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

## ADDED Requirements

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

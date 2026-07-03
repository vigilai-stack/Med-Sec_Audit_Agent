## ADDED Requirements

### Requirement: Layered validation
The system SHALL provide a validator that runs checks in layers and reports a consolidated pass/fail result with per-check detail. Schema validation MUST run first, and a schema failure MUST short-circuit downstream checks for that artifact.

#### Scenario: Schema failure short-circuits
- **WHEN** canonical source fails schema validation
- **THEN** the validator reports the schema error and does not run Mermaid, accessibility, or responsive checks

#### Scenario: Consolidated report
- **WHEN** all layers run
- **THEN** the validator emits a single report listing each check and its pass/fail status

### Requirement: Schema validation
The validator SHALL validate canonical source against the appropriate JSON Schema (base plus artifact overlay) and report all required-field and enum violations.

#### Scenario: Enum violation reported
- **WHEN** a source uses a `status` value outside the allowed enum
- **THEN** the validator reports the invalid enum value

### Requirement: Mermaid validation
The validator SHALL check every Mermaid section by parsing for fast failures and SHALL support rendering via the Mermaid CLI for higher-confidence verification in CI.

#### Scenario: Broken diagram caught
- **WHEN** a Mermaid section contains a syntax error
- **THEN** the validator reports a Mermaid parse/render failure identifying the section

### Requirement: Accessibility validation
The validator SHALL run accessibility checks on rendered HTML using Axe-core and SHALL enforce WCAG AA contrast (4.5:1 normal text, 3:1 large text). The check MUST pass with zero critical violations.

#### Scenario: Critical a11y violation fails
- **WHEN** rendered HTML has a critical accessibility violation
- **THEN** the validator marks the accessibility check as failed

### Requirement: Responsive validation
The validator SHALL render the HTML across at least one desktop and one mobile viewport and SHALL fail when content is clipped or produces uncontrolled horizontal overflow.

#### Scenario: Mobile overflow flagged
- **WHEN** the document overflows horizontally at mobile width
- **THEN** the responsive check fails

### Requirement: Print and PDF validation
The validator SHALL verify PDF export produces usable pagination and readable diagrams using the print CSS path.

#### Scenario: PDF pagination check
- **WHEN** PDF export is validated
- **THEN** the validator confirms the PDF generates with readable, paginated content

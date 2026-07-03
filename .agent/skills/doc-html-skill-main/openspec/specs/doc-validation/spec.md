# doc-validation Specification

## Purpose
Define the layered validator for branded review artifacts, covering schema, Mermaid, accessibility, responsive, and print/PDF checks with a consolidated pass/fail report.

## Requirements

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

### Requirement: Widget accessibility checks
The accessibility layer SHALL cover the new widget kinds: severity tags, badges, and callout text MUST meet WCAG AA contrast against their soft backgrounds, and `tabs` MUST be operable by keyboard with programmatically associated labels. Critical violations in any widget MUST fail the accessibility check.

#### Scenario: Low-contrast severity tag fails
- **WHEN** a rendered document contains a severity tag below 4.5:1 contrast
- **THEN** the accessibility check fails identifying the element

#### Scenario: Tabs keyboard operable
- **WHEN** the accessibility layer inspects a `tabs` widget
- **THEN** it verifies the tab controls are focusable and switchable without a pointer

### Requirement: Print content completeness
The print/PDF layer SHALL verify that no widget content is hidden in print output: all tab panes and all `details` bodies present in the source MUST be detectable in the print-rendered document.

#### Scenario: Hidden tab pane fails print check
- **WHEN** a tab pane's text content is absent from the print-rendered output
- **THEN** the print check fails identifying the section

### Requirement: Skin-aware validation runs
The validator SHALL run its rendered-output layers (accessibility, responsive, print) against the document's resolved skin, and SHALL support validating one source under an explicitly requested skin for matrix testing in CI.

#### Scenario: Validation respects override
- **WHEN** a source sets `theme.layout: brief`
- **THEN** rendered-output checks run against the brief-skin output

#### Scenario: Matrix run requested
- **WHEN** the validator is invoked with an explicit skin parameter for one source
- **THEN** it renders and validates that source under the requested skin

### Requirement: Dark-scheme accessibility validation
When a source declares `theme.mode: dark` or `auto`, the accessibility layer SHALL additionally run with dark color-scheme emulation (browser `prefers-color-scheme: dark`) and enforce the same WCAG AA thresholds and widget checks as the light pass. Documents with `mode: light` (or omitted) SHALL keep the single light pass.

#### Scenario: Auto document validated both ways
- **WHEN** the validator runs on a `mode: auto` source
- **THEN** accessibility checks execute under both light and dark emulation and both must pass

#### Scenario: Light document unchanged
- **WHEN** the validator runs on a source without `theme.mode`
- **THEN** only the light accessibility pass executes

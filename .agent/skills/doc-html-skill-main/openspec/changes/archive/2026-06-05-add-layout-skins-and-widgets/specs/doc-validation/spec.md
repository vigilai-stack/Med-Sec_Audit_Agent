# doc-validation Specification (delta)

## ADDED Requirements

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

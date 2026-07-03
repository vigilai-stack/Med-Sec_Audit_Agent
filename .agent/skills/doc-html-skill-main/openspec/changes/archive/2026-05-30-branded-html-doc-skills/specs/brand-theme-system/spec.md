## ADDED Requirements

### Requirement: Semantic theme-token model
The system SHALL define a semantic theme-token model covering at least colors (`bg`, `surface`, `text`, `text_dim`, `line`, `primary`, `primary_soft`, `success`, `warning`, `danger`), fonts (`sans`, `serif`, `mono`), `radius`, and `spacing`. Tokens MUST be the single source of truth for both page and diagram styling.

#### Scenario: Token set drives styling
- **WHEN** a theme token set is supplied to the renderer
- **THEN** all page colors and fonts derive from those tokens with no hard-coded color values in output

### Requirement: Token-to-CSS-variable mapping
The system SHALL map each semantic color, font, radius, and spacing token to a corresponding CSS custom property (e.g. `primary` → `--color-primary`, `sans` → `--font-sans`).

#### Scenario: CSS variables emitted
- **WHEN** the renderer applies a theme token set
- **THEN** the output HTML defines CSS custom properties for every mapped token

### Requirement: Token-to-Mermaid mapping
The system SHALL map relevant tokens into Mermaid `themeVariables` using the modifiable `base` theme (`primary` → `primaryColor`/`primaryBorderColor`, `text` → `primaryTextColor`/`textColor`, `line` → `lineColor`, `bg` → `background`, `sans` → `fontFamily`).

#### Scenario: Diagram inherits brand colors
- **WHEN** a theme defines `primary` and `line` tokens
- **THEN** the injected Mermaid config sets the matching `themeVariables` so diagrams match the page

### Requirement: Default theme fallback
The system SHALL provide a default theme token set so artifacts render with a coherent neutral brand when no company theme is supplied.

#### Scenario: Render without custom theme
- **WHEN** no theme tokens are provided
- **THEN** the renderer applies the default token set and produces a styled document

### Requirement: Contrast-safe tokens
The theme system SHALL support validation of color tokens against WCAG AA contrast thresholds (4.5:1 normal text, 3:1 large text) so brand customizations can be checked.

#### Scenario: Low-contrast theme flagged
- **WHEN** a supplied theme pairs `text` and `bg` below 4.5:1 contrast
- **THEN** the validator reports a contrast violation

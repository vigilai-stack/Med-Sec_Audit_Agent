# brand-theme-system Specification

## Purpose
Define the semantic theme-token model that is the single source of truth for page and diagram styling, including CSS-variable and Mermaid mappings, a default theme fallback, and contrast-safety validation.

## Requirements

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

### Requirement: Skin token layers
The theme system SHALL support skin-level token overrides resolved in the order: default theme, then brand theme, then skin overrides. Resolved tokens MUST remain the single source of truth for both page CSS custom properties and Mermaid `themeVariables` under every skin.

#### Scenario: Resolution order applied
- **WHEN** the default theme, a brand theme, and the active skin each define `primary`
- **THEN** the skin's value wins in the rendered CSS variables and Mermaid config

#### Scenario: Brand survives skin switch
- **WHEN** the same brand theme is rendered under two different skins
- **THEN** brand tokens not overridden by either skin are identical in both outputs

### Requirement: Widget semantic tokens
The token model SHALL include semantic tokens required by the widget library: callout intent colors (`note`, `tip`, `warning`, `danger`), severity colors (`high`, `medium`, `low`, `info`), code block surface/text colors, and heatmap level colors. Each soft background token MUST pair with a text token meeting WCAG AA contrast.

#### Scenario: Severity tokens emitted
- **WHEN** a theme is applied
- **THEN** CSS custom properties exist for every severity and callout intent pair

#### Scenario: Intent pair passes contrast
- **WHEN** a brand theme overrides a callout background token
- **THEN** contrast validation checks the paired text token against the new background at 4.5:1

### Requirement: Dark token palette
The theme system SHALL provide a complete dark color palette in the default theme under a `dark` group using the same keys as `color`. Brand themes and skin token files MAY override any subset of dark keys under their own `dark` group, resolved with the same layering as light tokens (default → brand → skin). Dark keys not overridden anywhere SHALL fall back to the resolved default dark value, and dark keys absent from the default SHALL fall back to the resolved light value.

#### Scenario: Default dark palette complete
- **WHEN** no brand or skin dark overrides are supplied
- **THEN** every light color token has a resolved dark counterpart from the default theme

#### Scenario: Partial brand dark override
- **WHEN** a brand theme overrides only `dark.primary`
- **THEN** the resolved dark palette uses the brand's primary and the default dark values for all other keys

### Requirement: Dark palette contrast safety
All dark-mode token pairs that carry text — text/background, dim-text/background, callout intent pairs, severity pairs, badge pairs, code surface pair, heatmap level pairs — SHALL meet WCAG AA contrast (4.5:1 normal text, 3:1 large text), and the contrast validation path SHALL check dark pairs when a dark palette is in play.

#### Scenario: Dark severity tag passes AA
- **WHEN** a document renders in dark mode with a `high` severity tag
- **THEN** the tag's text color meets 4.5:1 against its dark soft background

#### Scenario: Careless dark override caught
- **WHEN** a brand theme sets a dark callout background that drops its paired text below 4.5:1
- **THEN** the validation run under dark emulation reports a contrast violation

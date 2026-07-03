# brand-theme-system Specification (delta)

## ADDED Requirements

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

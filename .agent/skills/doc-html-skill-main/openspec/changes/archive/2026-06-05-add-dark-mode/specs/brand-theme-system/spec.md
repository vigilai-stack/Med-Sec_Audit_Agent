# brand-theme-system Specification (delta)

## ADDED Requirements

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

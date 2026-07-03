# doc-validation Specification (delta)

## ADDED Requirements

### Requirement: Dark-scheme accessibility validation
When a source declares `theme.mode: dark` or `auto`, the accessibility layer SHALL additionally run with dark color-scheme emulation (browser `prefers-color-scheme: dark`) and enforce the same WCAG AA thresholds and widget checks as the light pass. Documents with `mode: light` (or omitted) SHALL keep the single light pass.

#### Scenario: Auto document validated both ways
- **WHEN** the validator runs on a `mode: auto` source
- **THEN** accessibility checks execute under both light and dark emulation and both must pass

#### Scenario: Light document unchanged
- **WHEN** the validator runs on a source without `theme.mode`
- **THEN** only the light accessibility pass executes

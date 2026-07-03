# layout-skin-system Specification (delta)

## ADDED Requirements

### Requirement: Per-skin dark treatment
Each skin SHALL render correctly under the dark palette via skin-level dark token overrides: `docs-site` darkens its topbar/TOC chrome consistently with the canvas; `editorial` uses a warm dark slate (not pure black) preserving its print-first character; `brief` darkens its hero gradient stops and raises chip/shadow contrast. Skin dark overrides participate in the standard token resolution and MUST NOT introduce hard-coded colors in skin CSS.

#### Scenario: Every skin renders dark
- **WHEN** the same `mode: dark` source is rendered under each of the three skins
- **THEN** all three produce dark-palette output with readable chrome and no light-palette remnants

#### Scenario: Brief hero legible in dark
- **WHEN** a `mode: dark` document renders under the `brief` skin
- **THEN** hero title, lead, and chips meet WCAG AA against the darkened gradient

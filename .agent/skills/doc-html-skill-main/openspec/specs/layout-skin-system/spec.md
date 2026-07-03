# layout-skin-system Specification

## Purpose
Define the three render skins (docs-site, editorial, brief) layered over a single shared widget library and canonical content model, including per-artifact-type default selection, brief-skin width hints, print behavior, and skin-aware diagram theming.

## Requirements

### Requirement: Three render skins over one widget library
The system SHALL provide three render skins — `docs-site` (sticky table-of-contents sidebar with top brand bar), `editorial` (serif, print-first report layout), and `brief` (KPI stat row with bento card grid) — implemented as a skin template plus a skin CSS layer. All skins MUST consume the same shared widget macros and the same canonical content model, differing only in page scaffold, typography scale, and component skinning.

#### Scenario: Same source renders under every skin
- **WHEN** one schema-valid canonical source is rendered once per skin
- **THEN** all three outputs contain the same content (headings, widget data, diagrams, evidence) presented in skin-specific layout

#### Scenario: Skins share widget behavior
- **WHEN** a section kind (e.g. `callout`) is rendered under two different skins
- **THEN** both outputs use the same widget markup structure with skin-level styling differences only

### Requirement: Per-artifact-type default skin with override
The renderer SHALL select a default skin from the artifact type — `architecture-review` and `test-charter` default to `docs-site`; `prd-review` and `user-story-review` default to `editorial`; `risk-analysis` defaults to `brief` — and SHALL honor an optional `theme.layout` field that overrides the default. An unknown `theme.layout` value MUST fail schema validation.

#### Scenario: Default applied by type
- **WHEN** an `architecture-review` source omits `theme.layout`
- **THEN** the document renders with the `docs-site` skin

#### Scenario: Author override wins
- **WHEN** a `prd-review` source sets `theme.layout: brief`
- **THEN** the document renders with the `brief` skin

#### Scenario: Invalid layout rejected
- **WHEN** a source sets `theme.layout: fancy`
- **THEN** schema validation fails identifying the invalid enum value

### Requirement: Brief-skin width hints
The `brief` skin SHALL honor an optional per-section `width` hint (`full` or `half`), placing `half` sections side by side in its grid. Other skins MUST ignore the hint. The renderer MUST fall back to full width for section kinds that cannot shrink (e.g. `mermaid`, wide `table`).

#### Scenario: Half sections paired
- **WHEN** two consecutive sections declare `width: half` under the `brief` skin
- **THEN** they render side by side at desktop width and stack at narrow viewports

#### Scenario: Hint ignored elsewhere
- **WHEN** a section declares `width: half` under the `editorial` skin
- **THEN** the section renders full width with no layout error

### Requirement: Skin print behavior
Each skin SHALL provide a print CSS path in which no content is hidden: all tab panes are displayed (stacked with their labels) and all collapsible details are expanded. The `editorial` skin is the print-optimized reference layout, and PDF export MUST be available for every skin.

#### Scenario: Tabs expanded on paper
- **WHEN** a document containing a `tabs` section is exported to PDF
- **THEN** every tab pane appears in the PDF preceded by its tab label

#### Scenario: Details expanded on paper
- **WHEN** a document containing a `details` section is exported to PDF
- **THEN** the collapsed content is fully visible in the PDF

### Requirement: Readable, expandable diagrams
Every Mermaid figure SHALL render at full content width under every skin, and SHALL provide a fullscreen expand control that works without JavaScript (CSS-only) and remains available in frozen mode. Interactive mode SHALL additionally support wheel/pinch zoom and drag panning inside the expanded view. The expand control MUST be hidden in print output.

#### Scenario: Diagram expandable without JS
- **WHEN** a rendered document is opened with scripting disabled and the expand control is activated
- **THEN** the diagram fills the viewport with scrollable overflow and a visible close control

#### Scenario: Zoom in interactive mode
- **WHEN** a diagram is expanded in interactive mode
- **THEN** the user can zoom with the scroll wheel and pan by dragging

#### Scenario: Print hides controls
- **WHEN** the document is printed
- **THEN** no expand/close controls appear and the diagram renders at full page width

### Requirement: Skin-aware diagram theming
Each skin SHALL contribute diagram token overrides so Mermaid `themeVariables` (interactive mode) and the Mermaid CLI config (frozen mode) follow the active skin's palette. Token resolution MUST apply in the order: default theme, then brand theme, then skin overrides.

#### Scenario: Editorial diagrams match palette
- **WHEN** a document renders under the `editorial` skin
- **THEN** diagram node fills, borders, and text derive from the editorial skin's resolved tokens rather than Mermaid defaults

### Requirement: Per-skin dark treatment
Each skin SHALL render correctly under the dark palette via skin-level dark token overrides: `docs-site` darkens its topbar/TOC chrome consistently with the canvas; `editorial` uses a warm dark slate (not pure black) preserving its print-first character; `brief` darkens its hero gradient stops and raises chip/shadow contrast. Skin dark overrides participate in the standard token resolution and MUST NOT introduce hard-coded colors in skin CSS.

#### Scenario: Every skin renders dark
- **WHEN** the same `mode: dark` source is rendered under each of the three skins
- **THEN** all three produce dark-palette output with readable chrome and no light-palette remnants

#### Scenario: Brief hero legible in dark
- **WHEN** a `mode: dark` document renders under the `brief` skin
- **THEN** hero title, lead, and chips meet WCAG AA against the darkened gradient

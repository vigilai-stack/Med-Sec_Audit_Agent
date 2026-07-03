# branded-html-renderer Specification

## Purpose
Define the deterministic renderer that converts schema-valid canonical source into a single self-contained branded HTML file, owning all chrome, rendering sections by kind, supporting interactive and frozen Mermaid modes, optional PDF export, and a CLI.

## Requirements

### Requirement: Deterministic source-to-HTML rendering
The renderer SHALL convert schema-valid canonical source into a single self-contained HTML file using Jinja templates, producing identical output for identical input. The renderer MUST validate the source against its schema before rendering and MUST refuse to render invalid source.

#### Scenario: Valid source renders
- **WHEN** a schema-valid YAML or JSON source is passed to the renderer
- **THEN** it produces a single HTML file with hero, sections, evidence, and inlined CSS

#### Scenario: Invalid source blocked
- **WHEN** source that fails schema validation is passed to the renderer
- **THEN** the renderer exits with an error and does not write HTML

#### Scenario: Deterministic output
- **WHEN** the same source is rendered twice
- **THEN** the two HTML outputs are byte-identical

### Requirement: Renderer owns all chrome
The renderer SHALL own all HTML boilerplate, CSS, layout, print styles, and Mermaid bootstrapping. The canonical source MUST NOT contain hand-authored HTML, CSS, or JavaScript for page chrome.

#### Scenario: No chrome in source
- **WHEN** canonical source contains only content fields
- **THEN** the rendered HTML includes complete page chrome supplied entirely by the renderer templates

### Requirement: Section rendering by kind
The renderer SHALL render each section according to its `kind` using a shared widget macro library consumed by all skins: `prose` as styled prose; `mermaid` as a Mermaid diagram block with optional caption and automatic figure numbering; `table` as a styled table built from `columns` and `rows`; `callout` as an intent-styled admonition (note/tip/warning/danger); `stats` as KPI stat cards or a stat band; `steps` as a numbered procedure; `cards` as a card grid with variant styling (generic, decision, rejected, persona); `keyvalue` as a definition list; `code` as a monospace block with optional filename header and language tag; `tabs` as keyboard-accessible CSS-only tabbed panes; `details` as a native collapsible block; `timeline` as an ordered event list; `heatmap` as a colored matrix grid; and `meters` as labeled progress bars.

#### Scenario: Mixed section document
- **WHEN** a document contains prose, mermaid, and table sections
- **THEN** each is rendered with the layout appropriate to its kind

#### Scenario: Callout intent styling
- **WHEN** a document contains `callout` sections with different `intent` values
- **THEN** each renders with the icon and color treatment of its intent, sourced from theme tokens

#### Scenario: Tabs render without JavaScript
- **WHEN** a document with a `tabs` section is rendered and opened with scripting disabled
- **THEN** tab switching still works via form controls and all panes remain reachable by keyboard

#### Scenario: Figure numbering deterministic
- **WHEN** a document contains multiple `mermaid` sections with captions
- **THEN** figures are numbered in source order and two renders of the same source produce identical numbering

### Requirement: Two Mermaid rendering modes
The renderer SHALL support an interactive mode (Mermaid runs client-side from embedded source) as the default, and a frozen mode (diagrams pre-rendered to SVG via the Mermaid CLI and inlined) selected by `export.freeze_diagrams` or a CLI flag. Interactive mode MUST initialize Mermaid with `securityLevel: strict` by default.

#### Scenario: Interactive default
- **WHEN** a document is rendered without freeze enabled
- **THEN** the HTML embeds Mermaid source and initializes Mermaid client-side with `securityLevel: strict`

#### Scenario: Frozen archival mode
- **WHEN** `freeze_diagrams` is true
- **THEN** diagrams are pre-rendered to inline SVG and the output requires no client-side Mermaid

### Requirement: Optional PDF export
The renderer SHALL support optional PDF export of the rendered HTML using a headless browser print path honoring print CSS, gated by `export.pdf`.

#### Scenario: PDF requested
- **WHEN** `export.pdf` is true
- **THEN** a PDF is produced from the rendered HTML using print styles

### Requirement: CLI interface
The renderer SHALL expose a command-line interface accepting input source path, schema path, template directory, template name, and output path.

#### Scenario: CLI render
- **WHEN** the renderer is invoked with `--input`, `--schema`, `--template-dir`, and `--output`
- **THEN** it validates and renders to the given output path

### Requirement: Skin template selection
The renderer SHALL choose the skin template and CSS layer from the artifact type's default mapping, overridden by `theme.layout` when present, and SHALL inline only the active skin's CSS layer into the output.

#### Scenario: Only active skin CSS inlined
- **WHEN** a document renders under the `brief` skin
- **THEN** the output HTML contains the shared widget CSS and the brief skin layer, but not the docs-site or editorial layers

### Requirement: Overlay data rendering
The renderer SHALL render artifact overlay fields as widgets in a fixed position (after the summary, before authored sections): architecture `decisions` as decision cards, `constraints` as a severity-tagged list, `interfaces` as a key-value block, `alternatives` as rejected-variant cards, and `deployment_context` as a note callout. Equivalent mappings SHALL apply to the other artifact types' overlay fields. Overlay rendering MUST be deterministic and MUST NOT require authors to duplicate overlay data into `sections`.

#### Scenario: Decisions become visible
- **WHEN** an `architecture-review` source contains `decisions` entries
- **THEN** the rendered HTML displays each decision with its title, rationale, and status

#### Scenario: Constraint severity displayed
- **WHEN** a constraint carries `severity: high`
- **THEN** it renders with a high-severity tag styled from theme tokens

#### Scenario: No overlay data, no empty shells
- **WHEN** a source omits all overlay fields
- **THEN** the output contains no empty overlay sections

### Requirement: Print expansion of interactive widgets
The renderer's print path SHALL ensure no content is hidden on paper: all tab panes display stacked with their labels and all `details` blocks render expanded.

#### Scenario: Print shows every pane
- **WHEN** print CSS is applied to a document with `tabs` and `details` sections
- **THEN** all pane and detail content is visible without interaction

### Requirement: Mode-aware CSS emission
The renderer SHALL honor `theme.mode`: `light` (default) emits light tokens in `:root`; `dark` emits dark tokens in `:root`; `auto` emits light tokens in `:root` plus dark tokens under `@media (prefers-color-scheme: dark)` scoped to `:root[data-theme-mode="auto"]`. Widget and skin CSS MUST NOT change per mode — only the custom-property values swap. Output MUST remain deterministic for all modes.

#### Scenario: Explicit dark document
- **WHEN** a source sets `theme.mode: dark`
- **THEN** the rendered page uses the dark palette regardless of OS preference

#### Scenario: Auto follows the OS
- **WHEN** a source sets `theme.mode: auto` and the reader's OS prefers dark
- **THEN** the page renders with the dark palette, and with the light palette when the OS prefers light

#### Scenario: Omitted mode unchanged
- **WHEN** a source omits `theme.mode`
- **THEN** the rendered output is identical to today's light rendering

### Requirement: Mode-aware Mermaid theming
Interactive Mermaid initialization SHALL select `themeVariables` matching the active palette: dark variables for `mode: dark`, and for `mode: auto` the palette matching `prefers-color-scheme` evaluated at load time. Frozen mode SHALL resolve deterministically: `dark` freezes with dark variables; `light` and `auto` freeze with light variables, and a frozen `auto` document SHALL pin its page palette to light so page and diagrams cannot mismatch.

#### Scenario: Dark diagrams match dark page
- **WHEN** a `mode: dark` document renders interactively
- **THEN** Mermaid initializes with the dark theme variables and diagrams match the page palette

#### Scenario: Frozen auto pins light
- **WHEN** a `mode: auto` document is frozen
- **THEN** both the page and the inlined SVGs use the light palette

### Requirement: Print stays light under every mode
The embedded print CSS SHALL force the light/white print palette for documents of every mode, including `dark`.

#### Scenario: Dark document prints white
- **WHEN** a `mode: dark` document is printed or exported to PDF
- **THEN** the output uses a white background with light-palette token values

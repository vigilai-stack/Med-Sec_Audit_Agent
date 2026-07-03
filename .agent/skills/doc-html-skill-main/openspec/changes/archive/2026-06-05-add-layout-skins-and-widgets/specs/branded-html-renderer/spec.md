# branded-html-renderer Specification (delta)

## MODIFIED Requirements

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

## ADDED Requirements

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

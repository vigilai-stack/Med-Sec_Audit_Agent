## ADDED Requirements

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
The renderer SHALL render each section according to its `kind`: `prose` as styled prose, `mermaid` as a Mermaid diagram block, and `table` as a styled table built from `columns` and `rows`.

#### Scenario: Mixed section document
- **WHEN** a document contains prose, mermaid, and table sections
- **THEN** each is rendered with the layout appropriate to its kind

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

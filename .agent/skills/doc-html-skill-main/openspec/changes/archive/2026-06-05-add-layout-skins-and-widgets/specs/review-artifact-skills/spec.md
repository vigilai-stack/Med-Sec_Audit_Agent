# review-artifact-skills Specification (delta)

## ADDED Requirements

### Requirement: Widget-aware authoring guidance
Each artifact skill SHALL include guidance for choosing among the widget section kinds (when to use `callout`, `stats`, `steps`, `cards`, `keyvalue`, `code`, `tabs`, `details`, `timeline`, `heatmap`, `meters` versus plain `prose`/`table`), and SHALL prefer the type's signature widgets (e.g. risk-analysis emits a `heatmap`; test-charter emits `meters` for coverage; architecture emits decision content through overlay fields). Skills MUST NOT overuse decorative widgets — guidance SHALL cap `stats` at one section per document by default.

#### Scenario: Risk skill emits heatmap
- **WHEN** the risk-analysis skill authors a document with a risk matrix
- **THEN** it emits a `heatmap` section rather than a plain table by default

#### Scenario: Restraint on decorative widgets
- **WHEN** an artifact skill authors a typical document
- **THEN** it emits at most one `stats` section unless explicitly asked for more

### Requirement: Overlay fields authored as first-class content
Each artifact skill SHALL author its overlay fields (e.g. architecture `decisions`, `constraints` with severity, `interfaces`, `alternatives`) knowing they render as visible components, and MUST NOT duplicate overlay content into `sections`.

#### Scenario: No duplicated decisions
- **WHEN** the architecture skill records decisions
- **THEN** they appear in the `decisions` overlay field and not as a redundant cards section

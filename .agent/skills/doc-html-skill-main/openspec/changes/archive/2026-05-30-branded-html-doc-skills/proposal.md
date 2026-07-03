## Why

Agent-generated analysis (user-story reviews, architecture docs, PRDs, risk registers, test charters) currently lands as unreadable terminal text or one-off, prompt-authored HTML that repeats boilerplate on every run — expensive in output tokens, inconsistent in branding, and hard to diff in git. Research (`docs/research/deep-research-report (9).md`) shows a stronger pattern proven by `walkthrough`, `visual-explainer`, and Ring's branded explainers: a **schema-first, renderer-second** architecture where thin skills author compact structured source and a deterministic renderer owns all theme, layout, and Mermaid chrome.

## What Changes

- Introduce a **schema-first document pipeline**: agents emit compact, validated YAML/JSON canonical source; a deterministic renderer produces single-file branded HTML. The model authors content, never chrome.
- Add a **shared base schema** (`schema_version`, `artifact_type`, `title`, `summary`, `sections`, `evidence`, `export`) with artifact-specific overlays, expressed as JSON Schema for validation.
- Add a **brand theme-token system** that maps semantic tokens (color, font, radius, spacing) into both CSS variables and Mermaid `themeVariables`, keeping page and diagrams visually consistent.
- Add a **deterministic renderer** (Jinja templates + `render.py`) that emits self-contained HTML with two Mermaid modes: interactive (client-side, `securityLevel: strict`) by default and frozen SVG for archival/PDF.
- Add a **layered validator** covering schema, Mermaid parse/render, accessibility (Axe / WCAG AA contrast), responsive layout, and print/PDF.
- Add an **orchestrator skill** that routes a request to the right artifact type, assembles canonical source, and selects a template.
- Add **five artifact specialist skills**: user-story review, architecture review, PRD review, risk analysis, and test charter — each a thin `SKILL.md` extending the base schema.
- Establish token-efficiency operating targets (canonical source 2–12 KB, 0 KB model-emitted HTML boilerplate, Mermaid blocks under 40 lines, section-level regeneration).
- **Non-goals (this change):** Docusaurus publication path, GitHub Actions/Pages preview pipeline, and pre-commit hooks are deferred to a later operations/publication wave.

## Capabilities

### New Capabilities
- `canonical-doc-schema`: Shared base document schema plus per-artifact overlays (user-story, architecture, PRD, risk, test-charter), defined as JSON Schema for validation and git-friendly diffing.
- `brand-theme-system`: Semantic theme-token model and its mapping into CSS variables and Mermaid theme variables, enabling consistent company branding without hard-coded styles.
- `branded-html-renderer`: Deterministic renderer that turns validated canonical source into self-contained branded HTML, with interactive and frozen Mermaid modes and optional PDF export.
- `doc-validation`: Layered validation of canonical source and rendered HTML — schema, Mermaid syntax/render, accessibility, responsive layout, and print/PDF.
- `review-doc-orchestrator`: Entry skill that classifies the request, selects artifact type and template, gathers evidence scope, and produces validated canonical source ready to render.
- `review-artifact-skills`: The five thin artifact specialist skills that author compact, schema-valid canonical source for their respective review document types.

### Modified Capabilities
<!-- None — this is a greenfield capability suite; no existing specs in openspec/specs/. -->

## Impact

- **New code/assets**: `.claude/skills/` tree — orchestrator, five artifact skills, `render-branded-html` (schemas, Jinja templates, theme CSS, `render.py`, `freeze_mermaid.sh`, `export_pdf.py`), and `validate-branded-doc` (schema/Mermaid/a11y/responsive/export validators).
- **Dependencies**: Python (Jinja2, PyYAML, jsonschema), Node + Mermaid CLI (`@mermaid-js/mermaid-cli`), Playwright + Axe-core for validation.
- **Runtime/context**: Each invoked `SKILL.md` stays under Anthropic's 500-line guidance; heavy reference material and templates live in support files loaded only when needed.
- **Out of scope / future**: Docusaurus export target, CI preview and Pages deployment, pre-commit integration.

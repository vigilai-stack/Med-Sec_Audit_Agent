# Proposal: add-layout-skins-and-widgets

## Why

Every rendered document today is the same vertical stack of identical white cards built from only three section kinds (`prose`, `mermaid`, `table`), and the architecture overlay's richest structured data (`decisions`, `constraints`, `interfaces`, `alternatives`, `deployment_context`) is validated but **never rendered** — it is silently invisible in the HTML. Design exploration (see `experiments/design-{a,b,c}-*.html`) produced three validated visual directions and a widget catalog that make documents far more attractive and readable without breaking the schema-first, single-file, token-driven architecture.

## What Changes

- Add a **widget library** of new section kinds to the base schema and renderer:
  - Tier 1 (all artifact types): `callout` (note/tip/warning/danger), `stats` (KPI cards/band), `steps` (numbered procedure), `cards` (generic/decision card grid), `keyvalue` (definition list), semantic badge intents, figure captions + numbering for `mermaid` sections.
  - Tier 2 (dev/architecture): `code` (filename header, language, copy button), `tabs` (CSS-only, keyboard accessible), `details` (collapsible), `timeline`.
  - Tier 3 (type-specific): `heatmap` (risk matrix), `meters` (coverage bars), persona cards and KPI-delta variants of `cards`/`stats`.
- Add **three render skins** sharing one widget library and one token pipeline: `docs-site` (sticky TOC sidebar, topbar), `editorial` (serif print-first report), `brief` (KPI row + bento grid).
- Add **per-artifact-type default skin with `theme.layout` override** (default + override model): architecture/test-charter → `docs-site`, PRD/user-story → `editorial`, risk-analysis/benchmark-style → `brief`.
- **Render the overlay data** that is currently invisible: `decisions` → decision cards/ledger, `constraints` → severity-tagged callouts/list, `interfaces` → key-value table, `alternatives` → rejected-alternative blocks, `deployment_context` → note aside.
- Add optional per-section `width: full | half` hint consumed by the `brief` skin (ignored by other skins).
- Extend **print/PDF behavior**: print CSS force-opens `tabs` and `details` so no content is hidden on paper.
- Extend **validation**: schema layer covers new kinds; a11y layer checks widget contrast (severity tags, badges) and keyboard operability of tabs; Mermaid `themeVariables` follow the active skin's tokens so diagrams never clash with the page palette.
- Update authoring skills and orchestrator guidance so the model knows when to use which widget and how skin defaults are chosen.
- All changes are **additive** (no breaking schema changes): existing v1 sources render unchanged under their type's default skin.

## Capabilities

### New Capabilities
- `layout-skin-system`: Skin definitions (docs-site, editorial, brief), per-artifact-type defaults, `theme.layout` override, per-skin print behavior, and skin-aware Mermaid theming.

### Modified Capabilities
- `canonical-doc-schema`: New section `kind` values (callout, stats, steps, cards, keyvalue, code, tabs, details, timeline, heatmap, meters), optional `theme.layout`, optional per-section `width` hint, figure caption fields on mermaid sections.
- `branded-html-renderer`: Render all new widget kinds; render overlay fields (decisions, constraints, interfaces, alternatives, deployment_context) as distinct components; select template/CSS by skin; print expansion of interactive widgets.
- `brand-theme-system`: Token set extended per skin; tokens drive both page CSS and Mermaid `themeVariables` for every skin.
- `doc-validation`: Schema validation of new kinds; a11y checks for new widgets (contrast, keyboard access); print layer verifies tabs/details are expanded.
- `review-artifact-skills`: Authoring guidance for choosing widget kinds and emitting overlay data knowing it will render.

## Impact

- **Schemas**: `.claude/skills/render-branded-html/schemas/*.json` (base + overlays) gain new section kinds and theme/layout fields (additive).
- **Renderer**: `render.py`, `templates/standard.html.j2` (split into skin templates + shared widget macros), `templates/print.html.j2`, `assets/theme.css` (widget library + per-skin CSS), `assets/mermaid-config.js`.
- **Validation**: `validate-branded-doc/scripts/validate_all.py` and its layer checks.
- **Skills**: SKILL.md guidance in the five artifact skills, `render-branded-html`, `review-doc-orchestrator`.
- **Examples**: `examples/*.yaml` extended to exercise new widgets; `experiments/design-*.html` retained as visual reference for each skin.
- **Dependencies**: none added — same Python/Jinja + optional Node (Mermaid CLI/Playwright) stack.

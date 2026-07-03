# Tasks: add-layout-skins-and-widgets

## 1. Schema additions (additive)

- [x] 1.1 Add new section kinds (`callout`, `stats`, `steps`, `cards`, `keyvalue`, `code`, `tabs`, `details`, `timeline`, `heatmap`, `meters`) with per-kind content contracts to `review-artifact.schema.json`
- [x] 1.2 Add optional `caption` to `mermaid` sections and optional per-section `width` (`full`/`half`) hint
- [x] 1.3 Add `theme.layout` enum (`docs-site`, `editorial`, `brief`) to the base schema
- [x] 1.4 Extend architecture overlay: `constraints` entries as string or `{text, severity}` (severity enum `high`/`medium`/`low`/`info`); bump `schema_version` to 2 (no backward compat needed)
- [x] 1.5 Migrate all `examples/*.yaml` and `examples/*.json` to schema v2 and confirm they validate

## 2. Theme tokens

- [x] 2.1 Add widget semantic tokens to `default-theme.json` and `theme.css` `:root` (callout intents, severities, code surface, heatmap levels) with AA-paired text colors
- [x] 2.2 Implement skin token layers in `render.py` with resolution order default → brand → skin
- [x] 2.3 Map skin-resolved tokens into Mermaid `themeVariables` (interactive) and the `mmdc` theme config (frozen)
- [x] 2.4 Extend contrast validation to cover the new intent/severity background+text pairs

## 3. Widget library (shared macros + CSS)

- [x] 3.1 Extract section rendering from `standard.html.j2` into `templates/widgets.html.j2` macros (prose, mermaid, table)
- [x] 3.2 Implement Tier 1 widget macros + CSS: `callout`, `stats`, `steps`, `cards` (variants generic/decision/rejected/persona), `keyvalue`, figure captions with deterministic numbering
- [x] 3.3 Implement Tier 2 widget macros + CSS: `code` (filename header, optional copy button stripped in frozen mode), `tabs` (radio-input, keyboard accessible), `details`, `timeline`
- [x] 3.4 Implement Tier 3 widget macros + CSS: `heatmap`, `meters`
- [x] 3.5 Unit-test renderer output per kind (golden-file or snapshot comparison; assert determinism)
- [x] 3.6 Diagram presentation: full-width figures, raised Mermaid font size, CSS-only fullscreen expand (no duplication), JS wheel-zoom/drag-pan enhancement in interactive mode, toggle hidden in print

## 4. Skins

- [x] 4.1 Restructure templates into `templates/skins/` with shared base; rebuild current layout as the `docs-site` skin (topbar, sticky TOC from section list, anchor links) using `experiments/design-a-docs-site.html` as visual reference
- [x] 4.2 Implement `editorial` skin (masthead, numbered sections, stat band, ledger-styled cards, booktabs tables) per `experiments/design-b-editorial.html`, token-driven
- [x] 4.3 Implement `brief` skin (hero, KPI row, 12-col bento grid honoring `width: half` with fallback to full) per `experiments/design-c-dashboard.html`
- [x] 4.4 Implement per-artifact-type default skin mapping + `theme.layout` override in `render.py`; inline only the active skin's CSS layer
- [x] 4.5 Render every example under each applicable skin; confirm byte-identical re-renders

## 5. Overlay rendering

- [x] 5.1 Implement overlay→widget normalization in `render.py` (architecture: decisions→decision cards, constraints→severity list, interfaces→keyvalue, alternatives→rejected cards, deployment_context→note callout)
- [x] 5.2 Add overlay mappings for the other artifact types (user-story personas/journey states, PRD goals/coverage, risk triggers/controls, test-charter missions/exit criteria)
- [x] 5.3 Place overlay blocks deterministically (after summary, before authored sections); no empty shells when fields absent
- [x] 5.4 Re-render `examples/rf-mcp-architecture.yaml` and confirm all four decisions and constraints are now visible

## 6. Print/PDF

- [x] 6.1 Update `print.css` (per skin) to force-display all tab panes with labels and expand all `details`
- [x] 6.2 Verify PDF export for one document per skin: pagination usable, no hidden widget content, diagrams readable

## 7. Validation layers

- [x] 7.1 Update `validate_all.py` schema layer for new kinds, `theme.layout`, severity vocabulary
- [x] 7.2 Add a11y checks: severity/badge/callout contrast, tabs keyboard operability (Axe + targeted assertions)
- [x] 7.3 Add print completeness check: all tab/details text present in print-rendered output
- [x] 7.4 Add skin-aware validation: run rendered-output layers against the resolved skin; support explicit `--skin` parameter for matrix runs

## 8. Skills & docs

- [x] 8.1 Update `render-branded-html/SKILL.md` with skins, widget kinds, defaults, and override
- [x] 8.2 Add widget when-to-use guidance to the five artifact skills (signature widgets per type; stats capped at one; overlay fields not duplicated into sections)
- [x] 8.3 Update `review-doc-orchestrator/SKILL.md` with skin selection guidance
- [x] 8.4 Extend examples to exercise new widgets (at least: architecture with callouts/steps/tabs, risk with heatmap, charter with meters) and update README

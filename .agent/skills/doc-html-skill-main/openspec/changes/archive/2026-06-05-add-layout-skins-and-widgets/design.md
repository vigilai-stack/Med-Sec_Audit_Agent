# Design: add-layout-skins-and-widgets

## Context

The current renderer produces one fixed layout: a 960px single-column stack of identical white cards, built from three section kinds (`prose`, `mermaid`, `table`). `standard.html.j2` renders only `summary`, `sections`, and `evidence` — overlay fields (`decisions`, `constraints`, `interfaces`, `alternatives`, `deployment_context`, plus the other artifact types' overlays) are schema-validated but never displayed.

Design exploration produced three working, self-contained mockups from the real `rf-mcp-architecture.yaml` content (`experiments/design-a-docs-site.html`, `design-b-editorial.html`, `design-c-dashboard.html`). They share one content model and differ only in template + CSS, which validated the "skins over one schema" approach. Feedback gathered during exploration locked three decisions: hybrid skin architecture, all three widget tiers, and per-type default skin with author override.

Hard constraints carried over from the original architecture (unchanged):
- Single self-contained HTML output, deterministic (byte-identical for identical input).
- Renderer owns all chrome; canonical source is content-only.
- One token set drives both page CSS and Mermaid `themeVariables`.
- WCAG AA, responsive, print/PDF support, layered validation.

## Goals / Non-Goals

**Goals:**
- One shared widget library (new section kinds) rendered consistently by all skins.
- Three skins — `docs-site`, `editorial`, `brief` — selected by per-artifact-type default with `theme.layout` override.
- Overlay data rendered as first-class components in every skin.
- Print/PDF correctness for interactive widgets (tabs, details force-opened).
- **Readability first**: base font ≥ 16px, generous line-height, all text/background pairs WCAG AA (including dim text and widget tags).
- **Diagrams big or zoomable**: Mermaid figures render full content width and every diagram gets a fullscreen expand control (CSS-only, works without JS) with wheel-zoom/drag-pan as a JS enhancement in interactive mode.
- Backward compatibility is NOT required (per user directive): `schema_version` bumps to 2 and existing examples are migrated in this change.

**Non-Goals:**
- No client-side framework or CDN runtime (no Shoelace/Tailwind/Bootstrap); CSS + minimal vanilla JS only.
- No syntax highlighting engine in wave 1 (`code` kind renders styled monospace; Pygments build-time highlighting is a candidate follow-up).
- No JS scroll-spy for the docs-site TOC in wave 1 (static TOC links; progressive enhancement later).
- No Docusaurus export, CI preview, or pre-commit hooks (still deferred per original change).
- No per-skin user-authored CSS; brand customization stays token-only.

## Decisions

### D1 — Skins are template + CSS layers over one widget library
Each skin is a Jinja template (`templates/skins/<skin>.html.j2`) plus a skin CSS layer, both consuming a **shared widget macro file** (`templates/widgets.html.j2`) and the shared token CSS. Widgets are written once; skins control page scaffold (topbar/TOC vs masthead vs hero/bento), typography scale, and component skinning via CSS custom properties and skin-scoped class on `<body>` (`.skin-editorial` etc.).

*Alternative considered:* three fully independent templates (as in the mockups). Rejected: triples widget maintenance and lets skins drift behaviorally.

### D2 — Widget vocabulary as new `kind` values, one schema for all skins
New kinds: `callout`, `stats`, `steps`, `cards`, `keyvalue`, `code`, `tabs`, `details`, `timeline`, `heatmap`, `meters`. Each gets a small required-field contract (e.g., `callout` requires `intent` ∈ note|tip|warning|danger and `body`; `stats` requires `items[]` of `{value,label}`; `tabs` requires `items[]` of `{label,body}`). `mermaid` gains optional `caption`; figures are auto-numbered by the renderer in document order.

*Alternative considered:* nested "blocks" inside prose sections (Notion-style). Rejected for wave 1: bigger schema redesign; flat section kinds match the existing model and the renderer's section loop.

### D3 — Default skin per artifact type, `theme.layout` override
Mapping lives in the renderer (single source of truth, exposed in docs): `architecture-review`/`test-charter` → `docs-site`; `prd-review`/`user-story-review` → `editorial`; `risk-analysis` → `brief`. `theme.layout` (enum) overrides. Unknown value = schema validation error.

*Alternative considered:* author always picks. Rejected: violates "model writes content, not presentation"; defaults keep authoring zero-cost.

### D4 — Overlay data renders via skin-agnostic component mapping
The renderer normalizes overlay fields into widget structures before templating: `decisions` → `cards` (variant: decision, with status tag + optional ADR ref), `constraints` → severity list (severity optional, defaults to `info`), `interfaces` → `keyvalue`, `alternatives` → rejected-cards, `deployment_context` → note `callout`. Skins then style those widgets natively (cards vs ledger vs tiles). Overlay sections are placed in a fixed position (after summary, before authored sections) so output stays deterministic.

*Alternative considered:* require authors to move overlay data into `sections`. Rejected: breaking, duplicates data, and the overlays are the per-type contract that skills already author.

### D5 — `width: half|full` as a hint, honored only by `brief`
Per-section optional `width`. The `brief` skin places `half` sections in a 12-col grid (6+6); other skins ignore it. Renderer falls back to `full` when a `half` section is a kind that can't shrink (`mermaid`, wide `table`).

### D6 — Interactive widgets must degrade on paper and without JS
`tabs` implemented with radio inputs + labels (keyboard accessible, zero JS); `details` uses native element; the only JS in wave 1 is the existing Mermaid bootstrap plus an optional copy-button handler (omitted in frozen/print builds). `print.css` force-displays all tab panes (stacked, each pane preceded by its label) and sets `details[open]` via `<details open>` injected in the print template.

### D8 — Diagram presentation: full-width figures + fullscreen expand
Every `mermaid` figure renders at full content width (no artificial max), with a checkbox-driven fullscreen mode: checking the toggle promotes the existing figure node to a fixed full-viewport overlay with scrollable stage (no content duplication, works JS-free, works in frozen mode). Interactive mode layers a small inline script on top: wheel/pinch zoom, drag pan, Esc to close. Print CSS hides the toggle. Mermaid `fontSize` is raised so node labels stay legible at default scale.

*Alternative considered:* external pan-zoom library (svg-pan-zoom). Rejected: CDN dependency conflicts with self-containment; ~30 lines of vanilla JS suffice.

### D7 — Skin-aware Mermaid theming
Each skin contributes a token subset (`diagram.*`) mapped into Mermaid `themeVariables` (and into the `mmdc` config for frozen mode), so diagrams inherit the skin palette — fixing the clash observed in the editorial mockup. Token resolution order: default theme → brand theme → skin overrides.

## Risks / Trade-offs

- [Widget sprawl makes authoring guidance harder; models may overuse flashy kinds] → SKILL.md guidance includes a "when to use" table per kind; validation warns (not fails) on e.g. >2 `stats` sections.
- [Bento (`brief`) layout breaks with unbalanced content] → `width` is only a hint with renderer fallback to full width; responsive collapse to single column below 860px.
- [Three skins × widget library grows CSS beyond comfortable inline size] → budget ~35KB inlined CSS per document (only the active skin's layer is inlined, not all three).
- [CSS-only tabs hide unselected panes from a11y tree scanning] → panes remain in DOM; Axe layer asserts labels/roles; print expands all panes so PDF never loses content.
- [Determinism risk from figure auto-numbering and overlay normalization] → both are pure functions of source order; covered by the existing byte-identical render test.
- [Per-type defaults may surprise users expecting old look] → old look is effectively `docs-site`-lite; release notes + `theme.layout` escape hatch.

## Migration Plan

1. Land schema additions (additive) + validator updates; all existing examples must still pass.
2. Extract shared widget macros from current template; current layout becomes the basis of `docs-site`.
3. Add `editorial` and `brief` skins; port experiment CSS into token-driven layers.
4. Wire overlay rendering + per-type defaults; re-render all `examples/` and visually diff.
5. Rollback: skins are render-time only — reverting the renderer restores previous output; sources need no changes.

## Open Questions

- Should `benchmark-report` (currently rendered via base schema) become a first-class artifact type with `brief` default, or stay type-less with `theme.layout: brief`? (Wave 1: stay type-less.)
- Copy-button JS in interactive mode: include (small inline script) or defer to wave 2? (Default: include, stripped in frozen mode.)
- Severity vocabulary for constraints: reuse status badge tokens or introduce `severity` enum (high/medium/low/info)? (Default: introduce enum, additive.)

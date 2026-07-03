---
name: render-branded-html
description: Deterministically render validated canonical review-doc source (YAML/JSON) into a single self-contained branded HTML file, with three layout skins (docs-site, editorial, brief), light/dark/auto mode, a widget section library, interactive or frozen Mermaid with fullscreen zoom, and optional PDF. Use when a review artifact's canonical source is ready and you need the styled HTML/PDF output. The model authors content; this renderer owns all chrome.
---

# render-branded-html

Turns schema-valid canonical source into branded, single-file HTML. The renderer
owns **all** chrome (HTML boilerplate, CSS, layout, print styles, Mermaid
bootstrapping, widget markup). Canonical source carries content only — never
hand-author HTML.

## Contract

- Input: a canonical YAML/JSON artifact (schema v2; see summary below).
- The renderer **validates first** and refuses to render invalid source.
- Output is **deterministic** — identical input yields byte-identical HTML.
- One HTML file serves screen *and* print: print CSS is embedded via
  `@media print` (tabs stack labelled, details expand, controls hide).

## Skins

One widget library, three skins. Default is chosen by `artifact_type`;
authors override with `theme.layout`; the CLI `--skin` flag overrides both.

| Skin | Look | Default for |
|---|---|---|
| `docs-site` | sticky TOC sidebar, topbar, anchor links | architecture-review, test-charter |
| `editorial` | serif print-first report, numbered sections | prd-review, user-story-review |
| `brief` | gradient hero, KPI cards, bento grid (honors section `width: half`) | risk-analysis |

## Render

```bash
python .claude/skills/render-branded-html/scripts/render.py \
  --input examples/architecture-review.yaml \
  --output build/architecture-review.html [--skin brief] [--theme brand.json]
```

The correct overlay schema is auto-selected from `artifact_type`.

## Widget section kinds

`prose`, `mermaid`, `table`, `callout` (note/tip/warning/danger), `stats`,
`steps`, `cards` (generic/decision/rejected/persona), `keyvalue`, `code`
(filename + copy button), `tabs` (CSS-only, keyboard operable, ≤6 tabs),
`details`, `timeline`, `heatmap` (risk matrix), `meters` (coverage bars).
Each kind's contract is in `schemas/review-artifact.schema.json`.

**Overlay fields render automatically** (after summary, before authored
sections): architecture `decisions`→decision cards, `constraints`→severity
list, `interfaces`→list, `deployment_context`→note callout,
`alternatives`→rejected cards — and equivalents for the other types. Never
duplicate overlay data into `sections`.

## Diagrams: big or zoomable

Every `mermaid` figure renders full content width with an auto-numbered
caption (`caption` field) and a **fullscreen expand control** that works
without JavaScript; interactive mode adds wheel-zoom, drag-pan, and Esc-close
(`assets/enhance.js`). Mermaid base font size is 16px for legibility.

- **Interactive (default):** Mermaid runs client-side, `theme: 'base'`,
  `securityLevel: 'strict'`, brand `themeVariables`.
- **Frozen (archival/PDF):** diagrams pre-rendered to inline SVG with the
  same skin-resolved theme (the script asks render.py via
  `--print-mermaid-config`):

```bash
bash .claude/skills/render-branded-html/scripts/freeze_mermaid.sh \
  examples/architecture-review.yaml build/architecture-review.frozen.html
```

## PDF export

```bash
python .claude/skills/render-branded-html/scripts/export_pdf.py \
  --input build/architecture-review.frozen.html \
  --output build/architecture-review.pdf
```

Freeze diagrams before exporting so they appear in the headless print
context. The exporter expands all `details` and exits any fullscreen
diagram before printing.

## Layout

```
schemas/    review-artifact.schema.json (base, v2) + 5 overlays
templates/  widgets.html.j2 (shared macros) + skins/{docs-site,editorial,brief}.html.j2
assets/     theme.css (widget library), skins/*.css + skins/*.tokens.json,
            print.css, enhance.js, default-theme.json, mermaid-config.js
scripts/    render.py, freeze_mermaid.sh, export_pdf.py, test_render.py
```

## Dark mode

`theme.mode` is functional: `light` (default), `dark` (always dark), `auto`
(follows the reader's OS via `prefers-color-scheme`, scoped so explicit-light
docs are immune). The dark palette is a parallel `dark` token group
(default theme → brand → skin layering, same as light; missing dark keys fall
back to light). Mermaid picks the matching palette at load time — an OS
scheme switch applies on reload, not live. **Frozen `auto` pins to light**
(page + baked SVGs can never mismatch); explicit `mode: dark` freezes dark.
**Print is always light/white**, even for dark documents.

## Theme tokens

Resolution order: `default-theme.json` → brand theme (`--theme`) → skin
overrides (`assets/skins/<skin>.tokens.json`). Resolved tokens map to **both**
CSS custom properties (generic flatten: `color.primary_soft` →
`--color-primary-soft`) and Mermaid `themeVariables`
(`assets/mermaid-config.js` mirrors `render.py`), so page and diagrams stay
visually consistent under every skin. Widget semantics (callout intents,
severity tags, code surfaces, heatmap levels) have dedicated AA-paired tokens.

## Self-test

```bash
python .claude/skills/render-branded-html/scripts/test_render.py
```

Exercises every widget kind under every skin, asserts overlay rendering,
figure numbering, validation gates, and byte-identical determinism.

## Setup

```bash
python -m venv .venv && .venv/bin/pip install jinja2 jsonschema pyyaml referencing
# optional, for freeze + PDF:
npm i -g @mermaid-js/mermaid-cli
pip install playwright && playwright install chromium
```

## Canonical schema (summary)

Base requires `schema_version: 2`, `artifact_type`, `title`. Supports
`subtitle`, `audience`, `status`, `owner`, `updated_at`,
`theme{mode,brand,density,layout}`, `summary[]`, `sections[]`, `evidence[]`,
`export{pdf,freeze_diagrams}`. Sections carry `id`, `title`, `kind`, optional
`width: full|half`, plus the kind's own fields. Each `artifact_type` adds
overlay fields — see `schemas/`.

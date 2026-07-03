# Changelog

## v0.1.0 — 2026-06-05

First public release of the branded HTML documentation skill suite.

### Features
- **Schema-first canonical source (v2)** — one base JSON Schema + five artifact
  overlays (user-story, architecture, PRD, risk-analysis, test-charter),
  authorable as YAML or JSON.
- **Widget section library** — 14 section kinds: prose, mermaid, table,
  callout, stats, steps, cards, keyvalue, code, tabs, details, timeline,
  heatmap, meters. Overlay fields (decisions, constraints, acceptance
  criteria, …) render automatically as styled components.
- **Three layout skins** over one widget library — `docs-site` (sticky TOC),
  `editorial` (serif print-first report), `brief` (KPI cards + bento grid),
  with per-artifact-type defaults and `theme.layout` override.
- **Dark mode** — `theme.mode: light | dark | auto`; diagrams switch palette
  with the page; print always stays white.
- **Readable, zoomable diagrams** — full-width Mermaid figures with captions,
  figure numbering, CSS-only fullscreen expand, JS wheel-zoom/drag-pan.
- **Deterministic renderer** — byte-identical output for identical input;
  single self-contained HTML serving both screen and print.
- **Layered validation** — JSON Schema → Mermaid → accessibility (Axe,
  WCAG AA, light + dark passes) → responsive → print/PDF completeness.
- **Brand theming** — semantic token sets drive both page CSS and Mermaid
  themeVariables; fictional sample brands included (Fizzberg, Möbelhaus
  Norda, Quantix, Cargonia Logistics).

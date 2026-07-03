---
name: risk-analysis-review-doc
description: Author compact canonical source for a RISK ANALYSIS review (artifact_type risk-analysis) — risk matrix, triggers, controls, residual risk, owners, review cadence. Produces content-only YAML/JSON validated against the base + risk overlay schema; render with render-branded-html. Use for QA/product/operations risk reviews.
---

# risk-analysis-review-doc

Authors **content only** for a risk analysis. Emit canonical YAML/JSON — no
HTML/CSS/JS. Target 2–12 KB. The renderer owns all chrome.

## Required & overlay fields

- Base: `schema_version: 2`, `artifact_type: risk-analysis`, `title`.
- Overlay: `triggers[]`, `controls[]`, `residual_risk`, `owners[]`,
  `review_cadence`.

## Section shape (default)

1. `risk-matrix` — **table** (the core artifact): columns
   `[risk, likelihood, impact, mitigation]`, one row per risk.
2. `concentration` — **mermaid** `flowchart` (one diagram, < 40 lines): where
   risk concentrates in the flow.

Use `summary[]` for the top residual risks. Cite incidents/docs in `evidence[]`
as `{label, href}`.

## Widgets (schema v2)

Beyond `prose`/`mermaid`/`table`, sections may use: `callout`
(note/tip/warning/danger), `stats` (KPI numbers), `steps`, `cards`
(generic/decision/rejected/persona), `keyvalue`, `code` (+`filename`),
`tabs` (2–6 alternatives), `details` (collapsible deep-dive), `timeline`,
`heatmap`, `meters`. Pick the widget that matches the data — and show
restraint: **at most one `stats` section** per document; prefer `prose` when
nothing structural is gained. Give every `mermaid` section a `caption`;
`width: half` pairs small sections side by side under the `brief` skin.

**Overlay fields render automatically** as styled components (after the
summary) — author them fully and do NOT duplicate them into `sections`.
Signature widget for this type: a `heatmap` section (likelihood ×
impact, levels 1–5) alongside the risk-matrix table; `meters` can express
control maturity.

Layout: the renderer picks the skin from `artifact_type` (brief here); set
`theme.layout: docs-site | editorial | brief` only when the user asks for a
different look.

## Authoring rules

- Always include the risk-matrix table; it is the heart of this artifact.
- Use consistent likelihood/impact vocabulary (e.g. low/medium/high).
- Set `residual_risk` and `review_cadence` so owners know the standing posture.
- Regenerate a single section when revising — don't re-emit the whole document.

## Example

```bash
python .claude/skills/validate-branded-doc/scripts/validate_all.py --input source.yaml
python .claude/skills/render-branded-html/scripts/render.py --input source.yaml --output out.html
```
See `examples/risk-analysis.yaml`.

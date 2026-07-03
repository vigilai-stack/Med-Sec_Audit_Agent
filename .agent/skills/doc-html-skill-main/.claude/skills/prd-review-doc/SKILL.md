---
name: prd-review-doc
description: Author compact canonical source for a PRD review (artifact_type prd-review) — business goals, out-of-scope, requirement coverage, stakeholders, readiness. Produces content-only YAML/JSON validated against the base + PRD overlay schema; render with render-branded-html. Use for product/delivery PRD reviews.
---

# prd-review-doc

Authors **content only** for a PRD review. Emit canonical YAML/JSON — no
HTML/CSS/JS. Target 2–12 KB. The renderer owns all chrome.

## Required & overlay fields

- Base: `schema_version: 2`, `artifact_type: prd-review`, `title`.
- Overlay: `business_goals[]`, `out_of_scope[]`, `requirement_coverage[]`
  (`{requirement, covered?, notes?}`), `stakeholders[]`.

## Section shape (default)

1. `goals` — **prose**: goals and success metrics.
2. `coverage` — **table**: columns `[requirement, covered, notes]`, one row per
   requirement (mirror `requirement_coverage[]`).
3. Optional `dependencies` — **mermaid** `flowchart` for cross-feature deps.

Use `summary[]` for the readiness summary (covered vs gaps). Cite the PRD and
related docs in `evidence[]` as `{label, href}`.

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
Signature widgets for this type: `requirement_coverage[]` (renders as a
✓/✗ table) and `business_goals[]` (checklist); a single `stats` section
works well for goal metrics.

Layout: the renderer picks the skin from `artifact_type` (editorial here); set
`theme.layout: docs-site | editorial | brief` only when the user asks for a
different look.

## Authoring rules

- Keep `out_of_scope[]` explicit — scope clarity is the point of a PRD review.
- Reflect every `requirement_coverage[]` entry in the coverage table.
- One primary diagram only when dependencies warrant it.
- Regenerate a single section when revising — don't re-emit the whole document.

## Example

```bash
python .claude/skills/validate-branded-doc/scripts/validate_all.py --input source.yaml
python .claude/skills/render-branded-html/scripts/render.py --input source.yaml --output out.html
```
See `examples/prd-review.yaml`.

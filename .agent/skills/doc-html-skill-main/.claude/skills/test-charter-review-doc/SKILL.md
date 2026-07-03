---
name: test-charter-review-doc
description: Author compact canonical source for an exploratory TEST CHARTER (artifact_type test-charter) — missions, heuristics, coverage boundaries, exit criteria, states explored. Produces content-only YAML/JSON validated against the base + test-charter overlay schema; render with render-branded-html. Use for QA exploratory-testing charters.
---

# test-charter-review-doc

Authors **content only** for an exploratory test charter. Emit canonical
YAML/JSON — no HTML/CSS/JS. Target 2–12 KB. The renderer owns all chrome.

## Required & overlay fields

- Base: `schema_version: 2`, `artifact_type: test-charter`, `title`.
- Overlay: `missions[]` (**required**), `heuristics[]`, `coverage_boundaries[]`,
  `exit_criteria[]`.

## Section shape (default)

1. `mission` — **prose**: what to investigate and why.
2. `states` — **mermaid** `state` (one diagram, < 40 lines): the states explored.
3. `coverage` — **table**: columns `[area, in_scope, notes]`.

Use `summary[]` for the charter focus and timebox. Cite specs/areas in
`evidence[]` as `{label, href}`.

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
Signature widgets for this type: `meters` for coverage confidence per
area and `missions[]` (renders as steps — use `Mission — detail`).

Layout: the renderer picks the skin from `artifact_type` (docs-site here); set
`theme.layout: docs-site | editorial | brief` only when the user asks for a
different look.

## Authoring rules

- Frame `missions[]` as questions to answer, not test cases to pass.
- Keep `coverage_boundaries[]` explicit (in vs out) and set `exit_criteria[]`.
- One primary diagram per core section; keep Mermaid small.
- Regenerate a single section when revising — don't re-emit the whole document.

## Example

```bash
python .claude/skills/validate-branded-doc/scripts/validate_all.py --input source.yaml
python .claude/skills/render-branded-html/scripts/render.py --input source.yaml --output out.html
```
See `examples/test-charter.yaml`.

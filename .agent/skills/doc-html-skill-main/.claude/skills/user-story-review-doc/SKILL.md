---
name: user-story-review-doc
description: Author compact canonical source for a USER STORY review (artifact_type user-story-review) — acceptance criteria, personas, journey states, dependencies, scope gaps. Produces content-only YAML/JSON validated against the base + user-story overlay schema; render with render-branded-html. Use for PM/design story reviews.
---

# user-story-review-doc

Authors **content only** for a user-story review. Emit canonical YAML/JSON — no
HTML/CSS/JS. Target 2–12 KB. The renderer owns all chrome.

## Required & overlay fields

- Base: `schema_version: 2`, `artifact_type: user-story-review`, `title`.
- Overlay: `acceptance_criteria[]` (**required**), plus `as_a`, `i_want`,
  `so_that`, `personas[]`, `journey_states[]`, `dependencies[]`.

## Section shape (default)

1. `scope` — **prose**: what's in/out of scope, key assumptions.
2. `journey` — **mermaid** `journey` (one diagram, < 40 lines): the shopper/user path.
3. `acceptance` — **table**: columns `[criterion, status, notes]`, one row per AC.

Use `summary[]` for the 2–4 bullet executive summary (scope gaps, open questions).
Cite sources in `evidence[]` as `{label, href}`.

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
Signature widgets for this type: `acceptance_criteria[]` (renders as a
checklist), `personas[]` (persona cards — use `Name — description`),
`journey_states[]` (timeline).

Layout: the renderer picks the skin from `artifact_type` (editorial here); set
`theme.layout: docs-site | editorial | brief` only when the user asks for a
different look.

## Authoring rules

- One primary diagram per core section; keep Mermaid small.
- Put each acceptance criterion in `acceptance_criteria[]` AND reflect its status
  in the acceptance table.
- Regenerate a single section when revising — don't re-emit the whole document.

## Example

See `examples/user-story-review.yaml`. Validate + render:

```bash
python .claude/skills/validate-branded-doc/scripts/validate_all.py --input source.yaml
python .claude/skills/render-branded-html/scripts/render.py --input source.yaml --output out.html
```

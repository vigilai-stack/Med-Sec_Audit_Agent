---
name: architecture-review-doc
description: Author compact canonical source for an ARCHITECTURE review (artifact_type architecture-review) — decisions, constraints, interfaces, deployment context, alternatives, and interaction diagrams. Produces content-only YAML/JSON validated against the base + architecture overlay schema; render with render-branded-html. Use for architecture/engineering reviews.
---

# architecture-review-doc

Authors **content only** for an architecture review. Emit canonical YAML/JSON —
no HTML/CSS/JS. Target 2–12 KB. The renderer owns all chrome.

## Required & overlay fields

- Base: `schema_version: 2`, `artifact_type: architecture-review`, `title`.
- Overlay: `decisions[]` (`{title, rationale?, status?}`), `constraints[]`,
  `interfaces[]`, `deployment_context`, `alternatives[]`.

## Section shape (default)

1. `context` — **prose**: what the review covers and why.
2. `sequence` (or `topology`) — **mermaid** `sequence`/`flowchart` (one diagram,
   < 40 lines): the key interaction or component layout.
3. `findings` — **table**: columns `[finding, severity, recommendation]`.

Use `summary[]` for the executive summary (top gaps/risks). Cite ADRs and code
in `evidence[]` as `{label, href}`.

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
Signature widgets for this type: `decisions[]` (with `ref` for ADR ids) and
`constraints[]` as `{text, severity}` objects; add `tabs`/`code` for setup
and install variants, `steps` for runtime flows.

Layout: the renderer picks the skin from `artifact_type` (docs-site here); set
`theme.layout: docs-site | editorial | brief` only when the user asks for a
different look.

## Authoring rules

- Record real decisions in `decisions[]` with a short rationale and status.
- One primary diagram per core section; prefer `sequence` for flows, `flowchart`
  for topology. Reserve ELK/large graphs for explicit requests.
- Regenerate a single section when revising — don't re-emit the whole document.

## Example

See `examples/architecture-review.yaml`. Validate + render:

```bash
python .claude/skills/validate-branded-doc/scripts/validate_all.py --input source.yaml
python .claude/skills/render-branded-html/scripts/render.py --input source.yaml --output out.html
```

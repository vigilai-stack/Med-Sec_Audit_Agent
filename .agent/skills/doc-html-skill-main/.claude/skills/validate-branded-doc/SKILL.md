---
name: validate-branded-doc
description: Validate canonical review-doc source and rendered HTML across layers — JSON Schema, Mermaid syntax/render, accessibility (Axe/WCAG AA), responsive layout, and print/PDF. Use before sharing or committing a branded review artifact, in CI, or as a pre-commit hook.
---

# validate-branded-doc

Layered validation for branded review documents. Schema validation runs **first**
and short-circuits the rest on failure — a structurally invalid artifact never
reaches the Mermaid, accessibility, responsive, or export checks.

## When to use

- Before rendering/sharing a review artifact.
- In CI on changed canonical source files.
- As a pre-commit gate (schema + Mermaid are fast and dependency-light).

## Layers

| Layer | Script | Pass condition |
|---|---|---|
| Schema | `scripts/validate_schema.py` | all required fields + enums valid (base + overlay) |
| Mermaid | `scripts/validate_mermaid.mjs` | every diagram parses (add `--render` for mmdc render in CI) |
| Accessibility | `scripts/validate_accessibility.mjs` | zero critical Axe violations; contrast ≥ WCAG AA |
| Responsive | `scripts/validate_responsive.mjs` | no horizontal overflow at desktop + mobile |
| Print/PDF | `scripts/validate_export.mjs` | PDF exports with ≥1 readable page; print completeness — every tab pane and details body visible, screen-only controls hidden |

For sources declaring `theme.mode: dark` or `auto`, an additional
`accessibility-dark` pass runs under dark color-scheme emulation
(`--color-scheme dark`) with the same WCAG AA thresholds.

The accessibility layer also runs widget checks: tabs keyboard-operable with
associated labels, diagram zoom toggles carry accessible names, and severity /
callout tag contrast is enforced via Axe's WCAG AA color-contrast rule.

## Quick start

Run the whole suite (renders HTML automatically if `--html` is omitted):

```bash
python .claude/skills/validate-branded-doc/scripts/validate_all.py \
  --input examples/architecture-review.yaml
```

Validate the same source under an explicit skin (matrix testing in CI):

```bash
python .claude/skills/validate-branded-doc/scripts/validate_all.py \
  --input examples/architecture-review.yaml --skin editorial
```

Run a single layer:

```bash
python .claude/skills/validate-branded-doc/scripts/validate_schema.py --input source.yaml
node   .claude/skills/validate-branded-doc/scripts/validate_mermaid.mjs --input source.yaml --render
node   .claude/skills/validate-branded-doc/scripts/validate_accessibility.mjs --input doc.html
```

## Behavior notes

- **Short-circuit:** a schema failure marks downstream layers `SKIP` and fails the run.
- **Graceful degradation:** HTML layers need optional Node deps (`playwright`,
  `@axe-core/playwright`). When absent they report `SKIP` (not `FAIL`) so the
  schema + Mermaid gate still works offline. Install deps to enforce them — see
  the renderer skill's setup notes.
- **Exit codes:** `0` all pass, `2` any explicit failure. `SKIP` never fails the run.
- **JSON output:** pass `--json` for machine-readable reports (CI).

## Dependencies

- Python (project `.venv`): `jsonschema`, `pyyaml`, `referencing`.
- Node: `playwright`, `@axe-core/playwright`; optional `@mermaid-js/mermaid-cli` for `--render`.

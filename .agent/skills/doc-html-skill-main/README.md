# doc-html-skill — Branded HTML Documentation Skills

A **schema-first, renderer-second** suite for turning agent-generated analysis
into reviewable, company-themed HTML artifacts. Thin agent skills author compact,
validated canonical source (YAML/JSON); a deterministic renderer owns all theme,
layout, and Mermaid chrome. The model writes **content, not boilerplate**.

Licensed under Apache-2.0. Design rationale:
`docs/research/deep-research-report (9).md` and the OpenSpec history under
`openspec/changes/archive/`.

## Install

```bash
# Python CLI (renderer + validator, schemas/templates/assets bundled)
pip install doc-html-skill
doc-html-render --input my-review.yaml --output my-review.html

# Or: copy the skills into a Claude Code project
npx doc-html-skill install        # writes .claude/skills/*

# Or: work from a clone (this repo IS a Claude Code project)
git clone https://github.com/manykarim/doc-html-skill
```

Optional extras: `pip install 'doc-html-skill[pdf]'` (Playwright PDF export);
`npm i -D playwright @axe-core/playwright @mermaid-js/mermaid-cli` for the
accessibility/responsive/print validation layers and frozen diagrams.

## Skills

| Skill | Role |
|---|---|
| `review-doc-orchestrator` | Entry point: classify request, gather evidence, delegate, render, validate |
| `user-story-review-doc` | Author user-story review source |
| `architecture-review-doc` | Author architecture review source |
| `prd-review-doc` | Author PRD review source |
| `risk-analysis-review-doc` | Author risk analysis source |
| `test-charter-review-doc` | Author exploratory test charter source |
| `render-branded-html` | Deterministic source → single-file branded HTML (+ frozen Mermaid, PDF) |
| `validate-branded-doc` | Layered validation: schema → mermaid → a11y → responsive → print/PDF |

## Setup

```bash
# Python (render + schema/validation core)
python -m venv .venv
.venv/bin/pip install -r requirements.txt

# Node (Mermaid CLI + Playwright/Axe validation layers) — optional
npm install
npx playwright install chromium
npm i -g @mermaid-js/mermaid-cli   # for freeze mode / --render
```

The schema + Mermaid gate works with Python + Node only. Accessibility,
responsive, and export layers need Playwright (they report `SKIP`, not `FAIL`,
when absent).

## Usage

```bash
# Validate (schema first; short-circuits on failure)
.venv/bin/python .claude/skills/validate-branded-doc/scripts/validate_all.py \
  --input examples/architecture-review.yaml

# Render single-file branded HTML (interactive Mermaid, securityLevel: strict)
.venv/bin/python .claude/skills/render-branded-html/scripts/render.py \
  --input examples/architecture-review.yaml \
  --output build/architecture-review.html

# Freeze diagrams to inline SVG (archival / PDF), then export PDF
bash .claude/skills/render-branded-html/scripts/freeze_mermaid.sh \
  examples/architecture-review.yaml build/architecture-review.frozen.html
.venv/bin/python .claude/skills/render-branded-html/scripts/export_pdf.py \
  --input build/architecture-review.frozen.html --output build/architecture-review.pdf
```

## Canonical source

One shared base schema v2 (`schema_version`, `artifact_type`, `title`, `summary`,
`sections`, `evidence`, `export`) plus a per-type overlay. Section kinds:
`prose`, `mermaid`, `table`, `callout`, `stats`, `steps`, `cards`, `keyvalue`,
`code`, `tabs`, `details`, `timeline`, `heatmap`, `meters`. Overlay fields
(decisions, constraints, acceptance criteria, …) render automatically as styled
components. Theme tokens (`assets/default-theme.json`) drive **both** CSS
variables and Mermaid `themeVariables`, so page and diagrams never drift.
Schemas: `.claude/skills/render-branded-html/schemas/`. Examples: `examples/`.

## Skins

One widget library, three layout skins — chosen per artifact type, overridable
via `theme.layout` or the CLI `--skin` flag:

| Skin | Look | Default for |
|---|---|---|
| `docs-site` | sticky TOC sidebar + topbar | architecture-review, test-charter |
| `editorial` | serif print-first report, numbered sections | prd-review, user-story-review |
| `brief` | gradient hero + KPI cards + bento grid | risk-analysis |

Every Mermaid diagram renders full-width with a fullscreen expand control
(CSS-only; JS adds wheel-zoom/drag-pan). Print CSS is embedded: one HTML file
both displays and prints (tabs stack labelled, details expand, controls hide).

Dark mode: `theme.mode: light | dark | auto` — auto follows the reader's OS;
diagrams switch palette with the page; print stays white in every mode.

## Out of scope (future waves)

Docusaurus export, GitHub Actions preview + Pages deploy, and pre-commit hooks
are intentionally deferred — see the OpenSpec change's `design.md` non-goals.

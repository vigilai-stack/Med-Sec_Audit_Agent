# Artifact types and overlay fields

All artifacts share the base schema (`schema_version`, `artifact_type`, `title`,
`subtitle?`, `audience?`, `status?`, `owner?`, `updated_at?`, `theme?`,
`summary[]?`, `sections[]?`, `evidence[]?`, `export?`). Sections are `prose`
(`body`), `mermaid` (`diagram_type`, `source`), or `table` (`columns`, `rows`).

Each type adds overlay fields and has a typical section/diagram shape.

## user-story-review
- Overlay: `as_a`, `i_want`, `so_that`, `acceptance_criteria[]` (required),
  `personas[]`, `journey_states[]`, `dependencies[]`.
- Typical sections: scope (prose), journey (mermaid `journey`), acceptance
  status (table: criterion, status, notes).

## architecture-review
- Overlay: `decisions[]` ({title, rationale?, status?}), `constraints[]`,
  `interfaces[]`, `deployment_context`, `alternatives[]`.
- Typical sections: context (prose), interaction flow (mermaid `sequence` or
  `flowchart`), findings (table: finding, severity, recommendation).

## prd-review
- Overlay: `business_goals[]`, `out_of_scope[]`, `requirement_coverage[]`
  ({requirement, covered?, notes?}), `stakeholders[]`.
- Typical sections: goals (prose), coverage (table: requirement, covered, notes),
  optional dependency map (mermaid).

## risk-analysis
- Overlay: `triggers[]`, `controls[]`, `residual_risk`, `owners[]`,
  `review_cadence`.
- Typical sections: risk matrix (table: risk, likelihood, impact, mitigation),
  risk concentration (mermaid `flowchart`).

## test-charter
- Overlay: `missions[]` (required), `heuristics[]`, `coverage_boundaries[]`,
  `exit_criteria[]`.
- Typical sections: mission (prose), states explored (mermaid `state`),
  coverage boundaries (table: area, in_scope, notes).

## Authoring targets (all types)

- Canonical source 2–12 KB. No HTML/CSS/JS — content only.
- One primary diagram per core section; Mermaid blocks under ~40 lines.
- Use `summary[]` for the executive summary humans read first.
- Cite sources in `evidence[]` as `{label, href}`.
- Regenerate at the section level when revising — don't re-emit the whole doc.

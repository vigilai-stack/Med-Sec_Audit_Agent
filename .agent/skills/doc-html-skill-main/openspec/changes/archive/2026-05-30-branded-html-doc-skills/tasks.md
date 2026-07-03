## 1. Foundation: schema and theme tokens

- [x] 1.1 Scaffold `.claude/skills/` tree (orchestrator, five artifact skills, `render-branded-html`, `validate-branded-doc`) per the research file layout
- [x] 1.2 Author `review-artifact.schema.json` (base): require `schema_version`, `artifact_type`, `title`; define `summary`, `sections`, `evidence`, `export`, `theme`, and optional metadata fields
- [x] 1.3 Define section block types in the base schema: `prose`, `mermaid` (`diagram_type`, `source`), `table` (`columns`, `rows`)
- [x] 1.4 Author overlay schemas: `user-story-review`, `architecture-review`, `prd-review`, `risk-analysis`, `test-charter` extending the base without dropping base requirements
- [x] 1.5 Create the semantic theme-token model (`theme.css` tokens + default token set): colors, fonts, radius, spacing
- [x] 1.6 Implement token → CSS custom property mapping and token → Mermaid `themeVariables` mapping (`mermaid-config.js`)
- [x] 1.7 Write golden-example canonical sources (one YAML + one JSON) and confirm both validate against the same schema

## 2. Renderer

- [x] 2.1 Implement `render.py` CLI: `load_source` (YAML/JSON), `validate_payload` (Draft 2020-12), `render_html` (Jinja, autoescape, trim/lstrip blocks)
- [x] 2.2 Make rendering refuse invalid source and verify byte-identical output for identical input (determinism test)
- [x] 2.3 Build `standard.html.j2` and `print.html.j2` templates owning all chrome (hero, sections, evidence, inline CSS)
- [x] 2.4 Implement section rendering by kind (prose / mermaid / table) including a `render_table` helper
- [x] 2.5 Implement interactive Mermaid mode: embed source, initialize with `theme: 'base'`, `securityLevel: 'strict'`, injected `themeVariables`
- [x] 2.6 Implement frozen mode via `freeze_mermaid.sh` (Mermaid CLI → inline SVG), switched by `export.freeze_diagrams`/CLI flag
- [x] 2.7 Implement `export_pdf.py` (headless-browser print path honoring print CSS), gated by `export.pdf`

## 3. Validator

- [x] 3.1 Implement `validate_schema.py` (base + overlay) reporting required-field and enum violations; short-circuit downstream on failure
- [x] 3.2 Implement `validate_mermaid.mjs`: parse-time check plus optional Mermaid CLI render for CI confidence
- [x] 3.3 Implement `validate_accessibility.mjs` (Playwright + Axe-core): zero critical violations; enforce WCAG AA contrast (4.5:1 / 3:1)
- [x] 3.4 Implement `validate_responsive.mjs`: render at desktop + mobile viewports; fail on clipping or horizontal overflow
- [x] 3.5 Implement `validate_export.mjs`: confirm PDF produces usable pagination and readable diagrams
- [x] 3.6 Wire a consolidated pass/fail report aggregating all layers and write `validate-branded-doc/SKILL.md`

## 4. Skills: orchestrator and artifact specialists

- [x] 4.1 Write `review-doc-orchestrator/SKILL.md` (<500 lines) with routing to the five artifact types; offload routing tables to `references/routing.md` and `references/artifact-types.md`
- [x] 4.2 Implement orchestrator behavior: classify request, clarify ambiguous type, assemble validated source, gather evidence scope, select template/theme
- [x] 4.3 Write `user-story-review-doc/SKILL.md`: emit `acceptance_criteria`, `journey_states`, personas; content-only, no chrome
- [x] 4.4 Write `architecture-review-doc/SKILL.md`: emit `decisions`, `constraints`, `interfaces`, sequence/topology diagrams
- [x] 4.5 Write `prd-review-doc/SKILL.md`: emit `business_goals`, `out_of_scope`, `requirement_coverage`, `stakeholders`
- [x] 4.6 Write `risk-analysis-review-doc/SKILL.md`: emit risk-matrix table (likelihood/impact/mitigation), `triggers`, `controls`, `residual_risk`
- [x] 4.7 Write `test-charter-review-doc/SKILL.md`: emit `missions`, `heuristics`, `coverage_boundaries`, `exit_criteria`
- [x] 4.8 Apply scoped-diagram defaults (one diagram per core section, <40 lines) and section-level regeneration across all artifact skills

## 5. Verification and acceptance

- [x] 5.1 Add dependencies (Python: Jinja2, PyYAML, jsonschema; Node: `@mermaid-js/mermaid-cli`; Playwright + Axe-core) and document setup
- [x] 5.2 End-to-end: each artifact skill → canonical source → schema-valid → rendered HTML for all five types
- [x] 5.3 Run full validation layer on the golden examples; confirm zero critical a11y issues, no responsive overflow, usable PDF
- [x] 5.4 Verify token-efficiency targets: ~0 KB model-emitted HTML boilerplate; canonical source 2–12 KB per artifact
- [x] 5.5 Confirm interactive (strict) vs frozen Mermaid modes both render correctly and share identical brand styling

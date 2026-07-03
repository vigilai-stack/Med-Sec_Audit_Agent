## Context

Teams repeatedly need agent-generated analysis turned into reviewable, company-themed documents: user-story reviews, architecture docs, PRD reviews, risk registers, and exploratory test charters. Today these arrive as terminal text or one-off prompt-authored HTML. Prompt-only HTML generation re-emits wrappers, utility classes, CSS, and JS bootstrapping on every run — a direct, recurring tax on the session token budget (invoked skill content persists in context and is only partially reattached after compaction). The research report (`docs/research/deep-research-report (9).md`) surveyed `walkthrough`, `visual-explainer`, Ring's branded explainers, Mermaid, Docusaurus, MkDocs, and Eleventy, and concluded the market proves the *value* of HTML explainers and Mermaid utilities but lacks the specific combination we need: a company-themed, review-oriented, schema-driven suite optimized for low model output volume.

This is a greenfield capability suite — there are no existing specs in `openspec/specs/` to modify. Constraints: each invoked `SKILL.md` should stay under Anthropic's 500-line guidance; heavy material belongs in support files; deterministic visual output should be script-backed.

## Goals / Non-Goals

**Goals:**
- A **schema-first, renderer-second** pipeline: agents author compact canonical YAML/JSON; a deterministic renderer owns all theme, layout, and Mermaid chrome.
- One shared base schema with thin per-artifact overlays, validated by JSON Schema, that diffs cleanly in git.
- A theme-token system that is the single source of truth for both CSS and Mermaid styling.
- Interactive Mermaid by default (client-side, `securityLevel: strict`), with a freeze-to-SVG mode for archival and PDF.
- Layered validation: schema → Mermaid → accessibility → responsive → print/PDF.
- Measurable token efficiency: ~0 KB model-emitted HTML boilerplate; 2–12 KB canonical source per artifact.

**Non-Goals:**
- Docusaurus publication path (deferred second-stage publication target).
- GitHub Actions preview pipeline, GitHub Pages deployment, and pre-commit hooks (operations wave).
- Material for MkDocs / Eleventy integrations (MkDocs entered maintenance mode Nov 2025; not a strategic default).
- A general-purpose website builder — output is single-file review artifacts, not a portal.

## Decisions

**1. Schema-first canonical source over prompt-authored HTML.**
The model authors content (summaries, findings, table rows, Mermaid source); the renderer authors chrome. Rationale: removes repeated boilerplate tokens, makes diffs small, enables reliable regeneration and section-level edits. *Alternative considered:* direct HTML emission per `visual-explainer`/`walkthrough` — rejected as the primary path because it repeats wrappers/CSS/JS each run and bloats context, though we borrow their UX strengths.

**2. JSON Schema (Draft 2020-12) as the contract; YAML or JSON as authoring formats.**
JSON Schema gives a standards-based validity/interoperability contract; YAML is human-friendly for authoring, JSON is convenient for CI/tests. Both validate against the same schema. *Alternative:* bespoke validation in Python — rejected; reinvents a solved, portable standard.

**3. Base schema + overlays, not per-artifact schemas.**
A common base (`schema_version`, `artifact_type`, `title`, `summary`, `sections`, `evidence`, `export`) keeps the renderer generic; overlays add only artifact-specific fields. *Alternative:* five independent schemas — rejected; duplicates structure and forces renderer branching.

**4. Jinja + `render.py` as the deterministic renderer.**
Jinja is purpose-built to generate HTML/text from structured input with autoescaping; a small Python CLI keeps the stack low-ceremony and testable. *Alternative:* a JS/React renderer — viable but heavier; Python aligns with the validation tooling and keeps the render path simple and deterministic.

**5. Two Mermaid modes with a single switch.** Interactive (`startOnLoad`, `theme: 'base'`, `securityLevel: strict`) by default for zoom and mode-sensitive theming; frozen SVG via the official Mermaid CLI for archival, stable screenshots, and PDF. Exposed as `freeze_diagrams`. *Rationale:* `base` is the only modifiable Mermaid theme, so `themeVariables` is the correct brand hook; `strict` is the safe default for internal artifacts, with `loose` only when clickable nodes are a deliberate requirement.

**6. Single token source mapped to both CSS variables and Mermaid `themeVariables`.**
Prevents brand drift between page and diagrams. *Alternative:* separate styling for page and diagrams — rejected; produces unpolished, inconsistent artifacts.

**7. Single-file HTML first; Docusaurus deferred.** Best for ad hoc review, local preview, and share/email flows with deterministic build output. Docusaurus is the clean second stage only once search, cross-linking, and versioning are required. MkDocs's maintenance-mode status makes it a weaker long-term foundation.

**8. Thin skills + support files + scripts.** Orchestrator and five artifact skills stay under 500 lines; routing tables, artifact-type detail, schemas, templates, and validators live in support files/scripts loaded only when needed.

## Risks / Trade-offs

- **Prompt drift across artifact skills** → one base schema, golden examples, renderer-owned layouts so structure/tone stay consistent.
- **Mermaid parse failures break trust** → lint early (parse), cap diagram complexity (one per section, <40 lines), support frozen-SVG fallback, render via CLI in CI.
- **Brand mismatch between page and diagrams** → single token source mapped to both CSS and Mermaid variables.
- **Skill context bloat raises per-session token cost** → thin `SKILL.md`, heavy support files, script-backed render.
- **Poor print/PDF output** → dedicated print CSS plus headless-browser PDF tests in the validator.
- **Accessibility regressions** → token contrast checks (WCAG AA), Axe scans, responsive baseline screenshots.
- **Over-engineering too early** → start single-file HTML, defer portalization, CI, and hooks to later waves.
- **Toolchain spread (Python + Node + Playwright)** → acceptable: Python owns render/schema, Node owns Mermaid CLI, Playwright owns a11y/responsive/PDF; each is the best-in-class tool for its layer.

## Migration Plan

Greenfield — nothing to migrate from. Rollout follows the research roadmap, scoped to this change's non-goals:
1. **Foundation**: shared base schema + overlays, theme-token model, Jinja templates, `render.py`, validator skeleton → first deterministic branded HTML.
2. **Artifact wave**: orchestrator + user-story, architecture, PRD skills → first real review workflows.
3. **QA wave**: risk-analysis and test-charter skills; Mermaid freeze mode; PDF export → full suite coverage.
4. **Validation hardening**: a11y, responsive, print/PDF checks wired into `validate-branded-doc`.

Canonical YAML/JSON is what lives in git (diff-friendly); HTML is a build artifact (committed selectively or regenerated). Rollback is trivial — the suite adds skills/assets and changes no existing behavior; removing the skill directories reverts it.

Deferred to a later change (explicit non-goals here): Docusaurus export target, GitHub Actions preview + Pages deploy, and pre-commit integration.

## Open Questions

- **Company theme specifics** are unspecified; we build around semantic tokens with a neutral default and confirm real brand values before pilot.
- **Ring's exact branded-HTML implementation** is not public enough to reuse directly; not a blocker given `walkthrough`/`visual-explainer`/Mermaid/Docusaurus evidence.
- **Frozen vs interactive default per context** — interactive is the chosen default, but pilots may reveal that certain shared/archived flows should default to frozen.
- **ELK layout threshold** — when to auto-suggest the heavier ELK engine for large graphs versus requiring an explicit opt-in.

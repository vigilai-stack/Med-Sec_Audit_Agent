# Design: prepare-public-release

## Context

The project is not a git repository. `gh` is authenticated as `manykarim`. The skill suite's source of truth is `.claude/skills/` (7 skill directories with scripts, schemas, templates, assets), with `examples/`, `experiments/` (visual specs), `bench/` (benchmark tooling + raw run transcripts), `openspec/` history, and heavyweight local dirs (`.venv/`, `node_modules/`, `build/`). The existing `package.json` is a private dev manifest. Three example themes carry real brand names (Coca-Cola, Google, IKEA) and must not go public; the user wants fictional simulated equivalents instead. Owner decisions: repo `manykarim/doc-html-skill`, Apache-2.0, package `doc-html-skill` on both registries, v0.1.0. Registry publishing is manual; repo creation and the GitHub release happen in this change (outward-facing — confirm before executing).

## Goals / Non-Goals

**Goals:**
- Public, license-clean, brand-clean, secret-clean repository with a coherent first commit.
- `pip install doc-html-skill` gives working `doc-html-render` / `doc-html-validate` / `doc-html-export-pdf` CLIs with all schemas/templates/assets bundled.
- `npx doc-html-skill install` copies the skills into a project's `.claude/skills/`.
- `v0.1.0` GitHub release with notes and downloadable artifacts.
- `RELEASING.md` makes the manual publish a two-command affair per registry.

**Non-Goals:**
- No PyPI/npm publishing (manual by owner).
- No CI/CD, no GitHub Actions (project non-goal, unchanged).
- No code changes to renderer/validators beyond path-resolution needed for packaging.
- No docs site.

## Decisions

### D1 — `.claude/skills/` stays the single source of truth; packages wrap it
No restructure. The Python wheel includes the skill tree verbatim via haticling's `force-include` (`.claude/skills` → `doc_html_skill/skills`), preserving relative layout. All scripts already resolve paths relative to `__file__` (`SKILL_ROOT = parents[1]`; the validator finds the renderer via `SKILL_ROOT.parent / "render-branded-html"`), so the bundled copies work unmodified. Console entry points are thin wrappers in `doc_html_skill/cli.py` that load the bundled script by path (`runpy`-style) and forward argv.

*Alternative considered:* move code into `src/doc_html_skill/` and make `.claude/skills` symlinks. Rejected: breaks the skill-first repo layout that Claude Code consumes directly from a clone.

### D2 — npm package is a dependency-free installer, not a library
`package.json` becomes publishable: name `doc-html-skill`, `bin` → `bin/cli.mjs` with an `install` command that copies `.claude/skills/*` into the target project's `.claude/skills/` (with `--force` overwrite flag and a dry-run listing). `files` whitelists `.claude/skills`, `bin`, `README.md`, `LICENSE`. Node validator deps (playwright, axe, mermaid-cli) stay **devDependencies** — consumers who want the optional validation layers install them per the README; the installer itself needs nothing. Verify dot-directory inclusion with `npm pack --dry-run` (npm includes explicitly listed dot-paths; only a fixed denylist like `.git` is forced out).

### D3 — Fictional brand themes, palette-faithful
Replace the three real-brand themes with four fictional ones exercising the same theming range (each with light + `dark` groups, AA-checked):
- `theme-fizzberg.json` — "Fizzberg" red soda brand (Coca-Cola-like red/white)
- `theme-mobelhaus.json` — "Möbelhaus Norda" blue/yellow flat-pack furniture (IKEA-like)
- `theme-quantix.json` — "Quantix" multicolor tech (Google-like primary palette)
- `theme-cargonia.json` — "Cargonia Logistics" deep blue/signal red freight (Schenker-like)
No real company names/trademarks anywhere in the public tree; `rf-theme` (the owner's own Robot Framework project identity) stays. Re-render the brand comparison screenshots from the fictional themes.

### D4 — Curated public tree via .gitignore, not deletion
`.gitignore` grows: `bench/runs/` (raw agent transcripts — bulky and may embed local context), `build/`, `node_modules/`, `.venv/`, `dist/`, `*.validate.html`. `bench/skillkit`, `bench/prompts`, `bench/results` (aggregated numbers) stay public. Local files keep working; only the public surface is curated. Real-brand theme files are genuinely deleted (replaced), not just ignored.

### D5 — Hygiene gate before anything goes public
A scripted scan over the to-be-committed tree (`git ls-files` after staging): no secret patterns (`token`, `api[_-]?key`, `AKIA`, `ghp_`, private keys), no absolute `/home/<user>` paths in published docs (allowed in openspec history? no — scrub or verify; openspec artifacts reference repo-relative paths only), and the only email is the owner's intended contact. The scan is a release gate: failures block the push.

### D6 — Release artifacts built locally, attached to the GH release
`python -m build` → `dist/doc_html_skill-0.1.0-py3-none-any.whl` + sdist; `npm pack` → `doc-html-skill-0.1.0.tgz`; `zip -r doc-html-skill-skills-0.1.0.zip .claude/skills` for skill-only consumers. All three attached to `gh release create v0.1.0`. `RELEASING.md` documents: `twine upload dist/*` and `npm publish doc-html-skill-0.1.0.tgz` (+ `--access public` note) for the manual step.

### D7 — Outward-facing actions are explicit checkpoints
`gh repo create --public`, the initial push, and `gh release create` are confirmed with the owner at apply time before execution (they publish content externally and are awkward to reverse).

## Risks / Trade-offs

- [npm may mangle `.claude` dot-path inclusion] → verified with `npm pack --dry-run` before tagging; fallback is a `prepack` copy step to `skills/`.
- [Wheel path assumptions break a script] → smoke test the installed wheel in a throwaway venv (`doc-html-render` against a bundled example) as a release gate.
- [PyPI/npm name `doc-html-skill` already taken] → checked during apply; if taken, owner picks fallback (`branded-doc-skills`) before tagging.
- [Raw bench transcripts leak via openspec/docs references] → hygiene scan covers all committed text, not just code.
- [Fictional palettes still evoke the real brands] → intended (they simulate the brands per directive) but names/strings contain no trademarks.

## Migration Plan

1. Local prep (license, themes, packaging, .gitignore, docs) — fully reversible.
2. Build + smoke-test artifacts locally; run hygiene gate.
3. Checkpoint with owner → `git init` + commit → `gh repo create` + push → tag + `gh release create` with artifacts.
4. Owner publishes manually per `RELEASING.md` whenever ready.
5. Rollback: a public repo/release can be deleted via `gh repo delete` / `gh release delete` (artifacts may have been downloaded in the interim — treat push as effectively public).

## Open Questions

- Attach the rendered example HTML (e.g. `rf-mcp` docs-site + dark) to the release as a visual demo, or keep artifacts to installables + skills zip? (Default: attach one demo HTML.)
- Include `experiments/` design mockups in the public tree as living visual specs? (Default: yes — they document the skins.)

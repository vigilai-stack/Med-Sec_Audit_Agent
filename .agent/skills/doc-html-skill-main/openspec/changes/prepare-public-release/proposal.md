# Proposal: prepare-public-release

## Why

The skill suite is feature-complete (schema v2, three skins, widget library, dark mode, layered validation) but lives only in a local working directory — it is not even a git repository. To be usable by anyone else it needs a public home, a versioned release, and installable distributions. Publishing to PyPI/npm will be done manually by the owner; this change prepares everything up to that step.

## What Changes

- **Initialize git + public GitHub repo** `manykarim/doc-html-skill` (Apache-2.0). Curate what goes public: skills, schemas, templates, examples, experiments (visual specs), openspec history, bench tooling — but NOT raw bench run transcripts, build outputs, venvs, or node_modules.
- **Brand hygiene (user directive)**: remove the real-brand example themes (`theme-cocacola.json`, `theme-google.json`, `theme-ikea.json`) and replace them with **fictional simulated brands** with equivalent palettes — e.g. a red soda brand, a blue/yellow furniture brand, a multicolor tech brand, and a logistics brand. No real company names, logos, or trademarks anywhere in the public tree (the owner's own `rf-theme`/rf-mcp content stays).
- **Pre-publication hygiene scan**: no secrets/tokens, no unintended personal data, no absolute local paths in published docs.
- **PyPI distribution `doc-html-skill` (v0.1.0)**: pip-installable package bundling the renderer + validator with all schemas/templates/assets as package data; console entry points (`doc-html-render`, `doc-html-validate`, `doc-html-export-pdf`); built sdist + wheel in `dist/` ready for manual `twine upload`.
- **npm distribution `doc-html-skill` (0.1.0)**: dependency-free installer package — `npx doc-html-skill install` copies the skill directories into a project's `.claude/skills/`; ships the full skill tree + node validator scripts; `npm pack` tarball ready for manual `npm publish`.
- **GitHub release `v0.1.0`**: annotated tag + `gh release` with generated notes (features, skins, widgets, dark mode, validation) and attached artifacts (wheel, sdist, npm tarball, standalone skills zip).
- **Release docs**: `LICENSE` (Apache-2.0), `CHANGELOG.md`, `RELEASING.md` with the exact manual publish commands (`twine upload`, `npm publish`).
- **Out of scope**: actually publishing to PyPI/npm (manual, per directive); CI/CD pipelines (still deferred per project non-goals).

## Capabilities

### New Capabilities
- `release-packaging`: Public-repo hygiene (license, fictional-brand-only assets, no secrets), Python and npm distributions of the full skill suite, versioned GitHub release with artifacts, and documented manual publishing.

### Modified Capabilities

(none — no renderer/validator behavior changes; packaging wraps the existing capabilities)

## Impact

- **New files**: `LICENSE`, `CHANGELOG.md`, `RELEASING.md`, `pyproject.toml`, npm `bin/` installer, fictional brand themes in `examples/`.
- **Modified**: `package.json` (publishable: name `doc-html-skill`, bin, files — no longer `private`), `.gitignore` (exclude bench runs/build outputs), `README.md` (install instructions for pip/npx paths).
- **Removed from public tree**: `examples/theme-cocacola.json`, `theme-google.json`, `theme-ikea.json` (replaced by fictional equivalents); raw `bench/runs/` transcripts excluded via .gitignore.
- **External actions** (confirmed with owner before execution): `gh repo create manykarim/doc-html-skill --public`, push, `gh release create v0.1.0`.
- **Dependencies**: build-time only — Python `build` (and `hatchling` backend) for the wheel; no new runtime deps.

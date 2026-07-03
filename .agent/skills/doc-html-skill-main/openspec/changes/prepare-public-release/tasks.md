# Tasks: prepare-public-release

## 1. Brand & hygiene cleanup

- [x] 1.1 Delete `examples/theme-cocacola.json`, `theme-google.json`, `theme-ikea.json`; create fictional simulated brand themes with light + dark palettes: `theme-fizzberg.json` (red soda), `theme-mobelhaus.json` (blue/yellow furniture), `theme-quantix.json` (multicolor tech), `theme-cargonia.json` (deep-blue logistics)
- [x] 1.2 Render + screenshot one example under each fictional theme to confirm palettes work (incl. dark); remove stale real-brand renders from `build/` references in docs
- [x] 1.3 Grep the whole tree for real-brand strings (cocacola, ikea, google-as-brand, schenker) and scrub remaining references (README, examples README mentions, openspec change history is internal — verify it is brand-clean too)
- [x] 1.4 Write `scripts/release_hygiene.sh` gate: secret patterns (token prefixes, cloud key ids, private-key blocks), `/home/<user>` absolute paths in docs, unexpected emails; run it clean

## 2. Repo metadata

- [x] 2.1 Add `LICENSE` (Apache-2.0, copyright 2026 the owner), `CHANGELOG.md` (v0.1.0 entry: schema v2, skins, widgets, dark mode, validation suite), update `README.md` with install paths (pip / npx / clone) and license badge-free plain mention
- [x] 2.2 Extend `.gitignore`: `bench/runs/`, `build/`, `dist/`, `.venv/`, `node_modules/`, `*.validate.html`, `__pycache__/`
- [x] 2.3 Write `RELEASING.md`: version bump points, build commands, hygiene gate, manual `twine upload dist/*` and `npm publish doc-html-skill-0.1.0.tgz --access public`, post-publish verification (`pip install`, `npx`)

## 3. PyPI package

- [x] 3.1 Add `pyproject.toml` (hatchling): name `doc-html-skill` 0.1.0, Apache-2.0, runtime deps (jinja2, jsonschema, pyyaml, referencing), optional extras `[pdf]` (playwright); force-include `.claude/skills` → `doc_html_skill/skills`
- [x] 3.2 Add `doc_html_skill/` wrapper package: locate bundled scripts, console entry points `doc-html-render`, `doc-html-validate`, `doc-html-export-pdf` forwarding argv
- [x] 3.3 Check name availability on PyPI; `python -m build`; smoke test wheel in a throwaway venv (render bundled example, run validator schema layer)

## 4. npm package

- [x] 4.1 Rewrite `package.json` as publishable: name `doc-html-skill` 0.1.0, license, repository field, `bin`, `files` ([".claude/skills", "bin", "README.md", "LICENSE"]), keep validator deps as devDependencies, drop `private`
- [x] 4.2 Write `bin/cli.mjs`: `install` (copy skills into target `.claude/skills/`, refuse overwrite without `--force`), `list` commands; no runtime deps
- [x] 4.3 Check name availability on npm; `npm pack --dry-run` to verify `.claude/skills` inclusion; pack tarball and test `install` from the tarball into a temp dir

## 5. Repo, tag, release (checkpoint with owner before each outward step)

- [x] 5.1 `git init`, stage curated tree, run hygiene gate, initial commit
- [x] 5.2 CHECKPOINT → `gh repo create manykarim/doc-html-skill --public --source . --push`
- [x] 5.3 Build release assets: wheel + sdist, npm tarball, `doc-html-skill-skills-0.1.0.zip`, one demo HTML (rf-mcp docs-site)
- [x] 5.4 CHECKPOINT → annotated tag `v0.1.0`; `gh release create v0.1.0` with generated notes and the four+demo assets; verify release page lists all assets

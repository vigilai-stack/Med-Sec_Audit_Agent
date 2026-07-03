# Releasing

Release preparation is automated up to the registry uploads; **publishing to
PyPI and npm is manual** by the repository owner.

## Version bump points

One version, three places — keep them in sync:

| File | Field |
|---|---|
| `pyproject.toml` | `[project] version` |
| `package.json` | `version` |
| `CHANGELOG.md` | new top entry |

## Build & gate

```bash
# 1. hygiene gate (secrets, abs paths, personal data, real-brand assets)
bash scripts/release_hygiene.sh

# 2. renderer self-test + full validation matrix
.venv/bin/python .claude/skills/render-branded-html/scripts/test_render.py
for f in examples/*.yaml; do
  .venv/bin/python .claude/skills/validate-branded-doc/scripts/validate_all.py --input "$f" || break
done

# 3. Python artifacts (dist/*.whl, dist/*.tar.gz)
.venv/bin/pip install build && .venv/bin/python -m build

# 4. smoke test the wheel in a clean venv
python3 -m venv /tmp/smoke && /tmp/smoke/bin/pip -q install dist/*.whl
/tmp/smoke/bin/doc-html-render --input examples/architecture-review.yaml --output /tmp/smoke/out.html

# 5. npm tarball (doc-html-skill-<version>.tgz)
npm pack
```

## Tag & GitHub release

```bash
git tag -a v0.1.0 -m "v0.1.0"
git push origin main --tags
gh release create v0.1.0 dist/*.whl dist/*.tar.gz doc-html-skill-0.1.0.tgz \
  doc-html-skill-skills-0.1.0.zip --notes-file <(sed -n '/^## v0.1.0/,/^## v/p' CHANGELOG.md)
```

## Manual publish (owner only)

One guided script — preflights the artifacts, re-runs the hygiene gate,
prompts per registry, asks for the PyPI token (hidden input), and for npm
uses (in order) an `NPM_TOKEN` env var, an existing `npm login` session, or
prompts for a token / interactive login. Tokens go into a chmod-600 throwaway
userconfig, never argv or your `~/.npmrc`. Post-publish verification offered:

```bash
bash scripts/publish_release.sh            # both registries
bash scripts/publish_release.sh --pypi-only
bash scripts/publish_release.sh --npm-only
NPM_TOKEN=npm_xxx bash scripts/publish_release.sh --npm-only   # token via env
```

Or by hand:

```bash
# PyPI — needs a PyPI API token (~/.pypirc or TWINE_PASSWORD)
pip install twine
twine upload dist/*

# npm — needs `npm login` with the owning account
npm publish doc-html-skill-0.1.0.tgz --access public
```

## Post-publish verification

```bash
pip install --no-cache-dir doc-html-skill && doc-html-render --help
npx --yes doc-html-skill@latest list
```

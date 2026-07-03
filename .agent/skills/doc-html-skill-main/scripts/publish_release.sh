#!/usr/bin/env bash
# publish_release.sh — manual publishing helper for PyPI + npm.
#
# Publishes the ALREADY-BUILT release artifacts (see RELEASING.md):
#   dist/doc_html_skill-<version>-py3-none-any.whl + .tar.gz   -> PyPI
#   doc-html-skill-<version>.tgz                               -> npm
#
# Interactive: asks per registry, prompts for the PyPI token (hidden input,
# never echoed or persisted), and runs `npm login` if you aren't logged in.
# Nothing is rebuilt here — publish exactly what the GitHub release carries.
#
# Usage: bash scripts/publish_release.sh [--pypi-only|--npm-only]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PY="${PYTHON:-$ROOT/.venv/bin/python}"
[ -x "$PY" ] || PY="$(command -v python3)"

VERSION=$("$PY" -c "import re,pathlib;print(re.search(r'^version = \"(.+?)\"', pathlib.Path('pyproject.toml').read_text(), re.M).group(1))")
WHEEL="dist/doc_html_skill-${VERSION}-py3-none-any.whl"
SDIST="dist/doc_html_skill-${VERSION}.tar.gz"
TGZ="doc-html-skill-${VERSION}.tgz"

DO_PYPI=1; DO_NPM=1
case "${1:-}" in
  --pypi-only) DO_NPM=0 ;;
  --npm-only)  DO_PYPI=0 ;;
  "") ;;
  *) echo "usage: $0 [--pypi-only|--npm-only]"; exit 2 ;;
esac

echo "doc-html-skill v${VERSION} — manual publish"
echo

# ---------------------------------------------------------------- preflight
fail=0
for f in "$WHEEL" "$SDIST"; do
  [ "$DO_PYPI" = 1 ] && [ ! -f "$f" ] && { echo "missing: $f (run: $PY -m build)"; fail=1; }
done
[ "$DO_NPM" = 1 ] && [ ! -f "$TGZ" ] && { echo "missing: $TGZ (run: npm pack)"; fail=1; }
[ "$fail" = 1 ] && exit 2

bash "$ROOT/scripts/release_hygiene.sh" >/dev/null \
  && echo "hygiene gate: PASS" \
  || { echo "hygiene gate: FAIL — aborting"; exit 2; }
echo

confirm() { # prompt -> 0/1
  local reply
  read -r -p "$1 [y/N] " reply
  [[ "$reply" =~ ^[Yy] ]]
}

# ---------------------------------------------------------------- PyPI
if [ "$DO_PYPI" = 1 ] && confirm "Publish ${WHEEL##*/} + sdist to PyPI?"; then
  "$PY" -m pip show -q twine 2>/dev/null || "$PY" -m pip install -q twine
  "$PY" -m twine check "$WHEEL" "$SDIST"

  echo "PyPI API token (create at https://pypi.org/manage/account/token/)."
  read -r -s -p "Token (input hidden, starts with pypi-): " PYPI_TOKEN; echo
  [ -n "$PYPI_TOKEN" ] || { echo "empty token — skipping PyPI"; PYPI_TOKEN=""; }

  if [ -n "$PYPI_TOKEN" ]; then
    TWINE_USERNAME="__token__" TWINE_PASSWORD="$PYPI_TOKEN" \
      "$PY" -m twine upload --non-interactive "$WHEEL" "$SDIST"
    unset PYPI_TOKEN
    echo "PyPI: published — https://pypi.org/project/doc-html-skill/${VERSION}/"
    if confirm "Verify with a clean pip install?"; then
      V="$(mktemp -d)/venv"; python3 -m venv "$V"
      "$V/bin/pip" -q install --no-cache-dir "doc-html-skill==${VERSION}" \
        && "$V/bin/doc-html-render" --help >/dev/null \
        && echo "verify: PASS (doc-html-render runs from PyPI install)" \
        || echo "verify: FAIL (index may need a minute to propagate — retry manually)"
    fi
  fi
else
  [ "$DO_PYPI" = 1 ] && echo "PyPI: skipped"
fi
echo

# ---------------------------------------------------------------- npm
if [ "$DO_NPM" = 1 ] && confirm "Publish ${TGZ} to npm (--access public)?"; then
  NPMRC=""
  cleanup_npmrc() { [ -n "$NPMRC" ] && rm -f "$NPMRC"; NPMRC=""; }
  trap cleanup_npmrc EXIT

  use_token() { # writes a throwaway userconfig so the token never hits argv/.npmrc
    NPMRC="$(mktemp)"
    chmod 600 "$NPMRC"
    printf '//registry.npmjs.org/:_authToken=%s\n' "$1" > "$NPMRC"
  }

  if [ -n "${NPM_TOKEN:-}" ]; then
    echo "npm: using token from NPM_TOKEN env"
    use_token "$NPM_TOKEN"
  elif npm whoami >/dev/null 2>&1; then
    echo "npm: logged in as $(npm whoami)"
  else
    echo "npm: not logged in. Auth options:"
    echo "  1) access token (create at https://www.npmjs.com/settings/~/tokens — granular, packages:read-write)"
    echo "  2) interactive 'npm login' (browser flow)"
    read -r -p "Choose [1/2]: " auth_choice
    if [ "$auth_choice" = "1" ]; then
      read -r -s -p "npm token (input hidden, starts with npm_): " NPM_TOKEN_IN; echo
      [ -n "$NPM_TOKEN_IN" ] || { echo "empty token — aborting npm publish"; exit 2; }
      use_token "$NPM_TOKEN_IN"
      unset NPM_TOKEN_IN
    else
      npm login
    fi
  fi

  if [ -n "$NPMRC" ]; then
    NPM_CONFIG_USERCONFIG="$NPMRC" npm publish "$TGZ" --access public
    cleanup_npmrc
  else
    npm publish "$TGZ" --access public
  fi
  echo "npm: published — https://www.npmjs.com/package/doc-html-skill"
  if confirm "Verify with npx?"; then
    npx --yes "doc-html-skill@${VERSION}" list >/dev/null \
      && echo "verify: PASS (npx doc-html-skill list works)" \
      || echo "verify: FAIL (registry may need a minute to propagate — retry manually)"
  fi
else
  [ "$DO_NPM" = 1 ] && echo "npm: skipped"
fi

echo
echo "Done. Remember: published versions are immutable — fixes go to $(echo "$VERSION" | awk -F. '{print $1"."$2"."$3+1}') per RELEASING.md."

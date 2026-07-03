#!/usr/bin/env bash
# release_hygiene.sh — pre-publication gate. Scans the to-be-published tree
# (git-tracked files if a repo exists, else the curated tree) for secrets,
# machine-local absolute paths, and unexpected personal data. Non-zero exit
# blocks the release.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
FAIL=0

list_files() {
  if git rev-parse --git-dir >/dev/null 2>&1; then
    git ls-files
  else
    find . -type f \
      -not -path "./node_modules/*" -not -path "./.venv/*" \
      -not -path "./build/*" -not -path "./dist/*" \
      -not -path "./bench/runs/*" -not -path "./.git/*" \
      -not -path "./.kilocode/*" -not -path "./.opencode/*" -not -path "./.codex/*" | sed 's|^\./||'
  fi
}

FILES=$(list_files)

check() { # label, grep-args...
  local label="$1"; shift
  local hits
  hits=$(echo "$FILES" | xargs -d '\n' grep -lI "$@" 2>/dev/null)
  if [ -n "$hits" ]; then
    echo "FAIL [$label]:"
    echo "$hits" | sed 's/^/  - /'
    FAIL=1
  else
    echo "PASS [$label]"
  fi
}

# 1. secret / credential patterns
check "secrets" -E "ghp_[A-Za-z0-9]{20,}|gho_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|xox[bporas]-[A-Za-z0-9-]{10,}|sk-[A-Za-z0-9]{20,}"

# 2. machine-local absolute paths in published docs/sources (allowed only in
#    this script itself)
hits=$(echo "$FILES" | grep -vE "^scripts/release_hygiene.sh$" | \
  xargs -d '\n' grep -lI "/home/[a-z]" 2>/dev/null)
if [ -n "$hits" ]; then
  echo "FAIL [abs-paths]:"; echo "$hits" | sed 's/^/  - /'; FAIL=1
else
  echo "PASS [abs-paths]"
fi

# 3. e-mail addresses — none expected in the published tree
hits=$(echo "$FILES" | xargs -d '\n' grep -lIE "[A-Za-z0-9._%+-]+@(gmail|outlook|yahoo|gmx|web)\.[a-z]+" 2>/dev/null)
if [ -n "$hits" ]; then
  echo "FAIL [personal-emails]:"; echo "$hits" | sed 's/^/  - /'; FAIL=1
else
  echo "PASS [personal-emails]"
fi

# 4. real-brand names must not appear in example assets / skills / README
hits=$(echo "$FILES" | grep -E "^(examples|\.claude|README|experiments)" | \
  xargs -d '\n' grep -lIiE "coca.?cola|ikea|schenker" 2>/dev/null)
if [ -n "$hits" ]; then
  echo "FAIL [real-brands]:"; echo "$hits" | sed 's/^/  - /'; FAIL=1
else
  echo "PASS [real-brands]"
fi

echo
if [ "$FAIL" -ne 0 ]; then echo "HYGIENE GATE: FAIL"; exit 2; fi
echo "HYGIENE GATE: PASS"

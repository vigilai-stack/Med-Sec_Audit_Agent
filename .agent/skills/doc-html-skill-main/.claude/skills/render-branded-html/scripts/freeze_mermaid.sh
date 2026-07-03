#!/usr/bin/env bash
# freeze_mermaid.sh — render a branded doc in FROZEN archival mode.
#
# Extracts each Mermaid section from the canonical source, renders it to a
# standalone SVG with the official Mermaid CLI (mmdc), then re-renders the HTML
# with those SVGs inlined (no client-side Mermaid). Best for archival, stable
# screenshots, and PDF export.
#
# Usage: freeze_mermaid.sh <input.yaml|json> <output.html> [theme.json]
# Requires: mmdc (npm i -g @mermaid-js/mermaid-cli), python (project .venv).
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_ROOT="$(cd "$SKILL_DIR/../../.." && pwd)"
PY="${PYTHON:-$PROJECT_ROOT/.venv/bin/python}"
RENDER="$SKILL_DIR/scripts/render.py"

INPUT="${1:?input source required}"
OUTPUT="${2:?output html path required}"
THEME="${3:-}"

if ! command -v mmdc >/dev/null 2>&1; then
  echo "error: mmdc (mermaid-cli) not found. Install: npm i -g @mermaid-js/mermaid-cli" >&2
  exit 3
fi

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# 1. Extract mermaid sections to <id>.mmd and emit an index of ids.
"$PY" - "$INPUT" "$WORK" <<'PY'
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
src, work = Path(sys.argv[1]), Path(sys.argv[2])
import yaml
text = src.read_text(encoding="utf-8")
payload = yaml.safe_load(text) if src.suffix.lower() in {".yaml", ".yml"} else json.loads(text)
ids = []
for s in payload.get("sections", []) or []:
    if s.get("kind") == "mermaid" and s.get("source"):
        (work / f"{s['id']}.mmd").write_text(s["source"], encoding="utf-8")
        ids.append(s["id"])
(work / "ids.json").write_text(json.dumps(ids), encoding="utf-8")
print(f"extracted {len(ids)} mermaid section(s)")
PY

# 2. Render each .mmd to .svg with mmdc.
# Some sandboxed CI/container environments disable the Chromium sandbox; mmdc
# uses Puppeteer, so pass --no-sandbox via a puppeteer config there. Override
# by setting MMDC_PUPPETEER_CONFIG to your own config path.
PUPPETEER_CFG="${MMDC_PUPPETEER_CONFIG:-$WORK/puppeteer.json}"
if [ -z "${MMDC_PUPPETEER_CONFIG:-}" ]; then
  printf '{ "args": ["--no-sandbox", "--disable-setuid-sandbox"] }' > "$PUPPETEER_CFG"
fi

# Resolved Mermaid config (skin-aware themeVariables) so frozen SVGs match
# the page palette exactly like interactive mode does.
THEME_ARG=()
[ -n "$THEME" ] && THEME_ARG=(--theme "$THEME")
"$PY" "$RENDER" --input "$INPUT" "${THEME_ARG[@]}" --print-mermaid-config > "$WORK/mermaid-config.json"

IDS=$("$PY" -c "import json,sys;print(' '.join(json.load(open(sys.argv[1]))))" "$WORK/ids.json")
for id in $IDS; do
  mmdc --input "$WORK/$id.mmd" --output "$WORK/$id.svg" \
    --backgroundColor transparent --puppeteerConfigFile "$PUPPETEER_CFG" \
    --configFile "$WORK/mermaid-config.json" >/dev/null
done

# 3. Build the {id: svg} map.
"$PY" - "$WORK" <<'PY'
import json, sys
from pathlib import Path
work = Path(sys.argv[1])
ids = json.loads((work / "ids.json").read_text())
svgs = {i: (work / f"{i}.svg").read_text(encoding="utf-8") for i in ids}
(work / "svgs.json").write_text(json.dumps(svgs), encoding="utf-8")
PY

# 4. Re-render HTML with inlined SVGs (frozen).
"$PY" "$RENDER" --input "$INPUT" --frozen-svgs "$WORK/svgs.json" "${THEME_ARG[@]}" --output "$OUTPUT"
echo "frozen HTML written to $OUTPUT"

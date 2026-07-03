#!/usr/bin/env bash
# run_one.sh <tool> <condition> [rep]
#   tool: claude | codex | opencode | kilo
#   condition: noskill | skill
# Sets up an isolated workdir, runs the CLI headless with timing, captures raw
# output + session export, and writes meta.json. Metric parsing is done later
# by extract.py.
set -uo pipefail
TOOL="${1:?tool}"; COND="${2:?condition}"; REP="${3:-1}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN="$ROOT/runs/${TOOL}-${COND}-${REP}"
rm -rf "$RUN"; mkdir -p "$RUN"

# Build the prompt (multiline-safe brief substitution via python).
python3 - "$ROOT/prompts/${COND}.md" "$ROOT/brief.md" "$RUN/prompt.txt" <<'PY'
import sys
tmpl, brief, out = sys.argv[1:4]
open(out,'w').write(open(tmpl).read().replace('{{BRIEF}}', open(brief).read()))
PY

# with-skill: drop the portable skillkit into the workdir.
if [ "$COND" = "skill" ]; then
  cp -r "$ROOT/skillkit/." "$RUN/"
fi

PROMPT="$(cat "$RUN/prompt.txt")"
START=$(date +%s%3N)

case "$TOOL" in
  claude)
    ( cd "$RUN" && claude -p "$PROMPT" --output-format json \
        --dangerously-skip-permissions > raw.json 2> raw.err ); EXIT=$?
    ;;
  codex)
    # workspace-write sandbox blocked writes/exec in this environment; use full
    # bypass (throwaway run dir) so codex can actually produce the deliverable.
    ( cd "$RUN" && codex exec --json --skip-git-repo-check \
        --dangerously-bypass-approvals-and-sandbox \
        "$PROMPT" < /dev/null > raw.jsonl 2> raw.err ); EXIT=$?
    ;;
  opencode)
    ( cd "$RUN" && opencode run --dangerously-skip-permissions "$PROMPT" \
        < /dev/null > raw.out 2> raw.err ); EXIT=$?
    SID=$(opencode session list 2>/dev/null | awk 'NR>2{print $1; exit}')
    echo "$SID" > "$RUN/session_id.txt"
    opencode export "$SID" > "$RUN/session.json" 2>/dev/null
    ;;
  kilo)
    ( cd "$RUN" && kilo run --auto "$PROMPT" \
        < /dev/null > raw.out 2> raw.err ); EXIT=$?
    SID=$(kilo session list 2>/dev/null | awk 'NR>2{print $1; exit}')
    echo "$SID" > "$RUN/session_id.txt"
    kilo export "$SID" > "$RUN/session.json" 2>/dev/null
    ;;
  *) echo "unknown tool $TOOL"; exit 2;;
esac

END=$(date +%s%3N)
WALL=$((END-START))

# Record meta + artifact inventory.
DOCBYTES=$( [ -f "$RUN/doc.html" ] && wc -c < "$RUN/doc.html" || echo 0 )
YAMLBYTES=$( [ -f "$RUN/doc.yaml" ] && wc -c < "$RUN/doc.yaml" || echo 0 )
python3 - "$RUN" "$TOOL" "$COND" "$REP" "$EXIT" "$WALL" "$DOCBYTES" "$YAMLBYTES" <<'PY'
import json,sys,os
run,tool,cond,rep,exit_,wall,docb,yamlb = sys.argv[1:9]
# list produced files (exclude skillkit + scaffolding)
skip={'prompt.txt','raw.json','raw.jsonl','raw.out','raw.err','session.json','session_id.txt','meta.json'}
skipdirs={'schemas','scripts','templates','assets'}
produced=[]
for f in os.listdir(run):
    if f in skip or f in skipdirs or f=='render': continue
    produced.append(f)
json.dump({'tool':tool,'condition':cond,'rep':int(rep),'exit':int(exit_),
           'wall_ms':int(wall),'doc_html_bytes':int(docb),'doc_yaml_bytes':int(yamlb),
           'produced_files':sorted(produced)},
          open(os.path.join(run,'meta.json'),'w'), indent=2)
PY
echo "[$TOOL/$COND/$REP] exit=$EXIT wall=${WALL}ms doc.html=${DOCBYTES}B doc.yaml=${YAMLBYTES}B"

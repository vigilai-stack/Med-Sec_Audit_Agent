#!/usr/bin/env bash
# run_reps.sh <tool> <rep...>  — run both conditions for each rep, sequentially
# (sequential per tool so opencode/kilo "newest session" capture stays correct).
set -uo pipefail
TOOL="$1"; shift
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for rep in "$@"; do
  for cond in noskill skill; do
    bash "$DIR/run_one.sh" "$TOOL" "$cond" "$rep"
  done
done
echo "[$TOOL] reps done: $*"

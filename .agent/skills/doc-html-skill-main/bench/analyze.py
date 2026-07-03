#!/usr/bin/env python3
"""analyze.py — merge metrics + quality into results/REPORT.md.

Produces:
  - a raw metrics table (all runs)
  - within-tool deltas (skill vs noskill) — the scientifically valid comparison
  - a quality table (accessibility / responsive / brief compliance)
  - a plain-language verdict with explicit caveats
"""
from __future__ import annotations
import json, os

BENCH = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(BENCH, "results")


def load(name):
    p = os.path.join(R, name)
    return json.load(open(p)) if os.path.exists(p) else None


def fmt(n):
    if n is None: return "—"
    if isinstance(n, bool): return str(n)
    if isinstance(n, float): return f"{n:.4f}" if n < 1 else f"{n:,.2f}"
    if isinstance(n, int): return f"{n:,}"
    return str(n)


def pct(old, new):
    if not old or new is None: return "—"
    d = (new - old) / old * 100
    return f"{d:+.0f}%"


def main():
    metrics = load("metrics.json") or []
    quality = load("quality.json") or {}
    by = {}
    for m in metrics:
        by.setdefault(m["tool"], {})[m["condition"]] = m

    lines = []
    L = lines.append
    L("# Skills vs. pure HTML generation — benchmark results\n")
    L("Same fixed content brief, same target (branded HTML, ≥3 diagrams, ≥2 tables). "
      "Two conditions per tool: **noskill** (model writes HTML directly) vs **skill** "
      "(model writes compact canonical YAML, the renderer owns all chrome). N=1 per cell.\n")

    L("## Raw metrics (all runs)\n")
    cols = [("tool","tool"),("condition","cond"),("model","model"),("out_tokens","out tok"),
            ("total_tokens","total tok"),("cost_usd","cost $"),("wall_ms","wall ms"),
            ("tool_calls","tools"),("doc_html_bytes","html B"),("doc_yaml_bytes","yaml B")]
    L("| " + " | ".join(c[1] for c in cols) + " |")
    L("|" + "---|"*len(cols))
    for m in metrics:
        L("| " + " | ".join(fmt(m.get(c[0])) for c in cols) + " |")
    L("")

    L("## Within-tool delta: skill vs noskill (the valid comparison)\n")
    L("Each tool runs the same model in both conditions, so the delta isolates the *method*.\n")
    L("| tool | model | out-tokens | total-tokens | cost | wall | tool-calls |")
    L("|---|---|---|---|---|---|---|")
    for tool, conds in by.items():
        ns, sk = conds.get("noskill"), conds.get("skill")
        if not ns or not sk: continue
        L(f"| {tool} | {sk.get('model')} | "
          f"{fmt(ns['out_tokens'])}→{fmt(sk['out_tokens'])} ({pct(ns['out_tokens'],sk['out_tokens'])}) | "
          f"{pct(ns['total_tokens'],sk['total_tokens'])} | "
          f"{fmt(ns['cost_usd'])}→{fmt(sk['cost_usd'])} ({pct(ns['cost_usd'],sk['cost_usd'])}) | "
          f"{pct(ns['wall_ms'],sk['wall_ms'])} | "
          f"{fmt(ns.get('tool_calls'))}→{fmt(sk.get('tool_calls'))} |")
    L("")

    if quality:
        L("## Output quality\n")
        L("| run | a11y (WCAG AA) | responsive | diagrams | tables | meets brief |")
        L("|---|---|---|---|---|---|")
        for name in sorted(quality):
            q = quality[name]
            if not q.get("exists"): L(f"| {name} | missing | | | | |"); continue
            L(f"| {name} | {q['accessibility']} | {q['responsive']} | {q['diagrams']} | {q['tables']} | "
              f"{'✅' if q['meets_brief'] else '❌'} |")
        L("")

    open(os.path.join(R, "REPORT.md"), "w").write("\n".join(lines))
    print("\n".join(lines))
    print("\n-> results/REPORT.md")


if __name__ == "__main__":
    main()

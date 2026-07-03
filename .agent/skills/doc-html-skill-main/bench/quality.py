#!/usr/bin/env python3
"""quality.py — assess the produced doc.html of each run (tool-agnostic).

Runs the suite's own accessibility + responsive validators on every run's
doc.html and counts Mermaid diagrams and tables, so we can compare OUTPUT
QUALITY, not just token cost. Writes results/quality.json.
"""
from __future__ import annotations
import json, os, subprocess, glob, re

BENCH = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(BENCH, "runs")
VDIR = os.path.join(BENCH, "..", ".claude", "skills", "validate-branded-doc", "scripts")
NODE = "node"


def node_check(script, html):
    try:
        r = subprocess.run([NODE, os.path.join(VDIR, script), "--input", html],
                           capture_output=True, text=True, timeout=120)
        if r.returncode == 3:
            return "skip"
        return "pass" if r.returncode == 0 else "fail"
    except Exception:
        return "error"


def main():
    out = {}
    for run in sorted(glob.glob(os.path.join(RUNS, "*"))):
        html = os.path.join(run, "doc.html")
        name = os.path.basename(run)
        if not os.path.exists(html) or os.path.getsize(html) == 0:
            out[name] = {"exists": False}
            continue
        text = open(html, encoding="utf-8", errors="ignore").read()
        diagrams = len(re.findall(r'class="mermaid"|<pre[^>]*mermaid|language-mermaid', text))
        tables = len(re.findall(r'<table', text, re.I))
        out[name] = {
            "exists": True,
            "bytes": os.path.getsize(html),
            "accessibility": node_check("validate_accessibility.mjs", html),
            "responsive": node_check("validate_responsive.mjs", html),
            "diagrams": diagrams,
            "tables": tables,
            "meets_brief": diagrams >= 3 and tables >= 2,
        }
        print(f"{name:24} a11y={out[name]['accessibility']:5} resp={out[name]['responsive']:5} "
              f"dia={diagrams} tab={tables} brief={'Y' if out[name]['meets_brief'] else 'N'}")
    os.makedirs(os.path.join(BENCH, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(BENCH, "results", "quality.json"), "w"), indent=2)
    print("-> results/quality.json")


if __name__ == "__main__":
    main()

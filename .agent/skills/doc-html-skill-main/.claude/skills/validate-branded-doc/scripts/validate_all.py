#!/usr/bin/env python3
"""validate_all.py — consolidated, layered validator.

Runs checks in order and produces a single pass/fail report:
  1. schema        (validate_schema.py)        — runs first; failure short-circuits
  2. mermaid       (validate_mermaid.mjs)
  3. accessibility (validate_accessibility.mjs) — needs rendered HTML
  4. responsive    (validate_responsive.mjs)    — needs rendered HTML
  5. export/pdf    (validate_export.mjs)         — needs rendered HTML

A schema failure marks the remaining checks as "skipped" and the run as failed.
HTML-based layers that need optional Node deps report "skipped" (not "failed")
when those deps are absent, so the core schema+mermaid gate still works offline.

Usage:
  validate_all.py --input <source.yaml|json> [--html <rendered.html>] [--json]
Exit: 0 all-pass, 2 any-fail.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent
RENDER = SKILL_ROOT.parent / "render-branded-html" / "scripts" / "render.py"
PYTHON = sys.executable
NODE = "node"


def run(cmd: list[str]) -> tuple[int, str]:
    # Node layers shell back to python for YAML parsing; hand them OUR
    # interpreter so installs outside the project .venv (e.g. pip wheels)
    # resolve correctly regardless of cwd.
    env = {**os.environ, "PYTHON": PYTHON}
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def parse_json_tail(output: str) -> dict | None:
    for line in reversed(output.splitlines()):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    return None


def node_check(script: str, html: Path, label: str, extra: list[str] | None = None) -> dict:
    code, out = run([NODE, str(HERE / script), "--input", str(html), "--json", *(extra or [])])
    if code == 3:  # missing optional deps
        return {"check": label, "passed": None, "skipped": True,
                "reason": "optional deps not installed", "detail": out}
    report = parse_json_tail(out) or {"check": label, "passed": code == 0, "errors": [out]}
    report.setdefault("check", label)
    report["passed"] = code == 0
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the full layered validation suite.")
    parser.add_argument("--input", required=True, help="canonical source (YAML/JSON)")
    parser.add_argument("--html", help="rendered HTML; auto-rendered if omitted")
    parser.add_argument("--skin", choices=["docs-site", "editorial", "brief"],
                        help="validate under an explicit skin (matrix testing); "
                             "default: the source's resolved skin")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    src = Path(args.input)
    results: list[dict] = []

    # 1. schema (gate)
    code, out = run([PYTHON, str(HERE / "validate_schema.py"), "--input", str(src), "--json"])
    schema_report = parse_json_tail(out) or {"check": "schema", "passed": code == 0, "errors": [out]}
    schema_report["passed"] = code == 0
    results.append(schema_report)

    if not schema_report["passed"]:
        for label in ("mermaid", "accessibility", "responsive", "export"):
            results.append({"check": label, "passed": None, "skipped": True,
                            "reason": "schema failed — short-circuited"})
        return _emit(results, args.json)

    # 2. mermaid (source-level)
    code, out = run([NODE, str(HERE / "validate_mermaid.mjs"), "--input", str(src), "--json"])
    mreport = parse_json_tail(out) or {"check": "mermaid", "passed": code == 0, "errors": [out]}
    mreport["passed"] = code == 0
    results.append(mreport)

    # 3-5. HTML-based layers — render if needed
    html = Path(args.html) if args.html else None
    if html is None:
        html = src.with_suffix(".validate.html")
        render_cmd = [PYTHON, str(RENDER), "--input", str(src), "--output", str(html)]
        if args.skin:
            render_cmd += ["--skin", args.skin]
        rc, rout = run(render_cmd)
        if rc != 0:
            results.append({"check": "render", "passed": False, "errors": [rout]})
            return _emit(results, args.json)

    results.append(node_check("validate_accessibility.mjs", html, "accessibility"))
    # dark/auto documents additionally get a dark-scheme accessibility pass
    try:
        import yaml as _yaml
        payload = (_yaml.safe_load(src.read_text(encoding="utf-8"))
                   if src.suffix.lower() in {".yaml", ".yml"}
                   else json.loads(src.read_text(encoding="utf-8")))
        mode = ((payload or {}).get("theme") or {}).get("mode") or "light"
    except Exception:
        mode = "light"
    if mode in {"dark", "auto"}:
        dark = node_check("validate_accessibility.mjs", html, "accessibility-dark",
                          extra=["--color-scheme", "dark"])
        dark["check"] = "accessibility-dark"
        results.append(dark)
    results.append(node_check("validate_responsive.mjs", html, "responsive"))
    results.append(node_check("validate_export.mjs", html, "export"))

    return _emit(results, args.json)


def _emit(results: list[dict], as_json: bool) -> int:
    # A run fails if any check explicitly failed (passed is False). Skipped
    # (passed is None) does not fail the run.
    failed = any(r.get("passed") is False for r in results)
    if as_json:
        print(json.dumps({"passed": not failed, "checks": results}, indent=2))
    else:
        print("=== Validation report ===")
        for r in results:
            status = "SKIP" if r.get("skipped") else ("PASS" if r.get("passed") else "FAIL")
            line = f"[{status:4}] {r['check']}"
            if r.get("reason"):
                line += f" — {r['reason']}"
            print(line)
            for e in r.get("errors", []) or []:
                print(f"         - {e}")
        print(f"\nOverall: {'PASS' if not failed else 'FAIL'}")
    return 2 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""test_render.py — renderer self-test: every widget kind, every skin.

Builds a synthetic architecture-review exercising ALL section kinds and all
overlay fields, renders it under each skin, and asserts:
  - schema validation passes for the synthetic source
  - every widget's structural marker appears in the output of every skin
  - overlay fields render (decision cards, severity tags, keyvalue, callout)
  - figure numbering is sequential and captions appear
  - renders are deterministic (byte-identical across two runs)
  - unknown section kind / bad enum is rejected by validation

Run: python scripts/test_render.py   (exit 0 = pass)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render import SKINS, render_html, resolve_skin, resolve_tokens, validate_payload  # noqa: E402

DOC = {
    "schema_version": 2,
    "artifact_type": "architecture-review",
    "title": "Widget exercise",
    "subtitle": "All kinds, one document",
    "status": "draft",
    "owner": "Tests",
    "updated_at": "2026-06-04",
    "summary": ["One summary point."],
    "decisions": [{"title": "Decide X", "rationale": "Because Y.", "status": "adopted", "ref": "ADR-001"}],
    "constraints": ["plain string constraint", {"text": "tagged constraint", "severity": "high"}],
    "interfaces": ["HTTP on :8000"],
    "deployment_context": "Runs locally.",
    "alternatives": ["Do nothing — rejected."],
    "sections": [
        {"id": "s-stats", "title": "Stats", "kind": "stats", "width": "half",
         "items": [{"value": 3, "label": "Things", "delta": "+1"}]},
        {"id": "s-prose", "title": "Prose", "kind": "prose", "body": "Para one.\n\nPara two."},
        {"id": "s-callout", "title": "Callout", "kind": "callout", "intent": "warning", "body": "Careful."},
        {"id": "s-mermaid", "title": "Diagram", "kind": "mermaid", "diagram_type": "flowchart",
         "source": "flowchart LR\n  A --> B", "caption": "A to B"},
        {"id": "s-table", "title": "Table", "kind": "table", "columns": ["a", "b"], "rows": [["1", "2"]]},
        {"id": "s-steps", "title": "Steps", "kind": "steps",
         "items": [{"title": "First", "body": "Do it."}]},
        {"id": "s-cards", "title": "Cards", "kind": "cards", "variant": "generic",
         "items": [{"title": "Card", "body": "Body", "tag": "tag", "ref": "REF-1"}]},
        {"id": "s-kv", "title": "KV", "kind": "keyvalue",
         "items": [{"key": "K", "value": "V"}]},
        {"id": "s-code", "title": "Code", "kind": "code", "language": "json",
         "filename": "x.json", "source": "{}"},
        {"id": "s-tabs", "title": "Tabs", "kind": "tabs",
         "items": [{"label": "One", "body": "1"}, {"label": "Two", "body": "2", "code": True}]},
        {"id": "s-details", "title": "Details", "kind": "details",
         "summary": "More", "body": "Hidden text."},
        {"id": "s-timeline", "title": "Timeline", "kind": "timeline",
         "items": [{"label": "Event", "body": "Happened", "date": "2026-01-01"}]},
        {"id": "s-heat", "title": "Heatmap", "kind": "heatmap",
         "x_labels": ["lo", "hi"], "y_labels": ["bad", "ok"],
         "cells": [{"x": 0, "y": 0, "level": 5, "label": "X"}, {"x": 1, "y": 1, "level": 1}]},
        {"id": "s-meters", "title": "Meters", "kind": "meters",
         "items": [{"label": "Coverage", "value": 70, "note": "good"}]},
        {"id": "s-mermaid2", "title": "Second diagram", "kind": "mermaid",
         "diagram_type": "sequence", "source": "sequenceDiagram\n  A->>B: hi"},
    ],
    "evidence": [{"label": "Source", "href": "https://example.com"}],
}

# structural marker per widget that must survive into every skin's HTML
MARKERS = {
    "stats": 'class="stats"',
    "prose": 'class="prose"',
    "callout": "callout--warning",
    "mermaid": 'class="fig-stage"',
    "zoom": "fig-zoom-toggle",
    "table": 'class="data"',
    "steps": 'class="steps"',
    "cards": 'class="cards cards--generic"',
    "keyvalue": 'class="keyvalue"',
    "code": 'class="codeblock"',
    "tabs": 'class="tabs"',
    "details": 'class="details"',
    "timeline": 'class="timeline"',
    "heatmap": "heat--5",
    "meters": 'class="meters"',
    # overlay rendering
    "overlay-decisions": "cards--decision",
    "overlay-sev": "sev--high",
    "overlay-kv": "overlay-interfaces",
    "overlay-callout": "callout--note",
    "overlay-rejected": "cards--rejected",
    # figures
    "fig1": "Figure 1.",
    "fig2": "Figure 2.",
    "caption": "A to B",
}


def main() -> int:
    failures: list[str] = []

    errs = validate_payload(DOC)
    if errs:
        failures += [f"synthetic doc should validate: {e}" for e in errs]

    bad = dict(DOC, sections=[{"id": "x", "title": "X", "kind": "sparkline", "body": "?"}])
    if not validate_payload(bad):
        failures.append("unknown kind 'sparkline' should be rejected")
    bad2 = dict(DOC, theme={"layout": "fancy"})
    if not validate_payload(bad2):
        failures.append("unknown theme.layout should be rejected")

    if resolve_skin(DOC) != "docs-site":
        failures.append("architecture-review should default to docs-site")
    if resolve_skin(dict(DOC, theme={"layout": "brief"})) != "brief":
        failures.append("theme.layout override should win")

    for skin in SKINS:
        tokens = resolve_tokens(None, skin)
        html = render_html(DOC, tokens, skin)
        html2 = render_html(DOC, tokens, skin)
        if html != html2:
            failures.append(f"[{skin}] render not deterministic")
        for name, marker in MARKERS.items():
            if marker not in html:
                failures.append(f"[{skin}] missing widget marker {name!r} ({marker})")
        if "--color-primary:" not in html:
            failures.append(f"[{skin}] theme CSS variables not injected")

        # mode-aware emission (CSS media block only — the mermaid init JS
        # always carries a matchMedia call, which is fine)
        if "color-scheme: light;" not in html or "@media (prefers-color-scheme: dark)" in html:
            failures.append(f"[{skin}] default (light) mode emission wrong")
        dark_doc = dict(DOC, theme={"mode": "dark"})
        dhtml = render_html(dark_doc, tokens, skin)
        if dhtml != render_html(dark_doc, tokens, skin):
            failures.append(f"[{skin}] dark render not deterministic")
        dark_bg = (tokens.get("dark") or {}).get("bg")
        if "color-scheme: dark;" not in dhtml or (dark_bg and f"--color-bg: {dark_bg};" not in dhtml):
            failures.append(f"[{skin}] dark mode must emit dark palette in :root")
        if "@media (prefers-color-scheme: dark)" in dhtml:
            failures.append(f"[{skin}] explicit dark must not depend on prefers-color-scheme CSS")
        auto_doc = dict(DOC, theme={"mode": "auto"})
        ahtml = render_html(auto_doc, tokens, skin)
        if "@media (prefers-color-scheme: dark)" not in ahtml or 'data-theme-mode="auto"' not in ahtml:
            failures.append(f"[{skin}] auto mode must emit scoped prefers-color-scheme block")
        if '"mode": "auto"' not in ahtml.replace("const mode = \"auto\"", '"mode": "auto"'):
            failures.append(f"[{skin}] auto mode missing from mermaid init")
        # frozen auto pins light: no dark media block when SVGs are baked
        fhtml = render_html(dict(auto_doc, export={"freeze_diagrams": True}), tokens, skin,
                            frozen_svgs={"s-mermaid": "<svg></svg>", "s-mermaid2": "<svg></svg>"})
        if "@media (prefers-color-scheme: dark)" in fhtml:
            failures.append(f"[{skin}] frozen auto must pin to light")

    if failures:
        print("FAIL")
        for f in failures:
            print(f"  - {f}")
        return 2
    print(f"PASS — {len(MARKERS)} markers × {len(SKINS)} skins, determinism, validation gates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

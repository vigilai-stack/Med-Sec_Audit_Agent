#!/usr/bin/env python3
"""Render branded review HTML from canonical YAML/JSON source.

The model authors content (canonical source); this renderer owns all chrome:
HTML boilerplate, CSS, layout, print styles, and Mermaid bootstrapping. Output
is deterministic — identical input yields byte-identical HTML.

Pipeline: load_source -> validate_payload (JSON Schema, Draft 2020-12)
-> render_html (Jinja, autoescaped). Theme tokens map to BOTH CSS custom
properties and Mermaid themeVariables so page and diagrams never drift.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = SKILL_ROOT / "schemas"
TEMPLATE_DIR = SKILL_ROOT / "templates"
ASSET_DIR = SKILL_ROOT / "assets"

# artifact_type -> overlay schema file
OVERLAY_BY_TYPE = {
    "user-story-review": "user-story-review.schema.json",
    "architecture-review": "architecture-review.schema.json",
    "prd-review": "prd-review.schema.json",
    "risk-analysis": "risk-analysis.schema.json",
    "test-charter": "test-charter.schema.json",
}

# token path -> CSS custom property (mirror of assets/mermaid-config.js CSS_VAR_MAP)
CSS_VAR_MAP = {
    "color.bg": "--color-bg",
    "color.surface": "--color-surface",
    "color.text": "--color-text",
    "color.text_dim": "--color-text-dim",
    "color.line": "--color-line",
    "color.primary": "--color-primary",
    "color.primary_soft": "--color-primary-soft",
    "color.success": "--color-success",
    "color.warning": "--color-warning",
    "color.danger": "--color-danger",
    "font.sans": "--font-sans",
    "font.serif": "--font-serif",
    "font.mono": "--font-mono",
    "radius.card": "--radius-card",
    "spacing.page_x": "--space-page-x",
    "spacing.section_y": "--space-section-y",
}


# ---------------------------------------------------------------- source I/O
def load_source(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(text)
    return json.loads(text)


def load_theme(tokens_path: Path | None) -> dict:
    path = tokens_path or (ASSET_DIR / "default-theme.json")
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- validation
def build_registry() -> Registry:
    resources = []
    for p in sorted(SCHEMA_DIR.glob("*.schema.json")):
        contents = json.loads(p.read_text(encoding="utf-8"))
        resource = Resource.from_contents(contents, default_specification=DRAFT202012)
        resources.append((p.name, resource))
        if "$id" in contents:
            resources.append((contents["$id"], resource))
    return Registry().with_resources(resources)


def schema_for(payload: dict) -> dict:
    artifact_type = payload.get("artifact_type")
    overlay = OVERLAY_BY_TYPE.get(artifact_type)
    if overlay is None:
        # Unknown/absent type: fall back to the base so required-field errors
        # (including the artifact_type enum) still surface.
        return json.loads((SCHEMA_DIR / "review-artifact.schema.json").read_text("utf-8"))
    return json.loads((SCHEMA_DIR / overlay).read_text("utf-8"))


def validate_payload(payload: dict) -> list[str]:
    """Return a list of human-readable validation errors (empty == valid)."""
    if not isinstance(payload, dict):
        return ["source root must be a mapping/object"]
    schema = schema_for(payload)
    validator = Draft202012Validator(schema, registry=build_registry())
    errors = sorted(validator.iter_errors(payload), key=lambda e: list(e.path))
    out = []
    for e in errors:
        loc = "/".join(str(p) for p in e.path) or "<root>"
        out.append(f"{loc}: {e.message}")
    return out


# ---------------------------------------------------------------- theme map
def _get(tokens: dict, path: str):
    cur = tokens
    for key in path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def tokens_to_css_vars(tokens: dict) -> str:
    lines = []
    for path, css_var in CSS_VAR_MAP.items():
        value = _get(tokens, path)
        if value is not None:
            lines.append(f"  {css_var}: {value};")
    return ":root {\n" + "\n".join(lines) + "\n}"


def tokens_to_mermaid_vars(tokens: dict) -> dict:
    color = tokens.get("color", {})
    font = tokens.get("font", {})
    return {
        "background": color.get("bg"),
        "primaryColor": color.get("primary_soft"),
        "primaryBorderColor": color.get("primary"),
        "primaryTextColor": color.get("text"),
        "lineColor": color.get("line"),
        "textColor": color.get("text"),
        "fontFamily": font.get("sans"),
    }


def mermaid_init_script(tokens: dict, security_level: str = "strict") -> str:
    config = {
        "startOnLoad": True,
        "theme": "base",
        "securityLevel": security_level,
        "look": "classic",
        "fontFamily": tokens.get("font", {}).get("sans", "Arial, sans-serif"),
        "themeVariables": {k: v for k, v in tokens_to_mermaid_vars(tokens).items() if v},
    }
    # Deterministic key order via sort_keys.
    return (
        "import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';\n"
        f"mermaid.initialize({json.dumps(config, sort_keys=True, indent=2)});"
    )


# ---------------------------------------------------------------- rendering
def build_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "xml", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


def render_html(payload: dict, tokens: dict, template_name: str, *, frozen_svgs: dict | None = None) -> str:
    env = build_env()
    base_css = (ASSET_DIR / "theme.css").read_text(encoding="utf-8")
    print_css = (ASSET_DIR / "print.css").read_text(encoding="utf-8")
    freeze = bool(payload.get("export", {}).get("freeze_diagrams")) or bool(frozen_svgs)
    template = env.get_template(template_name)
    return template.render(
        artifact=payload,
        theme_vars_css=tokens_to_css_vars(tokens),
        base_css=base_css,
        print_css=print_css,
        mermaid_init=mermaid_init_script(tokens),
        frozen=freeze,
        frozen_svgs=frozen_svgs or {},
    )


# ---------------------------------------------------------------- CLI
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render branded review HTML from canonical source.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--schema", required=False, help="(optional) reserved; schema is auto-selected by artifact_type")
    parser.add_argument("--template-dir", default=str(TEMPLATE_DIR))
    parser.add_argument("--template", default="standard.html.j2")
    parser.add_argument("--theme", default=None, help="path to a theme token JSON file")
    parser.add_argument("--frozen-svgs", default=None,
                        help="path to a JSON map {section_id: svg} for frozen archival mode")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    payload = load_source(Path(args.input))
    errors = validate_payload(payload)
    if errors:
        print("Schema validation failed:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 2

    frozen_svgs = {}
    if args.frozen_svgs:
        frozen_svgs = json.loads(Path(args.frozen_svgs).read_text(encoding="utf-8"))

    tokens = load_theme(Path(args.theme) if args.theme else None)
    # template-dir override (rare) — rebuild loader if a custom dir is passed
    if args.template_dir != str(TEMPLATE_DIR):
        env = Environment(
            loader=FileSystemLoader(args.template_dir),
            autoescape=select_autoescape(["html", "xml", "j2"]),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )
        base_css = (ASSET_DIR / "theme.css").read_text(encoding="utf-8")
        print_css = (ASSET_DIR / "print.css").read_text(encoding="utf-8")
        html = env.get_template(args.template).render(
            artifact=payload,
            theme_vars_css=tokens_to_css_vars(tokens),
            base_css=base_css,
            print_css=print_css,
            mermaid_init=mermaid_init_script(tokens),
            frozen=bool(payload.get("export", {}).get("freeze_diagrams")),
            frozen_svgs={},
        )
    else:
        html = render_html(payload, tokens, args.template, frozen_svgs=frozen_svgs)

    Path(args.output).write_text(html, encoding="utf-8")
    print(f"Rendered {args.output} ({len(html)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

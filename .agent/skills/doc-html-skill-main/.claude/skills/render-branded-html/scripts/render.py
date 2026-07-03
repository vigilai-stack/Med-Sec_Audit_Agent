#!/usr/bin/env python3
"""Render branded review HTML from canonical YAML/JSON source.

The model authors content (canonical source); this renderer owns all chrome:
HTML boilerplate, CSS, layout, print styles, and Mermaid bootstrapping. Output
is deterministic — identical input yields byte-identical HTML.

v2 pipeline:
  load_source -> validate_payload (JSON Schema, Draft 2020-12)
  -> resolve skin   (artifact-type default, theme.layout override, --skin flag)
  -> resolve tokens (default theme -> brand theme -> skin overrides)
  -> normalize      (overlay fields -> synthetic widget sections,
                     heatmap grids, figure numbering)
  -> render_html    (Jinja, autoescaped; skin template + shared widget macros)

Theme tokens map to BOTH CSS custom properties and Mermaid themeVariables so
page and diagrams never drift.
"""
from __future__ import annotations

import argparse
import copy
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

SKINS = ("docs-site", "editorial", "brief")

# artifact_type -> overlay schema file
OVERLAY_BY_TYPE = {
    "user-story-review": "user-story-review.schema.json",
    "architecture-review": "architecture-review.schema.json",
    "prd-review": "prd-review.schema.json",
    "risk-analysis": "risk-analysis.schema.json",
    "test-charter": "test-charter.schema.json",
}

# artifact_type -> default skin (theme.layout overrides; --skin overrides both)
SKIN_BY_TYPE = {
    "architecture-review": "docs-site",
    "test-charter": "docs-site",
    "prd-review": "editorial",
    "user-story-review": "editorial",
    "risk-analysis": "brief",
}
DEFAULT_SKIN = "docs-site"

# token group -> CSS custom property prefix; keys flatten with _ -> -
CSS_GROUP_PREFIX = {
    "color": "--color-",
    "font": "--font-",
    "radius": "--radius-",
    "spacing": "--space-",
}


# ---------------------------------------------------------------- source I/O
def load_source(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(text)
    return json.loads(text)


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


# ---------------------------------------------------------------- skin/theme
def resolve_skin(payload: dict, cli_skin: str | None = None) -> str:
    if cli_skin:
        if cli_skin not in SKINS:
            raise ValueError(f"unknown skin {cli_skin!r}; expected one of {SKINS}")
        return cli_skin
    layout = (payload.get("theme") or {}).get("layout")
    if layout:
        return layout
    return SKIN_BY_TYPE.get(payload.get("artifact_type"), DEFAULT_SKIN)


def _deep_merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def resolve_tokens(brand_theme_path: Path | None, skin: str) -> dict:
    """Token resolution order: default theme -> brand theme -> skin overrides."""
    tokens = json.loads((ASSET_DIR / "default-theme.json").read_text(encoding="utf-8"))
    if brand_theme_path:
        tokens = _deep_merge(tokens, json.loads(brand_theme_path.read_text(encoding="utf-8")))
    skin_path = ASSET_DIR / "skins" / f"{skin}.tokens.json"
    if skin_path.exists():
        overrides = json.loads(skin_path.read_text(encoding="utf-8"))
        overrides.pop("comment", None)
        tokens = _deep_merge(tokens, overrides)
    return tokens


def dark_colors(tokens: dict) -> dict:
    """Resolved dark palette: light colors overlaid by the merged `dark` group.

    Missing dark keys fall back to the resolved light value, so partial
    brand/skin dark overrides degrade gracefully.
    """
    return {**(tokens.get("color") or {}), **(tokens.get("dark") or {})}


def _color_var_lines(colors: dict, indent: str = "  ") -> list[str]:
    prefix = CSS_GROUP_PREFIX["color"]
    return [f"{indent}{prefix}{k.replace('_', '-')}: {colors[k]};"
            for k in sorted(colors) if colors[k] is not None]


def tokens_to_css_vars(tokens: dict) -> str:
    """Flatten token groups to CSS custom properties (deterministic order)."""
    lines = []
    for group, prefix in CSS_GROUP_PREFIX.items():
        values = tokens.get(group) or {}
        for key in sorted(values):
            value = values[key]
            if value is None:
                continue
            lines.append(f"  {prefix}{key.replace('_', '-')}: {value};")
    return ":root {\n" + "\n".join(lines) + "\n}"


def theme_vars_css_for_mode(tokens: dict, mode: str) -> str:
    """Mode-aware token emission.

    light: light vars in :root (plus color-scheme hint).
    dark:  light structure vars with the dark color palette in :root.
    auto:  light in :root + dark palette under prefers-color-scheme, scoped
           to :root[data-theme-mode="auto"] so explicit-light docs are immune.
    Widget/skin CSS never changes per mode — only custom-property values swap.
    """
    light = tokens_to_css_vars(tokens)
    if mode == "light":
        return light.replace(":root {\n", ":root {\n  color-scheme: light;\n", 1)
    dark_block = "\n".join(_color_var_lines(dark_colors(tokens)))
    if mode == "dark":
        non_color = {g: v for g, v in tokens.items() if g in CSS_GROUP_PREFIX and g != "color"}
        structure = tokens_to_css_vars(non_color)
        return structure.replace(
            ":root {\n", ":root {\n  color-scheme: dark;\n" + dark_block + "\n", 1)
    # auto
    light = light.replace(":root {\n", ":root {\n  color-scheme: light dark;\n", 1)
    return (
        light
        + "\n@media (prefers-color-scheme: dark) {\n"
        + ':root[data-theme-mode="auto"] {\n'
        + "  color-scheme: dark;\n"
        + "\n".join(_color_var_lines(dark_colors(tokens)))
        + "\n}\n}"
    )


def tokens_to_mermaid_vars(tokens: dict, palette: str = "light") -> dict:
    color = dark_colors(tokens) if palette == "dark" else tokens.get("color", {})
    font = tokens.get("font", {})
    return {
        "background": color.get("surface"),
        "primaryColor": color.get("primary_soft"),
        "primaryBorderColor": color.get("primary"),
        "primaryTextColor": color.get("text"),
        "secondaryColor": color.get("neutral_soft"),
        "tertiaryColor": color.get("bg"),
        "lineColor": color.get("line_strong"),
        "textColor": color.get("text"),
        "noteBkgColor": color.get("warning_soft"),
        "noteTextColor": color.get("text"),
        "fontFamily": font.get("sans"),
        "fontSize": "16px",
    }


def mermaid_config(tokens: dict, security_level: str = "strict", palette: str = "light") -> dict:
    return {
        "startOnLoad": True,
        "theme": "base",
        "securityLevel": security_level,
        "look": "classic",
        "fontFamily": tokens.get("font", {}).get("sans", "Arial, sans-serif"),
        "themeVariables": {k: v for k, v in tokens_to_mermaid_vars(tokens, palette).items() if v},
    }


def mermaid_init_script(tokens: dict, mode: str = "light", security_level: str = "strict") -> str:
    """Interactive init. Embeds BOTH palettes (sorted keys — deterministic);
    the palette branch happens client-side: dark for mode=dark, and for auto
    the one matching prefers-color-scheme at load time (reload follows an OS
    switch; no live re-render — documented limitation)."""
    config = mermaid_config(tokens, security_level)
    light_vars = config.pop("themeVariables")
    dark_vars = {k: v for k, v in tokens_to_mermaid_vars(tokens, "dark").items() if v}
    return (
        "import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';\n"
        f"const lightVars = {json.dumps(light_vars, sort_keys=True, indent=2)};\n"
        f"const darkVars = {json.dumps(dark_vars, sort_keys=True, indent=2)};\n"
        f"const mode = {json.dumps(mode)};\n"
        "const useDark = mode === 'dark' || (mode === 'auto' && matchMedia('(prefers-color-scheme: dark)').matches);\n"
        f"const config = {json.dumps(config, sort_keys=True, indent=2)};\n"
        "config.themeVariables = useDark ? darkVars : lightVars;\n"
        "mermaid.initialize(config);"
    )


# ---------------------------------------------------------------- normalize
def _severity_item(entry) -> dict:
    if isinstance(entry, str):
        return {"text": entry, "severity": "info"}
    return {"text": entry.get("text", ""), "severity": entry.get("severity", "info")}


def overlay_sections(payload: dict) -> list[dict]:
    """Map overlay fields to synthetic widget sections (deterministic order).

    Internal-only kinds used here (not part of the authored schema):
    `list`, `checklist`, `severitylist`.
    """
    t = payload.get("artifact_type")
    out: list[dict] = []

    def add(kind: str, sid: str, title: str, *, width: str = "full", **extra):
        out.append({"id": sid, "title": title, "kind": kind, "width": width,
                    "generated": True, **extra})

    if t == "architecture-review":
        if payload.get("decisions"):
            add("cards", "overlay-decisions", "Key decisions", variant="decision", items=[
                {"title": d.get("title", ""), "body": d.get("rationale", ""),
                 "tag": d.get("status", ""), "ref": d.get("ref", "")}
                for d in payload["decisions"]])
        if payload.get("constraints"):
            add("severitylist", "overlay-constraints", "Constraints", width="half",
                items=[_severity_item(c) for c in payload["constraints"]])
        if payload.get("interfaces"):
            add("list", "overlay-interfaces", "Interfaces", width="half",
                items=list(payload["interfaces"]))
        if payload.get("deployment_context"):
            add("callout", "overlay-deployment", "Deployment context",
                intent="note", body=payload["deployment_context"])
        if payload.get("alternatives"):
            add("cards", "overlay-alternatives", "Alternatives considered", variant="rejected",
                items=[{"title": a.split(" — ")[0] if " — " in a else "Rejected", "body": a}
                       for a in payload["alternatives"]])

    elif t == "user-story-review":
        story = [(k, payload.get(k)) for k in ("as_a", "i_want", "so_that")]
        if any(v for _, v in story):
            add("keyvalue", "overlay-story", "Story", width="half", items=[
                {"key": k.replace("_", " ").capitalize(), "value": v}
                for k, v in story if v])
        if payload.get("acceptance_criteria"):
            add("checklist", "overlay-acceptance", "Acceptance criteria",
                items=list(payload["acceptance_criteria"]))
        if payload.get("personas"):
            add("cards", "overlay-personas", "Personas", variant="persona",
                items=[{"title": p.split(" — ")[0] if " — " in p else p,
                        "body": p.split(" — ", 1)[1] if " — " in p else ""}
                       for p in payload["personas"]])
        if payload.get("journey_states"):
            add("timeline", "overlay-journey", "Journey states",
                items=[{"label": s, "body": ""} for s in payload["journey_states"]])
        if payload.get("dependencies"):
            add("list", "overlay-dependencies", "Dependencies", width="half",
                items=list(payload["dependencies"]))

    elif t == "prd-review":
        if payload.get("business_goals"):
            add("checklist", "overlay-goals", "Business goals",
                items=list(payload["business_goals"]))
        if payload.get("out_of_scope"):
            add("list", "overlay-out-of-scope", "Out of scope", width="half",
                items=list(payload["out_of_scope"]))
        if payload.get("stakeholders"):
            add("list", "overlay-stakeholders", "Stakeholders", width="half",
                items=list(payload["stakeholders"]))
        if payload.get("requirement_coverage"):
            add("table", "overlay-coverage", "Requirement coverage",
                columns=["Requirement", "Covered", "Notes"],
                rows=[[r.get("requirement", ""),
                       "✓" if r.get("covered") else "✗",
                       r.get("notes", "")] for r in payload["requirement_coverage"]])

    elif t == "risk-analysis":
        if payload.get("triggers"):
            add("list", "overlay-triggers", "Triggers", width="half",
                items=list(payload["triggers"]))
        if payload.get("controls"):
            add("checklist", "overlay-controls", "Controls", width="half",
                items=list(payload["controls"]))
        meta = [("Residual risk", payload.get("residual_risk")),
                ("Owners", ", ".join(payload.get("owners") or []) or None),
                ("Review cadence", payload.get("review_cadence"))]
        meta = [(k, v) for k, v in meta if v]
        if meta:
            add("keyvalue", "overlay-risk-meta", "Risk posture", width="half",
                items=[{"key": k, "value": v} for k, v in meta])

    elif t == "test-charter":
        if payload.get("missions"):
            add("steps", "overlay-missions", "Missions",
                items=[{"title": m.split(" — ")[0] if " — " in m else m,
                        "body": m.split(" — ", 1)[1] if " — " in m else ""}
                       for m in payload["missions"]])
        if payload.get("heuristics"):
            add("list", "overlay-heuristics", "Heuristics", width="half",
                items=list(payload["heuristics"]))
        if payload.get("coverage_boundaries"):
            add("list", "overlay-boundaries", "Coverage boundaries", width="half",
                items=list(payload["coverage_boundaries"]))
        if payload.get("exit_criteria"):
            add("checklist", "overlay-exit", "Exit criteria",
                items=list(payload["exit_criteria"]))

    return out


def enrich_heatmap(section: dict) -> dict:
    """Precompute the row-major grid so templates stay logic-light."""
    lookup = {(c["x"], c["y"]): c for c in section.get("cells", [])}
    grid = []
    for y in range(len(section.get("y_labels", []))):
        row = [lookup.get((x, y)) for x in range(len(section.get("x_labels", [])))]
        grid.append(row)
    out = dict(section)
    out["grid"] = grid
    return out


def normalize_sections(payload: dict) -> list[dict]:
    """Overlay sections first (fixed position), then authored sections.

    Adds deterministic figure numbers to mermaid sections and heatmap grids.
    """
    sections = overlay_sections(payload)
    for s in payload.get("sections") or []:
        sections.append(dict(s))
    fig_no = 0
    final = []
    for s in sections:
        if s.get("kind") == "mermaid":
            fig_no += 1
            s = dict(s)
            s["fig_no"] = fig_no
        elif s.get("kind") == "heatmap":
            s = enrich_heatmap(s)
        final.append(s)
    return final


# ---------------------------------------------------------------- rendering
def build_env(template_dir: str | None = None) -> Environment:
    return Environment(
        loader=FileSystemLoader(template_dir or str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "xml", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


def resolve_mode(payload: dict, *, frozen: bool = False) -> str:
    """theme.mode with the frozen-auto rule: frozen `auto` pins to light so
    baked SVGs and the page palette can never mismatch."""
    mode = (payload.get("theme") or {}).get("mode") or "light"
    if frozen and mode == "auto":
        return "light"
    return mode


def render_html(payload: dict, tokens: dict, skin: str, *,
                frozen_svgs: dict | None = None,
                template_dir: str | None = None) -> str:
    env = build_env(template_dir)
    base_css = (ASSET_DIR / "theme.css").read_text(encoding="utf-8")
    skin_css = (ASSET_DIR / "skins" / f"{skin}.css").read_text(encoding="utf-8")
    print_css = (ASSET_DIR / "print.css").read_text(encoding="utf-8")
    enhance_js = (ASSET_DIR / "enhance.js").read_text(encoding="utf-8")
    freeze = bool(payload.get("export", {}).get("freeze_diagrams")) or bool(frozen_svgs)
    mode = resolve_mode(payload, frozen=freeze)
    # Print is light under EVERY mode: prepend the resolved light palette so
    # dark documents print readable on white (print.css then forces white
    # surfaces on top).
    print_light_vars = ":root {\n  color-scheme: light;\n" + \
        "\n".join(_color_var_lines(tokens.get("color") or {})) + "\n}"
    sections = normalize_sections(payload)
    template = env.get_template(f"skins/{skin}.html.j2")
    return template.render(
        artifact=payload,
        sections=sections,
        skin=skin,
        mode=mode,
        theme_vars_css=theme_vars_css_for_mode(tokens, mode),
        base_css=base_css,
        skin_css=skin_css,
        print_css=print_light_vars + "\n" + print_css,
        enhance_js=enhance_js,
        mermaid_init=mermaid_init_script(tokens, mode),
        frozen=freeze,
        frozen_svgs=frozen_svgs or {},
    )


# ---------------------------------------------------------------- CLI
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render branded review HTML from canonical source.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--schema", required=False, help="(optional) reserved; schema is auto-selected by artifact_type")
    parser.add_argument("--template-dir", default=None, help="override template directory (must contain skins/)")
    parser.add_argument("--skin", default=None, choices=SKINS,
                        help="force a skin (overrides theme.layout and the artifact-type default)")
    parser.add_argument("--theme", default=None, help="path to a brand theme token JSON file")
    parser.add_argument("--frozen-svgs", default=None,
                        help="path to a JSON map {section_id: svg} for frozen archival mode")
    parser.add_argument("--print-mermaid-config", action="store_true",
                        help="print the resolved Mermaid config JSON (for mmdc --configFile) and exit")
    parser.add_argument("--output", required=False)
    args = parser.parse_args(argv)

    payload = load_source(Path(args.input))
    errors = validate_payload(payload)
    if errors:
        print("Schema validation failed:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 2

    skin = resolve_skin(payload, args.skin)
    tokens = resolve_tokens(Path(args.theme) if args.theme else None, skin)

    if args.print_mermaid_config:
        # Frozen resolution: dark only for an explicit mode of dark; light and
        # auto freeze with the light palette (frozen auto pins light).
        palette = "dark" if resolve_mode(payload, frozen=True) == "dark" else "light"
        cfg = mermaid_config(tokens, palette=palette)
        cfg.pop("startOnLoad", None)  # not meaningful for mmdc
        print(json.dumps(cfg, sort_keys=True, indent=2))
        return 0

    if not args.output:
        print("error: --output is required unless --print-mermaid-config is used", file=sys.stderr)
        return 2

    frozen_svgs = {}
    if args.frozen_svgs:
        frozen_svgs = json.loads(Path(args.frozen_svgs).read_text(encoding="utf-8"))

    html = render_html(payload, tokens, skin, frozen_svgs=frozen_svgs,
                       template_dir=args.template_dir)
    Path(args.output).write_text(html, encoding="utf-8")
    print(f"Rendered {args.output} ({len(html)} bytes, skin={skin})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

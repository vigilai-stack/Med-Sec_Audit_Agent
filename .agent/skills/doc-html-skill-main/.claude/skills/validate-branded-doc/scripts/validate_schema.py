#!/usr/bin/env python3
"""validate_schema.py — layer 1 of the validator.

Validates canonical source (YAML/JSON) against the base + artifact-overlay
JSON Schema (Draft 2020-12). This layer runs FIRST in the pipeline; a schema
failure short-circuits the downstream Mermaid/a11y/responsive/export checks.

Exit codes: 0 valid, 2 invalid, 3 usage/IO error.
Prints a JSON report ({"check":"schema","passed":bool,"errors":[...]}) when
--json is given, otherwise a human summary.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

# schemas live in the renderer skill
SCHEMA_DIR = (
    Path(__file__).resolve().parents[2] / "render-branded-html" / "schemas"
)

OVERLAY_BY_TYPE = {
    "user-story-review": "user-story-review.schema.json",
    "architecture-review": "architecture-review.schema.json",
    "prd-review": "prd-review.schema.json",
    "risk-analysis": "risk-analysis.schema.json",
    "test-charter": "test-charter.schema.json",
}


def load_source(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(text)
    return json.loads(text)


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
    overlay = OVERLAY_BY_TYPE.get(payload.get("artifact_type"))
    name = overlay or "review-artifact.schema.json"
    return json.loads((SCHEMA_DIR / name).read_text("utf-8"))


def validate(payload) -> list[str]:
    if not isinstance(payload, dict):
        return ["source root must be a mapping/object"]
    validator = Draft202012Validator(schema_for(payload), registry=build_registry())
    out = []
    for e in sorted(validator.iter_errors(payload), key=lambda e: list(e.path)):
        loc = "/".join(str(p) for p in e.path) or "<root>"
        out.append(f"{loc}: {e.message}")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate canonical source against JSON Schema.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--json", action="store_true", help="emit a JSON report")
    args = parser.parse_args(argv)

    path = Path(args.input)
    if not path.exists():
        print(f"error: input not found: {path}", file=sys.stderr)
        return 3

    errors = validate(load_source(path))
    passed = not errors
    if args.json:
        print(json.dumps({"check": "schema", "passed": passed, "errors": errors}))
    else:
        if passed:
            print("schema: PASS")
        else:
            print("schema: FAIL")
            for e in errors:
                print(f"  - {e}")
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())

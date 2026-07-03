"""Console entry points wrapping the bundled skill scripts.

The scripts resolve every path relative to their own location
(``SKILL_ROOT = Path(__file__).parents[1]``), and the wheel preserves the
skill-tree layout, so executing them in place needs no patching.
"""

from __future__ import annotations

import runpy
import sys

from . import SKILLS_DIR


def _run(relative: str) -> None:
    script = SKILLS_DIR / relative
    if not script.exists():  # broken install
        raise SystemExit(f"error: bundled script missing: {script}")
    sys.argv[0] = str(script)
    runpy.run_path(str(script), run_name="__main__")


def render() -> None:
    _run("render-branded-html/scripts/render.py")


def validate() -> None:
    _run("validate-branded-doc/scripts/validate_all.py")


def export_pdf() -> None:
    _run("render-branded-html/scripts/export_pdf.py")

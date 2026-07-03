#!/usr/bin/env python3
"""export_pdf.py — produce a PDF from a rendered branded HTML file.

Uses Playwright's headless-Chromium print path, which honors print CSS by
default (page.pdf() uses print media). Pair with freeze_mermaid.sh so diagrams
are inlined SVG before export — client-side Mermaid will not have run in the
headless print context otherwise.

Usage: export_pdf.py --input doc.html --output doc.pdf
Requires: playwright (pip install playwright && playwright install chromium).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def export_pdf(html_path: Path, pdf_path: Path) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:  # pragma: no cover - environment dependent
        print(
            "error: playwright not installed. Run:\n"
            "  pip install playwright && playwright install chromium",
            file=sys.stderr,
        )
        raise SystemExit(3)

    url = html_path.resolve().as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        # Print completeness: expand collapsibles and leave any fullscreen
        # diagram mode so no widget content is hidden in the PDF (belt and
        # braces alongside enhance.js's beforeprint handler + print.css).
        page.evaluate(
            "() => { document.querySelectorAll('details').forEach(d => d.open = true);"
            " document.querySelectorAll('.fig-zoom-toggle:checked').forEach(t => t.checked = false); }"
        )
        # Explicit print media so @media print / print.css rules apply.
        page.emulate_media(media="print")
        page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            margin={"top": "18mm", "bottom": "18mm", "left": "16mm", "right": "16mm"},
        )
        browser.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export branded HTML to PDF via headless print.")
    parser.add_argument("--input", required=True, help="rendered HTML file")
    parser.add_argument("--output", required=True, help="output PDF path")
    args = parser.parse_args(argv)

    html_path = Path(args.input)
    if not html_path.exists():
        print(f"error: input not found: {html_path}", file=sys.stderr)
        return 2
    export_pdf(html_path, Path(args.output))
    print(f"PDF written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

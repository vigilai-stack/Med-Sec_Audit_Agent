#!/usr/bin/env node
/*
 * validate_export.mjs — layer 5 of the validator.
 *
 * Exports the rendered HTML to PDF via the headless print path and checks the
 * result is usable: a non-trivial PDF with more than zero pages. Diagrams
 * should be frozen (inline SVG) before this step so they appear in print.
 *
 * Usage: node validate_export.mjs --input <doc.html> [--json]
 * Requires: playwright. Exit: 0 pass, 2 fail, 3 missing deps.
 */
import { existsSync, mkdtempSync, statSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

function parseArgs(argv) {
  const args = { json: false };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--input") args.input = argv[++i];
    else if (argv[i] === "--json") args.json = true;
  }
  return args;
}

function pdfPageCount(buf) {
  // Count "/Type /Page" objects — a cheap, dependency-free page estimate.
  const text = buf.toString("latin1");
  const matches = text.match(/\/Type\s*\/Page[^s]/g);
  return matches ? matches.length : 0;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!args.input || !existsSync(args.input)) {
    console.error("error: --input <doc.html> required and must exist");
    process.exit(3);
  }

  let chromium;
  try {
    ({ chromium } = await import("playwright"));
  } catch {
    console.error("error: requires playwright.\n  npm i -D playwright && npx playwright install chromium");
    process.exit(3);
  }

  const dir = mkdtempSync(join(tmpdir(), "pdf-"));
  const pdfPath = join(dir, "out.pdf");
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(pathToFileURL(args.input).href, { waitUntil: "networkidle" });
  // Mirror export_pdf.py's print preparation (expand details, exit fullscreen).
  await page.evaluate(() => {
    document.querySelectorAll("details").forEach((d) => (d.open = true));
    document.querySelectorAll(".fig-zoom-toggle:checked").forEach((t) => (t.checked = false));
  });
  await page.emulateMedia({ media: "print" });

  // Print completeness: no widget content may be hidden on paper.
  const printErrors = await page.evaluate(() => {
    const errs = [];
    const visible = (el) => {
      const cs = getComputedStyle(el);
      return cs.display !== "none" && cs.visibility !== "hidden";
    };
    document.querySelectorAll(".tab-pane").forEach((p2, i) => {
      if (!visible(p2)) errs.push(`tab pane ${i} ("${p2.dataset.label}") hidden in print`);
    });
    document.querySelectorAll(".details-body").forEach((b, i) => {
      if (!visible(b)) errs.push(`details body ${i} hidden in print`);
    });
    document.querySelectorAll(".fig-zoom-btn, .copy-btn, .toc, .topbar").forEach((el) => {
      if (visible(el)) errs.push(`screen-only control ${el.className} visible in print`);
    });
    return errs;
  });

  await page.pdf({
    path: pdfPath,
    format: "A4",
    printBackground: true,
    margin: { top: "18mm", bottom: "18mm", left: "16mm", right: "16mm" },
  });
  await browser.close();

  const errors = [...printErrors];
  const size = statSync(pdfPath).size;
  if (size < 1024) errors.push(`PDF suspiciously small (${size} bytes)`);
  const pages = pdfPageCount(readFileSync(pdfPath));
  if (pages < 1) errors.push("PDF reports zero pages");

  const passed = errors.length === 0;
  if (args.json) {
    console.log(JSON.stringify({ check: "export", passed, bytes: size, pages, errors }));
  } else {
    console.log(passed ? `export: PASS (${pages} page(s), ${size} bytes)` : "export: FAIL");
    errors.forEach((e) => console.log(`  - ${e}`));
  }
  process.exit(passed ? 0 : 2);
}

main();

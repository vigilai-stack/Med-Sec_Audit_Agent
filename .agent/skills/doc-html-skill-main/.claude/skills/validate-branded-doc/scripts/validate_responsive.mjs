#!/usr/bin/env node
/*
 * validate_responsive.mjs — layer 4 of the validator.
 *
 * Renders the HTML at a desktop and a mobile viewport and fails when content
 * is clipped or produces uncontrolled horizontal overflow (scrollWidth beyond
 * the viewport by more than a small tolerance).
 *
 * Usage: node validate_responsive.mjs --input <doc.html> [--json]
 * Requires: playwright. Exit: 0 pass, 2 fail, 3 missing deps.
 */
import { existsSync } from "node:fs";
import { pathToFileURL } from "node:url";

const VIEWPORTS = [
  { name: "desktop", width: 1280, height: 900 },
  { name: "mobile", width: 375, height: 812 },
];
const TOLERANCE = 2; // px

function parseArgs(argv) {
  const args = { json: false };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--input") args.input = argv[++i];
    else if (argv[i] === "--json") args.json = true;
  }
  return args;
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

  const browser = await chromium.launch();
  const errors = [];
  const url = pathToFileURL(args.input).href;

  for (const vp of VIEWPORTS) {
    const page = await browser.newPage({ viewport: { width: vp.width, height: vp.height } });
    await page.goto(url, { waitUntil: "networkidle" });
    const overflow = await page.evaluate(() => {
      const de = document.documentElement;
      return { scrollWidth: de.scrollWidth, clientWidth: de.clientWidth };
    });
    if (overflow.scrollWidth - overflow.clientWidth > TOLERANCE) {
      errors.push(`${vp.name} (${vp.width}px): horizontal overflow ` +
        `(scrollWidth ${overflow.scrollWidth} > clientWidth ${overflow.clientWidth})`);
    }
    await page.close();
  }
  await browser.close();

  const passed = errors.length === 0;
  if (args.json) {
    console.log(JSON.stringify({ check: "responsive", passed, errors }));
  } else {
    console.log(passed ? "responsive: PASS (no overflow at desktop/mobile)" : "responsive: FAIL");
    errors.forEach((e) => console.log(`  - ${e}`));
  }
  process.exit(passed ? 0 : 2);
}

main();

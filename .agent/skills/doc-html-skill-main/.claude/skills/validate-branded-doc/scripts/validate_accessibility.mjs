#!/usr/bin/env node
/*
 * validate_accessibility.mjs — layer 3 of the validator.
 *
 * Loads rendered HTML in headless Chromium, runs axe-core, and fails on any
 * critical violation. Also enforces WCAG AA contrast thresholds (4.5:1 normal
 * text, 3:1 large text) via axe's color-contrast rule.
 *
 * Usage: node validate_accessibility.mjs --input <doc.html> [--json]
 * Requires: playwright + @axe-core/playwright (or axe-core).
 * Exit: 0 pass, 2 fail, 3 missing deps.
 */
import { existsSync } from "node:fs";
import { pathToFileURL } from "node:url";

function parseArgs(argv) {
  const args = { json: false, colorScheme: "light" };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--input") args.input = argv[++i];
    else if (argv[i] === "--color-scheme") args.colorScheme = argv[++i];
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

  let chromium, AxeBuilder;
  try {
    ({ chromium } = await import("playwright"));
    ({ default: AxeBuilder } = await import("@axe-core/playwright"));
  } catch {
    console.error("error: requires playwright and @axe-core/playwright.\n" +
      "  npm i -D playwright @axe-core/playwright && npx playwright install chromium");
    process.exit(3);
  }

  const browser = await chromium.launch();
  // @axe-core/playwright requires a page created from a browser context.
  // colorScheme emulates prefers-color-scheme so dark/auto documents are
  // validated under their dark palette too.
  const context = await browser.newContext({ colorScheme: args.colorScheme });
  const page = await context.newPage();
  await page.goto(pathToFileURL(args.input).href, { waitUntil: "networkidle" });

  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
    .analyze();

  // Widget checks: tabs must be keyboard-operable (focusable radios with
  // label[for] association) and fig-zoom toggles must carry accessible names.
  const widgetErrors = await page.evaluate(() => {
    const errs = [];
    document.querySelectorAll(".tabs").forEach((tabs, i) => {
      const radios = tabs.querySelectorAll(":scope > input.tab-radio");
      const labels = tabs.querySelectorAll(".tab-bar label");
      if (radios.length !== labels.length)
        errs.push(`tabs[${i}]: ${radios.length} radios vs ${labels.length} labels`);
      radios.forEach((r) => {
        if (r.tabIndex < -1 || r.disabled) errs.push(`tabs[${i}]: radio not focusable`);
        if (!tabs.querySelector(`label[for="${r.id}"]`))
          errs.push(`tabs[${i}]: radio #${r.id} has no associated label`);
      });
    });
    document.querySelectorAll(".fig-zoom-toggle").forEach((t) => {
      if (!t.getAttribute("aria-label")) errs.push(`fig-zoom toggle #${t.id} missing aria-label`);
    });
    return errs;
  });
  await browser.close();

  const critical = results.violations.filter((v) => v.impact === "critical");
  const contrast = results.violations.filter((v) => v.id === "color-contrast");
  const errors = [
    ...critical.map((v) => `critical: ${v.id} — ${v.help}`),
    ...contrast.map((v) => `contrast: ${v.nodes.length} node(s) below WCAG AA`),
    ...widgetErrors.map((e) => `widget: ${e}`),
  ];

  const passed = errors.length === 0;
  if (args.json) {
    console.log(JSON.stringify({ check: "accessibility", passed,
      colorScheme: args.colorScheme, violations: results.violations.length, errors }));
  } else {
    console.log(passed ? "accessibility: PASS (no critical / contrast issues)" : "accessibility: FAIL");
    errors.forEach((e) => console.log(`  - ${e}`));
  }
  process.exit(passed ? 0 : 2);
}

main();

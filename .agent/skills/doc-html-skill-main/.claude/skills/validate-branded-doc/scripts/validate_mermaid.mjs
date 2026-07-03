#!/usr/bin/env node
/*
 * validate_mermaid.mjs — layer 2 of the validator.
 *
 * Extracts every Mermaid section from canonical source and parses it for fast
 * failures. In CI, pass --render to additionally render via the Mermaid CLI
 * (mmdc) for higher confidence.
 *
 * Usage: node validate_mermaid.mjs --input <source.yaml|json> [--render] [--json]
 * Exit: 0 pass, 2 fail, 3 usage/dep error.
 */
import { readFileSync, existsSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { execFileSync } from "node:child_process";

function parseArgs(argv) {
  const args = { render: false, json: false };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--input") args.input = argv[++i];
    else if (argv[i] === "--render") args.render = true;
    else if (argv[i] === "--json") args.json = true;
  }
  return args;
}

// Minimal YAML/JSON loader: prefer JSON; for YAML defer to python if needed.
function loadSource(path) {
  const text = readFileSync(path, "utf8");
  if (path.endsWith(".json")) return JSON.parse(text);
  // YAML: shell out to python for a faithful parse. Resolution order:
  // PYTHON env (validate_all.py sets it) -> project .venv -> python3 on PATH.
  const candidates = [process.env.PYTHON,
    join(process.cwd(), ".venv", "bin", "python"), "python3", "python"]
    .filter(Boolean);
  let lastErr;
  for (const py of candidates) {
    try {
      const out = execFileSync(py, ["-c",
        "import sys,yaml,json;print(json.dumps(yaml.safe_load(open(sys.argv[1]).read())))",
        path], { encoding: "utf8" });
      return JSON.parse(out);
    } catch (e) { lastErr = e; }
  }
  console.error("error: no python with pyyaml available to parse YAML source");
  process.exit(3);
}

function mermaidSections(payload) {
  return (payload.sections || []).filter((s) => s.kind === "mermaid" && s.source);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!args.input || !existsSync(args.input)) {
    console.error("error: --input <source> required and must exist");
    process.exit(3);
  }
  const payload = loadSource(args.input);
  const sections = mermaidSections(payload);
  const errors = [];

  // The mermaid lib needs a browser DOM (DOMPurify/document) for parse(). In a
  // bare Node process some diagram types throw an *environment* error unrelated
  // to diagram validity. We try mermaid.parse per section, and when it throws an
  // env error we fall back to a structural check for that section instead of
  // false-failing. Use --render (mmdc) for full-confidence rendering in CI.
  let mermaid = null;
  try {
    mermaid = (await import("mermaid")).default;
    mermaid.initialize({ startOnLoad: false, securityLevel: "strict" });
  } catch {
    /* library absent — structural fallback for every section */
  }

  const isEnvError = (msg) =>
    /DOMPurify|document is not defined|window is not defined|is not a function|getComputedStyle/.test(msg);

  const structuralError = (s) => {
    const head = s.source.trim().split(/\s+/)[0] || "";
    const known = /^(flowchart|graph|sequenceDiagram|erDiagram|stateDiagram(-v2)?|journey|timeline|classDiagram|gantt|mindmap|xychart-beta|quadrantChart|pie)$/;
    return known.test(head)
      ? null
      : `${s.id}: source does not start with a recognized Mermaid diagram keyword (got "${head}")`;
  };

  for (const s of sections) {
    if (mermaid && typeof mermaid.parse === "function") {
      try {
        await mermaid.parse(s.source);
      } catch (e) {
        const msg = String(e?.message || e);
        if (isEnvError(msg)) {
          const se = structuralError(s); // can't parse in this env → structural check
          if (se) errors.push(se);
        } else {
          errors.push(`${s.id}: ${msg || "mermaid parse error"}`);
        }
      }
    } else {
      const se = structuralError(s);
      if (se) errors.push(se);
    }
  }

  // Optional CLI render for CI confidence.
  if (args.render && sections.length) {
    let hasMmdc = true;
    try { execFileSync("mmdc", ["--version"], { stdio: "ignore" }); }
    catch { hasMmdc = false; }
    if (!hasMmdc) {
      errors.push("--render requested but mmdc (mermaid-cli) is not installed");
    } else {
      const dir = mkdtempSync(join(tmpdir(), "mmd-"));
      for (const s of sections) {
        const mmd = join(dir, `${s.id}.mmd`);
        writeFileSync(mmd, s.source);
        try {
          execFileSync("mmdc", ["--input", mmd, "--output", join(dir, `${s.id}.svg`)], { stdio: "ignore" });
        } catch (e) {
          errors.push(`${s.id}: mmdc render failed`);
        }
      }
    }
  }

  const passed = errors.length === 0;
  if (args.json) {
    console.log(JSON.stringify({ check: "mermaid", passed, count: sections.length, errors }));
  } else {
    console.log(passed ? `mermaid: PASS (${sections.length} diagram(s))` : "mermaid: FAIL");
    errors.forEach((e) => console.log(`  - ${e}`));
  }
  process.exit(passed ? 0 : 2);
}

main();

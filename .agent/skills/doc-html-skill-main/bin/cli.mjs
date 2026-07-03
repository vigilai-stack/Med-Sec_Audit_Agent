#!/usr/bin/env node
/*
 * doc-html-skill CLI — dependency-free installer for the skill suite.
 *
 *   npx doc-html-skill install [target-dir] [--force]
 *     Copy the bundled skill directories into <target>/.claude/skills/.
 *     Refuses to overwrite existing skill dirs unless --force is given.
 *
 *   npx doc-html-skill list
 *     Show the bundled skills and their one-line descriptions.
 */
import { cpSync, existsSync, mkdirSync, readdirSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PKG_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const SKILLS_SRC = join(PKG_ROOT, ".claude", "skills");

function skillDirs() {
  return readdirSync(SKILLS_SRC, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .map((d) => d.name)
    .sort();
}

function description(skill) {
  try {
    const text = readFileSync(join(SKILLS_SRC, skill, "SKILL.md"), "utf8");
    const m = text.match(/^description:\s*(.+)$/m);
    return m ? m[1].split(". ")[0] + "." : "";
  } catch {
    return "";
  }
}

function list() {
  console.log("Bundled skills:\n");
  for (const s of skillDirs()) console.log(`  ${s.padEnd(28)} ${description(s)}`);
}

function install(args) {
  const force = args.includes("--force");
  const target = resolve(args.find((a) => !a.startsWith("--")) || ".");
  const dest = join(target, ".claude", "skills");
  mkdirSync(dest, { recursive: true });

  const skipped = [];
  const installed = [];
  for (const s of skillDirs()) {
    const to = join(dest, s);
    if (existsSync(to) && !force) {
      skipped.push(s);
      continue;
    }
    cpSync(join(SKILLS_SRC, s), to, { recursive: true });
    installed.push(s);
  }
  installed.forEach((s) => console.log(`  installed ${s}`));
  skipped.forEach((s) => console.log(`  skipped   ${s} (exists — use --force to overwrite)`));
  console.log(`\n${installed.length} skill(s) installed to ${dest}`);
  if (skipped.length) process.exitCode = 1;
}

const [cmd, ...rest] = process.argv.slice(2);
if (cmd === "install") install(rest);
else if (cmd === "list") list();
else {
  console.log("Usage: doc-html-skill <install [dir] [--force] | list>");
  process.exitCode = cmd ? 1 : 0;
}

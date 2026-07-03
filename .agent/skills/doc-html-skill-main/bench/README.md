# Benchmark: skill-based vs. pure HTML generation

Measures the cost of generating branded HTML documentation **with** the
schema-first skill (author compact YAML → deterministic renderer) vs **without**
it (the model writes the whole HTML/CSS/diagrams directly), across four agent
CLIs.

## Design

- **Fixed content** (`brief.md`): a self-contained fictional system ("PaySwift").
  Facts are given in the prompt so there is **zero research variance** — we
  isolate the *generation method*, not retrieval effort.
- **Same target** for both conditions: a branded HTML doc with ≥3 Mermaid
  diagrams and ≥2 tables (`prompts/noskill.md`, `prompts/skill.md`).
- **Two conditions per tool**:
  - `noskill` — clean workdir, model writes `doc.html` directly.
  - `skill` — workdir seeded with the portable `skillkit/` (schemas, `render.py`,
    templates, theme, a `render` wrapper). Model authors `doc.yaml` and runs
    `./render`.
- **Isolation**: each run gets a fresh `runs/<tool>-<cond>-<rep>/` workdir.
  Claude still loads global `~/.claude/CLAUDE.md` (constant across conditions).

## Tools & metric sources (confirmed during recon)

| Tool | Model (default here) | Headless invocation | Metrics source |
|---|---|---|---|
| claude | claude-opus-4-8[1m] | `claude -p … --output-format json --dangerously-skip-permissions` | inline JSON `usage`/`total_cost_usd`/`duration_ms` |
| codex | codex-gpt | `codex exec --json … </dev/null` | JSONL `turn.completed.usage` |
| opencode | qwen/qwen3.7-max | `opencode run --dangerously-skip-permissions … </dev/null` | `opencode export <id>` → per-msg `tokens`/`cost` |
| kilo | MiniMax-M2.7 | `kilo run --auto … </dev/null` | `kilo export <id>` |

## Reproduce

```bash
bash run_one.sh <tool> <noskill|skill> [rep]   # one cell
python3 extract.py     # raw outputs -> results/metrics.{json,csv}
python3 quality.py     # validate each doc.html -> results/quality.json
python3 analyze.py     # -> results/REPORT.md
```

## Headline findings (see `results/REPORT.md`)

N=1 per cell — **directional**, but the three clean tools are three independent
replications of the same direction.

1. **Skills cut model OUTPUT tokens ~28–32%** (claude −28%, kilo −32%, opencode
   −31%). The model authors compact YAML instead of full HTML. ✅ confirms the
   core hypothesis about authoring effort.
2. **For a single doc, skills cost MORE overall**: total tokens +277–370%, cost
   +23–82%. The agent must read the JSON schemas and iterate the renderer, and
   that overhead isn't amortized over one document. ❌ refutes the naive
   "skills always save tokens."
3. **Quality flips the verdict**: every `noskill` doc **fails WCAG AA**; every
   `skill` doc **passes** a11y + responsive. Skill output is accessible,
   responsive, schema-valid, and deterministic by construction.
4. **Smaller models churn more** to drive the skill (opencode 17 tool-calls,
   kilo 8, vs 1 in noskill). Codex burned 235K input tokens reading schemas.
5. **Skills yield a reusable artifact**: a 5–8 KB diffable `doc.yaml`, not just HTML.

**When the skill pays off:** repeated/incremental generation (re-emit only
changed YAML sections; amortize schema-load), and whenever guaranteed
accessibility / branding / validation / a git-diffable source matter. **When it
doesn't:** one-shot throwaway docs judged purely on token cost.

## Caveats

- **N=1 per cell** — no variance estimate. Consistency across 3 models is the
  evidence, not repetition.
- **Cross-tool absolute numbers aren't comparable** (different models, tokenizers,
  pricing). Only the **within-tool delta** is valid.
- `total_tokens` counts `cache_read` at face value (billed ~10%); `cost_usd` is
  the economic truth.
- The `skillkit` hands agents the **raw JSON schemas** to read, which inflates
  input vs native Claude skill loading (a concise `SKILL.md` + lazy schema
  reads). So the skill input-overhead here is an **upper bound**.
- **codex**: its sandbox blocked file writes in this environment; the re-run with
  `--dangerously-bypass-approvals-and-sandbox` then hit the usage cap. Only
  partial token data was observed (one skill attempt: ~235K input / 5.6K output
  before failing) — consistent with skills inflating input. Not counted as a
  completed cell.
- Quality validators (a11y/responsive) require Playwright + `@axe-core/playwright`.

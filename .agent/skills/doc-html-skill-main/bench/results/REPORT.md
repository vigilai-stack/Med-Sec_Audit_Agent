# Skills vs. pure HTML generation — benchmark results

Same fixed content brief, same target (branded HTML, ≥3 diagrams, ≥2 tables). Two conditions per tool: **noskill** (model writes HTML directly) vs **skill** (model writes compact canonical YAML, the renderer owns all chrome). N=1 per cell.

## Raw metrics (all runs)

| tool | cond | model | out tok | total tok | cost $ | wall ms | tools | html B | yaml B |
|---|---|---|---|---|---|---|---|---|---|
| claude | noskill | claude-opus-4-8[1m] | 8,231 | 63,954 | 0.3326 | 80,159 | — | 16,281 | 0 |
| claude | noskill | claude-opus-4-8[1m] | 8,153 | 63,889 | 0.3308 | 80,544 | — | 16,504 | 0 |
| claude | noskill | claude-opus-4-8[1m] | 7,042 | 61,712 | 0.2963 | 69,857 | — | 14,344 | 0 |
| claude | skill | claude-opus-4-8[1m] | 5,950 | 300,288 | 0.4108 | 102,068 | — | 12,788 | 6,484 |
| claude | skill | claude-opus-4-8[1m] | 4,490 | 207,204 | 0.3186 | 60,507 | — | 13,636 | 7,349 |
| claude | skill | claude-opus-4-8[1m] | 4,775 | 209,039 | 0.3258 | 60,326 | — | 13,191 | 7,270 |
| codex | noskill | codex-gpt | 7,404 | 182,051 | — | 155,609 | 16 | 20,145 | 0 |
| codex | noskill | codex-gpt | 7,122 | 228,903 | — | 139,096 | 16 | 18,547 | 0 |
| codex | skill | codex-gpt | 4,965 | 547,176 | — | 116,129 | 36 | 14,063 | 7,319 |
| kilo | noskill | MiniMax-M2.7 | 2,836 | 35,454 | 0.0111 | 66,802 | 1 | 8,352 | 0 |
| kilo | noskill | MiniMax-M2.7 | 2,932 | 51,756 | 0.0106 | 29,137 | 2 | 8,297 | 0 |
| kilo | noskill | MiniMax-M2.7 | 0 | 0 | 0.0000 | 59,400 | 0 | 9,578 | 0 |
| kilo | skill | MiniMax-M2.7 | 1,942 | 138,037 | 0.0145 | 43,305 | 8 | 11,954 | 5,371 |
| kilo | skill | MiniMax-M2.7 | 3,196 | 153,729 | 0.0211 | 89,401 | 9 | 13,061 | 6,834 |
| kilo | skill | MiniMax-M2.7 | 5,898 | 364,787 | 0.0349 | 86,117 | 18 | 13,328 | 6,445 |
| opencode | noskill | qwen/qwen3.7-max | 3,799 | 29,113 | 0.0370 | 67,061 | 1 | 11,036 | 0 |
| opencode | noskill | qwen/qwen3.7-max | 3,399 | 28,113 | 0.0343 | 65,567 | 1 | 9,556 | 0 |
| opencode | noskill | qwen/qwen3.7-max | 378 | 59,989 | 0.0590 | 71,319 | 15 | 10,634 | 0 |
| opencode | skill | qwen/qwen3.7-max | 2,640 | 109,805 | 0.0673 | 60,925 | 17 | 14,016 | 7,704 |
| opencode | skill | qwen/qwen3.7-max | 2,332 | 117,520 | 0.0637 | 64,231 | 13 | 13,137 | 6,513 |
| opencode | skill | qwen/qwen3.7-max | 1,992 | 88,905 | 0.0523 | 63,935 | 15 | 12,187 | 5,717 |

## Within-tool delta: skill vs noskill (the valid comparison)

Each tool runs the same model in both conditions, so the delta isolates the *method*.

| tool | model | out-tokens | total-tokens | cost | wall | tool-calls |
|---|---|---|---|---|---|---|
| claude | claude-opus-4-8[1m] | 7,042→4,775 (-32%) | +239% | 0.2963→0.3258 (+10%) | -14% | —→— |
| codex | codex-gpt | 7,122→4,965 (-30%) | +139% | —→— (—) | -17% | 16→36 |
| kilo | MiniMax-M2.7 | 0→5,898 (—) | — | 0.0000→0.0349 (—) | +45% | 0→18 |
| opencode | qwen/qwen3.7-max | 378→1,992 (+427%) | +48% | 0.0590→0.0523 (-11%) | -10% | 15→15 |

## Output quality

| run | a11y (WCAG AA) | responsive | diagrams | tables | meets brief |
|---|---|---|---|---|---|
| claude-noskill-1 | fail | fail | 3 | 2 | ✅ |
| claude-noskill-2 | fail | pass | 3 | 2 | ✅ |
| claude-noskill-3 | fail | fail | 3 | 2 | ✅ |
| claude-skill-1 | pass | pass | 3 | 2 | ✅ |
| claude-skill-2 | pass | pass | 3 | 3 | ✅ |
| claude-skill-3 | pass | pass | 3 | 2 | ✅ |
| codex-noskill-1 | fail | fail | 3 | 3 | ✅ |
| codex-skill-1 | pass | pass | 3 | 3 | ✅ |
| kilo-noskill-1 | fail | fail | 3 | 2 | ✅ |
| kilo-noskill-2 | pass | fail | 3 | 2 | ✅ |
| kilo-noskill-3 | fail | fail | 3 | 2 | ✅ |
| kilo-skill-1 | pass | pass | 3 | 2 | ✅ |
| kilo-skill-2 | pass | pass | 4 | 2 | ✅ |
| kilo-skill-3 | pass | pass | 3 | 3 | ✅ |
| opencode-noskill-1 | fail | pass | 3 | 2 | ✅ |
| opencode-noskill-2 | fail | fail | 3 | 2 | ✅ |
| opencode-noskill-3 | fail | fail | 3 | 2 | ✅ |
| opencode-skill-1 | pass | pass | 3 | 3 | ✅ |
| opencode-skill-2 | pass | pass | 3 | 2 | ✅ |
| opencode-skill-3 | pass | pass | 3 | 2 | ✅ |

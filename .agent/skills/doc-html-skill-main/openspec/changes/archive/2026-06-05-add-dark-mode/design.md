# Design: add-dark-mode

## Context

Schema v2's `theme.mode` (`light | dark | auto`) is accepted but ignored: the v2 rewrite deliberately dropped the old auto-dark CSS block, and the skin templates only carry the value through as a `data-theme-mode` attribute. The token pipeline (default → brand → skin, flattened to CSS custom properties and Mermaid `themeVariables`) is single-palette. Everything downstream — widgets, skins, diagrams, validation — assumes light.

Because **every visible style already references a token** (no hard-coded colors in widget/skin CSS, enforced since the v2 rewrite), dark mode is a token-swap problem, not a restyling problem. The work concentrates in: a dark palette, mode-aware CSS emission, mode-aware Mermaid init, and validation.

## Goals / Non-Goals

**Goals:**
- `theme.mode` becomes functional: `light` (default), `dark`, and `auto` (follows `prefers-color-scheme`).
- One dark palette shared by all skins, with optional brand- and skin-level dark overrides — same layering as light.
- Mermaid diagrams match the active palette in interactive mode; frozen mode resolves deterministically.
- All widget token pairs meet WCAG AA in dark mode, verified by the validator under dark emulation.
- Print stays white under every mode (no change to the print guarantee).

**Non-Goals:**
- No in-page theme toggle widget (mode is an authoring decision; `auto` already follows the user's OS).
- No per-section or per-widget mode overrides.
- No dark variant of PDF output.
- No schema change (`theme.mode` already exists).

## Decisions

### D1 — Dark palette as a parallel `dark` token group, same keys as `color`
`default-theme.json` gains `"dark": { ...same keys as color... }`. Brand themes and `skins/<skin>.tokens.json` may override any subset under their own `dark` group. Resolution runs twice with the existing `_deep_merge`: once for `color`, once for `dark` (defaulting missing dark keys to the resolved light value so partial palettes degrade gracefully).

*Alternative considered:* separate `default-theme.dark.json` file. Rejected: doubles file plumbing and lets light/dark drift; one file keeps palettes reviewed together.

### D2 — Mode-aware CSS emission, not duplicate stylesheets
`tokens_to_css_vars()` grows a mode parameter and render emits:
- `light`: `:root { light vars }` (exactly today's output).
- `dark`: `:root { dark vars }`.
- `auto`: `:root { light vars }` plus `@media (prefers-color-scheme: dark) { :root[data-theme-mode="auto"] { dark vars } }`.

Widget/skin CSS is untouched — it only consumes variables. The `data-theme-mode` attribute scoping keeps `auto`'s media query from affecting explicitly-light documents.

### D3 — Mermaid picks its palette at init time
The init script embeds **both** light and dark `themeVariables` objects and selects by mode: `dark` → dark vars; `auto` → `matchMedia('(prefers-color-scheme: dark)').matches ? dark : light` (evaluated once at load; no live re-render on OS switch — documented limitation). Output stays deterministic: both palettes are serialized with sorted keys; the branch happens client-side.

*Alternative considered:* re-render diagrams on scheme change via `matchMedia` listener. Rejected for wave 1: mermaid re-init complexity for a rare event; reload picks up the change.

### D4 — Frozen mode resolves `auto` to light
`freeze_mermaid.sh` / `--print-mermaid-config` use: `dark` → dark vars, `light`/`auto` → light vars. Frozen output is archival/PDF-oriented where light is the correct default; an explicit `mode: dark` still freezes dark. Documented in SKILL.md.

### D5 — Dark palette is derived for chrome, hand-tuned for semantics
Neutral chrome (bg `#0F1522`-family, surface, line, text) is a standard dark scale. Semantic soft pairs (callout intents, severities, heat levels) are hand-tuned: dark soft backgrounds (low-luminance tints) with light text counterparts, each pair checked ≥ 4.5:1. `heat_5` keeps white-on-red. Brief's hero gradient and editorial's paper tone get skin-level dark overrides (editorial dark = warm slate, not pure black, preserving its print-first character on screen).

### D6 — Validation: dark emulation pass keyed off the source's mode
`validate_all.py` reads `theme.mode`; for `dark`/`auto` it passes `--color-scheme dark` to the accessibility layer, which sets Playwright's `colorScheme: 'dark'` before running Axe. Light documents keep today's single pass (no CI cost increase for the common case).

## Risks / Trade-offs

- [Dark soft-color pairs fail AA if brands override carelessly] → partial dark overrides inherit hand-tuned defaults; Axe dark pass catches regressions.
- [`auto` + frozen SVG mismatch: dark-OS reader sees light diagrams on a dark page] → for `auto`, frozen documents also pin the page to light (freeze implies a fixed palette); documented.
- [Mermaid `auto` picks palette only at load] → acceptable; reload follows the OS change. Documented limitation.
- [Brief hero gradient may lose contrast in dark] → skin dark override darkens gradient stops and raises chip contrast; included in the dark screenshot review.
- [Determinism] → both palettes always serialized (sorted keys); no runtime-dependent bytes in output.

## Migration Plan

1. Land tokens + renderer emission + mermaid init (mode still defaults to light — zero visual change for existing docs).
2. Flip two examples (`mode: auto`, `mode: dark`), screenshot all three skins dark, tune pairs.
3. Land validation dark pass; run example matrix.
4. Rollback: revert renderer emission — `theme.mode` returns to advisory; sources unaffected.

## Open Questions

- Should `auto` documents get a tiny inline scheme-change listener that prompts reload (1 line) rather than silently staying stale? (Default: no — silent is fine.)
- Editorial dark: warm slate (`#14161A`-family) vs neutral slate — pick during visual tuning.

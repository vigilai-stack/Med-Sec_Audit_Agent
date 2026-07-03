# Proposal: add-dark-mode

## Why

The base schema already accepts `theme.mode: light | dark | auto`, but since the skins-and-widgets rewrite the field is purely advisory — every document renders light regardless of mode. Engineers reviewing architecture docs in dark editors/browsers get a glaring white page, and the schema promises behavior the renderer does not deliver. This change makes `theme.mode` real across all three skins, every widget, and Mermaid diagrams, without compromising the readability (WCAG AA) and print-on-white guarantees.

## What Changes

- Add a **dark token palette** to the theme system: `default-theme.json` gains a complete dark color set; brand themes and skin token files MAY override it (`dark` group, same keys as `color`). Resolution order stays default → brand → skin, applied independently for light and dark palettes.
- Make the renderer **mode-aware**:
  - `mode: light` (default) — current behavior, light tokens only.
  - `mode: dark` — dark tokens emitted in `:root`; page renders dark everywhere.
  - `mode: auto` — light tokens in `:root`, dark tokens under `@media (prefers-color-scheme: dark)`, following the OS/browser preference.
- **Mermaid follows the mode**: interactive init picks light or dark `themeVariables` at load time (and for `auto`, matches `prefers-color-scheme`); frozen mode bakes SVGs with the resolved palette (`auto` freezes light, documented).
- **Widgets stay AA in dark**: all soft-background/text pairs (callout intents, severity tags, badges, code, heatmap levels, stat cards) get dark variants validated at 4.5:1.
- **Per-skin dark treatment**: docs-site topbar/TOC, editorial paper tone (dark "ink on slate" rather than pure black), brief hero gradient and bento shadows each get skin-level dark overrides.
- **Print is unaffected**: print CSS continues to force white background and light tokens for every mode.
- **Validation**: accessibility layer additionally runs with dark color-scheme emulation when the source declares `mode: dark` or `auto`; responsive/print layers unchanged.
- Examples: at least one example switched to `mode: auto` and one to `mode: dark` to exercise the path.

## Capabilities

### New Capabilities

(none — dark mode extends existing capabilities)

### Modified Capabilities

- `brand-theme-system`: dark token palette, per-mode resolution, AA contrast pairs for dark variants.
- `branded-html-renderer`: mode-aware CSS emission (`:root` vs `prefers-color-scheme`), mode-aware Mermaid initialization, frozen-mode behavior for `auto`.
- `layout-skin-system`: per-skin dark overrides; print stays light under every mode.
- `doc-validation`: dark-scheme accessibility validation for `dark`/`auto` documents.

## Impact

- **Assets**: `default-theme.json` (+`dark` group), `assets/skins/*.tokens.json` (optional `dark` groups), `theme.css` (no hard-coded colors today — verify), `mermaid-config.js` (mode-aware vars).
- **Renderer**: `render.py` (token resolution per mode, CSS emission, mermaid init), skin templates (already emit `data-theme-mode`).
- **Validation**: `validate_accessibility.mjs` (dark emulation pass), `validate_all.py` (plumb mode detection).
- **Schema**: none — `theme.mode` already exists (no schema bump).
- **Docs/examples**: SKILL.md updates (render + orchestrator), 2 examples flipped to dark/auto.
- **Dependencies**: none added.

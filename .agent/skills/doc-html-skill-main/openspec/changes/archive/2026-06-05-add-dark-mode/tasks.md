# Tasks: add-dark-mode

## 1. Dark token palette

- [x] 1.1 Add complete `dark` color group to `default-theme.json` (chrome scale derived; callout/severity/badge/code/heat pairs hand-tuned to AA)
- [x] 1.2 Add skin-level `dark` overrides: `editorial.tokens.json` (warm dark slate paper/ink/hairlines), `brief.tokens.json` (darkened gradient stops, shadow/chip adjustments), `docs-site.tokens.json` (topbar/TOC chrome)
- [x] 1.3 Extend `resolve_tokens()` in `render.py`: layer `dark` groups default → brand → skin; fall back missing dark keys to resolved light values
- [x] 1.4 Mirror dark-palette helpers in `assets/mermaid-config.js` (light/dark variable builders)

## 2. Mode-aware rendering

- [x] 2.1 Extend `tokens_to_css_vars()` + `render_html()` to emit per `theme.mode`: light in `:root`; dark in `:root`; auto = light + `@media (prefers-color-scheme: dark)` scoped to `:root[data-theme-mode="auto"]`
- [x] 2.2 Mode-aware Mermaid init: embed light+dark `themeVariables` (sorted keys, deterministic), select by mode / `matchMedia` at load
- [x] 2.3 Frozen resolution: `--print-mermaid-config` and `freeze_mermaid.sh` use dark vars for `mode: dark`, light otherwise; frozen `auto` pins the page palette to light
- [x] 2.4 Confirm print CSS forces the light/white palette for `mode: dark` documents (PDF spot-check)

## 3. Visual tuning

- [x] 3.1 Render a widget-complete document in `mode: dark` under all three skins; screenshot and tune dark pairs (callouts, severity tags, heatmap, code, stats, hero gradient, editorial slate)
- [x] 3.2 Extend `scripts/test_render.py`: mode emission assertions (dark vars in `:root` for dark, media-query block for auto, byte-identical re-renders per mode)

## 4. Validation

- [x] 4.1 Add `--color-scheme` option to `validate_accessibility.mjs` (Playwright `colorScheme` emulation)
- [x] 4.2 `validate_all.py`: read `theme.mode`; run the dark accessibility pass for `dark`/`auto` sources (both passes for `auto`)
- [x] 4.3 Run the full example matrix; all layers green including dark passes

## 5. Examples & docs

- [x] 5.1 Flip `examples/rf-mcp-architecture.yaml` to `mode: auto` and one example (e.g. `examples/architecture-review.yaml`) to `mode: dark`; validate and screenshot
- [x] 5.2 Update `render-branded-html/SKILL.md` (mode semantics, frozen-auto rule, load-time-only auto switch) and `validate-branded-doc/SKILL.md` (dark pass); note dark availability in README

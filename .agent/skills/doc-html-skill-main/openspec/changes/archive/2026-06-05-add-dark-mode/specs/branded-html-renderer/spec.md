# branded-html-renderer Specification (delta)

## ADDED Requirements

### Requirement: Mode-aware CSS emission
The renderer SHALL honor `theme.mode`: `light` (default) emits light tokens in `:root`; `dark` emits dark tokens in `:root`; `auto` emits light tokens in `:root` plus dark tokens under `@media (prefers-color-scheme: dark)` scoped to `:root[data-theme-mode="auto"]`. Widget and skin CSS MUST NOT change per mode — only the custom-property values swap. Output MUST remain deterministic for all modes.

#### Scenario: Explicit dark document
- **WHEN** a source sets `theme.mode: dark`
- **THEN** the rendered page uses the dark palette regardless of OS preference

#### Scenario: Auto follows the OS
- **WHEN** a source sets `theme.mode: auto` and the reader's OS prefers dark
- **THEN** the page renders with the dark palette, and with the light palette when the OS prefers light

#### Scenario: Omitted mode unchanged
- **WHEN** a source omits `theme.mode`
- **THEN** the rendered output is identical to today's light rendering

### Requirement: Mode-aware Mermaid theming
Interactive Mermaid initialization SHALL select `themeVariables` matching the active palette: dark variables for `mode: dark`, and for `mode: auto` the palette matching `prefers-color-scheme` evaluated at load time. Frozen mode SHALL resolve deterministically: `dark` freezes with dark variables; `light` and `auto` freeze with light variables, and a frozen `auto` document SHALL pin its page palette to light so page and diagrams cannot mismatch.

#### Scenario: Dark diagrams match dark page
- **WHEN** a `mode: dark` document renders interactively
- **THEN** Mermaid initializes with the dark theme variables and diagrams match the page palette

#### Scenario: Frozen auto pins light
- **WHEN** a `mode: auto` document is frozen
- **THEN** both the page and the inlined SVGs use the light palette

### Requirement: Print stays light under every mode
The embedded print CSS SHALL force the light/white print palette for documents of every mode, including `dark`.

#### Scenario: Dark document prints white
- **WHEN** a `mode: dark` document is printed or exported to PDF
- **THEN** the output uses a white background with light-palette token values

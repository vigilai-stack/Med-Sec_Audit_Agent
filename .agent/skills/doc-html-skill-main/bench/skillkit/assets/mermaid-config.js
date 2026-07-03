/*
 * mermaid-config.js — single-source token → style mapping.
 *
 * The same semantic theme tokens drive BOTH the page (CSS custom properties)
 * and the diagrams (Mermaid themeVariables), so the page and its Mermaid
 * diagrams never drift apart. Mermaid's `base` theme is the only modifiable
 * theme, so themeVariables is the correct brand hook.
 *
 * Usable both client-side (interactive mode) and from the validator (Node).
 */

// token path -> CSS custom property name
export const CSS_VAR_MAP = {
  "color.bg": "--color-bg",
  "color.surface": "--color-surface",
  "color.text": "--color-text",
  "color.text_dim": "--color-text-dim",
  "color.line": "--color-line",
  "color.primary": "--color-primary",
  "color.primary_soft": "--color-primary-soft",
  "color.success": "--color-success",
  "color.warning": "--color-warning",
  "color.danger": "--color-danger",
  "font.sans": "--font-sans",
  "font.serif": "--font-serif",
  "font.mono": "--font-mono",
  "radius.card": "--radius-card",
  "spacing.page_x": "--space-page-x",
  "spacing.section_y": "--space-section-y"
};

function get(tokens, path) {
  return path.split(".").reduce((o, k) => (o == null ? undefined : o[k]), tokens);
}

/** Flatten theme tokens into a list of "--var: value;" declarations. */
export function tokensToCssVars(tokens) {
  const out = [];
  for (const [path, cssVar] of Object.entries(CSS_VAR_MAP)) {
    const value = get(tokens, path);
    if (value != null) out.push(`${cssVar}: ${value};`);
  }
  return out;
}

/** Map tokens into Mermaid `base` theme variables. */
export function tokensToMermaidVars(tokens) {
  const c = tokens.color || {};
  const f = tokens.font || {};
  return {
    background: c.bg,
    primaryColor: c.primary_soft,
    primaryBorderColor: c.primary,
    primaryTextColor: c.text,
    lineColor: c.line,
    textColor: c.text,
    fontFamily: f.sans
  };
}

/** Build the full mermaid.initialize() config object. */
export function mermaidConfig(tokens, opts = {}) {
  return {
    startOnLoad: opts.startOnLoad !== false,
    theme: "base",
    securityLevel: opts.securityLevel || "strict",
    look: opts.look || "classic",
    fontFamily: (tokens.font && tokens.font.sans) || "Arial, sans-serif",
    themeVariables: tokensToMermaidVars(tokens)
  };
}

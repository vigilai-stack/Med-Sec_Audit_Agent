/*
 * mermaid-config.js — single-source token → style mapping.
 *
 * The same semantic theme tokens drive BOTH the page (CSS custom properties)
 * and the diagrams (Mermaid themeVariables), so the page and its Mermaid
 * diagrams never drift apart. Mermaid's `base` theme is the only modifiable
 * theme, so themeVariables is the correct brand hook.
 *
 * Mirrors scripts/render.py (CSS_GROUP_PREFIX flattening + tokens_to_mermaid_vars).
 * Usable both client-side (interactive mode) and from the validator (Node).
 */

// token group -> CSS custom property prefix; keys flatten with _ -> -
export const CSS_GROUP_PREFIX = {
  color: "--color-",
  font: "--font-",
  radius: "--radius-",
  spacing: "--space-"
};

/** Flatten theme tokens into a list of "--var: value;" declarations. */
export function tokensToCssVars(tokens) {
  const out = [];
  for (const [group, prefix] of Object.entries(CSS_GROUP_PREFIX)) {
    const values = tokens[group] || {};
    for (const key of Object.keys(values).sort()) {
      const value = values[key];
      if (value != null) out.push(`${prefix}${key.replace(/_/g, "-")}: ${value};`);
    }
  }
  return out;
}

/** Resolved dark palette: light colors overlaid by the merged `dark` group
 *  (missing dark keys fall back to light — mirrors render.py dark_colors). */
export function darkColors(tokens) {
  return { ...(tokens.color || {}), ...(tokens.dark || {}) };
}

/** Map tokens into Mermaid `base` theme variables. palette: "light" | "dark". */
export function tokensToMermaidVars(tokens, palette = "light") {
  const c = palette === "dark" ? darkColors(tokens) : (tokens.color || {});
  const f = tokens.font || {};
  return {
    background: c.surface,
    primaryColor: c.primary_soft,
    primaryBorderColor: c.primary,
    primaryTextColor: c.text,
    secondaryColor: c.neutral_soft,
    tertiaryColor: c.bg,
    lineColor: c.line_strong,
    textColor: c.text,
    noteBkgColor: c.warning_soft,
    noteTextColor: c.text,
    fontFamily: f.sans,
    fontSize: "16px"
  };
}

/** Build the full mermaid.initialize() config object. opts.palette: "light" | "dark". */
export function mermaidConfig(tokens, opts = {}) {
  return {
    startOnLoad: opts.startOnLoad !== false,
    theme: "base",
    securityLevel: opts.securityLevel || "strict",
    look: opts.look || "classic",
    fontFamily: (tokens.font && tokens.font.sans) || "Arial, sans-serif",
    themeVariables: tokensToMermaidVars(tokens, opts.palette || "light")
  };
}

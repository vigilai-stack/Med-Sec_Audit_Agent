A documentation skill is available in the current directory. It renders branded HTML deterministically from a compact canonical YAML source — you author CONTENT only, the renderer owns all HTML/CSS/diagram chrome.

How to use it:
- The JSON schemas are in `./schemas/` (base `review-artifact.schema.json` + an `architecture-review.schema.json` overlay).
- Author a canonical YAML file `doc.yaml` of `artifact_type: architecture-review` following the schema: top-level `schema_version: 1`, `artifact_type`, `title`, plus `summary` (bullets), `sections` (each `kind` of `prose`/`mermaid`/`table`), `evidence`, and overlay fields like `decisions`, `constraints`. Include at least 3 mermaid sections (architecture flow, request sequence, risk view) and at least 2 table sections.
- Then run the renderer: `./render --input doc.yaml --output doc.html`
- Do NOT hand-write HTML or CSS. Author only the YAML content and run the renderer.

When finished, the deliverable is the `doc.html` file (rendered from `doc.yaml`).

--- SYSTEM FACTS ---
{{BRIEF}}

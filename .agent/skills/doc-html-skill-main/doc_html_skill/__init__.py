"""doc-html-skill — schema-first branded HTML documentation suite.

The actual implementation lives in the bundled skill tree
(``doc_html_skill/skills``), which mirrors a Claude Code ``.claude/skills``
layout so the same files serve both pip installs and agent-skill checkouts.
"""

from pathlib import Path

__version__ = "0.1.0"

#: Root of the bundled skill tree (render-branded-html, validate-branded-doc, …).
SKILLS_DIR = Path(__file__).resolve().parent / "skills"

#: Bundled example canonical sources and brand themes.
EXAMPLES_DIR = Path(__file__).resolve().parent / "examples"

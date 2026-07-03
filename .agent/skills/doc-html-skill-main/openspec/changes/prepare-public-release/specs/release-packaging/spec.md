# release-packaging Specification (delta)

## ADDED Requirements

### Requirement: Public repository hygiene
The public repository SHALL carry an Apache-2.0 `LICENSE`, a `CHANGELOG.md`, and a curated tree: skill directories, schemas, templates, assets, examples, experiments, openspec history, and benchmark tooling are public; raw benchmark run transcripts, build outputs, virtual environments, and dependency directories are excluded. The published tree MUST contain no real-brand names or trademarks in example assets (fictional simulated brands only; the owner's own project identity is permitted), no secrets or credential patterns, and no machine-local absolute paths in documentation.

#### Scenario: Real-brand themes absent
- **WHEN** the public tree is scanned for the replaced brand names (e.g. Coca-Cola, Google, IKEA as brand assets)
- **THEN** no example theme or asset references them, and fictional equivalents are present instead

#### Scenario: Hygiene gate blocks secrets
- **WHEN** a staged file matches a secret/credential pattern
- **THEN** the release gate fails before any push

### Requirement: Python distribution
The suite SHALL be packaged as a pip-installable distribution named `doc-html-skill` that bundles the full skill tree (scripts, schemas, templates, assets) as package data and exposes console entry points for rendering, validating, and PDF export. A built wheel and sdist MUST exist in `dist/`, and the installed wheel MUST pass a smoke test (render a bundled example end-to-end in a clean environment).

#### Scenario: CLI works from a clean install
- **WHEN** the wheel is installed into a fresh virtual environment and `doc-html-render` runs against a bundled example
- **THEN** it produces valid HTML output without referencing the source checkout

#### Scenario: Validator finds the renderer
- **WHEN** `doc-html-validate` runs from the installed package
- **THEN** the schema layer and auto-render path resolve inside the installed package data

### Requirement: npm distribution
The suite SHALL be packaged as an npm package named `doc-html-skill` (matching version) whose binary installs the skill directories into a consumer project's `.claude/skills/`. The package MUST be dependency-free at runtime, MUST whitelist its published files, and a `npm pack` tarball MUST exist containing the complete skill tree.

#### Scenario: Skills install into a project
- **WHEN** the package binary's `install` command runs in a target project
- **THEN** all skill directories appear under that project's `.claude/skills/` and existing files are only overwritten with an explicit force flag

#### Scenario: Tarball completeness
- **WHEN** the packed tarball is inspected
- **THEN** it contains every skill directory, the installer binary, README, and LICENSE

### Requirement: Versioned GitHub release
The repository SHALL have an annotated `v0.1.0` tag and a GitHub release whose notes summarize the suite's capabilities, with the wheel, sdist, npm tarball, and a standalone skills zip attached as release assets. Repository creation, the initial push, and release creation MUST be confirmed with the owner before execution.

#### Scenario: Release carries installables
- **WHEN** the v0.1.0 release page is viewed
- **THEN** wheel, sdist, npm tarball, and skills zip are downloadable assets

### Requirement: Manual publishing documented
A `RELEASING.md` SHALL document the exact manual commands to publish the prepared artifacts to PyPI (`twine upload`) and npm (`npm publish`), including credential prerequisites and a post-publish verification step. The release preparation MUST NOT publish to either registry.

#### Scenario: No registry publish during prepare
- **WHEN** the release-preparation tasks complete
- **THEN** nothing has been uploaded to PyPI or npm, and dist artifacts plus documented commands exist for the owner

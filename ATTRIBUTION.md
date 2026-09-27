# Attribution

Third-party skills vendored into this library, with provenance and license.

## anthropics/knowledge-work-plugins

- Source commit: `94e1a089d28d3e0c2ad9af696f8499cd8c6f7205`
- License: Apache-2.0. The full text is in
  [`LICENSES/Apache-2.0.txt`](LICENSES/Apache-2.0.txt) (the canonical text from
  https://www.apache.org/licenses/LICENSE-2.0.txt). Upstream ships no `NOTICE`
  file at this commit.
- Imported paths (upstream `data/skills/<name>/` → repo root `<name>/`):

  - `sql-queries/`
  - `statistical-analysis/`
  - `explore-data/`
  - `validate-data/`
  - `data-visualization/`

Local modifications to imported files: frontmatter trigger phrasing
normalized to skill-lib convention (`Use this when`), Cowork-only
frontmatter keys removed, and a Workflow/Anti-patterns/Provenance/hmmm
bookend appended per `skill-build` compliance. Upstream bodies are
otherwise unmodified. This repository is MPL-2.0 (`LICENSE`); imported files remain
available under Apache-2.0 (`LICENSES/Apache-2.0.txt`) as noted per file.

Usage: if you redistribute any of the imported skills, include
`LICENSES/Apache-2.0.txt`, keep this attribution and the per-file Provenance
section, and keep the note that the files were modified (Apache-2.0 §4(a)–(b)).

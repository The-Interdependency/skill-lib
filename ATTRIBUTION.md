# Attribution

Third-party skills vendored into this library, with provenance and license.

## anthropics/knowledge-work-plugins

- Source commit: `94e1a089d28d3e0c2ad9af696f8499cd8c6f7205`
- License: Apache-2.0. The governing text is upstream `data/LICENSE` at
  `94e1a08`, which sits beside the imported `data/skills/` and is byte-identical
  to https://www.apache.org/licenses/LICENSE-2.0.txt. A copy is in
  [`LICENSES/Apache-2.0.txt`](LICENSES/Apache-2.0.txt).
  The upstream root `LICENSE` has the same Apache-2.0 text followed by 10 lines
  of unrelated text that third-party PR #193 (anthropics/knowledge-work-plugins,
  merged 2026-04-27 PT) appended. Those lines are not a `NOTICE` and are not
  reproduced here. Upstream ships no `NOTICE` file at this commit.
- Imported paths (upstream `data/skills/<name>/` → repo root `<name>/`):

  - `sql-queries/`
  - `statistical-analysis/`
  - `explore-data/`
  - `validate-data/`
  - `data-visualization/SKILL.md` only (upstream
    `data/skills/data-visualization/` contains no other file at `94e1a08`)

Local modifications to imported files: frontmatter trigger phrasing
normalized to skill-lib convention (`Use this when`), Cowork-only
frontmatter keys removed, and a Workflow/Anti-patterns/Provenance/hmmm
bookend appended per `skill-build` compliance. Upstream bodies are
otherwise unmodified. `data-visualization/SKILL.md` additionally carries a
locally appended, clearly marked The Interdependency information-design
extension (skill-lib `868de86`).

Local files in imported skill directories: `data-visualization/examples/`,
`data-visualization/references/`,
`data-visualization/information_design_audit.py`, and
`data-visualization/visual-grammar.json` were not supplied by upstream. They
were added in skill-lib `868de86` and are original to skill-lib under MPL-2.0
(`LICENSE`).

This repository is MPL-2.0 (`LICENSE`); imported files remain
available under Apache-2.0 (`LICENSES/Apache-2.0.txt`) as noted per file.

Usage: if you redistribute any of the imported skills, include
`LICENSES/Apache-2.0.txt`, keep this attribution and the per-file Provenance
section, and keep the note that the files were modified (Apache-2.0 §4(a)–(b)).

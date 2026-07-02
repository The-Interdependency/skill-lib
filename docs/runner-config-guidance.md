# msdmd runner configuration guidance

The raw parser can walk a tree, but production compliance needs a small
repo-local policy so the denominator is honest. Use this guidance when adding a
collector, visualizer, or compliance gate to a target repository.

## Default scan policy

Collectors should include executable source files with supported comment
markers:

- Python: `.py`
- TypeScript / JavaScript: `.ts`, `.tsx`, `.js`, `.jsx`
- shell and adjacent source files when a supported marker exists

Collectors should skip:

- `.git/`
- `.agents/skills/` copied from `skill-lib`
- `node_modules/`
- virtualenvs and build/cache directories
- generated artifacts
- historical archives
- explicit frozen research artifacts
- read-only upstream mirrors

## Per-repo skip examples

```json
{
  "repo": "The-Interdependency/ucns",
  "skip": [
    ".agents/skills",
    "code",
    "code/sweeps",
    "ucns_recursive",
    "examples/visualization"
  ],
  "note": "Separate live package coverage from frozen research artifacts."
}
```

```json
{
  "repo": "The-Interdependency/edcmbone",
  "skip": [
    ".agents/skills",
    "backend_old",
    "canon_eng/release",
    "edcmbone/edcmbone"
  ],
  "note": "Separate canonical backend package from migration scaffolds and frozen canon."
}
```

```json
{
  "repo": "The-Interdependency/a0",
  "skip": [
    ".agents/skills",
    "node_modules",
    "dist",
    "client/dist"
  ],
  "ratio_dialect": "a0 compact N:M C:D I:O",
  "note": "Do not report compact ratios as canonical parser drift; a0 owns its own enforcement."
}
```

## Expected blocks by repo maturity

Minimum expectation for new executable modules:

- `MODULE_BUILD`

High-value additions for services, routes, and security surfaces:

- `BOUNDARIES`
- `CAPABILITIES`
- `CONTRACTS`

Documentation-heavy repos may legitimately emphasize:

- `DOCS`
- `LLMS`
- `OWNERS`

Content/spec repos with no executable source should report `N/A`, not `0%`
failure.

## Collection point

Every consuming repo should eventually produce:

```text
<reponame>_msdmd.ts
```

The collection point should export `defineMsdmdCollection(...)` and should be
regenerated from the repo-local collector when possible. Manual seed files are
allowed only when marked as provisional with a `hmmm` gap.

## hmmm

This file is policy guidance, not an executable config format yet. The next
concrete implementation step is adding a `--config` argument to
`msdmd/collect.py` that accepts skip paths, expected blocks, and ratio dialect
metadata.

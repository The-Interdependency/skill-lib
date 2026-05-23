# skill-lib

Canonical organization-wide agent skill library for The Interdependency.

This repository is the source of truth for shared agent skills. Repo-local
copies may be installed under `.agents/skills/` so Codex, Claude, and other
agents can use the same module-build doctrine inside each repository.

## Corrected handoff status

create The-Interdependency/skill-lib, seed it from a0/skill-lib, then propagate repo-local .agents/skills copies organization-wide

## PR 0 — create canonical org skill repo

Goal:
Create the canonical organization-wide skill library for The Interdependency.

New repo:
`The-Interdependency/skill-lib`

Seed source:
`The-Interdependency/a0` repository, `skill-lib/` directory

Copy from `a0`:
- `README.md`
- `msdmd/`
- `test-build/`
- `meta-module-build/`

## PR 0.5 — propagation after canonical repo exists

Source:
`The-Interdependency/skill-lib`

Install into each target repo:
- `.agents/skills/msdmd/`
- `.agents/skills/test-build/`
- `.agents/skills/meta-module-build/`
- `.agents/skills/README.md`

Required PR sentence:
`This PR installs the canonical organization-wide skill library repo-locally for agents. It does not require retroactive MODULE_BUILD coverage for existing modules.`

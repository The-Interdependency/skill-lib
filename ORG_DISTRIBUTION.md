# Organization distribution

This repository is the canonical organization-wide skill library for
The Interdependency.

## Canonical source

All organization-level agent skill edits should happen here first.

Repo-local copies may exist under:

```text
.agents/skills/
```

Propagation PRs should cite this repository and the source commit SHA.

## Installed skills

* `msdmd/` — Module Self-Declared Metadata Markdown
* `test-build/` — contract-test metadata blocks
* `meta-module-build/` — metadata-first module scaffolding
* `visitor-intro/` — onboarding tour for newcomers landing at any org repo

## Target repos

* `The-Interdependency/a0`
* `The-Interdependency/ucns`
* `The-Interdependency/edcmbone`
* `The-Interdependency/interdependent-lib`
* `The-Interdependency/PTCA`
* `The-Interdependency/PCEA`
* `The-Interdependency/aimmh`
* `The-Interdependency/pcna`
* `The-Interdependency/ZFAE`
* `The-Interdependency/ai-tiw`
* `The-Interdependency/a0ucns`
* `The-Interdependency/eml_ucns`

## Rule

Before creating a new module, route, service, adapter, schema, worker,
engine, UI panel, migration, or experiment, agents should read:

```text
.agents/skills/meta-module-build/SKILL.md
```

New module work should start with a `MODULE_BUILD` block. Unknown fields
must be marked `hmmm`, not guessed.

Existing files are not retroactively noncompliant merely because they predate
this skill.

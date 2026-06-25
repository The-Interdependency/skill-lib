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
* `doc-build/` — documentation coverage metadata blocks
* `cap-build/` — capability inventory metadata blocks
* `deps-build/` — dependency topology metadata blocks
* `owner-build/` — module stewardship metadata blocks
* `test-build/` — contract-test metadata blocks
* `meta-module-build/` — metadata-first module scaffolding
* `risk-boundary-build/` — runtime risk and permission boundary metadata blocks
* `ratios/` — module composition ratio verification
* `canon/` — canonical-source and doctrine maintenance
* `visitor-intro/` — onboarding tour for newcomers landing at any org repo
* `char-compress/` — bone/flesh context compression for handoffs and skill writing
* `agent-instantiation/` — a0/a0ucns agent spawn/fork/merge lifecycle methodology
* `a0p-instancing/` — a0-betatest (a0p) per-user CRUD + native-ZFAE instancing methodology
* `manifest/` — living-spec generation
* `llms-build/` — root llms.txt generation from LLMS blocks
* `plain-lens/` — plain-language, multi-lens companion views of dense canonical text
* `meta/` — Meta Energy Theory Axioms canon skill
* `gonal-morphology/` — three-core gonal morphology canon (omega/phi/psi; ⊠ = UCNS carrier-LCM)
* `meta/` — Meta Energy Theory axioms and cross-domain resonance preservation

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

Before creating or maintaining a root `llms.txt`, agents should read:

```text
.agents/skills/llms-build/SKILL.md
```

Root LLM instructions should be declared in source `LLMS` blocks and generated
with the llms-build runner, not hand-maintained as separate doctrine.

Existing files are not retroactively noncompliant merely because they predate
this skill.

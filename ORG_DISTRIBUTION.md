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
* `typed-meta-frontend/` — TypeScript self-building frontend generation from backend module metadata
* `plain-lens/` — plain-language, multi-lens companion views of dense canonical text
* `meta/` — Meta Energy Theory Axioms canon skill
* `gonal-morphology/` — three-core gonal morphology canon (omega/phi/psi; ⊠ = UCNS carrier-LCM)
* `the-interdependency/` — org-wide workflow protocol and usage-guidance doctrine for The Interdependency projects
* `loop-eng/` — closed-loop engineering doctrine for repeatable Discover→Plan→Execute→Verify→Iterate workflows
* `skill-build/` — skill authoring, compliance, and individualized test-suite question workflow

## Target repos

**Active vendoring consumers** — carry a top-level `.agents/skills/<skill>/`
subset copied from here. These are exactly the repos the scheduled drift
detector (`.github/workflows/consumer-drift.yml`) checks:

* `The-Interdependency/a0`
* `The-Interdependency/ucns`
* `The-Interdependency/edcmbone`
* `The-Interdependency/edcm`
* `The-Interdependency/interdependent-lib`
* `The-Interdependency/aimmh`
* `The-Interdependency/ai-tiw`
* `The-Interdependency/eml_ucns`
* `The-Interdependency/zfae`
* `The-Interdependency/pcea`
* `The-Interdependency/a0-betatest`
* `The-Interdependency/metapat`

**Targets not in the drift matrix** (do not vendor a top-level subset yet, so
`--require-vendored` would fail them):

* `The-Interdependency/a0ucns` — an aggregator that embeds whole copies of other
  repos rather than vendoring a top-level `.agents/skills/` subset. Its nested
  embeds carry their own copies; re-sync those from their source repos.
* `The-Interdependency/ptcna` — the consolidated prime-tensor repo; carries no
  vendored skill subset yet. Add it above once it does.

**Superseded** — folded into `ptcna` and pending archival; not tracked:

* `The-Interdependency/PTCA`, `The-Interdependency/pcna` (→ `ptcna`)

Add a repo to the active list — and the drift matrix — once it carries a
canonical `.agents/skills/` subset.

## Collection points

Every consuming repo should eventually carry a root collection point:

```text
<reponame>_msdmd.ts
```

Use `python -m msdmd.collect --root . --repo <repo> --out <reponame>_msdmd.ts`
when the repo can run the collector locally. A provisional hand-seeded collection
point is allowed only when it records a `hmmm` gap explaining what local
generation still needs.

`skill-lib_msdmd.ts` is the root collection point for this canonical repo.

## Propagation checklist

Use `docs/propagation-checklist.md` for the concrete source-change →
target-repo PR sequence. Use `docs/runner-config-guidance.md` before judging
large or artifact-heavy repos; frozen research artifacts, archives, generated
trees, and vendored `.agents/skills/` copies should not pollute the denominator.

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

## hmmm

Target-repo propagation is not complete just because `skill-lib` is updated.
Each target repo still needs a repo-local propagation PR, source commit SHA,
collection point, and local verification record.

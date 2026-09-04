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
* `domain-claims/` — domain-first lexical standing, collision checks, and semantic provenance gating
* `visitor-intro/` — onboarding tour for newcomers landing at any org repo
* `char-compress/` — bone/flesh context compression for handoffs and skill writing
* `agent-instantiation/` — a0/a0ucns agent spawn/fork/merge lifecycle methodology
* `a0p-instancing/` — a0-betatest (a0p) per-user CRUD + native-ZFAE instancing methodology
* `manifest/` — living-spec generation
* `llms-build/` — root llms.txt generation from LLMS blocks
* `typed-meta-frontend/` — TypeScript self-building frontend generation from backend module metadata
* `plain-lens/` — plain-language, multi-lens companion views of dense canonical text
* `meta/` — consultation router for current METAPAT authority; no frozen doctrine copy
* `gonol-build/` — UCNS gonol construction, closure, atomic promotion, explicit function application, complete replay, and honest continuation boundaries
* `ucns-option-selection/` — fail-closed scoped UCNS option comparison, selection, ratification, non-transfer, rollback, and decision receipts
* `epac-selection-display/` — exact provisional EPAC target and representation selection with receipt-backed display, status preservation, and a read-only WebMCP handoff boundary
* `the-interdependency/` — org-wide workflow protocol and usage-guidance doctrine for The Interdependency projects
* `interdependent-work-graph/` — cross-repository identity, authority, coordination, and shared stack-manifest doctrine
* `project-incubation-graduation/` — incubation, qualification, extraction, release, reconsumption, and implementation-authority graduation doctrine
* `distributed-publication/` — provenance-bearing materialization of one ordered publication from independently owned source units
* `loop-eng/` — closed-loop engineering doctrine for repeatable Discover→Plan→Execute→Verify→Iterate workflows
* `fresh-making/` — deterministic derivation freshness, minimal affected rebuild closure, executor-independent restoration, verification, and receipts
* `action-calibration/` — action sizing doctrine for minimal decisive experiments, maximal coherent programs, prerequisite repair, and immediate containment
* `repo-audit-repair/` — evidence-led repository audit, classified findings, authorized repair, and terminal verification
* `skill-build/` — skill authoring, compliance, and individualized test-suite question workflow
* `skill-usage/` — evidence-bearing local invocation counts and maturity designations
* `ssh-automation/` — fail-closed SSH scripting and copy-paste automation doctrine
* `vm-mcp/` — private VM MCP control plane with loopback-only runtime, non-root shell, systemd host-write confinement, and private-tunnel deployment
* `sql-queries/` — warehouse SQL authoring doctrine (imported, Apache-2.0 — see `ATTRIBUTION.md`)
* `statistical-analysis/` — statistical methods doctrine (imported, Apache-2.0 — see `ATTRIBUTION.md`)
* `explore-data/` — dataset profiling doctrine (imported, Apache-2.0 — see `ATTRIBUTION.md`)
* `validate-data/` — analysis QA doctrine (imported, Apache-2.0 — see `ATTRIBUTION.md`)
* `data-visualization/` — chart-building doctrine (imported, Apache-2.0 — see `ATTRIBUTION.md`)

## Target repos

**Active vendoring consumers** — carry a top-level `.agents/skills/<skill>/`
subset copied from here. These are exactly the repos the scheduled drift
detector (`.github/workflows/consumer-drift.yml`) checks:

* `The-Interdependency/a0`
* `The-Interdependency/ucns`
* `The-Interdependency/edcm`
* `The-Interdependency/interdependent-lib`
* `The-Interdependency/aimmh`
* `The-Interdependency/ai-tiw`
* `The-Interdependency/eml_ucns`
* `The-Interdependency/zfae`
* `The-Interdependency/pcea`
* `The-Interdependency/a0-betatest`
* `The-Interdependency/metapat`
* `The-Interdependency/ptcna`

**Targets not in the drift matrix** (do not vendor a top-level subset yet, so
`--require-vendored` would fail them):

* `The-Interdependency/a0ucns` — an aggregator that embeds whole copies of other
  repos rather than vendoring a top-level `.agents/skills/` subset. Its nested
  embeds carry their own copies; re-sync those from their source repos.
**Archived or superseded** — not active drift consumers:

* `The-Interdependency/edcmbone` — archived; maintained EDCM work lives in `edcm`
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

Before assigning a stack-level task to one repository, agents should read:

```text
.agents/skills/interdependent-work-graph/SKILL.md
```

Resolve the exact participating repository and evidence-source identities first. Repository boundaries remain authority and provenance boundaries, not agent-attention boundaries.

Before deciding whether a component born inside a stack, integration, laboratory, or incubator repository should become an independent repository/package, or before extracting, publishing, reconsuming, or declaring such a component graduated, agents should read:

```text
.agents/skills/project-incubation-graduation/SKILL.md
```

Load `interdependent-work-graph` once the transition crosses repository boundaries. Graduation transfers implementation/public-contract authority only after qualification, release, and downstream reconsumption; it does not transfer semantic, proof, theorem, measurement, certification, or empirical status.

Before assembling one textbook, report, standard, corpus, archive, or public reading sequence from source-owned units distributed across repositories or independently owned files, agents should read:

```text
.agents/skills/distributed-publication/SKILL.md
```

Load `interdependent-work-graph` with it. Preserve ordered source identity, source-local licenses and statuses, correction routing, fail-closed production retrieval, explicit fallback, static reading access, and provenance in the published build artifact.

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

Before promoting a word or phrase into canon, a theorem, schema, ontology, encoding,
or other semantic control surface, agents should read:

```text
.agents/skills/domain-claims/SKILL.md
```

Establish the applicable domain-qualified sense and resolve collisions before
attaching provenance or authorizing structure.

Before constructing, reviewing, replaying, or extending UCNS gonols, agents should read:

```text
.agents/skills/gonol-build/SKILL.md
```

Resolve the current UCNS source and evidence identities first. Preserve closure and
atomic promotion, require explicit occurrence-addressed function plans, and do not
restore the superseded `gonal-morphology` language model.

Before selecting among UCNS options or declaring a scoped winner, agents should read:

```text
.agents/skills/ucns-option-selection/SKILL.md
```

Freeze scope, candidates, hard gates, evidence, policies, authority, and
ratification before outcome comparison. Do not let scores compensate for failed gates
or transfer a scoped result into universal UCNS canon.

Before selecting an EPAC artifact and representation for a human-facing or
WebMCP display, agents should read:

```text
.agents/skills/epac-selection-display/SKILL.md
```

Pin the provisional EPAC source, exact target, receipt, and available renderer;
preserve research standings, nonclaims, sealed-comparison boundaries, and `hmmm`;
and keep the WebMCP server a read-only registry/handoff rather than an EPAC
executor.

Before choosing between the smallest decisive action and a maximal coherent program,
selecting the highest-leverage next step under constrained time, attention, money,
compute, or coordination, or deciding whether a bounded falsifier should precede a
full build, agents should read:

```text
.agents/skills/action-calibration/SKILL.md
```

Name the decision, preserve load-bearing invariants, compare complete cost vectors,
freeze outcome-conditioned escalation rules, and let `loop-eng` execute the selected
bounded loop.

Before auditing or auditing and repairing an existing repository, agents should read:

```text
.agents/skills/repo-audit-repair/SKILL.md
```

Resolve exact repository identity and authority first; select checks from actual
repository claims; classify defects separately from environment, external service,
policy, and `hmmm`; repair only the owning layer under the user's authorization; and
verify merge, release, and deployment as distinct terminal states when applicable.

Before writing, reviewing, or troubleshooting repeatable SSH automation or a
large terminal paste that contains SSH, agents should read:

```text
.agents/skills/ssh-automation/SKILL.md
```

Fail closed on endpoint identity and host-key trust, preserve local/remote shell
boundaries, and keep bulk pasted error handling inside a child shell.

Before giving an MCP-capable agent operational contact with a private VM, agents should read:

```text
.agents/skills/vm-mcp/SKILL.md
```

Keep SSH/OS Login credentials outside the model path, install the service loopback-only and non-root, establish private authenticated transport, prove read-only contact before enabling shell execution, and add privileged administration only as named bounded capabilities rather than a generic root shell.

Existing files are not retroactively noncompliant merely because they predate
this skill.

## hmmm

Target-repo propagation is not complete just because `skill-lib` is updated.
Each target repo still needs a repo-local propagation PR, source commit SHA,
collection point, and local verification record.

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
* `char-compress/` — skill-lib-owned bone/flesh context compression for handoffs and skill writing; historical notation is not current UCNS mathematics
* `agent-instantiation/` — a0/a0ucns agent spawn/fork/merge lifecycle methodology
* `a0p-instancing/` — a0-betatest (a0p) per-user CRUD + native-ZFAE instancing methodology
* `manifest/` — living-spec generation
* `llms-build/` — root llms.txt generation from LLMS blocks
* `typed-meta-frontend/` — TypeScript self-building frontend generation from backend module metadata
* `plain-lens/` — plain-language, multi-lens companion views of dense canonical text
* `thought-lens/` — raw-thought to audience-legible translation with claim-kernel fidelity and back-translation checks
* `meta/` — consultation router for current METAPAT authority; no frozen doctrine copy
* `gonol-build/` — UCNS gonol objects/constructors/geometry + Stack language-construction research, closure, atomic participation, replay, and honest continuation boundaries; EDCM is measurement/evaluation only
* `ucns-option-selection/` — fail-closed scoped UCNS option comparison, selection, ratification, non-transfer, rollback, and decision receipts
* `epac-selection-display/` — exact provisional EPAC target and representation selection with receipt-backed display, status preservation, and a read-only WebMCP handoff boundary
* `the-interdependency/` — org-wide workflow protocol and usage-guidance doctrine for The Interdependency projects
* `interdependent-work-graph/` — cross-repository identity, authority, coordination, and shared stack-manifest doctrine
* `stack-update/` — fail-closed structural stack update protocol; keeps authority, relation, lifecycle, provenance, manifests, BASE records, and work-graph identity coherent in one transaction
* `project-incubation-graduation/` — incubation, qualification, extraction, release, reconsumption, and implementation-authority graduation doctrine
* `distributed-publication/` — provenance-bearing materialization of one ordered publication from independently owned source units
* `website-builder-journal/` — append-only model-attributed By the builder expansion required for every interdependentway.org modification
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
* `The-Interdependency/pubskill-lib`
* `The-Interdependency/epac`
* `The-Interdependency/stack`

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

`skill-lib_msdmd.ts` is the generated root collection point for this canonical
repo. Regenerate it from owning native and supplemental sources, never by editing
the projection:

```bash
python -m msdmd.collect --root . --repo The-Interdependency/skill-lib --import-path ./msdmd/collection --out skill-lib_msdmd.ts
python -m unittest tests.test_msdmd_native_contract_docs
```

The shipped collector defaults to schema 2. It integrates supported native facts
through `msdmd/readers.py` and supplemental MSDMD blocks through the universal
parser path. Its legacy/block-only output remains available only as an explicit
compatibility path and cannot silently represent native facts.

The schema-2 reader matrix is implemented in bounded subsets rather than as a
claim to every metadata convention. Unsupported, ambiguous, unreadable,
dynamic, or out-of-scope inputs remain visible findings; an empty `gaps` array
means only that the declared obligations for that run were satisfied. Deferred
limitations are declared in the collector's owning metadata; they are not
missing-block gaps. The generated file and its inputs travel in one Git commit;
the replay test checks their bytes.

Python repositories may additionally generate source-bound per-module sidecars:

```bash
python -m msdmd.module_projection --root . --repo <repo> --revision <exact-revision> --out-dir .msdmd/modules --write
python -m msdmd.module_projection --root . --repo <repo> --revision <exact-revision> --out-dir .msdmd/modules --check
```

This partial reader covers Python declarations, signatures, decorators,
docstrings, and structurally attached line comments. It does not replace
`<reponame>_msdmd.ts` and is not a repository-wide native coverage verdict. Keep
generated sidecars with the exact source and reader identity that their headers
record.

## Propagation checklist

Use `docs/propagation-checklist.md` for the concrete source-change →
target-repo PR sequence. Use `docs/runner-config-guidance.md` before judging
coverage. Distinguish schema-2 supported readers, legacy block-helper scans,
unsupported native discovery, including manifests, CODEOWNERS, documentation,
extensionless and unsupported sources. Record every exclusion and its reason,
including frozen research artifacts, archives, generated trees, and vendored
`.agents/skills/` copies. Declared scope can exclude them from live-module
obligations without hiding them from accounting.

## Rule

Before assigning a stack-level task to one repository, agents should read:

```text
.agents/skills/interdependent-work-graph/SKILL.md
```

Resolve the exact participating repository and evidence-source identities first. Repository boundaries remain authority and provenance boundaries, not agent-attention boundaries.

Before changing the structure of `The-Interdependency/stack` — including participant,
pin, authority, relation, workspace, BASE, extraction/graduation, or architecture
projections — agents should read:

```text
.agents/skills/stack-update/SKILL.md
```

Load `interdependent-work-graph` with it. Treat the mutation as one coherent
transaction: update every affected authority/provenance projection, remove superseded
claims, recompute the work-graph digest, and require the stack consistency checker to
pass before merge.

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

Before modifying any file in `The-Interdependency/The-Interdependency.github.io`, agents should read:

```text
.agents/skills/website-builder-journal/SKILL.md
```

Every website change transaction must append at least one new `By the builder` record containing date, time, and exact runtime model. The model chooses the subject and stops when it has properly explicated it. The journal append satisfies the transaction and does not recursively require another append.

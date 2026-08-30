---
name: project-incubation-graduation
description: Project incubation and graduation doctrine for emergent components born inside an integration, stack, laboratory, or incubator repository. Load this when several existing projects compose into a new candidate capability; when deciding whether that candidate should remain incubated or become its own repository/package; when extracting it with provenance; when establishing a new implementation authority boundary; when publishing the extracted project as a package such as PyPI; or when making the former incubator consume the released artifact instead of its local copy. Do not load for an ordinary new repository with no incubation history or for a routine package release whose authority boundary is already established.
---

# project-incubation-graduation — let the forge survive its products

Use this procedural skill when a new thing is born by composing existing things inside a repository that is intentionally allowed to incubate novel integrations.

The skill governs the transition from **candidate inside a forge** to **independent project with its own implementation authority**. It does not decide scientific truth, semantic canon, theorem status, measurement validity, or empirical validity.

## Core contract

```text
composition may create a candidate
candidate != independent project
graduation creates a new implementation-authority boundary
graduation is complete only after consumers use the released artifact
```

- Incubation is a legitimate ownership state, not architectural debt by definition.
- A candidate remains owned by its incubator until graduation gates are satisfied.
- Extraction alone is not graduation.
- Publishing alone is not graduation.
- The former incubator must successfully consume the released artifact before graduation is complete.
- Once graduated, the independent repository owns the candidate's implementation and public contract; the incubator becomes a consumer.
- No semantic, theorem, proof, certification, measurement, empirical, or domain-validity status transfers merely because implementation authority moves.
- Unknown readiness, ownership, migration, package, or release facts remain `hmmm`.

## Non-trigger

Do not load this skill for:

- creating an ordinary repository that was independent from inception;
- splitting a repository only for size, permissions, or team organization when no emergent candidate is being graduated;
- publishing a routine new version of an already-independent package;
- vendoring or mirroring code where authority does not change;
- a cross-repository task that only needs coordination; use `interdependent-work-graph` for that.

When graduation will cross repository boundaries, load `interdependent-work-graph` with this skill and use its exact identity, provenance, relation, and non-transfer discipline.

## Lifecycle

Use these states. Do not skip a state by renaming an unfinished candidate.

```text
incubating
    -> stabilizing
    -> qualified
    -> extracted
    -> released
    -> reconsumed
    -> graduated
```

### `incubating`

The candidate is legitimately implemented inside the forge/incubator. Its API may change. The incubator owns implementation authority.

Required evidence:

- candidate name or temporary identifier;
- originating composition and participating projects;
- current owning repository/path;
- purpose and scope;
- unresolved `hmmm`.

### `stabilizing`

The candidate has a coherent purpose and is being separated from incidental incubator structure.

Require:

- explicit public surface;
- explicit private/incubator-only surface;
- permitted upstream dependencies;
- forbidden dependencies or cycles;
- provenance of originating inputs and decisions;
- stated compatibility expectations;
- independent purpose that survives removal from the incubator.

### `qualified`

The candidate has earned extraction readiness.

Require evidence that:

- its public API is explicit enough to version;
- its tests can run without importing incubator-private modules;
- a clean environment can build/install it;
- permitted upstream dependencies resolve through public contracts;
- no hidden path, checkout, editable-install, environment-variable, or local-fixture dependency is required unless deliberately part of the contract;
- license, package metadata, ownership, security, and release boundaries are known or visibly `hmmm`;
- at least one downstream fixture demonstrates the candidate's intended value independently of its source folder location.

Qualification does **not** transfer authority. The incubator remains authoritative until graduation completes.

### `extracted`

Create the independent repository without pretending that a new Git root erases origin.

Preserve:

- relevant history when practical;
- exact source commit and source path used for extraction;
- provenance for copied or transformed material;
- license obligations;
- dependency identities;
- unresolved issues and `hmmm`;
- a migration note stating that the new repository is not yet fully graduated if release/reconsumption remains incomplete.

At this stage the new repository is the intended future authority, but the transition is still in progress.

### `released`

The independent repository produces a versioned artifact through its intended distribution channel.

For a Python package, normally require:

- `pyproject.toml` or equivalent package metadata;
- reproducible wheel/sdist build;
- package tests against the built artifact, not only the source tree;
- version and release notes;
- publication to the selected index, normally PyPI when that is the declared distribution surface;
- install by immutable version in a clean environment.

Do not make PyPI universal doctrine: other ecosystems may use another registry. The invariant is **released artifact through the project's declared distribution surface**.

### `reconsumed`

The forge proves the separation is real by replacing its local implementation path with the released artifact.

Require:

- incubator dependency points at a released version or otherwise immutable released artifact;
- local/source-tree imports of the graduated implementation are removed from the consuming path;
- integration tests run against the released artifact;
- cross-repository behavior remains compatible;
- rollback is defined if the released artifact cannot reproduce the incubated behavior.

A candidate that cannot be reconsumed has not completed graduation.

### `graduated`

Graduation is earned only when all prior gates are evidenced.

Then:

```text
implementation authority: independent repository
incubator relation: consumer/integration forge
released artifact: canonical consumption surface for ordinary downstream use
incubated implementation: removed, archived as provenance, or mechanically unreachable from production/import paths
```

The independent project may continue to depend on its originating projects. Independence means an independent authority and release boundary, not dependencylessness.

## Authority-transfer boundary

Before graduation:

```text
forge owns candidate implementation
candidate consumes upstream authorities
```

After graduation:

```text
new repository owns candidate implementation and public contract
forge consumes candidate through its released interface
upstream repositories retain their own authorities
```

Never write or imply:

```text
graduated from METAPAT/UCNS/EDCM
therefore inherits their semantic/proof/measurement status
```

Repository and package authority are operational boundaries. They do not promote claim status across domains.

## Graduation record

Maintain a small machine- or human-readable record in the incubator or extraction PR. Minimum shape:

```yaml
candidate: <name>
state: <incubating|stabilizing|qualified|extracted|released|reconsumed|graduated>
incubator:
  repository: <owner/name>
  source_commit: <immutable commit>
  source_path: <path>
future_authority:
  repository: <owner/name|hmmm>
distribution:
  kind: <pypi|registry|release-asset|other|hmmm>
  artifact: <name>
  version: <version|hmmm>
upstream:
  - repository: <owner/name>
    relation: <what is consumed>
    authority_transfer: false
gates:
  public_api: <pass|fail|hmmm>
  independent_tests: <pass|fail|hmmm>
  clean_build_install: <pass|fail|hmmm>
  provenance_preserved: <pass|fail|hmmm>
  released_artifact: <pass|fail|hmmm>
  downstream_reconsumption: <pass|fail|hmmm>
hmmm: []
```

This record may be embedded in a richer `interdependent-work-graph` artifact. Do not create a competing graph format when a shared work graph already exists.

## Workflow

1. **Identify the forge and candidate.** State why the candidate is legitimately incubated there and what composition produced it.
2. **Resolve authorities.** Load `interdependent-work-graph` once multiple repositories participate. Pin exact identities and preserve non-transfer boundaries.
3. **Classify lifecycle state.** Choose the highest state for which evidence already exists; do not classify by aspiration.
4. **Stabilize the seam.** Separate public candidate contracts from incubator-private conveniences. Declare allowed upstream dependencies and prohibited cycles.
5. **Run qualification gates.** Test independent purpose, public API, clean build/install, independent tests, provenance, packaging readiness, and downstream fixture behavior.
6. **Extract with provenance.** Create the new repository from the qualified source while preserving origin, history where practical, license, unresolveds, and exact extraction identity.
7. **Release from the new authority.** Build, test, version, and publish the artifact through the declared distribution surface.
8. **Reconsume from the forge.** Replace local implementation consumption with the released artifact and rerun integration evidence.
9. **Sever the old implementation path.** Remove or mechanically disable ordinary consumption of the incubated copy while retaining provenance where useful.
10. **Declare graduation.** Transfer implementation/public-contract authority to the new repository and update work graphs, docs, dependency manifests, and ownership records.
11. **Carry `hmmm`.** Anything unresolved after delivery remains visible and cannot be silently promoted to a passed gate.

## Output shape

When this skill is active, report:

```markdown
## Candidate
- name:
- forge:
- current state:
- intended independent authority:

## Composition and authority
- upstream: exact identity — authority — relation
- non-transfer boundaries:

## Graduation gates
- public API:
- independent tests:
- clean build/install:
- provenance:
- release:
- reconsumption:

## Actions
- now:
- after qualification:
- after release:

## hmmm
- ...
```

## Validation

A successful graduation demonstrates all of the following:

- the candidate's origin and source identity are preserved;
- the candidate has an independently coherent public contract;
- tests and clean installation succeed outside incubator-private paths;
- upstream dependencies are explicit and authority does not silently transfer;
- the independent repository builds the released artifact;
- a clean consumer can install the exact released version;
- the former incubator consumes that released version successfully;
- ordinary local imports of the incubated implementation no longer determine runtime behavior;
- rollback and unresolved `hmmm` remain visible;
- the new repository is the sole implementation/public-contract authority after graduation.

For Python/PyPI graduation, prefer terminal evidence shaped like:

```text
build wheel/sdist -> install exact built/released artifact in clean env -> run project tests -> install exact release in forge -> run forge integration tests
```

## Anti-patterns

- Treating creation of a new repository as proof of graduation.
- Publishing an artifact while the forge still imports its local copy.
- Copying code without preserving source commit/path provenance.
- Freezing an unstable API merely to satisfy a calendar date.
- Requiring an independent project to have zero dependencies.
- Allowing the graduated package to import incubator-private modules.
- Maintaining two writable implementations after graduation with no declared synchronization authority.
- Calling an editable install, local path dependency, or unreleased branch a released consumption path.
- Letting package/repository graduation imply semantic, theorem, proof, measurement, certification, or empirical promotion.
- Deleting unresolved migration problems instead of recording `hmmm`.

## Minimal example

```text
metapat + ucns + edcm
        |
        v
stack/incubator/epac
        |
        | qualification gates pass
        v
The-Interdependency/epac
        |
        | build + version + publish
        v
PyPI epac==X.Y.Z
        |
        | stack installs and integration-tests exact release
        v
EPAC graduated; stack resumes its role as forge/consumer
```

The example describes implementation lifecycle only. METAPAT, UCNS, EDCM, and EPAC each retain the authority and evidentiary status of their own domains.

## hmmm

- Whether the graduation record should later become a versioned schema/helper under this skill or remain a checklist-shaped procedural artifact until several real graduations expose the stable fields.
- Whether history extraction should become deterministic tooling; repository histories differ enough that the skill currently requires provenance preservation without mandating one Git surgery.
- Whether package publication should later split into a separate ecosystem-specific release skill after repeated use proves substantial independent complexity.
- A forge that cannot let go of its products is a warehouse with sparks; a product that cannot survive leaving the forge is still hot metal.

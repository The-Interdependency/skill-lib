---
name: gonol-build
description: Construction, closure, and replay contract for gonols across UCNS and EDCM. Load this when building or reviewing UCNS geometry used by gonols, or building EDCM character, word, definition, or recursive-relation gonols. UCNS owns geometry; EDCM owns text construction and admissible scale options. Closed gonols participate atomically at any admissible consuming scale; no universal adjacent-scale ladder is required. Pronunciation is not required unless an explicitly declared later experiment makes it part of the construction. Do not load for unrelated geometry, ordinary prose editing, or measurement over already-closed gonols.
---

# gonol-build

Use this skill to keep gonol construction on the declared architecture and nothing else.

## Workflow

1. Resolve the current UCNS and EDCM authorities before building.
2. Before launching construction or replay whose completion materially depends on scarce resources, preflight the resources required to finish the declared scope.
3. Resolve the EDCM constructor's declared scale option set and participant eligibility; do not impose a universal adjacent-scale ladder.
4. Close each completed gonol before it participates atomically at an admissible consuming scale.
5. If required UCNS geometry is unresolved, preserve that boundary as `hmmm`.
6. Replay the complete declared scope only where replay is required by the governing protocol.

## Authority

```text
UCNS      = geometry
EDCM      = text-domain gonol construction
skill-lib = construction/replay discipline
```

Resolve the current UCNS and EDCM authorities before building. Do not move text semantics into UCNS or invent geometry in EDCM.

## EDCM construction contract

```text
declared scale option set + eligible already-closed participants -> construction -> closure
```

EDCM owns the admissible scale options. Consult its exact current
`docs/GONOL_LANGUAGE_BOUNDARY.md` and `edcm/gonol.py` contract before selecting
participants. The sequence `characters -> words -> definitions -> recursive
gonol relations` may describe a particular construction, but is not a mandatory
ladder for all EDCM constructions.

- Every admitted character is a gonol.
- Ordered character gonols may close into a word gonol under its declared constructor.
- Any closed gonol is atomic at an admissible consuming scale while its constituent identities, order, multiplicity, source positions, and provenance remain recoverable.
- Definition gonols use eligible closed participants and exact source definition evidence; do not require word intermediates when EDCM admits another scale option.
- Recursive relations are constructed from already-closed gonols without reopening or erasing their internal structure.

Do not invent participant eligibility or another required stage. A permitted
character-to-definition construction must not be rejected solely because it
omits a word intermediate. Nor does this permit every scale combination: the
owning constructor's option set remains load-bearing.

## Pronunciation boundary

Pronunciation is not required for this construction. Pronunciation, phonetic spelling, IPA, audio, or other sound representations must not alter gonol identity, closure, ordering, or relations unless a later explicitly declared experiment makes phonology part of its construction.

Source pronunciation data may remain source metadata. It is not a dependency of the current build.

## Construction invariant

At every scale:

```text
ordered eligible gonols
-> authorized UCNS geometric relation/application
-> closure
-> deterministic identity + provenance receipt
-> atomic participation at an admissible consuming scale
```

Preserve exact source identity, occurrence order, multiplicity, and provenance. Do not normalize, deduplicate, infer relations, or substitute tokens, embeddings, hashes, or another representation for gonol identity unless the active contract explicitly authorizes it.

If required UCNS geometry is unresolved, preserve that boundary as `hmmm`; do not fill it with an invented rule.

## Candidate boundary

An unresolved constructor is permission to construct a named, bounded candidate; it does not block declared experimentation. It blocks promotion beyond the evidence, not construction or testing.

## Completion and replay

Before launching a construction or replay run whose completion materially depends on scarce resources, preflight the resources required to finish it. If the preflight cannot establish enough resource confidence to finish the declared scope, do not start the compute run; record the unresolved resource boundary as `hmmm` or narrow the declared scope under the governing protocol. Once a healthy admitted run begins, let it reach its natural terminal condition unless a genuine safety/resource boundary or preregistered load-bearing stop condition fires. Do not add arbitrary wall-clock limits.

A completion claim requires:

1. exact UCNS, EDCM, source/profile, and constructor identities;
2. the complete declared source scope;
3. deterministic construction receipts; and
4. independent complete replay where replay is required by the governing protocol.

Replay establishes reproducibility of that construction only. It does not by itself establish semantic quality, measurement validity, cognition claims, or canon outside the declared scope.

## Usage guidance

The executable cross-source witness is `gonol-build/check_edcm_boundary.py`.
Run it against a clean EDCM checkout at the script's exact `EDCM_COMMIT`:

```bash
python gonol-build/check_edcm_boundary.py /path/to/edcm
```

It checks direct character-to-definition construction, replay, candidate standing,
and refusal of an undeclared scale. This pinned witness is not a universal scale
registry; current construction must still resolve its owning EDCM option set.

For text construction, start in EDCM and consume current UCNS geometry.

```text
UCNS: geometry
EDCM: declared scale options, participant eligibility, text construction
```

When a gonol closes, use it atomically at any admissible consuming scale. Ignore pronunciation unless a future explicit construction says otherwise.

## Anti-patterns

- Moving text semantics into UCNS or inventing geometry in EDCM.
- Imposing an adjacent-scale ladder or inventing an eligible scale option without EDCM authority.
- Letting pronunciation alter gonol identity, closure, ordering, or relations unless a later explicitly declared experiment makes phonology part of its construction.
- Normalizing, deduplicating, inferring relations, or substituting tokens, embeddings, or hashes for gonol identity unless the active contract explicitly authorizes it.
- Adding arbitrary wall-clock limits to a healthy admitted run.
- Treating replay as semantic quality, measurement validity, cognition, or extra-scope canon.

## hmmm

- exact UCNS geometric operations that remain unresolved in current implementation;
- any future construction that explicitly adds phonology or another stage;
- any recursive relation whose governing source or geometry is not yet established.

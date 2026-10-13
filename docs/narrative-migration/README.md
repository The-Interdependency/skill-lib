# Narrative compression migration

Baseline: `023ae12bb19ced1a4f2494ed6507fc31285a5b8e`.
Governing change: [PR #122](https://github.com/The-Interdependency/skill-lib/pull/122),
merged October 10, 2026 as `19b1988706a91ba305834613facb907cb175ef71`.

This is an editorial implementation of `skill-build`'s narrative invariant.
It changes no product runtime implementation or domain doctrine.
[The inventory](inventory.json) records all 45 canonical skills, their kinds,
families, decisions, and before/after word counts. Generated `skills/` adapters
are discovery projections, not additional canonical skills.

## WDLL decision

FROM: approved compression method with repeated activation, procedural summaries,
and a competing a0p architecture snapshot still present.

TO: one reviewed canonical narrative per skill, executable discovery projections,
conserved schemas/commands/unresolveds, and reviewable migration evidence.

DONE WHEN every canonical skill has a disposition; removed prose has an identified
surviving rule or is non-operative explanation; discovery and generated artifacts
agree; applicable checks and independent reader review expose no migration loss.

PROVEN BY the inventory, preservation fixtures, decision-boundary tests, partial
installation test, independent reader exercise, generated-output checks, and
exact-head CI/review. Local evidence and remote admission remain distinct.

FAILS IF a trigger, non-trigger, permission, exception, requirement, authority,
failure state, or unresolved constraint is lost; if shared references break in a
supported installation; or if a shorter narrative is treated as proof of fidelity.

Selection order follows consequences: test lifecycle routing and authority first,
then inherited metadata contracts, communication/meaning, delivery, and analysis.
No narrative-length threshold determined selection or acceptance.

## Family dispositions

| Family | Migrated | Reviewed and retained | Consequential change |
|---|---:|---:|---|
| Executive and runtime | 6 | 1 | Lifecycle activation and a0p authority; portable org rules; single usage requirement |
| Metadata and generation | 11 | 2 | Remove repeated application introductions; retain native coverage and runner distinctions |
| Meaning and communication | 8 | 2 | Discoverable triggers; preserve domain boundaries and reconstructability |
| Repository and delivery | 8 | 2 | Remove explanatory restatements; retain permission, publication and failure gates |
| Analysis and display | 5 | 0 | One workflow per skill; mandatory independent reproduction survives consolidation |

Totals: 38 migrated, seven retained. Canonical narrative word count changes from
71,871 to 69,121 (2,750 fewer; approximately 3.8%). This is an editorial measurement,
not a token estimate, quality score, or semantic-fidelity metric.

All five families received this pass; none remains unreviewed in this inventory.
A retained skill is an explicit no-change decision, not a claim that no future
compression is possible. Schemas, runtime exit states, non-trigger exceptions,
validation checklists, and examples retain repetition where it changes execution.

## Findings and ownership

- Lifecycle activation was repeated in frontmatter, introduction and trigger lists.
  Consolidate discovery in frontmatter; retain source and runtime requirements in
  their operative sections. Preserve prompt-only exclusions and `_legacy_a0` routing.
- `agent-instantiation` duplicated the a0p architecture despite a dedicated owner.
  Route to `a0p-instancing`; retain its per-user bank, readiness, native-only mode,
  override, persistence, and memory-scoping distinctions. Move the explicit S1–S13
  detail to the owner. Leave naming reconciliation and native-quality uncertainty open.
- Organization usage guidance had overlapping requirements. Consolidate its content
  while retaining runnable examples, invocation, integration, edge cases, limitations,
  and workflow participation.
- Explore/validate-data each had two top-level workflows. Remove the redundant
  exploration summary. Move validation's distinct mandatory reproduction,
  disconfirmation and evidence-standing requirements to their execution points.
- Native-first application introductions repeated their frontmatter and subsequent
  contracts. Remove only those introductions. Do not erase differing domain coverage,
  `PENDING`/`GAP` semantics, unsupported-reader states or supplemental block schemas.
- The reviewed UCNS/EDCM/METAPAT boundaries, permissions and merge requirements are
  not interchangeable concepts. Preserve them rather than deduplicating by vocabulary.

## Verification and limitations

Preservation fixtures bind the baseline's fenced schemas, commands, examples and
Markdown tables, plus final unresolved-boundary text. The only removed fence is
thought-lens's non-executable overview, whose sequence remains in its workflow.
The fixtures are conservation evidence, not a new authoritative home for doctrine.
Update a guard only with an explained contract change; never regenerate it from the
candidate merely to make a failure disappear.

The compliance checker rejects a second top-level `Workflow` section while ignoring
headings inside fenced examples. It does not infer semantic equivalence or reject
purposeful repetition in validation and failure checks.

A fresh reader answered three tasks using the revised lifecycle skills: an a0 child
worker and merge; an a0p native agent; and a prompt-only change. It recovered the
runtime sequence, gates, separate identities, naming `hmmm`, native readiness,
override halt, persistence, architecture exclusion, and non-trigger correctly.
This is a bounded skill-reading exercise; it did not run either external runtime.

Independent diff review found five preservation defects in the draft: unavailable
root-document references after partial vendoring; omitted usage details; stale
root attribution; missing spawn-executor trigger; and missing Harrison Hovel and
interdependentway.org activation anchors. All five were repaired and rechecked.
The shared-reference issue is why portable context/resource rules remain in the
org skill and why char-compress retains standalone distribution guidance.

Local verification used Python 3.13.16 and Node 24.15.0 (the CI-declared minor
and exact Node version). The focused migration/spec/authority selection passed
48 checks. The complete candidate suite ran 569 tests: 560 passed, eight skipped,
and one failed in unchanged VM process-isolation coverage. That test expects
`PermissionError` for a child's `/proc/<parent>/environ` read; this runner returned
`FileNotFoundError`. The same failure reproduced in the full suite at the untouched
baseline; the test passed in isolation there. Treat the cause as unresolved
suite/environment interaction, not a demonstrated migration defect or a passing
gate. The VM code and test remain unchanged. Hosted CI must establish its result.

## UCNS coupling points

Read-only source graph: [work-graph.json](work-graph.json). This proposal changes no
UCNS or METAPAT doctrine and installs no geometry requirement into skill discovery.

UCNS `src/ucns/scale_action.py` supplies a candidate exact operation:
`T_q(x)_i = q^w_i x_i`, for positive rational coordinates and factor, integer
weights. A ratio `x_i/x_j` is invariant when the two weights are equal. More
complex monomials are invariant when their exponent vector has zero weighted sum.

A direct execution of the pinned producer demonstrated:

| Case | Input | Weights | Factor | Output | Ratio |
|---|---|---|---|---|---|
| Coupled scale | `(2, 3)` | `(1, 1)` | `2` | `(4, 6)` | `2/3`, preserved |
| Discriminating control | `(2, 3)` | `(1, 2)` | `2` | `(4, 12)` | `1/3`, changed |
| Inverse | `(4, 6)` | `(1, 1)` | `1/2` | `(2, 3)` | original state recovered |

This exercises the candidate arithmetic only. It is not evidence that prose has
those coordinates or that semantic relations scale multiplicatively.

Useful candidate attachment points for a later declared construction:

| Existing relation | Candidate question | Required evidence |
|---|---|---|
| One authority with several consuming references | Can multiple views refer to one closed object while retaining each consumer's scope? | Reconstruct authority, exceptions and permissions for each occurrence |
| A rule coupled to an exception and a failure witness | Can a relational representation retain polarity and dependency order after compression? | Negation, quantifier, order and exception counterexamples |
| The same bounded relation at different scales | Which explicitly bound coordinate ratios survive the chosen transformation? | Exact producer receipt plus domain-specific invariant and counterexample |

Meaning, participant admission, coordinates, weights and relation eligibility must
be declared by the consuming domain. Geometry belongs to UCNS; METAPAT supplies
cross-domain restraint; measurement questions must be operationalized under EDCM
before claiming a semantic metric. A lexical-overlap score or ordinary dependency
graph is not silently substituted for a gonol construction.

A representative procedural migration makes the preservation test and recovery
pattern reviewable before broad reuse. It does not license an unreviewed bulk
rewrite or reduce the full-library scope to a pilot.

WDLL prioritization entails selecting the blocking cause, stating the transition
and falsifier, completing its dependent surfaces, recording remaining uncertainty,
and submitting evidence for integration. It grants no extra permission to merge.

## Reproduce and continue

Use the Python and Node versions declared by `.github/workflows/ci.yml`, install
its pinned reader/runtime requirements, then run:

```bash
python tools/check_skill_compliance.py --warnings-fail
python tools/check_skill_lib_drift.py --warnings-fail
python tools/build_codex_plugin_skills.py --check
python -m unittest discover -s tests -p 'test_narrative_migration.py'
python -m unittest discover -s tests
bash tools/check_gonol_authority.sh
python ratios/ratios_check.py --strict
python -m llms.build --root . --out llms.txt --check
python -m msdmd.collect --root . --repo The-Interdependency/skill-lib --snapshot-identity --import-path ./msdmd/collection --out skill-lib_msdmd.ts --strict --check
```

To change discovery, edit canonical frontmatter, update the matching `skills.json`
description, and run `python tools/build_codex_plugin_skills.py --apply`.
Regenerate MSDMD after all source and evidence edits. Do not edit its projection.

## hmmm

- Semantic equivalence for every future model/task is not established by these
  fixtures or the bounded reader exercise; preserve this limit in integration review.
- UCNS semantic binding, admissible construction, and lossless reconstruction remain
  candidate work. No geometric compression codec is installed by this migration.
- Remote CI and terminal review at the resulting head are integration evidence;
  this migration does not authorize or claim merge or downstream propagation.

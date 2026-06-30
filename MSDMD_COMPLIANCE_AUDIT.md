# msdmd Compliance Audit — The Interdependency

**Date:** 2026-06-30
**Scope:** 16 org repositories in session scope.
**Method:** Each repo's source tree was walked with the **canonical reference
parser** (`skill-lib/msdmd/parsers/universal.py`) — the same `parse_file` /
`walk_tree` / `ratios_placement` API the runner protocol mandates. Coverage
numbers below are **block-presence** counts (a file is "annotated" if the parser
extracts ≥1 entry of a block type). Vendored `.agents/skills/`, `.github/`,
`.git/`, build/cache dirs, and known legacy/archive trees (`_legacy_a0/`,
`backend_old/`, etc.) were excluded so the figures reflect each repo's **own
modules**, not the reference parsers (which carry their own `ratios:` bookends).

> **⚠️ `a0-betatest` is READ-ONLY.** It is mirrored from Emergent, which
> force-pushes and does not pull cleanly. It is **included in this report** for
> visibility but **must not be modified** here — any commit risks being
> overwritten/lost on the next upstream sync. Treat its row as observe-only.

## What "msdmd compliance" means here

Five independent dimensions, per `msdmd/SKILL.md` and the consuming-repo
CLAUDE.md expectations:

1. **Skill vendored** — `.agents/skills/msdmd/` present (and the application
   skills the repo relies on: `meta-module-build`, `test-build`, …).
2. **Module-local blocks** — source modules declare their blocks
   (`MODULE_BUILD` at minimum; `BOUNDARIES` / `CAPABILITIES` / `CONTRACTS` /
   `DOCS` where the repo's doctrine calls for them). Modules without a block are
   *visible gaps*, not failures — that visibility is the point.
3. **Collection point** — a repo-level `<reponame>_msdmd.ts` aggregation surface
   (msdmd spec says SHOULD).
4. **RATIOS bookends** — the single-line `ratios:` declaration on first/last
   non-blank lines (only for repos that adopt the `ratios` skill).
5. **Parser fidelity** — stdlib-only, unforked parsers (verbatim vendor copies).

## Scorecard

| Repo | Src files | Files w/ ≥1 block | Cov. | msdmd skill | Collection pt | RATIOS (both ends) | Verdict |
|---|---:|---:|---:|:---:|:---:|---:|---|
| **a0-betatest** 🔒 | 170 | 164 | **96%** | ✅ (52 skills) | ❌ | 125 | Best-in-class (read-only) |
| interdependent-lib | 63 | 45 | 71% | ✅ | ❌ | 0 | Good |
| metapat | 6 | 4 | 67% | ✅ (12 skills) | ✅ | 0 | Structural exemplar |
| pcna | 35 | 20 | 57% | ✅ | ❌ | 0 | Moderate |
| eml_ucns | 2 | 1 | 50% | ✅ | ❌ | 0 | Early stub, on track |
| ucns | 123 | 26 | 21% | ✅ | ❌ | 0 | Core annotated; artifacts not |
| edcm | 11 | 2 | 18% | ❌ | ❌ | 0 | **Not onboarded** |
| pcta | 6 | 1 | 17% | ✅ | ❌ | 0 | Entry module only |
| a0 | 503 | 80 | 16%† | ✅ (44 skills) | ❌ | 0† | Own dialect (see note) |
| pcea | 42 | 6 | 14% | ✅ | ❌ | 0 | Engine modules only |
| edcmbone | 189 | 9 | 5% | ✅ | ❌ | 0 | Large repo, low coverage |
| ptca | 24 | 1 | 4% | ✅ | ❌ | 0 | Entry module only |
| aimmh | 188 | 0 | **0%** | ✅ | ❌ | 0 | **Skill vendored, unused** |
| skill-lib | 27 | (n/a) | — | source | ❌ | 4 | Canonical source (see note) |
| zfae | 0 | — | — | ✅ | ❌ | — | Conceptual repo, no code |
| ai-tiw | 0 | — | — | ✅ | ❌ | — | Content archive, no code |

† **a0 uses its own annotation dialect**, not the skill-lib forms — see a0 note.
🔒 read-only mirror; do not modify.

## Per-repo findings

### a0-betatest 🔒 (read-only — do not modify)
Highest compliance in the org: **MODULE_BUILD 164/170, BOUNDARIES 163,
CAPABILITIES 158, CONTRACTS 132 files (151 entries), RATIOS bookends 125/170.**
Vendors 52 skills. This is the de-facto reference for what full module-local
msdmd adoption looks like. **Gap:** no `a0-betatest_msdmd.ts` collection point.
**No action** — Emergent force-pushes overwrite local commits.

### interdependent-lib — Good (71%)
`MODULE_BUILD` on 45/63 files. Vendors `msdmd`, `meta-module-build`,
`test-build`, plus a repo-local `hmmm` skill. Gaps: 18 files without
`MODULE_BUILD`; no `BOUNDARIES`/`CAPABILITIES`/`CONTRACTS` blocks; no collection
point. Reasonable for a meta-package whose primary code is a thin aggregator.

### metapat — Structural exemplar (67%, only collection point in the org)
Small (6 files) but the **only repo with a `metapat_msdmd.ts` collection
point**, and the broadest block diversity: `MODULE_BUILD` (4), `BOUNDARIES` (3),
`CAPABILITIES` (3), `DOCS` (2), `CONTRACTS` (2/7 entries), `DEPENDENCIES` (2),
`OWNERS` (3). Vendors 12 skills. This is the template other repos should copy
for collection-point + multi-block structure.

### pcna — Moderate (57%)
`MODULE_BUILD` on 20/35 files. No `BOUNDARIES`/`CAPABILITIES`/`CONTRACTS`
despite being an engine with clear risk surfaces (backend server, MongoDB).
Candidate for `risk-boundary-build` adoption.

### ucns — Core annotated, artifacts not (21%)
`MODULE_BUILD` on 26/123. The low ratio is expected: `code/` versioned
artifacts, root `*_probe*.py`, and the v0.6.5 snapshot are **explicitly
read-only research artifacts** (per CLAUDE.md) and legitimately carry no blocks.
Effective coverage of *live* engine modules is far higher than 21% implies.
Worth excluding artifact dirs from any future runner config so the gap list is
honest.

### a0 — Own dialect, not the skill-lib forms (16% by skill-lib parser)
a0 deliberately uses **its own annotation conventions**, so the skill-lib parser
under-counts it:
- **Ratios:** a0 stamps `# N:M C:D I:O` (code:comment, consumed:declared,
  fan-in:fan-out) via `scripts/annotate.py` on every file's first/last line —
  **not** the skill-lib `ratios:` line. Hence RATIOS-both-ends reads 0 even
  though a0 has near-universal bookend annotation in its own format.
- **Docs:** a0 route modules carry `# DOC` header comments, **not** `DOCS`
  blocks.
- **Contracts:** measured `CONTRACTS` on 8 files (34 entries) via
  `python/tests/contracts/`; `MODULE_BUILD` on 76 files.
This is a genuine **dialect divergence**: a0's self-declaration is real and
enforced (contract runner, console-tab guard, 400-line budget), but it is not
the canonical skill-lib block forms. Decision needed (see Recommendations):
treat a0's dialect as a sanctioned variant, or reconcile toward the canonical
`ratios:`/`DOCS` forms.

### pcea (14%), ptca (4%), pcta (17%)
Stack libraries: `MODULE_BUILD` present only on the entry/constants module(s)
(pcea 6/42, ptca 1/24, pcta 1/6). Skills vendored but adoption is shallow.
These are small, stable, security/structure-critical libraries; adding
`BOUNDARIES` (pcea is crypto) and broader `MODULE_BUILD` coverage would be
high-value, low-effort.

### edcmbone — Large repo, low coverage (5%)
`MODULE_BUILD` 9, `BOUNDARIES` 1, `DOCS` 1, `CONTRACTS` 1 (4 entries),
`DEPENDENCIES` 1 across 189 files. Much of the tree is in-progress migration
(`edcmbone/` root + `core/` stubs) and frozen canon — but the canonical
`backend/src/edcmbone/` package itself is largely un-annotated. Biggest
absolute gap in the org by un-annotated file count.

### aimmh — Skill vendored but unused (0%)
**188 source files, zero msdmd blocks.** `msdmd`/`meta-module-build`/
`test-build` are vendored but no module declares anything. Highest-leverage
onboarding target: the backend `routes/` + `services/` + `aimmh_lib/` would
benefit directly from `MODULE_BUILD` + `CONTRACTS`.

### edcm — Not onboarded (18%, no skills vendored)
Only repo (besides skill-lib) with **no `.agents/skills/` at all**. 2/11 files
carry `MODULE_BUILD` (likely hand-written). Consistent with its
"dependency-free, no tooling" stance, but it is the one consuming repo that has
not vendored the skill library at all.

### eml_ucns — Early stub, on track (50%)
1/2 files annotated; the bridge is an admitted stub. Fine for its stage.

### zfae, ai-tiw — N/A (no executable source)
zfae is a conceptual/spec repo (no runtime code yet); ai-tiw is a content
archive. Both correctly vendor the skill set for future use; nothing to annotate
today. Compliant by absence.

### skill-lib — Canonical source (not a consumer)
27 own source files (parsers, `tools/`, `llms/`). As the editorial source it is
**not** expected to carry `MODULE_BUILD` on its tools. It does carry `DOCS` (2)
and `LLMS` (2) blocks and 4 `ratios:` bookends (the reference parsers).
Compliant in its role.

## Systemic findings

1. **Collection points are almost entirely missing.** Only `metapat` has a
   `<reponame>_msdmd.ts`. The msdmd spec marks this SHOULD; 15/16 repos lack the
   aggregation surface, so no repo-level visualizer can render the module graph.
2. **RATIOS adoption is isolated.** Only `a0-betatest` (skill-lib form) and `a0`
   (own `N:M C:D I:O` form) bookend files; everyone else has zero.
3. **Vendored ≠ used.** `aimmh` (0%), `ptca`/`pcta` (~1 file), and `edcmbone`
   (5%) vendor the skills but barely apply them. The skill being present is not
   compliance; declared blocks are.
4. **One dialect fork (a0).** a0's self-declaration is substantive but diverges
   from the canonical block forms — the one place the "don't fork the
   convention" doctrine is under tension.
5. **Coverage % needs artifact-aware denominators.** ucns/edcmbone percentages
   are depressed by read-only research artifacts and migration stubs that
   legitimately carry no blocks. A per-repo runner `skip`/`extensions` config
   would make the gap list trustworthy.

## Recommendations (no changes made by this audit)

Ranked by leverage; none touch `a0-betatest`:

1. **aimmh** — onboard `MODULE_BUILD` + `CONTRACTS` across `routes/` and
   `services/`; it has the skills but 0 usage on 188 files.
2. **Collection points** — run the prototype generator
   `python -m msdmd.collect --root . --repo <name> --out <name>_msdmd.ts` in
   each consuming repo (metapat is the worked example).
3. **edcmbone** — annotate the canonical `backend/src/edcmbone/` package
   (currently 9/189).
4. **pcea / ptca / pcta** — extend beyond the entry module; add `BOUNDARIES` to
   `pcea` (crypto surfaces).
5. **a0 dialect decision** — explicitly sanction a0's `N:M C:D I:O` + `# DOC`
   forms as a documented variant, **or** reconcile toward canonical
   `ratios:`/`DOCS`. Record the choice in `ORG_DISTRIBUTION.md` so the fork is
   intentional, not drift.
6. **edcm** — decide whether it vendors the skill set at all (currently none).
7. **Runner configs** — give ucns/edcmbone artifact/stub skip lists so coverage
   gap lists are honest.

## Audit scope & limits (hmmm)

- This measures **block presence** via the canonical parser, not **executor
  validity** — required-field checks, `call:` target resolution, and contract
  *execution* were not run. A file counted "annotated" may still have an
  incomplete entry.
- Percentages are over all `.py/.ts/.tsx/.js/.jsx` files after the skip list; a
  per-repo runner with the repo's own skip config would refine ucns/edcmbone.
- No claim of theorem/proof/metric status is implied for any repo by this
  editorial audit.

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
4. **RATIOS bookends** — `ratios` is the **one declaration that is NOT a fenced
   block**: it is a single `ratios:` comment line carried on the file's **first
   and last non-blank lines** (`<marker> ratios: loc_comments=N:M
   imports_exports=N:M calls_definitions=N:M`). Measured here with
   `ratios_placement`, which checks first/last placement — not a block parse.
   **Every executable source file needs this bookend** (per the `ratios` skill:
   all executable `.py/.ts/.js/…`, but **not** `.json` or `.md`). A file with no
   `ratios:` line — or with it on only one end — is a gap, not exempt. So the
   "RATIOS (both ends)" column should be read against each repo's executable
   file count, where the target is 100%.
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
| a0 | 503 | 80 | 16%† | ✅ (44 skills) | ❌ | 0† | Canonical seal origin (see note) |
| pcea | 42 | 6 | 14% | ✅ | ❌ | 0 | Engine modules only |
| edcmbone | 189 | 9 | 5% | ✅ | ❌ | 0 | Large repo, low coverage |
| ptca | 24 | 1 | 4% | ✅ | ❌ | 0 | Entry module only |
| aimmh | 188 | 0 | **0%** | ✅ | ❌ | 0 | **Skill vendored, unused** |
| skill-lib | 27 | (n/a) | — | source | ❌ | 15/15 ✅ | Canonical source; ratios fixed in this PR |
| zfae | 0 | — | — | ✅ | ❌ | — | Conceptual repo, no code |
| ai-tiw | 0 | — | — | ✅ | ❌ | — | Content archive, no code |

† **a0's `N:M C:D I:O` annotation is the canonical ratios seal** — the skill-lib
`ratios:` form is the portable adaptation; the parser reads 0 here by design. See a0 note.
🔒 read-only mirror; do not modify.

## Per-repo findings

### a0-betatest 🔒 (read-only — do not modify)
Highest compliance in the org: **MODULE_BUILD 164/170, BOUNDARIES 163,
CAPABILITIES 158, CONTRACTS 132 files (151 entries), RATIOS bookends 125/170.**
Vendors 52 skills. This is the de-facto reference for what full module-local
msdmd adoption looks like. Verified that the RATIOS bookends are the **correct
single-line `# ratios:` form** on first/last lines (e.g. `backend/api_extensions.py`),
**not** fenced blocks. **Doc bug (cannot fix — read-only):** a0-betatest's own
`CLAUDE.md` says ratios are "bookended via `# === RATIOS ===`" — there are zero
such fenced blocks in the repo; the canonical form (and the actual usage) is the
single line. **Gap:** no `a0-betatest_msdmd.ts` collection point. **No action** —
Emergent force-pushes overwrite local commits.

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

### a0 — the canonical origin of the ratios seal (16% by skill-lib parser)
a0 uses **its own annotation conventions**, so the skill-lib parser under-counts
it — but the framing is the reverse of a "fork": **a0 is the canonical origin**;
the skill-lib `ratios:` form is the later, portable reinvention.
- **Ratios:** a0 stamps `# N:M C:D I:O` (code:comment, consumed:declared,
  fan-in:fan-out) via `scripts/annotate.py` on every file's first/last line.
  This **is the canonical seal** (settled by the maintainer); the skill-lib
  `ratios:` line is a per-file adaptation for standalone libraries. The
  skill-lib parser reads 0 here because it deliberately only parses the named
  form — expected, not a gap.
- **Docs:** a0 route modules carry `# DOC` header comments, **not** `DOCS`
  blocks.
- **Contracts:** measured `CONTRACTS` on 8 files (34 entries) via
  `python/tests/contracts/`; `MODULE_BUILD` on 76 files.
a0's self-declaration is real and enforced (annotate.py + contract runner,
console-tab guard, 400-line budget). **Resolved:** a0 is canon; the named
`ratios:` form is documented as the portable adaptation in `ratios/SKILL.md`.
No conversion of a0 is required.

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

### skill-lib — Canonical source (not a consumer); ratios now complete ✅
27 own source files. As the editorial source it is **not** expected to carry
`MODULE_BUILD` on its tools; it does carry `DOCS` (2) and `LLMS` (2) blocks.
**RATIOS — fixed in this PR.** Every executable source file needs the single-line
`ratios:` bookend. `ratios_check.py`'s own scope (it skips `tests/`) is 15 files;
previously only 4 carried the bookend. This PR stamped the remaining **11** using
`ratios_check.py`'s own compute functions, so `python ratios/ratios_check.py
--strict` now reports **15/15 covered, 0 gaps, 0 drift, 0 misplaced**:
`manifest/generate.py`, `llms/{__init__,build,metadata}.py`,
`tools/{char_compress_check,check_skill_compliance,check_skill_lib_drift,propagate_skills}.py`,
`msdmd/{collect,visualize}.py`, `msdmd/collection.ts`. Because placement is
strict (ratios on the first non-blank line), the **shebangs were removed from the
5 affected scripts** (`manifest/generate.py` + the 4 `tools/`) to match the
a0-betatest convention (no shebangs; everything is invoked via `python …`/`-m`,
per CLAUDE.md). All 52 skill-lib tests still pass and `llms.txt` shows no drift.
(`tests/` files are out of the checker's scope, so they were left unstamped.)

## Systemic findings

1. **Collection points are almost entirely missing.** Only `metapat` has a
   `<reponame>_msdmd.ts`. The msdmd spec marks this SHOULD; 15/16 repos lack the
   aggregation surface, so no repo-level visualizer can render the module graph.
2. **RATIOS is a near-org-wide gap.** Recall ratios is a single `ratios:` line on
   first/last non-blank lines (not a block) and **every executable source file
   needs it**. Measured against that bar, only `a0-betatest` (correct single-line
   `# ratios:` form, 125/170) and `a0` (its own single-line `N:M C:D I:O` form)
   carry bookends at scale; **skill-lib itself was only 4/15 — now fixed to
   15/15 in this PR** — and every other repo is at zero. This is the largest
   systemic gap after collection points:
   the overwhelming majority of executable files across the org are missing the
   required bookend. (Aside: a0-betatest's CLAUDE.md mis-documents the form as a
   fenced `=== RATIOS ===` block — it isn't.)
3. **Vendored ≠ used.** `aimmh` (0%), `ptca`/`pcta` (~1 file), and `edcmbone`
   (5%) vendor the skills but barely apply them. The skill being present is not
   compliance; declared blocks are.
4. **a0 is the canonical seal origin (not a fork).** a0's `N:M C:D I:O`
   first/last-line annotation predates and is the canon for the ratios seal; the
   skill-lib `ratios:` form is the portable per-file adaptation. Resolved in
   `ratios/SKILL.md` — no tension, no conversion needed.
5. **Coverage % needs artifact-aware denominators.** ucns/edcmbone percentages
   are depressed by read-only research artifacts and migration stubs that
   legitimately carry no blocks. A per-repo runner `skip`/`extensions` config
   would make the gap list trustworthy.

## Recommendations (no changes made by this audit)

Ranked by leverage; none touch `a0-betatest`:

1. **Ratios bookends on every executable.** Every executable `.py/.ts/.js/…`
   file (not `.json`/`.md`) needs the single-line `ratios:` bookend on its first
   and last non-blank lines. Use the `ratios` skill's `ratios_check.py` to
   recompute and stamp values, then gate it in CI like a0/a0-betatest do.
   **skill-lib's own gap is fixed in this PR (now 15/15);** the consuming repos
   are next. Note ratios placement is strict (first non-blank line), so scripts
   that need a shebang must instead be invoked via `python …`/`-m` (the org
   convention) — plan for that when stamping repos that ship CLI shebangs.
2. **aimmh** — onboard `MODULE_BUILD` + `CONTRACTS` across `routes/` and
   `services/`; it has the skills but 0 usage on 188 files.
2. **Collection points** — run the prototype generator
   `python -m msdmd.collect --root . --repo <name> --out <name>_msdmd.ts` in
   each consuming repo (metapat is the worked example).
3. **edcmbone** — annotate the canonical `backend/src/edcmbone/` package
   (currently 9/189).
4. **pcea / ptca / pcta** — extend beyond the entry module; add `BOUNDARIES` to
   `pcea` (crypto surfaces).
5. **a0 ratios canon — RESOLVED.** a0's `N:M C:D I:O` annotation is the
   canonical ratios seal; the named `ratios:` form is documented as the portable
   per-file adaptation in `ratios/SKILL.md`. a0 is not converted; already-stamped
   libraries keep the named form (grandfathered). Open follow-up: porting a0's
   repo-wide `C:D`/`I:O` index into a shared checker so the canonical metrics are
   verifiable outside a0 (today only `N:M`/`loc_comments` is per-file checkable).
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

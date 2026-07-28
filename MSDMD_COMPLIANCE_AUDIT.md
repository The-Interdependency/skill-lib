# msdmd Compliance Audit — The Interdependency

**Date:** 2026-07-26 (supersedes the 2026-06-30 audit; deltas noted throughout)
**Scope:** 18 org repositories in session scope.
**Method:** Each repo's source tree was walked with the **canonical reference
parser** (`skill-lib/msdmd/parsers/universal.py`) — the same `parse_file` /
`walk_tree` / `ratios_placement` API the runner protocol mandates. Coverage
numbers below are **block-presence** counts (a file is "annotated" if the parser
extracts ≥1 entry of a block type). Vendored `.agents/skills/`, `.github/`,
`.git/`, build/cache dirs, and known legacy/archive trees (`_legacy_a0/`,
`backend_old/`, `test_reports/`, vendored `skill-lib/` copies) were excluded so
the figures reflect each repo's **own modules**, not the reference parsers
(which carry their own `ratios:` bookends).

> **⚠️ `a0-betatest` is READ-ONLY.** It is mirrored from Emergent, which
> force-pushes and does not pull cleanly. It is **included in this report** for
> visibility but **must not be modified** here — any commit risks being
> overwritten/lost on the next upstream sync. Treat its row as observe-only.

> **Scope changes since 2026-06-30:** `pcna`/`pcta`/`ptca` were consolidated
> into the single **`ptcna`** repo; **`a0ucns`**, **`odysseus-a0`**,
> **`scared-sacred`**, and **`The-Interdependency.github.io`** entered session
> scope. `a0ucns` is an integration workspace whose `a0-betatest/`, `aimmh/`,
> and `odysseus-a0/` trees are **verbatim mirrors of upstream repos** — those
> trees are excluded from its row so siblings are not double-counted; its own
> content is the `archive/` tree (the pre-restructure a0 platform copy).

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
   file count, where the target is 100%. (a0's `N:M C:D I:O` first/last-line
   seal is the canonical origin form and is counted separately in its row.)
5. **Parser fidelity** — stdlib-only, unforked parsers (verbatim vendor copies).

## Scorecard

| Repo | Src files | Files w/ ≥1 block | Cov. | msdmd skill | Collection pt | RATIOS (both ends) | Verdict |
|---|---:|---:|---:|:---:|:---:|---:|---|
| **scared-sacred** ⭐ | 16 | 16 | **100%** | ✅ (7 skills) | ❌ | 16/16 ✅ | New — first repo at 100% blocks + 100% ratios |
| **a0-betatest** 🔒 | 184 | 176 | **96%** | ✅ (53 skills) | ✅ *(new)* | 112 | Best-in-class at scale (read-only) |
| metapat | 36 | 33 | 92% | ✅ (13 skills) | ✅ | 0 | Structural exemplar; grew 6→36 files |
| edcm | 88 | 55 | 62% | ⚠️ (2 skills, **no msdmd**) | ✅ *(new)* | 0 | Onboarded since June (was 18%, no skills) |
| interdependent-lib | 100 | 52 | 52% | ✅ (5 skills) | ✅ *(new)* | 39 | Good; ratios started |
| ucns | 198 | 77 | 39% | ✅ (7 skills) | ❌ | 12 | Improved (21%→39%); CONTRACTS/CHECKS live |
| The-Interdependency.github.io | 8 | 3 | 38% | ❌ | ❌ | 0 | Newly scoped; not onboarded |
| eml_ucns | 3 | 1 | 33% | ✅ (4 skills) | ✅ *(new)* | 0 | Early stub, on track |
| ptcna | 52 | 15 | 29% | ❌ | ❌ | 29 | **Consolidation dropped the vendored skills** |
| odysseus-a0 | 820 | 228 | 28% | ❌ | ❌ | 0 | Newly scoped; real block adoption, no vendoring |
| a0 | 505 | 80 | 16%† | ✅ (45 skills) | ✅ *(new)* | 0† (489 canonical seals) | Canonical seal origin (see note) |
| pcea | 43 | 6 | 14% | ✅ (5 skills) | ✅ *(new)* | **42** | Ratios nearly complete; blocks still shallow |
| zfae | 15 | 2 | 13% | ✅ (5 skills) | ✅ *(new)* | 9 | First runnable code (vernacular_floor) |
| edcmbone | 190 | 9 | 5% | ✅ (6 skills) | ✅ *(new)* | 66 | Ratios progress; block adoption stalled |
| a0ucns | 503\* | 10 | 2%\* | ❌ | ❌ | 0 | Integration workspace (archive-only count) |
| aimmh | 189 | 0 | **0%** | ✅ (4 skills) | ❌ | 58 | **Still zero blocks**; ratios stamped anyway |
| skill-lib | 41 | (n/a) | — | source | ✅ *(new)* | 21/21 ✅ (checker scope) | Canonical source; all 8 CI gates green |
| ai-tiw | 0 | — | — | ✅ (4 skills) | ❌ | — | Content archive, no code |

† **a0's `N:M C:D I:O` annotation is the canonical ratios seal** — the skill-lib
`ratios:` form is the portable adaptation; the named-form parser reads 0 here by
design, while the canonical seal is present on **489/505** files. See a0 note.
\* a0ucns counted over its own content only (`archive/`); the mirrored
`a0-betatest/`, `aimmh/`, `odysseus-a0/` trees are excluded (source of truth
stays upstream, per its README and `CONNECTIONS.md`).
🔒 read-only mirror; do not modify. ⭐ new entrant.

## What moved since 2026-06-30

1. **Collection points: 1 → 11 repos.** June's largest systemic gap is largely
   closed. `metapat` was the only repo with a `<reponame>_msdmd.ts`; now
   a0-betatest, edcm, interdependent-lib, eml_ucns, a0, pcea, zfae, edcmbone,
   and skill-lib itself all carry one. Still missing: scared-sacred, ucns,
   aimmh, ptcna, odysseus-a0, a0ucns, ai-tiw, github.io.
2. **Ratios bookends spread beyond the three origin repos.** June measured zero
   named-form bookends outside a0-betatest and skill-lib. Now: pcea 42/43,
   edcmbone 66, aimmh 58, interdependent-lib 39, ptcna 29, scared-sacred 16/16,
   ucns 12, zfae 9. Still at zero: metapat, edcm, odysseus-a0, a0ucns,
   github.io.
3. **edcm onboarded.** Was "not onboarded" (18%, no `.agents/skills/` at all);
   now 62% block coverage, an `edcm_msdmd.ts` collection point, CHECKS-bearing
   tests — but it vendors only `meta-module-build` + `the-interdependency`,
   **not `msdmd` itself**, so its vendored doctrine chain dead-ends (see
   systemic finding 3).
4. **The prime-tensor consolidation lost its vendoring.** `pcna` (57%, skills
   vendored) + `pcta` (17%) + `ptca` (4%) became `ptcna` — which has **no
   `.agents/skills/` directory at all**. 15/52 files carry `MODULE_BUILD` and
   29 carry ratios bookends, so the practice partially survived the migration,
   but the skill source did not.
5. **metapat scaled without dilution.** 6 → 36 files while holding 92% coverage
   and the broadest block diversity in the org (MODULE_BUILD 20, BOUNDARIES 10,
   CAPABILITIES 10, CONTRACTS 15, CHECKS 13, DOCS 9, DEPENDENCIES 2, OWNERS 3).
6. **aimmh did not move on blocks.** 189 files, still **zero** msdmd blocks —
   the same highest-leverage gap June named. Notably, 58 files *did* get ratios
   bookends, so the repo is being touched by compliance work; the block half
   simply hasn't happened.

## Per-repo findings

### scared-sacred ⭐ — first 100%/100% repo
16/16 files annotated (MODULE_BUILD 9, CONTRACTS 6, CHECKS 7) and 16/16 ratios
bookends. Vendors 7 skills including `msdmd` and a `doctrine/` dir. Small, but
it proves the full stack — blocks + bookends + vendoring — lands cleanly in a
new repo. Missing only a collection point.

### a0-betatest 🔒 (read-only — do not modify)
Still best-in-class at scale: MODULE_BUILD 169, BOUNDARIES 169, CAPABILITIES
166, CONTRACTS 136, CHECKS 7 across 184 files; 112 ratios bookends; 53 vendored
skills; and it now has the `a0-betatest_msdmd.ts` collection point June flagged
as missing. **Doc bug persists (cannot fix — read-only):** its `CLAUDE.md`
still says ratios are "bookended via `# === RATIOS ===`" fenced blocks; the
actual (and canonical) usage in-tree is the single-line `# ratios:` seal.

### metapat — structural exemplar, now at scale (92%)
See delta 5. Remains the worked example for collection-point + multi-block
structure; the only gap left is ratios bookends (0/36).

### edcm — onboarded, but the chain dead-ends (62%)
49 files with `MODULE_BUILD`, CHECKS on 6 test modules, a collection point, and
`edcm_msdmd.ts` generated. But `.agents/skills/` holds only `meta-module-build`
and `the-interdependency`; `meta-module-build/SKILL.md` opens by pointing at
`../msdmd/SKILL.md`, which is not vendored. Add `msdmd` (and `test-build`,
since CHECKS blocks are in use) to make the vendored set self-contained.

### interdependent-lib — good (52%), ratios started
`MODULE_BUILD` on 52/100 files, CONTRACTS on 2, 39 ratios bookends, collection
point present. The file count grew 63→100 (new skills/tests); coverage in
percentage terms dipped (71%→52%) purely from the larger denominator.

### ucns — improved (21% → 39%)
MODULE_BUILD 61, CONTRACTS 18, CHECKS 16 over 198 files; 12 ratios bookends.
The `verify_skill_lib_contracts.py` gate is in its required-gates list. Still
no collection point, and the artifact/probe trees still depress the
denominator — the per-repo skip-list recommendation from June stands.

### The-Interdependency.github.io — newly scoped, not onboarded (38%)
8 executable files (site tooling), 3 with MODULE_BUILD, 1 BOUNDARIES. No
`.agents/skills/`, no collection point, no ratios. Low file count keeps this
low-priority, but it is now the *second* repo (after ptcna) with real code and
no vendored skills.

### ptcna — consolidation dropped the vendoring (29%)
See delta 4. Highest-priority vendoring fix: it is the canonical prime-tensor
stack repo, it demonstrably uses the conventions (15 MODULE_BUILD files, 29
ratios bookends), and it has nowhere in-repo to read them from.

### odysseus-a0 — newly scoped; adoption without vendoring (28%)
228/820 files carry MODULE_BUILD + BOUNDARIES + CAPABILITIES (uniformly — the
annotated subset carries all three), CONTRACTS on 2. No `.agents/skills/`, no
collection point, no ratios bookends. The large unannotated remainder is mostly
vendored/adapted third-party surface (opencode, DeepResearch adaptations, UI).
Needs a skip-list decision before its gap list is meaningful.

### a0 — the canonical origin of the ratios seal (16% by named-form parser)
Unchanged framing from June: a0 stamps the **canonical** `# N:M C:D I:O` seal
via `scripts/annotate.py` — now measured at **489/505 files** — plus `# DOC`
headers and contract-runner CONTRACTS (8 files). MODULE_BUILD on 76 files. The
named `ratios:` form reads 0 here **by design**; no conversion is wanted. New
since June: an `a0_msdmd.ts` collection point.

### pcea — ratios nearly complete, blocks shallow (14%)
42/43 files carry ratios bookends (the repo's own `ratios:` seal + provenance
header discipline is CI-gated via `test_metadata_headers.py`). MODULE_BUILD
remains on only 6/43 files. June's recommendation stands: extend MODULE_BUILD
beyond the entry modules and add `BOUNDARIES` — it is the org's crypto surface.

### zfae — first runnable code (13%)
The `vernacular_floor` scaffold landed with 2 MODULE_BUILD files, 9 ratios
bookends, a collection point, and its own contract tests. Consistent with its
"conceptual home + one scaffold" charter.

### edcmbone — ratios moving, blocks stalled (5%)
66 ratios bookends (was 0) and a collection point are new; block adoption is
unchanged (9/190). Still the biggest absolute un-annotated file count after the
newly-scoped giants. The canonical `backend/src/edcmbone/` package remains the
target.

### a0ucns — integration workspace (2% own content)
Own content = `archive/` (the pre-restructure a0 platform copy; 10 files with
CONTRACTS) plus root docs. The mirrored sibling trees are excluded here.
As an integration-design workspace whose README says "the source of truth stays
upstream," block compliance belongs upstream; no vendoring action recommended
until it grows first-party modules outside `archive/`.

### aimmh — still the standout gap (0%)
**189 source files, zero msdmd blocks, unchanged since June** — despite 58
files now carrying ratios bookends and 4 skills vendored. Highest-leverage
onboarding target in the org, same as last audit: `routes/`, `services/`, and
`aimmh_lib/` want `MODULE_BUILD` + `CONTRACTS`.

### eml_ucns, ai-tiw
`eml_ucns`: 1/3 files annotated, bridge still an admitted stub — fine for its
stage, and it gained a collection point. `ai-tiw`: content archive, no
executable source; compliant by absence.

### skill-lib — canonical source; all gates green
41 own source files (growth from new skill helpers). As the editorial source it
is not expected to carry `MODULE_BUILD` on its tools; it carries DOCS (2), LLMS
(2), CONTRACTS/CHECKS (RepoLOTO), MODULE_BUILD (2). `ratios_check.py --strict`
reports **21/21 covered, 0 gaps, 0 drift, 0 misplaced** in its own scope; the
full CI matrix (108 unit tests, drift, compliance, Codex adapters, llms-build,
RepoLOTO 7/7) was re-run green at `df5f6ba` (2026-07-25). It now also ships its
own `skill-lib_msdmd.ts` collection point.

## Systemic findings

1. **The propagation gap is closing, unevenly.** June's two biggest systemic
   gaps — collection points (1→11 repos) and ratios bookends (3→11 repos with
   ≥1) — both moved substantially. What has *not* moved is deep block adoption
   in the large consumer repos: aimmh (0%), edcmbone (5%), and a0's Python tree
   (16%) are where the un-annotated file mass lives.
2. **Ratios adoption is outpacing block adoption.** pcea (42 bookends, 6
   MODULE_BUILD), aimmh (58 bookends, 0 blocks), and edcmbone (66 bookends, 9
   blocks) show the seal being stamped without the declarations. The bookend is
   mechanical; the blocks require thought — expected, but worth naming so
   "ratios done" is not mistaken for "msdmd done."
3. **Vendoring integrity regressed in three places.** (a) `ptcna` lost the
   skills in the pcna/pcta/ptca consolidation; (b) `edcm` vendored application
   skills without `msdmd`, so its doctrine chain points at a missing file;
   (c) `odysseus-a0` adopted the blocks with no vendored source at all. All
   three are one `propagate_skills.py` run each. `consumer-drift.yml` catches
   *drifted* copies but not *absent* ones — a repo with no `.agents/skills/` is
   invisible to it.
4. **Vendored ≠ used, still.** aimmh remains the canonical case: 4 skills
   vendored, 189 files, zero declarations, four weeks later.
5. **a0 is the canonical seal origin (settled).** 489/505 files carry the
   `N:M C:D I:O` seal; the named `ratios:` form remains the portable
   adaptation. No tension, no conversion.
6. **Coverage % still needs artifact-aware denominators.** ucns, edcmbone,
   odysseus-a0, and a0ucns percentages are all depressed by artifact, vendored,
   or migration trees. Per-repo runner `skip`/`extensions` configs remain the
   fix so gap lists are honest.

## Recommendations (no changes made by this audit)

Ranked by leverage; none touch `a0-betatest`:

1. **Re-vendor where the chain is broken** — one `propagate_skills.py` run
   each: `ptcna` (full set), `edcm` (add `msdmd`, `test-build`),
   `odysseus-a0` (msdmd + meta-module-build + ratios at minimum). Extend
   `consumer-drift.yml`'s repo list to cover the newly-scoped repos so absence
   is at least reported per-repo.
2. **aimmh blocks** — unchanged from June, now with sharper contrast: the repo
   accepted 58 ratios bookends, so compliance work *is* landing there; direct
   the next pass at `MODULE_BUILD` + `CONTRACTS` on `routes/` + `services/` +
   `aimmh_lib/`.
3. **Finish ratios where it is nearly done** — pcea is at 42/43; edcmbone,
   interdependent-lib, and ucns have momentum. metapat and edcm are the two
   compliant-on-blocks repos at zero bookends.
4. **Collection points for the stragglers** — scared-sacred, ucns, aimmh,
   ptcna, odysseus-a0 (`python -m msdmd.collect --root . --repo <name> --out
   <name>_msdmd.ts`).
5. **edcmbone canonical package** — annotate `backend/src/edcmbone/`
   (unchanged since June; 9/190).
6. **Skip-list configs** for ucns, edcmbone, odysseus-a0, a0ucns so
   denominators reflect first-party live code.
7. **a0-betatest CLAUDE.md ratios wording** — the fenced-block description is
   still wrong; fix upstream in Emergent (the mirror cannot be edited here).

## Audit scope & limits (hmmm)

- This measures **block presence** via the canonical parser, not **executor
  validity** — required-field checks, `call:` target resolution, and contract
  *execution* were not run. A file counted "annotated" may still have an
  incomplete entry.
- Percentages are over all `.py/.ts/.tsx/.js/.jsx` files after the skip list; a
  per-repo runner with the repo's own skip config would refine ucns, edcmbone,
  odysseus-a0, and a0ucns.
- `a0ucns` mirrors and `odysseus-a0` vendored/adapted trees blur "own modules";
  their rows are best-effort pending per-repo skip decisions.
- Repo trees were read from fresh session checkouts on 2026-07-26; `a0-betatest`
  numbers can shift on any upstream force-push.
- No claim of theorem/proof/metric status is implied for any repo by this
  editorial audit.

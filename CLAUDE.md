# CLAUDE.md — skill-lib

AI-assistant guidance for `The-Interdependency/skill-lib`.

## Core facts

- `skill-lib` is the canonical organization-wide source for reusable agent skills.
- Other The Interdependency repos vendor repo-local copies from here.
- Edit skills here first; propagate later with the source commit SHA.
- License: MPL-2.0 (relicensed from MIT; weak/file-level copyleft — embed anywhere, changes to these files must be published).
- Entry points: `README.md`, `AGENTS.md`, `skills.json`, `ORG_DISTRIBUTION.md`, `llms.txt`, each `<skill>/SKILL.md`.
- No package manifest, Makefile, package.json, or pyproject.toml is declared here. The only CI is `.github/workflows/hygiene.yml`, a narrow guard that fails any push/PR carrying tracked Python bytecode (`*.pyc`/`__pycache__`); it does not run the editorial helper tools.
- Validation here is editorial plus optional pure-stdlib helper scripts in `tools/`.
- The `llms/` package exists only to expose the stdlib `python -m llms.build` runner for `llms-build`.

## Layout

```text
README.md              # human-facing overview and skill index
AGENTS.md              # agent-facing entry point
ORG_DISTRIBUTION.md    # canonical-source rule, target repos, propagation rule
skills.json            # machine-readable skill index
llms.txt               # generated root LLM instructions from LLMS blocks
CLAUDE.md              # assistant guidance
LICENSE                # MPL-2.0
tools/README.md        # local maintenance helper documentation
tools/*.py             # pure-stdlib helper scripts
llms/                  # python -m llms.build reference runner
<skill-name>/SKILL.md  # required skill spec
<skill-name>/<helpers> # optional parsers, runners, examples
```

## Skills

| Skill | Kind | Depends on | Purpose |
|---|---|---|---|
| `msdmd/` | metadata-block | — | Foundational convention. Defines the comment-block syntax, the parser contract, the runner protocol, reserved field names, and the visible gap-reporting requirement. Ships reference parsers under `msdmd/parsers/`. Every metadata-block skill builds on it. |
| `doc-build/` | metadata-block | `msdmd` | Self-declaring documentation coverage. Modules declare `# === DOCS ===` blocks; a runner verifies documentation paths/anchors and reports stale docs plus visible gaps. |
| `cap-build/` | metadata-block | `msdmd` | Self-declaring capability inventory. Modules declare `# === CAPABILITIES ===` blocks; a runner builds a capability map and verifies exposed surfaces. |
| `deps-build/` | metadata-block | `msdmd` | Self-declaring dependency topology. Modules declare `# === DEPENDENCIES ===` blocks; a runner builds import/call/capability graphs and reports unresolved edges, cycles, and visible gaps. |
| `owner-build/` | metadata-block | `msdmd`, `risk-boundary-build` | Self-declaring module stewardship. Modules declare `# === OWNERS ===` blocks; a runner reports unowned modules, unresolved owners, and review coverage gaps. |
| `test-build/` | metadata-block | `msdmd` | Self-declaring contract tests. Each module declares a `# === CONTRACTS ===` block; a runner discovers and executes the referenced test functions and reports per-contract status plus modules with no CONTRACTS as coverage gaps. |
| `meta-module-build/` | metadata-block | `msdmd` | Metadata-first module scaffolding. Each module declares a `# === MODULE_BUILD ===` block (manifest: surfaces, boundaries, tests, rollout, rollback) before implementation. New module work in any org repo is expected to start here. |
| `risk-boundary-build/` | metadata-block | `msdmd`, `meta-module-build` | Runtime risk and permission boundaries. Existing modules declare `# === BOUNDARIES ===` blocks for auth, storage, network, user-data, admin, and operational effects. |
| `ratios/` | metadata-block | `msdmd` | Self-declaring module composition ratios for executable source files. Each module records `loc_comments`, `imports_exports`, and `calls_definitions` in a single `ratios:` line on the file's first and last line (not a fenced block); this is not for `json` or `.md` files. The reference `ratios_check.py` recomputes values, fails on drift or misplacement, and reports visible gaps. |
| `manifest/` | metadata-block | `msdmd` | Living-spec generator. Derives observable repo facts from `pyproject.toml` + the file tree and splices them into a machine-owned marked block in `CLAUDE.md`, with a CI `--check` drift gate. |
| `llms-build/` | metadata-block | `msdmd` | Root LLM instruction generation. Modules or central files declare `# === LLMS ===` blocks; `python -m llms.build` aggregates them into canonical root `llms.txt` and reports drift. |
| `canon/` | procedural | — | Canonical-source and doctrine maintenance. Helps agents distinguish source-backed canon, proposed canon, repo-local practice, and `hmmm`. No metadata block. |
| `visitor-intro/` | procedural | — | Onboarding tour. Lets any agent give a coherent, repo-aware orientation to newcomers at any org repo without inventing org-level facts. No metadata block. |
| `char-compress/` | procedural | — | Unit Circle Number System-derived bone/flesh context compression. Carry flesh, frozen bones, transforms, and `hmmm`; drop only safely regenerable scaffold. Do not claim unearned theorem/status support or edcmbone metric status. |
| `agent-instantiation/` | procedural | — | a0/a0ucns agent lifecycle methodology. Spawn sub-agents via the `sub_agent_spawn` tool → spawn executor; fork/merge `PCNAEngine` instances via `InstanceMerge` (fork/absorb/converge); compose identities per the canonical `username(a0(energy)auditor)` grammar; honor spawn caps + write-route gating. Canonical source is `a0`; `a0-betatest` diverged (per-user native-ZFAE) and is out of scope. Repo-specific runtime doctrine (no theorem transfer). |
| `a0p-instancing/` | procedural | — | Peer for a0-betatest (a0p): agents are per-user CRUD `AgentInstance` + `CharacterSheet`, each owning a trained native ZFAE weight bank (three 157-seed cores); no `sub_agent_spawn`/executor/`InstanceMerge` — only volatile `MemoryCore.spawn_sub/merge_sub`. Sequence: create→distill-train→readiness gate→mode inference→sentinel/pending-override→safetensors checkpoint. Canonical source is `a0-betatest`. |
| `plain-lens/` | procedural | — | Plain-language, multi-lens companion views of dense canonical text. Build easier on-ramps (domain/audience/role lens selectors, progressive disclosure) that never replace or talk down to the source, keep a static fallback under any dynamic layer, preserve operators/negations/quantifiers, and report an EDCM-style body-vs-footnote tension reading as an illustrative heuristic (not an edcmbone metric runtime). |
| `gonal-morphology/` | procedural | — | Three-core gonal morphology canon. omega=bones (closed-class+affixes, weight 0.8), phi=roots (open-class, 0.4), psi=words=`phi⊠omega` (1.0); leaf=157 chars, seed=phrase/clause (equivalent under LCM). One operator ⊠ = UCNS `multiplyFuel` at every depth — reuse, don't reimplement. Recomposition runs; decomposition domain-confirmed (`AlignedComplete`) but proof-pending (no theorem-status transfer). |
| `meta/` | procedural | — | Meta Energy Theory axioms. Extract and preserve Energy Theory axioms from resonances among small network architectures, with formula-backed examples and overlap grids; keep Energy Theory distinct from EDCMBONE flesh/bone and FLAR implementation detail. |
| `the-interdependency/` | procedural | — | Workflow protocol for The Interdependency org: code/research/GitHub maintenance, EDCMBONE transcript assembly and analysis, and mandatory usage-guidance + structure-preservation doctrine across artifacts. |
| `loop-eng/` | procedural | — | Loop engineering doctrine for closed feedback cycles (Discover→Plan→Execute→Verify→Iterate), maker/checker subagent separation, and autonomous verify-iterate workflows integrated with a0p/AIMMH and EDCMBONE Verify stages. |

---

## Anatomy of a skill

Every skill is a directory at the repo root containing **at least a `SKILL.md`**. Optional
supporting files (parsers, executors, examples) live alongside it. Repo-level helper packages may
also exist when a skill exposes a module command, as `llms-build` does with `llms/build.py`.

### SKILL.md frontmatter

`SKILL.md` opens with YAML frontmatter:

```yaml
---
name: <slug>
description: <load-bearing trigger paragraph>
---
```

The `description` is the loading contract. Keep it specific. List triggers. Do not bury operative conditions in prose.

Two kinds:

- **Metadata-block skills** apply the msdmd convention to a named block (`DOCS`, `CAPABILITIES`, `DEPENDENCIES`, `OWNERS`, `CONTRACTS`,
  `MODULE_BUILD`, `BOUNDARIES`, `RATIOS`, `MANIFEST`, `LLMS`, …). They define a field schema, a thin executor that consumes parsed
  entries, and a runner that emits a visible gap list. `test-build/` is the canonical worked
  example; `doc-build/`, `cap-build/`, `deps-build/`, `owner-build/`,
  `risk-boundary-build/`, `ratios/`, `manifest/`, and `llms-build/` define adjacent applications. `msdmd` itself is the foundation.
- **Procedural skills** define an agent behaviour with no msdmd block. They state the doctrine
  they enforce and the output shape they produce. `canon/`, `visitor-intro/`, `char-compress/`, `agent-instantiation/`, `a0p-instancing/`, `plain-lens/`, `gonal-morphology/`, `meta/`, `the-interdependency/`, and `loop-eng/` are the examples.

## msdmd block syntax

```python
# === <BLOCK_NAME> ===
# id: <unique_snake_case_id>
#   <field>: <value>
#   <field>: <value>
# === END <BLOCK_NAME> ===
```

- The comment marker (`#`, `//`, `--`) is whatever is idiomatic for the file's language; the
  fence text and field structure are identical across languages.
- `BLOCK_NAME` is uppercase snake case. Every entry begins with `id:` (unique within the block,
  stable across refactors). Field lines are indented one level beneath the id.
- A file may contain multiple blocks of the same or different types; parsers concatenate entries.
- See `msdmd/SKILL.md` for the authoritative spec, reserved field names, and runner protocol.

### The reference parsers (`msdmd/parsers/`)

| File | Public API | Notes |
|---|---|---|
| `universal.py` | `parse_text(text, block_name, marker="#")`, `parse_file(path, block_name)`, `walk_tree(root, block_name, *, skip=None, extensions=None)`, `marker_for(path)` | Pure Python stdlib. `walk_tree` returns `(annotated, untested)` so coverage gaps stay observable. |
| `universal.ts` | `parseText`, `parseFile`, `walkTree`, `markerFor`, `Entry`, `WalkOptions` | Pure Node stdlib (`node:fs`, `node:path`). TypeScript counterpart. |
| `__init__.py` | — | Package marker / docstring. |

`msdmd/collection.ts` defines the TypeScript shapes for generated repo-level
`<reponame>_msdmd.ts` collection points. `msdmd/collect.py` is a stdlib
generator prototype that emits that shape from parsed module-local blocks.
`msdmd/visualize.py` renders a minimal Mermaid graph from JSON or generated
TypeScript collection points.

Both parsers commit to **zero non-stdlib dependencies** and auto-detect the comment marker by
file extension. They are designed to be copied verbatim into any consuming project. A parser is
a pure function over file text: it returns all entries from all matching blocks, does not
interpret field semantics (that is the executor's job), and returns an empty list for files
with no block of the requested type.

Flesh to preserve:

- comment marker is language-idiomatic;
- fence text and field structure are identical across languages;
- `BLOCK_NAME` is uppercase snake case;
- every entry begins with stable `id:`;
- field lines are indented beneath the id;
- files may contain multiple blocks;
- parsers concatenate matching entries;
- unknown fields stay visible as `hmmm` where the skill requires it.

Reference parsers:

```text
msdmd/parsers/universal.py  # Python stdlib
msdmd/parsers/universal.ts  # Node stdlib
```

Parser contract:

- pure functions over file text;
- no non-stdlib dependencies;
- auto-detect comment marker by extension;
- return entries, not interpreted semantics;
- return empty list when no matching block exists;
- runners must report gap lists visibly.

## llms-build runner

`llms-build/SKILL.md` defines the `LLMS` metadata block. The reference command is:

```bash
python -m llms.build --root . --out llms.txt
python -m llms.build --root . --out llms.txt --apply
python -m llms.build --root . --out llms.txt --check
```

The runner lives in `llms/build.py`. It parses `LLMS` blocks, ignores Markdown fenced-code examples,
generates the canonical root `llms.txt`, and reports drift in `--check` mode. Edit source `LLMS`
blocks first; do not hand-edit `llms.txt` as independent doctrine.

## Maintenance tools

```bash
python tools/check_skill_lib_drift.py
python tools/char_compress_check.py
python tools/propagate_skills.py ../target-repo          # dry-run
python tools/propagate_skills.py ../target-repo --apply  # local copy
python -m llms.build --root . --out llms.txt --check
```

Tool boundaries:

There is a small stdlib Python editorial test suite. There is still no `package.json`,
`pyproject.toml`, or `Makefile`. The only CI workflow is `hygiene.yml` (tracked-bytecode
guard); it does not run the editorial helper tools. Do not invent commands beyond the
checks that exist here.

- Run `python -m unittest discover -s tests` to validate skill registration,
  skills.json semantics, per-skill spec coverage, SKILL.md frontmatter, README
  index coverage, collection-point schema/generator/visualizer coverage, universal parser
  behavior, llms-build behavior, and parser ratio bookends.
- The parsers are reference implementations; the test suite covers core parser
  behavior and library integration, not every consuming-runner contract.
- `check_skill_lib_drift.py` checks editorial agreement among skill directories, `skills.json`, `README.md`, `ORG_DISTRIBUTION.md`, `AGENTS.md`, `CLAUDE.md`, and generated `llms.txt`.
- `char_compress_check.py` runs preservation fixtures from `char-compress/fixtures.json`; it is not the full Unit Circle Number System compression engine.
- `propagate_skills.py` copies canonical skill directories into a checked-out target repo; it does not commit, push, open pull requests, or contact GitHub.
- Runner sections in application SKILLs are contracts or patterns for *consuming* repos to
  implement against their own source trees, not scripts that live or run here unless the skill
  directory includes a helper file or package module.
- Validation here is editorial: keep `SKILL.md` frontmatter accurate, keep `skills.json` and the
  README table in sync with the directories present, keep generated files in sync with declarations,
  and keep the parsers/runners stdlib-only.

## Consumption and propagation

- Canonical install path inside consuming repos: `.agents/skills/<skill-name>/`.
- Other paths may work only if the harness walks them.
- Copy skill directories verbatim.
- Add or preserve a target `.agents/skills/README.md` citing this repo and source commit SHA.
- Repo-local copies are never the source of truth.
- Target repos are listed in `ORG_DISTRIBUTION.md`.

## Editing doctrine

1. Edit here first.
2. Keep `skills.json`, `README.md`, `ORG_DISTRIBUTION.md`, `AGENTS.md`, `CLAUDE.md`, and generated `llms.txt` synchronized when adding, renaming, or removing a skill.
3. Preserve load-bearing descriptions.
4. Mark unknowns as `hmmm`; do not guess.
5. New module work in consuming repos should start with `MODULE_BUILD`.
6. Contracts belong in source modules, not test files.
7. Do not fork parser dialects; propose an `msdmd` extension instead.
8. Do not invent undeclared package/build commands for this repo.
9. Apply `char-compress` when compressing repo context: carry flesh, frozen bones, transforms, and hmmm; drop only safely regenerable scaffold.
10. Treat `char-compress` as Unit Circle Number System-derived compression doctrine, but do not claim unearned theorem/status support or edcmbone metric status.
11. For LLM instructions, edit `LLMS` source blocks and regenerate `llms.txt` with `python -m llms.build --root . --out llms.txt --apply`.

## hmmm

- no CI currently runs the helper tools automatically
- propagation still requires review, commit, and pull request work in target repos
- `char_compress_check.py` is deterministic fixture support, not the full Unit Circle Number System compression engine

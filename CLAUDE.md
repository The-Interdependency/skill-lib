# CLAUDE.md — skill-lib

AI-assistant guidance for `The-Interdependency/skill-lib`.

## Core facts

- `skill-lib` is the canonical organization-wide source for reusable agent skills.
- Other The Interdependency repos vendor repo-local copies from here.
- Edit skills here first; propagate later with the source commit SHA.
- License: MIT.
- Entry points: `README.md`, `AGENTS.md`, `skills.json`, `ORG_DISTRIBUTION.md`, each `<skill>/SKILL.md`.
- No package manifest, Makefile, package.json, pyproject.toml, or CI is declared here.
- Validation here is editorial plus optional pure-stdlib helper scripts in `tools/`.

## Layout

```text
README.md              # human-facing overview and skill index
AGENTS.md              # agent-facing entry point
ORG_DISTRIBUTION.md    # canonical-source rule, target repos, propagation rule
skills.json            # machine-readable skill index
CLAUDE.md              # assistant guidance
LICENSE                # MIT
tools/README.md        # local maintenance helper documentation
tools/*.py             # pure-stdlib helper scripts
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
| `ratios/` | metadata-block | `msdmd` | Self-declaring module composition ratios. Each module records `loc_comments`, `imports_exports`, and `calls_definitions` in bookend `# === RATIOS ===` blocks; a runner recomputes values, fails on drift, and reports visible gaps. |
| `canon/` | procedural | — | Canonical-source and doctrine maintenance. Helps agents distinguish source-backed canon, proposed canon, repo-local practice, and `hmmm`. No metadata block. |
| `visitor-intro/` | procedural | — | Onboarding tour. Lets any agent give a coherent, repo-aware orientation to newcomers at any org repo without inventing org-level facts. No metadata block. |
| `char-compress/` | procedural | — | Unit Circle Number System-derived bone/flesh context compression. Carry flesh, frozen bones, transforms, and `hmmm`; drop only safely regenerable scaffold. Do not claim unearned theorem/status support or edcmbone metric status. |

---

## Anatomy of a skill

Every skill is a directory at the repo root containing **at least a `SKILL.md`**. Optional
supporting files (parsers, executors, examples) live alongside it.

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
  `MODULE_BUILD`, `BOUNDARIES`, `RATIOS`, …). They define a field schema, a thin executor that consumes parsed
  entries, and a runner that emits a visible gap list. `test-build/` is the canonical worked
  example; `doc-build/`, `cap-build/`, `deps-build/`, `owner-build/`,
  `risk-boundary-build/`, and `ratios/` define adjacent applications. `msdmd` itself is the foundation.
- **Procedural skills** define an agent behaviour with no msdmd block. They state the doctrine
  they enforce and the output shape they produce. `canon/`, `visitor-intro/`, and `char-compress/` are the examples.

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
- `BLOCK_NAME` is uppercase snake_case. Every entry begins with `id:` (unique within the block,
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

## Maintenance tools

```bash
python tools/check_skill_lib_drift.py
python tools/char_compress_check.py
python tools/propagate_skills.py ../target-repo          # dry-run
python tools/propagate_skills.py ../target-repo --apply  # local copy
```

Tool boundaries:

There is a small stdlib Python editorial test suite. There is still no `package.json`,
`pyproject.toml`, `Makefile`, or CI workflow. Do not invent commands beyond the
checks that exist here.

- Run `python -m unittest discover -s tests` to validate skill registration,
  skills.json semantics, per-skill spec coverage, SKILL.md frontmatter, README
  index coverage, collection-point schema/generator/visualizer coverage, universal parser
  behavior, and parser ratio bookends.
- The parsers are reference implementations; the test suite covers core parser
  behavior and library integration, not every consuming-runner contract.
- `check_skill_lib_drift.py` checks editorial agreement among skill directories, `skills.json`, `README.md`, `ORG_DISTRIBUTION.md`, `AGENTS.md`, and `CLAUDE.md`.
- `char_compress_check.py` runs preservation fixtures from `char-compress/fixtures.json`; it is not the full Unit Circle Number System compression engine.
- `propagate_skills.py` copies canonical skill directories into a checked-out target repo; it does not commit, push, open pull requests, or contact GitHub.
- Runner sections in application SKILLs are contracts or patterns for *consuming* repos to
  implement against their own source trees, not scripts that live or run here unless the skill
  directory includes a helper file.
- Validation here is editorial: keep `SKILL.md` frontmatter accurate, keep `skills.json` and the
  README table in sync with the directories present, and keep the parsers stdlib-only.

## Consumption and propagation

- Canonical install path inside consuming repos: `.agents/skills/<skill-name>/`.
- Other paths may work only if the harness walks them.
- Copy skill directories verbatim.
- Add or preserve a target `.agents/skills/README.md` citing this repo and source commit SHA.
- Repo-local copies are never the source of truth.
- Target repos are listed in `ORG_DISTRIBUTION.md`.

## Editing doctrine

1. Edit here first.
2. Keep `skills.json`, `README.md`, `ORG_DISTRIBUTION.md`, `AGENTS.md`, and `CLAUDE.md` synchronized when adding, renaming, or removing a skill.
3. Preserve load-bearing descriptions.
4. Mark unknowns as `hmmm`; do not guess.
5. New module work in consuming repos should start with `MODULE_BUILD`.
6. Contracts belong in source modules, not test files.
7. Do not fork parser dialects; propose an `msdmd` extension instead.
8. Do not invent undeclared package/build commands for this repo.
9. Apply `char-compress` when compressing repo context: carry flesh, frozen bones, transforms, and hmmm; drop only safely regenerable scaffold.
10. Treat `char-compress` as Unit Circle Number System-derived compression doctrine, but do not claim unearned theorem/status support or edcmbone metric status.

## hmmm

- no CI currently runs the helper tools automatically
- propagation still requires review, commit, and pull request work in target repos
- `char_compress_check.py` is deterministic fixture support, not the full Unit Circle Number System compression engine

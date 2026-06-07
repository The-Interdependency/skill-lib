# CLAUDE.md — skill-lib

This file gives AI assistants context needed to work effectively in this repository.

---

## Overview

`skill-lib` is the canonical, organization-wide library of reusable agent skills for
**The Interdependency**. It is the single source of truth from which every other org repo
propagates its local copy of these skills.

The library is built around **msdmd** — *Module Self-Declared Metadata in Markdown* — a
language-agnostic convention where each source module declares its own structured metadata
inside a fenced comment block. A meta-runner walks the tree, parses every block, and acts on
it; modules without the relevant block surface as *visible coverage gaps*. The contract lives
in the same file as the code it describes, so deleting the code deletes its declaration in the
same diff.

- **Role in the org:** canonical skill source. Other repos vendor copies; edits happen here first.
- **License:** Apache 2.0 (see `LICENSE`).
- **Entry points:** `README.md` (human-facing), `AGENTS.md` (agent-facing), `skills.json`
  (machine-readable index), `ORG_DISTRIBUTION.md` (propagation rules and target-repo list).

There is **no build system, package manifest, test runner, or CI** in this repo. It is a
content library plus two reference parsers. See *Build / test / lint* below.

---

## Repository layout

```text
README.md              # human-facing overview, what's-inside table, block syntax
AGENTS.md              # agent-facing entry point (how to load/install skills)
ORG_DISTRIBUTION.md    # canonical-source rule, target-repo list, propagation contract
skills.json            # machine-readable skill index (version, install_path, skills[])
CLAUDE.md              # this file — AI-assistant guidance and repo context
LICENSE                # Apache 2.0
<skill-name>/SKILL.md  # one directory per skill, each with a required SKILL.md
```

Skills present:

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

---

## Anatomy of a skill

Every skill is a directory at the repo root containing **at least a `SKILL.md`**. Optional
supporting files (parsers, executors, examples) live alongside it.

### SKILL.md frontmatter

`SKILL.md` opens with YAML frontmatter:

```yaml
---
name: <slug>
description: <one paragraph; ends with explicit "Load this when …" triggers>
---
```

The `description` is **load-bearing**: the harness reads it to decide whether to load the rest
of the skill. Keep it specific and list the triggers explicitly — do not bury them.

### Two kinds of skill

- **Metadata-block skills** apply the msdmd convention to a named block (`DOCS`, `CAPABILITIES`, `DEPENDENCIES`, `OWNERS`, `CONTRACTS`,
  `MODULE_BUILD`, `BOUNDARIES`, `RATIOS`, …). They define a field schema, a thin executor that consumes parsed
  entries, and a runner that emits a visible gap list. `test-build/` is the canonical worked
  example; `doc-build/`, `cap-build/`, `deps-build/`, `owner-build/`,
  `risk-boundary-build/`, and `ratios/` define adjacent applications. `msdmd` itself is the foundation.
- **Procedural skills** define an agent behaviour with no msdmd block. They state the doctrine
  they enforce and the output shape they produce. `canon/` and `visitor-intro/` are the examples.

### The msdmd block syntax

```python
# === <BLOCK_NAME> ===
# id: <unique_snake_case_id>
#   <field>: <value>
#   <field>: <value>
#
# id: <next_entry_id>
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

Both parsers commit to **zero non-stdlib dependencies** and auto-detect the comment marker by
file extension. They are designed to be copied verbatim into any consuming project. A parser is
a pure function over file text: it returns all entries from all matching blocks, does not
interpret field semantics (that is the executor's job), and returns an empty list for files
with no block of the requested type.

---

## How skills are consumed by other repos

`skill-lib` is the canonical source. Every target repo in the org carries a repo-local copy.

- **Canonical install path:** `.agents/skills/<skill-name>/` inside the consuming repo. Other
  paths (`.skills/`, `.local/skills/`, `skill-lib/`) also work as long as the agent harness
  walks them.
- **Loading:** a harness walks the skills root for directories containing `SKILL.md`, parses
  the frontmatter, indexes by `name` and `description`, and reads a skill's full `SKILL.md`
  when a request matches its triggers. `skills.json` is the machine-readable alternative to
  walking the tree.
- **Propagation:** copy a skill directory verbatim into the target repo and add a short
  `.agents/skills/README.md` there citing this repo and the source commit SHA. Propagation PRs
  must cite this repo and the SHA. **Repo-local copies are never the source of truth — edit
  here first, then propagate.**
- **Target repos** (see `ORG_DISTRIBUTION.md`): `a0`, `ucns`, `edcmbone`, `interdependent-lib`,
  `PTCA`, `PCEA`, `aimmh`, `pcna`, `ZFAE`, `ai-tiw`, `a0ucns`, `eml_ucns`.

---

## Build / test / lint

There is a small stdlib Python editorial test suite. There is still no `package.json`,
`pyproject.toml`, `Makefile`, or CI workflow. Do not invent commands beyond the
checks that exist here.

- Run `python -m unittest discover -s tests` to validate skill registration,
  per-skill spec coverage, SKILL.md frontmatter, README index coverage,
  universal parser behavior, and parser ratio bookends.
- The parsers are reference implementations; the test suite covers core parser
  behavior and library integration, not every consuming-runner contract.
- Runner sections in application SKILLs are contracts or patterns for *consuming* repos to
  implement against their own source trees, not scripts that live or run here unless the skill
  directory includes a helper file.
- Validation here is editorial: keep `SKILL.md` frontmatter accurate, keep `skills.json` and the
  README table in sync with the directories present, and keep the parsers stdlib-only.

---

## Conventions & gotchas

- **`description` is a public contract.** It decides whether a skill loads. Keep it specific;
  list triggers explicitly; never bury them.
- **Unknown fields are written `hmmm`, not guessed.** Applies to any msdmd metadata block and to
  manifest authoring under `meta-module-build`.
- **New module work starts with a `MODULE_BUILD` block** (`meta-module-build/SKILL.md`),
  including its boundary fields (`auth_boundary`, `storage_boundary`, `network_boundary`,
  `user_data_boundary`, `admin_only`). Existing files are not retroactively noncompliant merely
  because they predate the skill.
- **Contracts belong in the source module, not the test file.** Putting a `CONTRACTS` block in
  the test file inverts the doctrine. Ids must describe the protected capability
  (`chat_get_other_owner_404`), not the implementation (`chat_returns_200`).
- **Never silently drop modules without a block.** A msdmd runner must emit the gap list in
  normal output; that visibility is the whole point.
- **Don't fork the parser or introduce parser dialects.** If you need richer syntax, propose an
  msdmd extension rather than a variant; portability depends on one parser contract.
- **Block syntax is a stable contract.** Breaking changes (renaming the fence, changing
  field-line indentation, renaming reserved fields) require a major version bump and a migration
  note in the README. Reserved field names are additive-only. Application SKILLs version
  independently in their own files.

---

## Workflow for editing this repo

1. Edit skills here first; this is the canonical source.
2. Keep `skills.json`, the `README.md` table, and `ORG_DISTRIBUTION.md` consistent whenever you
   add, rename, or remove a skill.
3. When adding a skill, register it in `skills.json`, link it from the README table, and follow
   the appropriate authoring path (metadata-block vs procedural) in `README.md` and
   `msdmd/SKILL.md`.
4. Propagation to target repos happens via separate PRs in those repos that cite this repo and
   the source commit SHA — not from within this repo.

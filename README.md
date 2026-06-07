# skill-lib

A portable library of agent skills built on **msdmd** — Module Self-
Declared Metadata Markdown — a language-agnostic convention where each
module declares its own structured metadata in a fenced comment block.

Licensed under Apache 2.0. The canonical install path inside a
consuming repo is `.agents/skills/<skill-name>/`; every target repo in
The Interdependency follows this convention (see
[`ORG_DISTRIBUTION.md`](ORG_DISTRIBUTION.md)). Other paths like
`.skills/` or `.local/skills/` also work as long as your agent harness
walks them.

Agents consuming this lib should start at
[`AGENTS.md`](AGENTS.md); a machine-readable index of skills is at
[`skills.json`](skills.json).

## What's inside

| Skill | Purpose |
|---|---|
| [`msdmd/`](msdmd/SKILL.md) | The foundational convention. Defines the block syntax, parser contract, and visibility (gap-reporting) requirement. Every metadata-block skill in this lib depends on it. |
| [`doc-build/`](doc-build/SKILL.md) | Applies msdmd → documentation coverage. Modules declare `# === DOCS ===` blocks; a runner verifies documentation paths and anchors, reports stale docs, and surfaces visible gaps. |
| [`cap-build/`](cap-build/SKILL.md) | Applies msdmd → capability inventory. Modules declare `# === CAPABILITIES ===` blocks; a runner builds a capability map and verifies exposed surfaces. |
| [`deps-build/`](deps-build/SKILL.md) | Applies msdmd → dependency topology. Modules declare `# === DEPENDENCIES ===` blocks; a runner builds import/call/capability graphs, detects unresolved edges, and reports cycles. |
| [`owner-build/`](owner-build/SKILL.md) | Applies msdmd → module stewardship. Modules declare `# === OWNERS ===` blocks; a runner reports unowned modules, unresolved owners, and review coverage gaps. |
| [`test-build/`](test-build/SKILL.md) | Applies msdmd → contract test runner. Each module declares its test contracts in a `# === CONTRACTS ===` block; the runner walks the tree, parses, runs them, and reports per-contract status plus visible coverage gaps. |
| [`meta-module-build/`](meta-module-build/SKILL.md) | Applies msdmd → metadata-first module scaffolding. Each module declares its build manifest in a `# === MODULE_BUILD ===` block before implementation drifts into unscoped patches. |
| [`risk-boundary-build/`](risk-boundary-build/SKILL.md) | Applies msdmd → runtime boundary declarations. Modules declare `# === BOUNDARIES ===` blocks for auth, storage, network, user-data, admin, and operational effects. |
| [`ratios/`](ratios/SKILL.md) | Applies msdmd → module composition ratio verification. Each module records `loc_comments`, `imports_exports`, and `calls_definitions` in bookend `# === RATIOS ===` blocks that a runner recomputes and checks for drift. |
| [`canon/`](canon/SKILL.md) | Canonical-source and doctrine maintenance. Helps agents decide what is source-backed canon, proposed canon, or `hmmm` before changing skills or org doctrine. Independent of msdmd. |
| [`visitor-intro/`](visitor-intro/SKILL.md) | Onboarding tour skill. Lets any agent give a coherent, repo-aware orientation to newcomers landing at any The-Interdependency repo, without inventing org-level facts. Independent of msdmd. |

|∆|Implementation status: this repo ships the universal msdmd parsers and skill
specifications. Most application skills define runner contracts for consuming
repos; they do not ship standalone executors here unless a helper file exists
in that skill directory.|∆|

## The core idea

Most "keep docs/tests/configs in sync with code" attempts rot because the
contract lives in a separate file from the code it describes. Anyone can
delete the code and forget the doc; the lie persists.

msdmd inverts this: the contract lives **in the same file as the code that
implements it**, in a structured comment block. A meta-runner walks the
tree, parses every block, and acts on it. Modules without the relevant
block surface as visible coverage gaps in the runner output. Coverage is
observable, not implicit.

The same convention covers tests, docs, capability registries, dependency
topologies, ownership manifests — anywhere a module needs to declare
something structured about itself for an external tool to read.

## Block syntax (universal)

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

The comment marker (`#`, `//`, `--`, etc.) is whatever's idiomatic for
the file's language. The fence text and field structure are identical
across languages. See [`msdmd/SKILL.md`](msdmd/SKILL.md) for the
authoritative spec.

## Extending the lib

Skills come in two kinds. Pick the right one for what you're adding.

**Metadata-block skills** apply the `msdmd` convention to a new block
name (`doc-build`, `cap-build`, `deps-build`, `owner-build`, `test-build`, `meta-module-build`, `risk-boundary-build`, `ratios` are the existing examples).
To add one:

1. Pick a `<BLOCK_NAME>` (e.g. `DOCS`, `CAPABILITIES`, `OWNERS`).
2. Decide the field schema (which fields are required, which optional).
3. Specify the runner/executor contract, or write a thin executor that takes
   parsed entries from `msdmd/parsers/universal.py` and does something with
   them.
4. Author a `SKILL.md` that documents the convention and runner behavior.

`test-build/` is the canonical worked example.

**Procedural skills** define an agent behaviour without an `msdmd`
block (`canon` and `visitor-intro` are the existing examples). To add one:

1. Define when the skill loads (the `description` field in the YAML
   frontmatter is what your harness will read).
2. State the doctrine the skill enforces and the output shape it
   produces.
3. Author the `SKILL.md` as a self-contained behavioural spec — no
   block schema or executor is required.

Whichever kind you add, register it in [`skills.json`](skills.json)
and link it from the table above.

## Versioning and stability

- The msdmd block syntax is treated as a stable contract — breaking
  changes will go through a major version bump.
- Skill executors and field schemas live in their own SKILL.md files and
  may evolve independently.
- The universal parsers (`msdmd/parsers/universal.{py,ts}`) commit to
  pure-stdlib dependencies; you can copy them anywhere.
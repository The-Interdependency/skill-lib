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
| [`msdmd/`](msdmd/SKILL.md) | The foundational convention. Defines the block syntax, parser contract, and visibility (gap-reporting) requirement. Every other skill in this lib depends on it. |
| [`test-build/`](test-build/SKILL.md) | Applies msdmd → contract test runner. Each module declares its test contracts in a `# === CONTRACTS ===` block; the runner walks the tree, parses, runs them, and reports per-contract status plus visible coverage gaps. |
| [`meta-module-build/`](meta-module-build/SKILL.md) | Applies msdmd → metadata-first module scaffolding. Each module declares its build manifest in a `# === MODULE_BUILD ===` block before implementation drifts into unscoped patches. |
| [`ratios/`](ratios/SKILL.md) | Applies msdmd → module composition ratio verification. Each module records `loc_comments`, `imports_exports`, and `calls_definitions` in bookend `# === RATIOS ===` blocks that a runner recomputes and checks for drift. |
| [`visitor-intro/`](visitor-intro/SKILL.md) | Onboarding tour skill. Lets any agent give a coherent, repo-aware orientation to newcomers landing at any The-Interdependency repo, without inventing org-level facts. Independent of msdmd. |

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
name (`test-build`, `meta-module-build`, `ratios` are the existing examples).
To add one:

1. Pick a `<BLOCK_NAME>` (e.g. `DOCS`, `CAPABILITIES`, `OWNERS`).
2. Decide the field schema (which fields are required, which optional).
3. Write a thin executor that takes parsed entries from
   `msdmd/parsers/universal.py` and does something with them.
4. Author a `SKILL.md` that documents the convention and the executor.

`test-build/` is the canonical worked example.

**Procedural skills** define an agent behaviour without an `msdmd`
block (`visitor-intro` is the existing example). To add one:

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
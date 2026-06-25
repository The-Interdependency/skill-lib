# skill-lib

A portable library of agent skills built on **msdmd** — Module Self-
Declared Metadata Markdown — a language-agnostic convention where each
module declares its own structured metadata in a fenced comment block.

Licensed under MPL-2.0 (relicensed from MIT; weak copyleft — embed anywhere,
changes to these files must be published). The canonical install path inside a
consuming repo is `.agents/skills/<skill-name>/`; every target repo in
The Interdependency follows this convention (see
[`ORG_DISTRIBUTION.md`](ORG_DISTRIBUTION.md)). Other paths like
`.skills/` or `.local/skills/` also work as long as your agent harness
walks them.

Agents consuming this lib should start at
[`AGENTS.md`](AGENTS.md); a machine-readable index of skills is at
[`skills.json`](skills.json). Root LLM-facing instructions are generated
into [`llms.txt`](llms.txt) from self-declared `LLMS` blocks.

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
| [`ratios/`](ratios/SKILL.md) | Applies msdmd → module composition ratio verification. Each executable/source module records `loc_comments`, `imports_exports`, and `calls_definitions` in a single `ratios:` line on the file's first and last line (not a fenced block; JSON/Markdown are out of scope); the reference `ratios_check.py` recomputes them and checks for drift and misplacement. |
| [`manifest/`](manifest/SKILL.md) | Living-spec generator (msdmd family). Derives observable repo facts from `pyproject.toml` + the tree and splices them into a machine-owned marked block in `CLAUDE.md`, with a CI `--check` drift gate. |
| [`llms-build/`](llms-build/SKILL.md) | Applies msdmd → canonical root `llms.txt`. Modules or central files declare `# === LLMS ===` blocks; `python -m llms.build` aggregates them, writes `llms.txt`, and reports drift. |
| [`canon/`](canon/SKILL.md) | Canonical-source and doctrine maintenance. Helps agents decide what is source-backed canon, proposed canon, or `hmmm` before changing skills or org doctrine. Independent of msdmd. |
| [`visitor-intro/`](visitor-intro/SKILL.md) | Onboarding tour skill. Lets any agent give a coherent, repo-aware orientation to newcomers landing at any The-Interdependency repo, without inventing org-level facts. Independent of msdmd. |
| [`char-compress/`](char-compress/SKILL.md) | Unit Circle Number System-derived bone/flesh context compression for agent handoff and skill writing. Preserves irreducible flesh, frozen bones, transforms, and `hmmm`; drops only safely regenerable scaffold. Independent of msdmd. |
| [`agent-instantiation/`](agent-instantiation/SKILL.md) | Methodology for instantiating, forking, running, merging, and retiring agents in `a0` and its mirror `a0ucns`. Spawn via the `sub_agent_spawn` tool → executor; fork/merge `PCNAEngine` instances via `InstanceMerge`; compose identities; honor spawn caps and write-route gating. `a0-betatest` diverges (per-user native-ZFAE) and is out of scope. Independent of msdmd. |
| [`a0p-instancing/`](a0p-instancing/SKILL.md) | Peer of `agent-instantiation` for a0-betatest (a0p), whose model diverges: agents are per-user CRUD `AgentInstance` entities bound to a `CharacterSheet`, each owning a trained native ZFAE weight bank; no spawn/fork/merge — only volatile sub-context memory. Covers create→train→readiness-gate→mode inference→sentinel/override→safetensors checkpoint. Independent of msdmd. |
| [`plain-lens/`](plain-lens/SKILL.md) | Plain-language, multi-lens companion views of dense canonical text — easier on-ramps that do not replace or talk down to the source. Domain/audience/role lens selectors, progressive-disclosure reading UX, static fallback for dynamic pages, and EDCM-style body-vs-footnote tension readings. Independent of msdmd. |
| [`meta/`](meta/SKILL.md) | Meta Energy Theory Axioms. Extracts and preserves Energy Theory axioms from resonances among small network architectures, with formula-backed examples and overlap grids; keeps Energy Theory distinct from EDCMBONE flesh/bone and FLAR implementation detail. Independent of msdmd. |
| [`gonal-morphology/`](gonal-morphology/SKILL.md) | Canonical three-core gonal morphology: text as UCNS objects across a char→root/bone/word→phrase/clause ladder under one carrier-LCM operator (⊠ = UCNS `multiplyFuel`). omega=bones, phi=roots, psi=words=`phi⊠omega`; adj/adv are flesh. Reuse the UCNS operator. Recomposition runs; decomposition is domain-confirmed (`AlignedComplete`) but proof-pending. Independent of msdmd. |
| [`the-interdependency/`](the-interdependency/SKILL.md) | Workflow and protocol for code building, researching, GitHub maintenance and updates, EDCMBONE transcript assembly for analysis, and anything that touches The Interdependency organization or The Interdependent Way projects. Enforces structure preservation (neurodivergence-compatible), mandatory usage guidance in all artifacts, framework-aligned EDCMBONE analysis, and org-standard GitHub hygiene. Independent of msdmd. |
| [`loop-eng/`](loop-eng/SKILL.md) | Loop engineering for designing closed feedback cycles (Discover→Plan→Execute→Verify→Iterate), single-agent and fleet loops with subagent maker/checker separation, and automated verify-iterate workflows. Integrates with a0p/AIMMH orchestration, EDCMBONE Verify stages, skill-lib Skills, and structure-preserving practices. Independent of msdmd. |

## Maintenance tools

Pure-stdlib helper scripts live in [`tools/`](tools/README.md). The small
`llms/` package exists only to provide the `python -m llms.build` command.

```bash
python tools/check_skill_lib_drift.py
python tools/char_compress_check.py
python tools/propagate_skills.py ../target-repo          # dry-run
python tools/propagate_skills.py ../target-repo --apply  # copy local files
python -m llms.build --root . --out llms.txt             # dry-run
python -m llms.build --root . --out llms.txt --apply     # write generated file
python -m llms.build --root . --out llms.txt --check     # drift gate
```

The drift checker compares skill directories, `skills.json`, `README.md`,
`ORG_DISTRIBUTION.md`, `AGENTS.md`, and `CLAUDE.md`. The propagation helper
copies canonical skill directories into a checked-out target repo. The
char-compress runner executes preservation fixtures for negation, quantifier,
order, values, statuses, secrets, `hmmm`, and unearned theorem/status leakage.
The llms-build runner generates the root `llms.txt` from `LLMS` blocks and can
fail on drift in `--check` mode.

|∆|Implementation status: this repo ships the universal msdmd parsers, skill
specifications, selected pure-stdlib helper tools, and the `llms-build` runner.
Most other application skills define runner contracts for consuming repos; they
do not ship standalone executors here unless a helper file exists in that skill
directory or package.| ∆|

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
name (`doc-build`, `cap-build`, `deps-build`, `owner-build`, `test-build`, `meta-module-build`, `risk-boundary-build`, `ratios`, `manifest`, and `llms-build` are the existing examples).
To add one:

1. Pick a `<BLOCK_NAME>` (e.g. `DOCS`, `CAPABILITIES`, `OWNERS`, `LLMS`).
2. Decide the field schema (which fields are required, which optional).
3. Specify the runner/executor contract, or write a thin executor that takes
   parsed entries from `msdmd/parsers/universal.py` or an equivalent parser and does something with
   them.
4. Author a `SKILL.md` that documents the convention and runner behavior.

`test-build/` is the canonical worked example. `llms-build/` is the worked
example for a metadata-block skill that also ships a stdlib command module.

**Procedural skills** define an agent behaviour without an `msdmd`
block (`canon`, `visitor-intro`, `char-compress`, `agent-instantiation`,
`a0p-instancing`, `plain-lens`, `gonal-morphology`, and `meta` are the existing examples). To add one:

1. Define when the skill loads (the `description` field in the YAML
   frontmatter is what your harness will read).
2. State the doctrine the skill enforces and the output shape it
   produces.
3. Author the `SKILL.md` as a self-contained behavioural spec — no
   block schema or executor is required.

Whichever kind you add, register it in [`skills.json`](skills.json)
and link it from the table above.

## Testing

Run the stdlib editorial test suite after changing skills or parser files:

```bash
python -m unittest discover -s tests
```

The suite checks skill/index consistency, skills.json semantics, per-skill
spec coverage, SKILL.md frontmatter, README skill links, collection-point
schema, generator, visualizer coverage, universal parser behavior, llms-build
behavior, and parser ratio bookends.

## Versioning and stability

- The msdmd block syntax is treated as a stable contract — breaking
  changes will go through a major version bump.
- Skill executors and field schemas live in their own SKILL.md files and
  may evolve independently.
- The universal parsers (`msdmd/parsers/universal.{py,ts}`) commit to
  pure-stdlib dependencies; you can copy them anywhere.
- The repo-level collection point shape lives in `msdmd/collection.ts`;
  consuming repos can import or copy it for `<reponame>_msdmd.ts`.
- A stdlib collection generator prototype lives at `msdmd/collect.py` and can
  emit `<reponame>_msdmd.ts` from parsed module-local blocks.
- A minimal Mermaid visualizer prototype lives at `msdmd/visualize.py` and can
  render collection edges and gaps.
- The `llms-build` runner lives at `llms/build.py` and can generate or check
  root `llms.txt` from `LLMS` blocks.

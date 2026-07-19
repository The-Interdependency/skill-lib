name: skill-lib
description: |
  Canonical organization-wide agent skill library for The Interdependency.
  This file is the agent-facing entry point. The human-facing entry point is
  README.md. If you are an agent operating inside this repo, read on.

# You are an agent in The-Interdependency/skill-lib

This repository is the canonical home for the organization's reusable
agent skills. Every other repo in the org carries a repo-local copy of
this lib under `.agents/skills/`; this is the source of truth those
copies are propagated from.

## What lives here

```text
<skill-name>/SKILL.md          # required: the skill itself
<skill-name>/<helpers>...      # optional: parsers, executors, examples
llms/                          # stdlib module for python -m llms.build
```

Every skill is a directory at the repo root containing at least a
`SKILL.md`. The `SKILL.md` opens with YAML frontmatter:

```yaml
---
name: <slug>
description: <one paragraph; ends with explicit "Load this when …" triggers>
---
```

The `description` is what your harness uses to decide whether to load
the skill. Treat it as the public contract.

## How to load a skill

1. Walk the configured skills root (commonly `.agents/skills/` in
   consuming repos) for directories containing `SKILL.md`.
2. Parse the YAML frontmatter; index by `name` and `description`.
3. When a user request matches the triggers in a `description`, read
   that skill's full `SKILL.md` before acting.
4. Some skills (currently `msdmd`, `doc-build`, `cap-build`, `deps-build`,
   `owner-build`, `test-build`, `meta-module-build`, `risk-boundary-build`,
   `ratios`, `manifest`, `llms-build`, and `typed-meta-frontend`) define metadata blocks that other
   modules declare inside their own source files. Other skills (currently
   `canon`, `domain-claims`, `char-compress`, `visitor-intro`, `agent-instantiation`,
   `a0p-instancing`, `plain-lens`, `gonal-morphology`, `meta`, `the-interdependency`, `interdependent-work-graph`, `loop-eng`, `skill-build`, `sql-queries`, `statistical-analysis`, `explore-data`, `validate-data`, `data-visualization`) are procedural and
   define no block.

A machine-readable index is also available at `skills.json` if you
prefer not to walk the tree.

This repo ships the universal msdmd parser implementations plus skill
specifications. Treat per-skill runner sections as contracts for consuming
repos unless the skill directory or repo package includes an actual helper
script. `llms-build` includes the stdlib command module `llms/build.py`.

## How to install this lib into another repo

The canonical install path inside a consuming repo is:

```text
.agents/skills/<skill-name>/
```

Copy the skill directory there verbatim. Add a short
`.agents/skills/README.md` in the target repo that cites this repo and
the source commit SHA. Every target repo in The Interdependency
already follows this convention; see `ORG_DISTRIBUTION.md` for the
list and the propagation rule.

Repo-local copies are not the source of truth. Edit skills here first;
propagate from here.

## Doctrine while editing skills

- A `SKILL.md`'s `description` field is load-bearing — your harness
  uses it to decide whether to read the rest. Keep it specific. List
  the triggers explicitly. Do not bury them.
- Unknown fields are written `hmmm`, not guessed. This applies to any
  metadata block declared via `msdmd`.
- New module work in any repo should start with a `MODULE_BUILD`
  block; see `meta-module-build/SKILL.md`.
- If you are creating or maintaining a root `llms.txt`, load
  `llms-build/SKILL.md`, edit source `LLMS` blocks first, then run
  `python -m llms.build --root . --out llms.txt --apply`.
- If you are deciding whether repo-local practice should become org doctrine,
  load `canon/SKILL.md` and keep unsupported claims as `hmmm`.
- If a word or phrase is being promoted into canon, a theorem term, ontology
  primitive, schema field, encoding label, cross-domain mapping, or other
  meaning-bearing control surface, load `domain-claims/SKILL.md` before
  attaching provenance. Establish the domain-qualified sense, scope, exclusions,
  and collision result first; then use `canon` to evaluate authority.
- If you are compressing a thread, document, repo audit, canon handoff, or
  working-memory state, load `char-compress/SKILL.md`; carry flesh, frozen
  bones, transforms, and `hmmm`; drop only safely regenerable scaffold.
- If you are an agent introducing a newcomer to the org, load
  `visitor-intro/SKILL.md` and follow its output rubric.
- If you are instantiating, forking, merging, or retiring an agent or
  sub-agent in `a0` / `a0ucns`, load `agent-instantiation/SKILL.md` and
  follow its instantiation sequence. For `a0-betatest` (a0p), whose model
  diverges, load `a0p-instancing/SKILL.md` instead.
- If you are making a dense document approachable — a plain-language or
  multi-lens companion view, a progressive-disclosure reader, or a dynamic
  page that must keep a static fallback — load `plain-lens/SKILL.md`; keep the
  paraphrase subordinate to the canon and mark uncertain mappings as `hmmm`.
- If you are building code, researching, performing GitHub maintenance or updates, assembling EDCMBONE transcripts for analysis, or any work that touches The Interdependency organization, The Interdependent Way projects, or related assets (edcmbone, ucns, pcea, skill-lib, a0, aimmh, etc.), load `the-interdependency/SKILL.md` and follow its structure-preservation, EDCMBONE framework, mandatory usage-guidance, and org-workflow rules.
- If the task spans, consumes, compares, publishes to, or changes the contract between multiple repositories, load `interdependent-work-graph/SKILL.md` before choosing an edit workspace. Resolve exact commits, authority roles, relations, non-transfer boundaries, and one shared graph record.
- If you are designing, implementing, or reviewing agent feedback loops, closed cycles, subagent fleets (maker vs checker), orchestration in a0p/AIMMH, or any repeatable AI workflow that should run autonomously with Verify → Iterate stages, load `loop-eng/SKILL.md` and apply its 5-stage cycle, 6 building blocks, and structure-preserving closed-loop principles.
- If you are creating a new skill, revising an existing skill, bringing skills into compliance, or designing a skill-specific test suite, load `skill-build/SKILL.md` and answer its trigger, source-of-truth, workflow, validation, and `hmmm` question sets before patching.

## Pointers

- `README.md` — human-facing overview, what's-inside table, msdmd
  block syntax.
- `ORG_DISTRIBUTION.md` — canonical-source rule, target repos,
  propagation contract.
- `skills.json` — machine-readable skill index.
- `llms.txt` — generated LLM-facing root instructions.
- Each `<skill>/SKILL.md` — the authoritative skill spec.
- `llms/build.py` — reference runner for `llms-build`.

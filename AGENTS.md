name: skill-lib
description: |
  Canonical organization-wide agent skill library for The Interdependency.
  This file is the agent-facing entry point. The human-facing entry point is
  README.md. If you are an agent operating inside this repo, read on.

# You are an agent in The-Interdependency/skill-lib

This repository is the canonical home for the organization's reusable agent
skills. Consuming repos vendor copies under `.agents/skills/<skill-name>/`;
repo-local copies are never the source of truth (edit here first, then
propagate per [`ORG_DISTRIBUTION.md`](ORG_DISTRIBUTION.md)).

## Agent-context invariant — binding

`skill-lib` is standing agent context, not optional reference material.

At **every agent instantiation**, before that agent may reason about or execute
org work, resolve the available skill-lib entrypoint/index and the governing
repository instructions. Load `wdll/SKILL.md` for any nontrivial spawned or
newly-scoped work whose target state, scope, or proof is not already explicit.
At **the start of every unit of work**, reevaluate the current request against
skill descriptions and read every applicable `SKILL.md` before acting. A
child/sub-agent inherits the parent's already-resolved repository identities,
governing contracts, and applicable skill context, then reevaluates triggers
for its own assigned work; it does not reconstruct stable project semantics from
the conversational prompt.

Previously resolved authoritative instructions remain resolved until their
source changes, conflicts, becomes unavailable, or is explicitly superseded. Do
not ask the user to restate repository knowledge that an authoritative source
already resolves. If required authority cannot be resolved, stop that work
boundary as `hmmm`; do not guess and do not substitute conversational repetition
for source resolution.

```text
agent birth -> resolve repo instructions + skill-lib -> inherit authority -> ready
work start  -> reevaluate triggers -> load applicable contracts -> act
missing authority -> hmmm, not invention or user repetition
```

## Resource-run invariant — binding

Read [`RESOURCE_RUN_INVARIANT.md`](RESOURCE_RUN_INVARIANT.md) before any
compute run whose completion depends materially on scarce resources.

**Resource scarcity requires contemplation BEFORE a compute run begins. Once
begun, let it finish. If there is doubt you can finish it, do not start it.** Do
not invent a wall-clock cutoff merely to make a healthy computation bounded or
falsifiable; runtime is a stopping criterion only when it is actually
load-bearing to the claim, safety boundary, or an externally imposed hard limit.

## How to load and maintain skills

1. Walk the skills root (repo root here; `.agents/skills/` in consumers) for
   `<skill-name>/SKILL.md`, or read [`skills.json`](skills.json).
2. Match the YAML `description` triggers (`Load this when …` / `Use this when …`)
   and read the full `SKILL.md` before acting. Treat `description` as a
   load-bearing public contract.
3. Treat per-skill runner sections as consumer contracts unless a helper lives
   in that skill directory or package (e.g. `msdmd/collect.py`,
   `llms/build.py`).

## Repo editing doctrine

- **Edit here first; keep indexes honest**: When adding, renaming, or removing a
  skill, synchronize `skills.json`, `README.md`, `ORG_DISTRIBUTION.md`,
  `AGENTS.md`, `CLAUDE.md`, `skills/` Codex adapters (`tools/build_codex_plugin_skills.py --apply`),
  `llms.txt`, and `skill-lib_msdmd.ts`. See [`skill-build/SKILL.md`](skill-build/SKILL.md)
  (including the narrative compression invariant: one authoritative home per
  concept, one semantic job per clause, repetition only when it changes execution).
- **Unknowns stay `hmmm`**: Never guess missing metadata or unsupported reader
  fields.
- **Native-first modules**: New module work starts with native manifests,
  schemas, and design records; use supplemental `MODULE_BUILD` blocks only for
  unexpressed facts (purpose, surfaces, boundaries, tests, rollout, rollback
  required; see `meta-module-build/SKILL.md`).
- **Source vs test ownership**: Source modules own `CONTRACTS`; test modules own
  `CHECKS`. Never put test `call:` topology in source contracts.
- **No parser forks or invented build commands**: Propose extensions in `msdmd`
  rather than forking parser dialects. This repo has no root `package.json`,
  `pyproject.toml`, or `Makefile`; use only the declared checks in
  [`tools/README.md`](tools/README.md) and `.github/workflows/ci.yml`.
- **LLM instructions**: Edit source `LLMS` blocks first, then run
  `python -m llms.build --root . --out llms.txt --apply` (`llms-build/SKILL.md`).

## Skill routing

Load the matching `<skill>/SKILL.md` whenever work enters its scope:

- **Metadata & module specs**: `msdmd` (native-first metadata & blocks),
  `doc-build` (docs/docstrings), `cap-build` (capabilities/APIs), `deps-build`
  (dependencies), `owner-build` (stewardship), `test-build` (contracts/checks),
  `meta-module-build` (module build contracts), `risk-boundary-build` (effect &
  trust boundaries), `ratios` (`loc_comments`, `imports_exports`, `calls_definitions`),
  `manifest` (living spec in `CLAUDE.md`), `llms-build` (`llms.txt`),
  `typed-meta-frontend` (metadata-driven TypeScript UI).
- **Canon, prose & elicitation**: `canon` (org doctrine vs local practice),
  `domain-claims` (domain-qualified terms before canon/provenance),
  `char-compress` (context compression preserving flesh, frozen bones, transforms, `hmmm`),
  `visitor-intro` (repo onboarding tour), `adaptive-elicitation` (one neutral
  question per turn after harvesting context), `plain-lens` (subordinate
  plain-language/multi-lens views), `thought-lens` (freeze claim kernel before
  translating coined/fragmentary thought).
- **UCNS, EPAC & Stack**: `gonol-build` (resolve current UCNS authority and exact owning Stack research workspace first; EDCM is measurement/evaluation only),
  `ucns-option-selection` (hard eligibility/evidence gates + scoped ratification),
  `epac-selection-display` (pin source/receipt/renderer; read-only WebMCP),
  `interdependent-work-graph` (multi-repo authority/provenance before choosing an
  edit workspace), `stack-update` (coherent `The-Interdependency/stack` mutations),
  `project-incubation-graduation` (qualify, extract, reconsumption, sever),
  `distributed-publication` (multi-source books/reports/archives).
- **Agents, orchestration & verification**: `the-interdependency` (org-wide
  protocol, EDCM transcripts, mandatory usage guidance), `agent-instantiation`
  (`a0`/`a0ucns` lifecycle; use `a0p-instancing` for `a0-betatest`),
  `loop-eng` (closed Verify→Iterate loops), `agent-ops` (bot permissions,
  approvals, untrusted data, evals, memory, budgets), `pstack-orchestration`
  (bound repo contracts & PASS/FAIL/NOT_RUN evidence), `wdll` (job selection &
  falsifiable completion), `action-calibration` (minimal falsifier vs maximal
  build), `fresh-making` (rebuild stale derived artifacts), `repo-audit-repair`
  (evidence-led repo audits/repairs), `github-tests` (CI/test execution audits),
  `skill-build` (authoring/compliance/tests), `skill-usage` (record material skill
  use; `hmmm` on unknown outcome), `website-builder-journal` (`The-Interdependency.github.io`
  builder records).
- **Infrastructure & data**: `vm-mcp` (keep credentials out of model path; choose
  bounded vs `personal-console` explicitly), `ssh-automation` (host trust, stdin/PTY
  boundaries, child-shell isolation), `sql-queries`, `statistical-analysis`,
  `explore-data`, `validate-data`, `data-visualization`.

## Pointers

- [`README.md`](README.md) — human overview, skill table, Codex plugin install, launchers, `msdmd` block syntax.
- [`ORG_DISTRIBUTION.md`](ORG_DISTRIBUTION.md) — target repos, `.agents/skills/` install rule, propagation workflow.
- [`RESOURCE_RUN_INVARIANT.md`](RESOURCE_RUN_INVARIANT.md) — binding preflight-and-finish compute doctrine.
- [`skills.json`](skills.json) — machine-readable skill index; [`llms.txt`](llms.txt) — generated root LLM instructions.
- [`tools/README.md`](tools/README.md), [`tools/WORK.md`](tools/WORK.md), [`tools/A0-VAULT.md`](tools/A0-VAULT.md) — helper CLIs, `ai.sh`/`work.sh`/`install_ai.sh`, OpenBao vault setup.

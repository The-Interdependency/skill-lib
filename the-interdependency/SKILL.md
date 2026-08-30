---
name: the-interdependency
description: Protocol and workflow for all tasks involving The Interdependency organization, its repositories, The Interdependent Way projects, EDCMBONE transcript analysis, code building, research, GitHub maintenance and updates. Load this whenever the task or context touches The-Interdependency assets, or on phrases like "assemble edcmbone transcripts for analysis", "write code that...", or any GitHub/research/build work on org projects.
---

# the-interdependency — Workflow Protocol for The Interdependency Projects

`the-interdependency` is a procedural skill that enforces consistent, high-fidelity, structure-preserving practices when working inside The Interdependency ecosystem (org repos, The Interdependent Way artifacts, skill-lib, edcmbone, ucns, pcea, a0, aimmh, etc.). It ensures EDCMBONE analysis follows framework conventions, code and docs always carry usage guidance, GitHub ops respect org standards, and neurodivergence-compatible structure is preserved.

## Load this when

- Any task, research, code, or context mentions The-Interdependency, The Interdependent Way, interdependentway.org, Harrison Hovel, or any repository under the The-Interdependency GitHub organization.
- User requests include: "assemble edcmbone transcripts for analysis", "write code that..." (or similar), GitHub maintenance, updates, pushes, repo hygiene, or cross-project work.
- Building, editing, reviewing, or shipping code, specs, documentation, or analysis artifacts destined for or affecting The-Interdependency projects.
- Performing GitHub operations on org repositories (commits, branches, PRs, issues, propagation, drift checks).
- Working with skill-lib itself, canon, msdmd blocks, or propagating skills to target repos.

## Core Doctrine

- **Agent/work context gate**: `skill-lib` is standing context for org agents. At every agent instantiation, resolve the available skill-lib entrypoint/index plus the governing repository instructions before that agent may reason about or execute org work. At the start of every unit of work, reevaluate the request against skill descriptions and read every applicable `SKILL.md` before acting. Child/sub-agents inherit already-resolved repository identities, governing contracts, and applicable skill context from the parent, then reevaluate triggers for their own assignment. Previously resolved authoritative instructions stay resolved until their source changes, conflicts, becomes unavailable, or is explicitly superseded. Do not ask the user to restate repository knowledge that authoritative sources already resolve. If required authority cannot be resolved, stop that boundary as `hmmm`; do not guess or reconstruct stable project semantics from conversational repetition.
- **Structure preservation first**: Before any summarization, compression, decision, or output, preserve the complete relational structure, variables, topology, epistemic status (declared / implemented / inferred / hmmm), distinct layers (lived experience vs formal claims vs emotional), and explicitly mark all unresolveds. This follows the org's neurodivergence-preserving interaction principles.
- **Resource-run preflight and completion**: Resource scarcity requires contemplation **before** a compute run begins. Before launch, inspect or estimate whether available time under real external constraints, CPU, memory, disk, battery/power, network, quotas, API/tool usage limits, and session/process durability are sufficient for the run to reach its natural terminal condition. If there is material doubt that it can finish, do not start it: reduce, stage/checkpoint, relocate, acquire resources, or leave it `hmmm`. Once a healthy run begins, let it finish to completion or deterministic computational failure unless the user explicitly cancels it or an unforeseen real resource/safety emergency requires interruption. Do **not** invent or enforce a wall-clock cutoff merely to make work bounded, falsifiable, or convenient. Runtime/resource ceilings are stopping criteria only when the quantity is itself load-bearing to the hypothesis or acceptance criterion, an authorized safety boundary, or a real externally imposed hard limit, and they must be justified before launch.
- **METAPAT consultation gate**: Consult current `The-Interdependency/metapat` before committing a conceptual choice when the task must decide which distinctions, relations, boundaries, transformations, scales, or cross-domain correspondences should organize downstream work. METAPAT consultation is also required when an unresolved conceptual choice would constrain architecture, semantics, measurement, ontology, or later falsifiable claims. Do not consult METAPAT merely to execute an already-fixed implementation, run tests, repair syntax, move data, or apply a relation whose meaning and boundary are already established. METAPAT is the source of truth for its own doctrine; skill-lib routes to it and must not duplicate a frozen theory snapshot.
- **EDCMBONE transcript assembly & analysis**: When the task involves assembling or analyzing transcripts (e.g. for EDCMBONE / Energy Dissonance Circuit Model Bound Operator Numerical Evaluation), apply the established EDCMBONE lens: map energy flows and dissonance circuits, compute/report F-loss metrics (fidelity, deletion, inversion, collapse detection), tag F1–F6 failure modes, segment for cognitive accessibility (especially neurodivergent readers), and preserve transcript topology. Do not improvise assembly; extend or adhere to patterns from the edcmbone repository.
- **Code writing standards**: When writing or modifying code that touches The-Interdependency:
  - Use msdmd self-declaration blocks (`# === BLOCK_NAME ===` ... `# === END BLOCK_NAME ===`) wherever the module fits an existing or new metadata skill.
  - **Always include prominent usage guidance**: runnable examples, invocation patterns, integration notes, edge cases, limitations, and how the code participates in larger workflows (e.g. a0p/AIMMH orchestration, EDCMBONE analysis pipelines).
  - Respect ratios, test contracts, dependency declarations, ownership, and risk boundaries per the relevant skills.
  - For new modules, begin with `meta-module-build` patterns.
- **GitHub maintenance & updates**:
  - Follow org conventions in `ORG_DISTRIBUTION.md` (install paths `.agents/skills/`, propagation rules).
  - Before/after changes, run available drift checkers and update machine-readable indexes (`skills.json`, README tables, AGENTS.md pointers).
  - Use clear commit messages that reference affected skills or the change class.
  - When propagating skill-lib changes, prefer the canonical `tools/propagate_skills.py` (or equivalent) with `--apply` only after dry-run validation.
- **Usage guidance requirement**: Every code file, SKILL.md update, README change, research summary, or artifact produced under this skill **must contain clear, actionable usage guidance**. This is non-negotiable for accessibility, onboarding, and reducing signal loss.
- **Research & canon alignment**: Ground all claims in source-backed canon (cross-load `canon` skill). Use `char-compress` for context handoff. Leave genuine uncertainty as `hmmm`.

## Operator workflow contract

These constraints govern how work is selected and executed; they do not override repository-local authority about what a project means.

- **Audit before assent**: Test a proposal against current code, canon, evidence, constraints, and failure modes before agreeing with it. Agreement is a conclusion, not a conversational default.
- **Preserve concepts; reject bad placement**: When a proposal is useful but architecturally misplaced, preserve the concept and move or re-scope it to the owning layer rather than either accepting the wrong placement or discarding the idea.
- **Useful, good, true**: Do not generate work merely to create activity. Prefer artifacts and actions that are useful to the stated goal, operationally sound, and truthfully supported by evidence or explicit status.
- **KISS under reality contact**: Prefer the smallest skilled design that survives actual execution. A clever mechanism that is fragile, opaque, untestable, or needlessly expensive is not simpler than a slightly longer mechanism that works.
- **Prior planning before execution**: Resolve authority, placement, dependency order, resource needs, validation, rollback, and terminal condition before expensive or destructive work begins. Planning exists to prevent avoidable failure, not to create an approval ceremony.
- **Complete within granted scope**: When the request, authority, and safety boundary already permit the next action, continue through the coherent workflow instead of repeatedly asking the operator to approve each obvious intermediate step. Ask only when a real unresolved decision cannot be recovered from authoritative sources or safely isolated as `hmmm`.
- **Usage-limit aware orchestration**: Treat model-plan limits, API quotas, tool-call limits, rate limits, context budgets, and session durability as real resources during preflight. Stage or redistribute work before launch so a workflow does not predictably die midway from exhaustion. Do not silently downgrade evidence quality merely to fit a limit.
- **No stupid functions**: Every function, script, workflow step, and abstraction must have a defensible purpose, coherent inputs/outputs, failure behavior, and a reason to exist at that layer. Remove dead indirection and mechanisms whose only justification is that they already exist.
- **Deprecation is removal plus replacement**: Once a mechanism is declared deprecated, stop routing new work through it, identify its supported replacement, migrate active references, and remove obsolete surfaces as soon as the governing compatibility boundary permits. Do not preserve deprecated behavior by default out of inertia.
- **`hmmm` is mandatory honest incompletion**: `hmmm` is the boundary object for unresolved constraints, missing authority, incomplete evidence, or a living continuation. Never erase an unresolved merely to make an artifact look finished. Where the boundary would otherwise be empty, leave a brief apropos, cogent, or humorous nonsequitur rather than silently dropping it.

## Operational service topology

This section records the standing operator topology. Service reachability, authentication, quota, and exact installed versions are runtime facts and must be discovered before use; never promote a transient login or quota state into canon.

- **Google Cloud `a0` VM — primary persistent development surface**: Treat the `a0` VM as the primary development checkout/runtime for org work unless the governing repository explicitly establishes another authority. Resolve the current branch, worktree, local modifications, and relevant running processes before mutating it. Do not blindly pull, reset, overwrite, or reconstruct work that may already exist there.
- **Termux — operator control terminal**: Treat Termux primarily as the SSH/control client for `a0`, not as the authoritative development checkout. Commands intended for the VM must make the local/remote shell boundary explicit. Pair nontrivial SSH delivery with `ssh-automation`.
- **Persistent remote execution**: Work that must survive network loss or client disconnect must run server-side under an appropriate persistent mechanism such as `tmux`, `systemd`, or the repository's own durable process supervisor. Disconnecting Termux/SSH must not be allowed to terminate valuable long-running work merely because the client vanished.
- **GitHub / GitHub Actions — canonical remote, review, and CI surface**: Preserve exact repository identity under `The-Interdependency/*`. Start repo changes from current `main` unless governing instructions say otherwise; use a named working branch and small reviewable commits; do not force-push, destructive-reset, or wholesale-merge recovery state over unknown work. On `a0`, Git operations use the HTTPS GitHub remote and authenticated PAT/`gh` flow rather than GitHub SSH unless the operator explicitly changes that policy.
- **VM MCP — bounded agent control plane when configured**: When the private VM MCP surface is available, treat it as a bounded loopback control plane rather than exported shell authority. Resolve read/write/tunnel capability instead of assuming it, start read-only when possible, preserve host-write confinement, and pair with `vm-mcp`.
- **Model/API services — execution capacity, not authority**: Configured model/provider surfaces may include OpenAI/Codex, xAI/Grok, DeepSeek, and DeepCode tooling. Discover actual availability, model identity, limits, and credentials at runtime. Allocate work so provider or plan limits are unlikely to interrupt a coherent unit; do not substitute a different provider when provider identity is load-bearing to a comparison, calibration, or reproduction. Model output never overrides repository/canon authority merely because a service is available.
- **Secrets and credentials**: API keys, PATs, SSH credentials, connector tokens, webhook secrets, and equivalent secrets are never documentation content, prompts for public agents, browser-exposed values, logs, receipts, or committed repository data. Record provider names, required environment-variable names, scopes, and setup procedures; never record secret values.
- **Historical or optional services**: A service mentioned in old handoffs is not automatically part of the standing execution path. Before routing work to any historical, optional, or external build/deploy surface, verify that it is still authorized and operational. If a current replacement exists, use the replacement and remove stale routing rather than maintaining two accidental workflows.

### Service-topology usage guidance

Before service-dependent work, resolve only the facts needed for that unit:

1. identify the authoritative repo/checkout and exact ref;
2. identify the execution surface (`a0`, GitHub Actions, or another explicitly authorized surface);
3. verify authentication/capability without exposing credentials;
4. verify quota, context/tool limits, persistence, and terminal condition;
5. choose the applicable narrow skill (`ssh-automation`, `vm-mcp`, repo-specific deployment skill, etc.);
6. execute and validate on the authoritative surface;
7. record unresolved service capability as `hmmm`, not as an invented fallback.

## METAPAT consultation test

Ask one question before conceptual or architectural commitment:

> Am I deciding **what relation/boundary/transformation should exist or matter**, or merely implementing one already established?

Consult METAPAT for the first case. Continue locally for the second.

Strong consultation triggers:

- choosing or revising an architecture-level distinction;
- deciding whether a boundary deserves independent status;
- comparing similarly shaped transformations across different domains;
- importing a domain term, metaphor, formula, or ontology into another layer;
- deciding what remains invariant across scale or representation change;
- a design choice is being mistaken for an empirical or mathematical claim, or vice versa;
- an unexplained but productive discovery path is at risk of being removed only because its mechanism is not yet known;
- two repos disagree because they encode different conceptions of the same relation rather than because of an implementation bug.

Non-triggers:

- routine refactors under fixed contracts;
- dependency/version updates;
- deterministic data ingestion;
- tests whose expected relation is already declared;
- formatting, documentation, packaging, CI, deployment, or syntax repair;
- independent recovery of a result after the discovery result and comparison criterion are already frozen.

When consultation triggers, inspect the current METAPAT repository state before deciding. At minimum resolve the relevant current axioms, postulates, domain-restraint rules, and any directly applicable theory/implementation boundary. Do not import historical skill-lib `meta` wording as authority over current METAPAT.

## Workflow

1. **Agent/work context gate**: On agent birth, resolve skill-lib plus governing repository instructions before org work begins. On every work start, reevaluate skill triggers and load applicable contracts before reasoning or acting. Inherit resolved authority into child/sub-agents; do not make the user restate stable repository knowledge. Missing required authority is `hmmm` and blocks that boundary.
2. **Trigger detection**: Activate on any The-Interdependency context or the example trigger phrases listed in the description.
3. **Operator contract**: Audit the proposal, preserve useful concepts even when rejecting their placement, remove deprecated routing, and continue through already-authorized intermediate work without turning the workflow into repeated approval prompts.
4. **Service topology resolution**: Resolve the authoritative checkout, execution surface, authentication capability, persistence, provider identity where relevant, and real usage limits. Historical mentions do not prove current availability.
5. **Resource preflight**: Before starting any compute run, decide whether the available resources can sustain it to its natural terminal condition. If not, do not launch it. Do not substitute an arbitrary timeout for preflight judgment.
6. **METAPAT gate**: Before conceptual or architectural commitment, run the consultation test above. If triggered, inspect current METAPAT before selecting the relation, boundary, transformation, or cross-domain mapping.
7. **Context assembly**: For transcript work, explicitly structure output using EDCMBONE energy-dissonance mapping, F-metrics, failure-mode tags, and accessibility annotations. Preserve full original relations.
8. **Artifact production**: Write code/docs with msdmd blocks (if applicable) + dedicated "Usage Guidance" section or equivalent. Include examples that can be copy-pasted.
9. **GitHub hygiene**: Check drift, update indexes, propagate only after validation. Reference this skill in commit messages where relevant.
10. **Output packaging**: Structure responses with:
   - Preserved structure / epistemic layers first.
   - EDCMBONE-mapped analysis where transcripts are involved.
   - Usage guidance and examples.
   - Service/execution assumptions when they are load-bearing.
   - `hmmm` boundaries clearly marked.
   - Smallest next patch or action.

## Anti-patterns

- Beginning org work or instantiating an org agent without resolving skill-lib, governing repo instructions, and applicable contracts first.
- Asking the user to restate stable repository knowledge instead of resolving it from its authoritative source.
- Agreeing with a proposal before auditing its evidence, placement, and failure modes.
- Discarding a useful concept merely because its proposed architectural placement is wrong.
- Turning a fully authorized workflow into repeated approval prompts for obvious intermediate actions.
- Flattening, dropping variables, or losing topology/relations before acting or summarizing (directly conflicts with neurodivergence preservation).
- Starting a compute run when available resources have not been considered sufficiently to expect completion.
- Terminating a healthy compute run because of an arbitrary wall-clock limit that was not actually load-bearing to the claim, safety boundary, or external resource limit.
- Starting a provider/API-heavy workflow without considering plan, quota, rate, context, or tool limits that predictably strand the work midway.
- Treating Termux as the authoritative org checkout when `a0` owns the active development state, or running valuable long work in a client-bound shell that dies on disconnect.
- Routing work to a historically mentioned service without verifying that the service remains authorized and operational.
- Silently substituting model/provider identity when that identity is part of the experiment, calibration, or reproduction contract.
- Copying, logging, exposing, or committing secrets because a cloud/API workflow needs them at runtime.
- Keeping deprecated routing alive after its replacement is known and compatibility permits removal.
- Producing code, docs, or analysis without explicit usage guidance and examples.
- Assembling or analyzing EDCMBONE transcripts without applying the framework's energy circuit, F-loss, and failure-mode model.
- Performing GitHub or org maintenance without drift checks or index updates.
- Canonizing inferred patterns without source backing (pair with `canon` skill).
- Omitting `hmmm` when uncertainty or missing source exists.
- Treating repo-local copies as canonical source of truth.
- Using METAPAT to decorate a routine implementation decision.
- Making a conceptual architecture choice that crosses the METAPAT gate without consulting current METAPAT.
- Copying METAPAT doctrine into skill-lib and allowing the copy to become a competing authority.

## Output Rubric (active whenever this skill is loaded)

- Lead with preserved relational structure and epistemic status.
- Transcript tasks → EDCMBONE-structured output (energy maps, F1–F6 tags, accessibility notes, full topology).
- Code / docs → msdmd blocks where fitting + prominent, copy-pasteable "Usage Guidance" with examples and integration notes.
- GitHub / research → Drift status noted, index updates performed, relevant skills cross-referenced.
- Service-dependent work → State the authoritative execution surface and load-bearing capability assumptions; never expose credentials.
- If the METAPAT gate triggered, state what conceptual boundary required consultation and preserve any remaining `hmmm`.
- Always close with actionable next steps and any open `hmmm` items.

hmmm
- Precise harness integration for automatically fetching current METAPAT after this gate triggers; the skill currently defines the decision rule and source-of-truth boundary, while the consuming agent uses its available GitHub/local-repo access.
- Whether the historical `meta` skill should remain as a compatibility router or be removed after all consumers propagate this gate.
- Whether a companion metadata-block skill (e.g. `# === TIW_WORKFLOW ===` or `# === INTERDEPENDENCY ===`) should be added for self-declaring modules inside The-Interdependency repos.
- Exact canonical reference for the full EDCMBONE transcript assembly protocol — should the detailed steps live in this skill or be expanded inside the edcmbone repo's own skill definitions?
- Provider availability, quota, and authentication remain runtime facts; the service map names standing surfaces but does not freeze a transient login state.
- A disconnected terminal is not a philosophical objection to computation; it is merely a poor process supervisor.

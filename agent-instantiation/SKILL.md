---
name: agent-instantiation
description: Methodology for instantiating, forking, running, merging, and retiring agents in the a0-family agent platform (a0, a0ucns, a0-betatest). Load this when adding or changing a sub-agent spawn path, a PCNA instance fork/merge, an agent definition or naming scheme, spawn caps or approval gating, an agent run/log table, a heartbeat-driven agent task, or a checkpoint of agent state. Use it before writing any code that creates, addresses, schedules, or tears down an agent or sub-agent, so the new code follows the platform's existing lifecycle, fork/merge, identity, and gating contracts rather than inventing a parallel one.
---

# agent-instantiation — How a0 brings agents into being

a0 runs **one persistent agent** (ZFAE) and lets it **fork sub-agents**
(`a0(model)zeta{n}`) that run in parallel and **merge back**. An agent is
not an LLM call: the LLM is an interchangeable *energy provider*, while the
agent *is* a `PCNAEngine` instance (six prime-indexed rings) plus its
identity, memory, run record, and checkpoint. This skill captures the
methodology a coding agent must follow so a new spawn path, ring fork, merge
mode, or agent definition plugs into the existing lifecycle instead of
growing a second, divergent one.

## Load this when

- Adding or editing a sub-agent **spawn** path, or any code that creates an
  `agent_runs` row.
- Adding a **fork**, **merge**, or **converge** of a `PCNAEngine` instance.
- Defining a **new agent** (its name/symbol/slot/directives/tools) or
  changing the **naming** scheme.
- Touching **spawn caps**, **approval gating**, or the **spawn executor**.
- Persisting agent state (**checkpoints**, **run logs**) or scheduling an
  agent task on the **heartbeat**.

Do not load this for ordinary LLM-call/inference-prompt work that does not
create or reshape an agent instance.

## Scope and source boundary

The **canonical source is `a0`** (`python/engine/`, `python/services/`,
`python/agents/`, `shared/schema.ts`). `a0ucns` and `a0-betatest` mirror it.
This is **repo-specific runtime doctrine**, not org-universal math: it
transfers no UCNS / PCNA / PCTA theorem status (see each repo's boundary
notes). Cite the a0 files below; if a mechanism is not in them, mark it
`hmmm` rather than inventing it.

## The model: persistent agent vs sub-agents

- **Persistent agent (ZFAE).** Defined as a plain dict in
  `python/agents/zfae.py` (`ZFAE_AGENT_DEF`: `name`, `symbol`, `slot`,
  `directives`, `tools`, `sentinel_seed_indices`, `is_persistent`). Its
  runtime body is a **singleton** `PCNAEngine` created once at FastAPI
  lifespan startup via `get_pcna()` in `python/main.py`, restored from its
  checkpoint.
- **Sub-agents.** Forked children of the persistent instance, held in the
  in-memory registry `_sub_agents: dict[str, (PCNAEngine, meta)]` in
  `python/services/agent_lifecycle.py`. Each carries `parent_id`,
  `parent_run_id`, and `run_id` so it can be capped, found, and retired.

## Lifecycle states

A sub-agent run is a row in the `agent_runs` table (`shared/schema.ts`) and
moves through:

```
running   → queued by the sub_agent_spawn tool (no worker yet)
executing → claimed by the spawn executor; inference in progress
completed → inference finished, result logged
failed    → exception raised; error recorded on the row
merged    → terminal; sub_agent_merge absorbed it into the parent
```

In-memory state (the forked `PCNAEngine`) lives in `_sub_agents`; durable
state (status, depth, lineage, summary) lives in `agent_runs`; the event
stream lives in `agent_logs`. Keep these three in agreement.

## Instantiation sequence (dependency order — follow it top to bottom)

1. **Define the agent, don't hardcode it.** Add/extend an agent-definition
   dict in `python/agents/` with `name`, `symbol`, `slot`, `directives`,
   `tools`, `is_persistent`. Address it through the naming helpers, never a
   literal string.
2. **Boot the primary as a singleton.** One `PCNAEngine` per process via
   `get_pcna()` at lifespan startup; `await pcna.load_checkpoint()` to
   restore learned ring state; ensure its row in the agent/instance table.
   Do not construct a second primary.
3. **Spawn only through the `sub_agent_spawn` tool**
   (`python/services/tools/sub_agent_spawn.py`). Never `INSERT` an
   `agent_runs` row by hand. The tool checks spawn caps, derives
   `root_run_id`/`depth` from the parent run scope, inserts the row
   `status='running'`, and returns `{ok, agent_id, run_id}` immediately
   (spawn is non-blocking).
4. **Fork the engine via `InstanceMerge.fork(parent)`**
   (`python/engine/merge.py`) — returns `(child, meta)`. The child gets
   independent tensors with small Gaussian noise (a0: σ≈0.02 on Φ/Ψ/Ω,
   ≈0.01 on Θ; Memory-L copied deterministically). Register it in
   `_sub_agents` with `parent_id` + `run_id`. Never share tensor references
   between instances.
5. **Execute via the spawn executor, not inline.** The background loop in
   `python/services/spawn_executor.py` claims one `running` row atomically
   (`SELECT … FOR UPDATE SKIP LOCKED` in `spawn_db.py`), resolves the
   provider, runs one turn, emits to `agent_logs`, and sets the terminal
   status (with the row's retry policy on transient errors). Do not call the
   model directly from the spawn path.
6. **Merge with `InstanceMerge.absorb(parent, child)`** when the child's
   work is done — federated averaging blends the rings (a0: donor α≈0.15 on
   Φ/Ψ/Ω, ≈0.8 on Memory-L). Then unregister the child, mark its row
   `merged`, and archive its log stream. Use `fork`/`absorb` for the
   parent⇄child path; `converge(a, b, α)` only for two live peers that both
   continue.
7. **Persist on a cadence, validate on restore.** Save ring tensors to the
   checkpoint store (a0: base64 in `system_toggles`) from a **heartbeat
   task**, not ad hoc; on load, validate every ring's shape and assign
   nothing if any mismatches (all-or-nothing restore).
8. **Gate every mutation.** Manual spawn/merge routes call
   `require_admin(request)` (or are listed in the gating allowlist with a
   justification). Tools that cause side effects honor the approval scope
   (`get_approval_scope_user_id()`); spawn caps and parent run scope ride
   `ContextVars` so nested spawns inherit the correct lineage and limits.

## Fork / merge primitives (the only three)

| Op | Signature | Effect |
|---|---|---|
| `fork` | `InstanceMerge.fork(parent) -> (child, meta)` | Parent continues; child is a noised copy. Spawn path. |
| `absorb` | `InstanceMerge.absorb(parent, donor) -> dict` | Donor blended into parent (fed-avg), donor retired. Merge-back path. |
| `converge` | `InstanceMerge.converge(a, b, alpha=0.5) -> dict` | Two live peers exchange state; both continue. |

Blending uses `_fed_avg(a, b, alpha) = clip(alpha*a + (1-alpha)*b, 0, 1)`.
The constants above are a0's current values, not invariants — read them from
`merge.py`, don't reproduce them from memory.

## Identity and addressing

- **Names are composed, never literal.** Primary: `compose_name(...)` →
  `a0({model})zfae`. Sub-agent: `sub_agent_name(index, ...)` →
  `a0({model})zeta{index}`. The model tag is `model_id`, else `provider`,
  else `?`.
- **The instance address is `engine.theta.instance_id`** (generated per
  Θ tensor). Use it as the canonical handle for a running instance.
- **Run lineage is `(run_id, parent_run_id, root_run_id, depth)`** on
  `agent_runs`; logs in `agent_logs` carry the same keys. Identity (who),
  lineage (where in the tree), and instance (which tensors) are distinct —
  keep them so.

## Guardrails to honor

- **Spawn caps** (depth / fanout / concurrent-live, tier-scoped) are checked
  in the spawn tool; raise/return the cap result, never bypass it.
- **Write-route gating** — every `@router.{post,patch,put,delete}` on agent
  state calls `require_admin` or is allowlisted.
- **Module-build doctrine** — every new Python module opens with a
  `# === MODULE_BUILD ===` block; unknown fields are `hmmm`, not guessed
  (`meta-module-build`).
- **400-line budget** and the `N:M C:D I:O` file annotation
  (`scripts/annotate.py`) apply to new agent modules.

## Anti-patterns (refuse these)

- Inserting `agent_runs` rows or calling the LLM directly from a spawn path
  instead of going through `sub_agent_spawn` → executor.
- Sharing or mutating another instance's tensors in place instead of
  `fork`/`absorb`/`converge`.
- A second primary `PCNAEngine`, or addressing an agent by a hardcoded name
  string.
- Merging without retiring the donor row and archiving its logs (orphaned
  `executing` rows / dangling registry entries).
- Skipping `require_admin` / approval-scope checks on a new spawn or merge
  surface.

## hmmm

- a0's `fork()` seeds its RNG from `time.time()`; rapid successive forks can
  collide (flagged in `merge.py`). Prefer a UUID-derived seed if you extend it.
- Several `spawn_executor` contracts (stale-sweep, retry-once-on-transient)
  are declared but not all implemented; verify against the live file before
  relying on them.
- The merge blend weights and noise σ are tunable constants, not proven
  optima — treat them as `repo-local`, not canonical.

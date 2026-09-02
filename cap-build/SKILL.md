---
name: cap-build
description: Self-declaring capability inventory built on msdmd. Each module declares the capabilities it exposes in a `# === CAPABILITIES ===` block; a runner builds a capability map, verifies referenced surfaces still exist, reports duplicate or missing capability declarations, and surfaces visible gaps. Load this when declaring what a module can do, when building capability registries for agents, or when auditing exposed surfaces against declared capabilities.
---

# cap-build — Capability declarations on msdmd

`cap-build` is an application of [msdmd](../msdmd/SKILL.md). It gives
agents and humans a source-backed inventory of what modules can do, where
those capabilities are exposed, and which boundaries they cross.

Implementation status: this skill defines the `CAPABILITIES` block and runner
contract. This repo does not currently ship a CAPABILITIES runner script;
consuming repos should implement the contract below against their own surfaces.

Read `msdmd/SKILL.md` first if you have not. The block syntax, parser
contract, and visible gap rule are inherited.

## The block

```python
# === CAPABILITIES ===
# id: agent_supervisor_dynamic_spawn
#   summary: spawns child agents under a bounded supervisor
#   exposes: AgentSupervisor.start_child/1
#   inputs: child_spec
#   outputs: supervisor_child_ref
#   boundaries: auth:none, storage:none, network:none, user_data:none
#   owner: runtime-platform
# === END CAPABILITIES ===
```

## Field schema

Required:

| Field | Meaning |
|---|---|
| `id` | Stable capability id. |
| `summary` | One-sentence capability description. |
| `exposes` | Function, class, route, command, UI component, or other public surface that exposes the capability; use `hmmm` if unresolved. |

Optional:

| Field | Meaning |
|---|---|
| `inputs` | Comma-separated input names or shapes. |
| `outputs` | Comma-separated output names or shapes. |
| `boundaries` | Comma-separated `name:value` boundary summary (`auth:none`, `storage:read`, etc.). Use `hmmm` for unresolved values. |
| `requires` | Comma-separated capability or module ids this capability depends on. |
| `class` | Free-text capability class (`runtime`, `ui`, `data`, `agent`, `ops`). |
| `owner` | Person, role, or team responsible for the capability. |
| `since` | Version or date this capability was added. |
| `deprecated` | If present, marks the capability as scheduled for removal. |
| `executable` | `true` only when this module is intentionally supported as a directly executable program. `hmmm` records unresolved intent. A positive claim requires a literal line-1 shebang. |

## Direct-execution invariant

A shebang is executable architecture, not decoration. A module that declares
`executable: true` in any local `CAPABILITIES` entry MUST carry a valid shebang
on literal line 1. Conversely, a source module carrying a line-1 shebang MUST
have at least one local `CAPABILITIES` or `CONTRACTS` entry declaring
`executable: true`.

The reciprocal check is deliberate:

- declaration without shebang is a broken executable capability;
- shebang without declaration is a visible capability/contract gap;
- `executable: hmmm` is pending and does not satisfy the positive declaration;
- absence of the field makes no direct-execution claim.

When a shebang is present, RATIOS uses the sanctioned executable preamble rule:
the shebang occupies literal line 1, the opening RATIOS seal occupies literal
line 2, and the matching closing RATIOS seal remains the last non-blank line.
See [ratios](../ratios/SKILL.md).

## Runner contract

A CAPABILITIES runner MUST:

1. Parse every `CAPABILITIES` block with the universal msdmd parser.
2. Build a capability map keyed by `id`.
3. Report duplicate ids as errors.
4. Verify each non-`hmmm` `exposes` target still resolves when a resolver
   exists for the language or framework.
5. Report unresolved `exposes: hmmm` and `boundaries` containing `hmmm` as
   pending, not passing.
6. Report modules with exposed public surfaces but no CAPABILITIES block as
   visible gaps when the runner can detect public surfaces.
7. Audit the direct-execution invariant: `executable: true` without a line-1
   shebang is an error; a line-1 shebang without a local `CAPABILITIES` or
   `CONTRACTS` `executable: true` declaration is a visible gap.
8. Exit non-zero for duplicate ids, malformed required fields, broken
   resolvable exposure targets, or broken positive direct-execution claims.
   Coverage gaps fail only in strict mode.

## Reporting shape

- `CAPABILITY`: id, summary, exposing module, owner, and boundaries.
- `BROKEN_EXPOSES`: declared surface no longer resolves.
- `BROKEN_EXECUTABLE`: `executable: true` but literal line 1 is not a shebang.
- `DUPLICATE`: id appears more than once.
- `PENDING`: unresolved `hmmm` capability fields.
- `GAP`: public-looking modules or surfaces without capability metadata, including a shebang with no positive local direct-execution declaration.

## Anti-patterns

- Declaring capabilities in a central registry while omitting the module-local block.
- Using implementation-shaped ids (`function_runs`) instead of capability-shaped ids (`agent_supervisor_dynamic_spawn`).
- Hiding boundary uncertainty; write `hmmm` where the effect is unresolved.
- Treating a module import as a capability without identifying the exposed behavior.
- Adding a shebang "just in case" to a library module. A shebang claims direct execution and therefore requires a local declaration.
- Declaring `executable: true` while relying on `python file.py`, `bash file.sh`, or another caller-selected interpreter instead of providing the required line-1 shebang.

hmmm
- exact resolver syntax for framework-specific route and UI surfaces
- whether capability ids should be globally unique across a repo or only within a block
- whether private capabilities deserve a separate block or a `class: internal` tag
- whether direct-execution audits should be centralized in a shared msdmd runner once CAPABILITIES gains a reference executor

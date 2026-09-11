---
name: msdmd
description: Module Self-Declared Metadata Markdown — a language-agnostic convention where each source module declares its own structured metadata in fenced comment blocks. Load this when creating, parsing, validating, or extending msdmd block syntax; when a repo needs self-declared module metadata; when another msdmd-family skill needs parser behavior or comment-marker rules; or when checking whether a proposed metadata convention belongs in the foundational parser rather than a runner-local dialect.
---

# msdmd — Module Self-Declared Metadata Markdown

msdmd is a convention for putting small, structured declarations beside the
source that owns them. The declarations are ordinary line comments, so they
remain readable in any editor and require no framework runtime.

The design rule is simple:

```text
owner module declares local facts -> shared parser reads them -> specialized runner interprets them
```

Do not fork parser syntax in a consumer. If a field shape is generally useful,
extend the canonical parser contract here and keep the Python/TypeScript
reference implementations aligned.

## Canonical shape

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

### Universal rules

- **Fence**: `=== <BLOCK_NAME> ===` opens, `=== END <BLOCK_NAME> ===`
  closes. Block name is uppercase snake_case (e.g. `CONTRACTS`,
  `CHECKS`, `DOCS`, `CAPABILITIES`, `OWNERS`).
- **Comment marker**: whatever is idiomatic for the file's language. The
  reference parsers auto-detect these line-comment families by extension:
  `#` for Python, Ruby, Elixir, shell, Perl, R, Julia, PowerShell, Tcl, and
  Raku; `//` for TypeScript/JavaScript, Rust, Go, Java, C, C++ (including
  `.c+`, `.c++`, `.cxx`, and header variants), Swift, Kotlin, C#,
  Objective-C++, Scala, Dart, Zig, Groovy, and PHP; `--` for SQL, Lua,
  Haskell, Ada, VHDL, and Lean; `%` for Erlang and Prolog; `;` for
  Clojure/Lisp/Scheme/Racket; `!` for Fortran; `'` for Visual Basic; and
  `*>` for COBOL. The marker appears at the start of every line in the block.
  `COMMENT_MARKERS` in both universal parsers is the exact extension registry.
- **Entry boundary**: every entry begins with `id:`. The id must be
  unique within its block and stable across refactors (so it can be
  referenced from external tooling).
- **Field lines**: indented one level beneath the id (two spaces of
  visible indent inside the comment). Field names are lowercase snake_case
  followed by `:` and a value. Digits are allowed after the first character,
  so names such as `evidence_sha256` are valid; the first character must be a
  lowercase letter or underscore.
- **Multiple blocks per file**: a module may declare more than one
  block, of the same or different types. The parser concatenates
  entries.
- **Multiple block types per file**: a module may declare both
  `CONTRACTS` and `DOCS` (and any others). Each is parsed
  independently by its respective application.

### Example (Python source module)

```python
# === CONTRACTS ===
# id: chat_get_other_owner_404
#   given: GET /api/v1/conversations/{id} with x-user-id != row.user_id
#   then:  404 (existence non-disclosure)
#   class: security
# === END CONTRACTS ===
```

### Example (Python test module)

```python
# === CHECKS ===
# id: check_chat_get_other_owner_404_http
#   proves: chat_get_other_owner_404
#   call: self::test_chat_get_other_owner_404_http
#   requires: python3, posix_shell
#   timeout: 20
#   mutates: db
#   cleanup: transaction_rollback
# === END CHECKS ===
```

### Example (TypeScript source module)

```typescript
// === CONTRACTS ===
// id: chat_input_send_disabled_while_pending
//   given: a message is in flight
//   then:  send button is disabled and shows pending state
//   class: ux_correctness
// === END CONTRACTS ===
```

### Example (Elixir)

```elixir
# === CAPABILITIES ===
# id: agent_supervisor_dynamic_spawn
#   summary: spawns child agents under a DynamicSupervisor with max_children=cap
#   exposes: AgentSupervisor.start_child/1
# === END CAPABILITIES ===
```

The block content is identical across languages — only the comment
marker changes.

## The parser contract

A msdmd parser is a pure function over file text:

```
parse(file_text: str, block_name: str) -> list[Entry]
```

where `Entry` is a flat `dict[str, str]` containing at minimum the
`id` field plus whatever fields the entry declared. The parser:

- Returns all entries from all matching blocks (using
  `re.finditer`-style iteration, not just the first block).
- Does not interpret or validate field semantics — that's the
  application's job. An entry missing a required field surfaces as an
  error in the executor, not in the parser.
- Does not fail on missing block type — returns empty list if no block
  of that name exists.

A reference implementation in pure stdlib Python lives at
`parsers/universal.py`; the TypeScript equivalent at `parsers/universal.ts`.
Both commit to zero non-stdlib dependencies so you can copy them into
any project.

Extension detection refuses ambiguous suffixes rather than sniffing content.
For example, `.m` can mean Objective-C or MATLAB/Octave and therefore has no
automatic marker. A caller that already knows the language may still call
`parse_text` / `parseText` with an explicit marker. Languages that cannot carry
the msdmd shape as repeated line comments need a future versioned syntax
extension; they are not approximated with an invalid fence.

The paired RATIOS helper preserves the interpreter boundary: a non-empty
line-1 shebang may precede opening RATIOS, which must then occupy line 2 with no
gap. See [`ratios/SKILL.md`](../ratios/SKILL.md) for the complete seal contract.

## Repo collection point and visualizer

Every consuming repo SHOULD maintain one repo-level collection point named
`<reponame>_msdmd.ts` (for example, `a0_msdmd.ts`). This file is the
canonical aggregation surface for all parsed msdmd declarations in that
repo. It does not replace module-local blocks; it is generated from them
or maintained as a thin index over them.

The collection point SHOULD use the shared shapes in `msdmd/collection.ts`
(or a verbatim copy in consuming repos) and export a `MsdmdCollection`:

```typescript
import { defineMsdmdCollection } from "./.agents/skills/msdmd/collection";

export default defineMsdmdCollection({
  repo: "<reponame>",
  declarations: [
    { file: "path/to/module.py", block: "CONTRACTS", id: "...", fields: { summary: "..." } },
    { file: "tests/test_module.py", block: "CHECKS", id: "...", fields: { proves: "..." } },
  ],
  gaps: [
    { file: "path/to/module.py", missing: ["CONTRACTS", "DOCS"] },
  ],
});
```

The collection point is an index, not a second authority. Module-local blocks
remain authoritative for their own declarations.

## Usage guidance

Use the parser directly when a runner needs multiple block families without
inventing syntax:

```python
from msdmd.parsers.universal import parse_file

contracts = parse_file(path, "CONTRACTS")
docs = parse_file(path, "DOCS")
```

To add a new metadata skill:

1. define its block name and field semantics in that skill;
2. keep the universal parser generic;
3. write the runner against the shared parser output;
4. surface unannotated modules as visible gaps instead of pretending coverage;
5. propose a canonical parser extension here before accepting any syntax the
   shared parser cannot represent.

## Anti-patterns

- Creating a runner-local parser dialect.
- Treating absence of a block as evidence that the module has no obligation.
- Inferring a comment marker from content when the extension is ambiguous.
- Adding block-specific semantic validation to the universal parser.
- Hiding parse or coverage gaps to make a report look complete.

## hmmm

- block schema/version negotiation across independently evolving consumers
- a canonical escape/multiline-value syntax beyond the current flat line form
- whether ids should receive a stricter lexical grammar than the current
  non-whitespace stable-identity rule
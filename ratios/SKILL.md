---
name: ratios
description: Self-declaring module composition ratios built on msdmd. Each module records its own ratios (lines of code to lines commented, imports to exports, and calls to definitions) in a `# === RATIOS ===` block that bookends the file — first line and last line — and a runner recomputes each recorded ratio from the source and fails on drift, while reporting visible coverage gaps. Load this when recording a module's composition ratios, when authoring or extending the ratio registry, or when wiring ratio verification into CI.
---

# ratios — Module composition ratios on msdmd

`ratios` is an application of [msdmd](../msdmd/SKILL.md). The foundational
skill defines the comment-block convention, the universal parser, and the
gap-reporting requirement; this skill applies the convention to a module's
own composition ratios and defines the executor contract.

Read `msdmd/SKILL.md` first if you haven't — block syntax, the parser
contract, and the visibility rules below are inherited from there and not
redefined.

A ratio is a fact a module owns about its own shape. Like a contract, it
belongs in the file it describes, not in a side report that can drift out
of sync. Unlike a contract, it is not asserted by a human — it is
*recomputed from the source*, so a recorded ratio that no longer matches
the file is a build failure, not a stale comment nobody noticed.

## The block, and the bookend rule

Every module records its ratios in a `RATIOS` block placed at **both
boundaries of the file** — the block is the literal first line and the
literal last line. The file is a self-measuring object; its boundary lines
carry the measurement, opening and closing.

```python
# === RATIOS ===
# id: loc_comments
#   summary: lines of code to lines commented
#   value: 141:40
#   basis: N = non-blank non-comment code lines; M = strict hash-comment + docstring lines; RATIOS block lines excluded
#
# id: imports_exports
#   summary: import statements to public exports
#   value: 8:5
#   basis: imports = lines matching ^(import |from \S+ import); exports = top-level def/class with no leading underscore + 1 if __all__ present; RATIOS block lines excluded
#
# id: calls_definitions
#   summary: call sites to definitions
#   value: 34:12
#   basis: definitions = top-level def + class lines; calls = non-definition lines containing a call expression \w+\(; RATIOS block lines excluded
# === END RATIOS ===
```

The same block opens and closes the file. The parser iterates all matching
blocks, so the bookend is read from both ends; the runner verifies they
agree.

## Field schema

Required:

| Field | Meaning |
|---|---|
| `id` | Ratio identifier, stable across refactors. Must match a computer in the registry to be *verified*; an id with no registered computer is recorded but unverifiable. |
| `value` | The recorded ratio as `A:B`, or `hmmm` if the ratio is declared-but-not-yet-resolved. |

Optional:

| Field | Meaning |
|---|---|
| `summary` | One-sentence human description. |
| `basis` | The counting rule used, in-band, so the recorded value is reproducible. Required in practice for any verified ratio whose definition admits a choice. |
| `class` | Free-text tag (`composition`, `coverage`, `complexity`). |
| `since` | Version or date the ratio was added. |
| `deprecated` | If present, the runner skips and reports the entry as deprecated. |

## The registry and the verify contract

A ratio is *verified* when its `id` maps to a computer in the runner's
registry. A computer is a pure function `file_text -> "A:B"`. The runner:

- recomputes the ratio from the source, excluding the RATIOS block lines
  themselves so a measuring block never inflates its own measurement;
- compares the recomputed value to the recorded `value`;
- on mismatch, emits a **drift** error and exits non-zero;
- on `value: hmmm`, reports a living continuation (pending), never a
  failure — the transition out of `hmmm` is the owner's decision;
- on an id with no registered computer, reports it as recorded-but-
  unverifiable (informational), so unknown ratios stay visible rather than
  silently trusted.

Files with no RATIOS block surface as coverage gaps, exactly as in the
build checker. The gap list is informational unless `--strict`.

## The three ratios

### 1. `loc_comments` — lines of code to lines commented

`loc_comments` is `lines_of_code : lines_commented`.

- **N (lines of code)**: physical lines carrying a code token — not blank,
  not a pure comment, not a docstring-only line. Matches the `N` in the
  a0p `# N:M` bookend annotation (`scripts/annotate.py`).
- **M (lines commented)**: strict `#`-comment lines plus docstring lines
  (`"""` / `'''` blocks). Matches the `M` in `# N:M`.
- **self-exclusion**: lines inside any `=== RATIOS ===` … `=== END RATIOS ===`
  fence are excluded from both counts.

The `loc_comments` computer agrees with `scripts/annotate.py` by
construction — the same counting rule, so a file with a green `# N:M`
bookend will always produce a matching `loc_comments` value.

Diagnostic signal: a ratio that drifts toward very high N:M (many code
lines, few comments) is approaching the 400-line code budget with low
documentation coverage. A ratio drifting toward very low N:M may indicate
grounding load — overhead accumulating faster than implementation.

---

### 2. `imports_exports` — import statements to public exports

`imports_exports` is `import_count : export_count`.

- **import_count**: lines whose stripped content matches
  `^(import |from \S+ import)`. Continuation lines of a multi-line import
  are not counted separately — only the opening `import` / `from` line.
- **export_count**: count of top-level `def` and `class` declarations
  whose names carry no leading underscore (public surface), **plus 1** if
  `__all__` appears anywhere in the file (counts as one explicit export
  declaration regardless of how many names it lists).
- **TypeScript / TSX**: import_count = lines matching `^import `;
  export_count = lines carrying the `export ` keyword at the start
  (excluding `export default` re-exports of imported names — those are
  pass-through, not definitions).
- **self-exclusion**: RATIOS block lines excluded from both counts.

Diagnostic signal: a high imports:exports ratio (many imports, few
public symbols) suggests the module is a consumer or orchestrator — low
surface, high dependency. A low ratio (few imports, many exports) suggests
a leaf module or utility layer. Neither is wrong; the ratio makes the
shape visible and detectable when it drifts unexpectedly.

---

### 3. `calls_definitions` — call sites to definitions

`calls_definitions` is `call_count : definition_count`.

- **definition_count**: top-level `def` and `class` lines (all
  visibility, not just public). Nested `def` inside a class counts as a
  definition. Nested `def` inside another `def` (closures) does not count
  — only one level of nesting beneath a class.
- **call_count**: non-definition, non-comment, non-blank lines containing
  at least one call expression matching `\w+\(` — a word character
  sequence immediately followed by `(`. Each physical line counts once
  regardless of how many calls it contains.
- **self-exclusion**: RATIOS block lines excluded from both counts.

Diagnostic signal: a very high calls:definitions ratio suggests a dense
orchestration file with few definitions and many invocations — close
coupling. A low ratio suggests mostly definitions with few call sites —
a library or schema module. Drift in this ratio across refactors signals
a module changing its architectural role.

---

## The runner

```bash
# verify one file's recorded ratios against its source
python ratios_check.py path/to/module.py

# walk a tree, verifying every RATIOS block and listing files that have none
python ratios_check.py --root .

# strict: files with no RATIOS block also fail (CI gate)
python ratios_check.py --root . --strict
```

Exit codes: `0` all recorded ratios match (gaps allowed unless `--strict`);
`1` a ratio drifted from source, or — under `--strict` — a coverage gap.

## Anti-patterns

- Recording a ratio by hand instead of recomputing it. The point is that
  the file measures itself; a hand-typed value is a contract that drifts.
- Placing the block anywhere but the file boundaries. The bookend is the
  convention; a mid-file RATIOS block defeats the at-a-glance reading.
- Counting the RATIOS block in its own ratio. Always self-exclude.
- Inventing ratio ids whose computer does not exist and recording a number
  for them. If there's no computer, the value cannot be verified — record
  `hmmm` until a computer is registered.
- Introducing a parser dialect for ratios. RATIOS is an ordinary msdmd
  block; if richer syntax is needed, extend msdmd, do not fork it.
- Counting `export default` re-exports of imports as definitions in TS.
  Pass-through re-exports are not definitions — they inflate the export
  count without adding surface.

## Completion criteria

A run is complete when it produces either a SKILL-only declaration (the
convention, before any executor) or an executor plus a registry with all
three computers (`loc_comments`, `imports_exports`, `calls_definitions`)
registered and a passing self-verification on the files it covers.

hmmm
- whether the bookend blocks must be byte-identical or may differ in whitespace
- whether ratios verification joins CI beside the MODULE_BUILD check
- calls_definitions: whether lambda assignments count as definitions
- imports_exports: whether re-exported names from __init__.py aggregate files count once or per-name

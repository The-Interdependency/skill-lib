---
name: ratios
description: Self-declaring module composition ratios built on msdmd. Each executable/source module records its own ratios (lines of code to lines commented, imports to exports, and calls to definitions) in a single `ratios:` comment line placed on the file's first line and last line — not a fenced block — and a runner recomputes each recorded ratio from the source and fails on drift or misplacement, while reporting visible coverage gaps. JSON, Markdown, and other data/documentation files are out of scope for the first-line/last-line rule. Load this when recording a module's composition ratios, when authoring or extending the ratio registry, or when wiring ratio verification into CI.
---

# ratios — Module composition ratios on msdmd

`ratios` is an application of [msdmd](../msdmd/SKILL.md). The foundational
skill defines the comment-block convention, the universal parser, and the
gap-reporting requirement; this skill applies the convention to a module's
own composition ratios and defines the executor contract.

Read `msdmd/SKILL.md` first if you haven't — the parser contract and the
visibility rules below are inherited from there and not redefined.

A ratio is a fact an executable/source module owns about its own shape. Like a contract, it
belongs in the file it describes, not in a side report that can drift out
of sync. Unlike a contract, it is not asserted by a human — it is
*recomputed from the source*, so a recorded ratio that no longer matches
the file is a build failure, not a stale comment nobody noticed.

## The single line, and the first/last rule

RATIOS is the one msdmd declaration that is **not a fenced block**. It applies
to executable/source files with a language comment marker (`#`, `//`, or `--`),
not to JSON, Markdown, or other data/documentation files. In covered source
files it is a single comment line carrying all three ratios, placed on the
file's **literal first line and its last non-blank line**:

```python
# ratios: loc_comments=128:49 imports_exports=4:7 calls_definitions=51:10
"""The module body lives between the two ratio lines."""
...
# ratios: loc_comments=128:49 imports_exports=4:7 calls_definitions=51:10
```

The form is:

```text
<marker> ratios: loc_comments=N:M imports_exports=N:M calls_definitions=N:M
```

- `<marker>` is the language-idiomatic comment marker (`#`, `//`, `--`) for executable/source files only; JSON and Markdown are intentionally not covered by this rule.
- The three ids are fixed: `loc_comments`, `imports_exports`,
  `calls_definitions`. Each carries an `A:B` value, or `hmmm` if the ratio is
  declared-but-not-yet-resolved.
- The same line opens and closes the file. The file is a self-measuring
  object; its boundary lines carry the measurement, opening and closing.

There is no fenced `# === RATIOS === … # === END RATIOS ===` block. An earlier
draft of this skill described one; that was wrong. Tooling reads the single
line from both ends and verifies they agree.

## How it is parsed

The reader lives in the msdmd universal parser as a sanctioned extension, not
a fork (`msdmd/parsers/universal.py`):

```python
from msdmd.parsers.universal import parse_ratios, ratios_placement, RATIO_IDS

parse_ratios(text, marker)      # -> [{"id": "loc_comments", "value": "128:49"}, ...]
ratios_placement(text, marker)  # -> (first_line_ok, last_non_blank_line_ok)
```

`parse_ratios` returns one flat `{"id", "value"}` dict per (declaration line ×
ratio token), so the drift gate can verify every occurrence. It interprets no
semantics — that is the runner's job. A file with no `ratios:` line yields `[]`
and surfaces as a coverage gap.

## The registry and the verify contract

A ratio is *verified* when its `id` maps to a computer in the runner's
registry. A computer is a pure function `file_text -> "A:B"`. The runner:

- recomputes the ratio from the source, **excluding every `ratios:` line**
  (and any tolerated legacy fence) so a measuring line never inflates its own
  measurement;
- compares the recomputed value to the recorded value;
- on mismatch, emits a **drift** error and exits non-zero;
- on a declaration that is not on both the first and last line, emits a
  **misplaced** error and exits non-zero;
- on `value: hmmm`, reports a living continuation (pending), never a failure —
  the transition out of `hmmm` is the owner's decision;
- on an id with no registered computer, reports it as recorded-but-
  unverifiable (informational), so unknown ratios stay visible rather than
  silently trusted.

Covered source files with no `ratios:` line surface as coverage gaps, exactly
as in the build checker. JSON, Markdown, and other files with no supported
source comment marker are skipped rather than reported as gaps. The gap list is
informational unless `--strict`.

## The three ratios

### 1. `loc_comments` — lines of code to lines commented

`loc_comments` is `lines_of_code : lines_commented`.

- **N (lines of code)**: physical lines carrying a code token — not blank,
  not a pure comment, not a docstring-only line.
- **M (lines commented)**: strict `#`-comment lines plus docstring lines
  (`"""` / `'''` blocks).
- **self-exclusion**: every `ratios:` line is excluded from both counts.

Diagnostic signal: a ratio that drifts toward very high N:M (many code
lines, few comments) is approaching a code budget with low documentation
coverage. A ratio drifting toward very low N:M may indicate grounding load —
overhead accumulating faster than implementation.

---

### 2. `imports_exports` — import statements to public exports

`imports_exports` is `import_count : export_count`.

- **import_count**: lines whose stripped content matches
  `^(import |from \S+ import)`. Continuation lines of a multi-line import
  are not counted separately — only the opening `import` / `from` line.
- **export_count**: count of top-level `def` and `class` declarations
  whose names carry no leading underscore (public surface), **plus 1** if
  `__all__` appears anywhere in the file.
- **self-exclusion**: `ratios:` lines excluded from both counts.

Diagnostic signal: a high imports:exports ratio (many imports, few public
symbols) suggests the module is a consumer or orchestrator — low surface,
high dependency. A low ratio suggests a leaf module or utility layer.

---

### 3. `calls_definitions` — call sites to definitions

`calls_definitions` is `call_count : definition_count`.

- **definition_count**: top-level `def` and `class` lines plus one level of
  method nesting beneath a class. Closures nested inside another `def` do not
  count.
- **call_count**: non-definition, non-comment, non-blank, non-string lines
  containing at least one call expression matching `\w+\(`. Each physical
  line counts once regardless of how many calls it contains.
- **self-exclusion**: `ratios:` lines excluded from both counts.

Diagnostic signal: a very high calls:definitions ratio suggests a dense
orchestration file — close coupling. A low ratio suggests mostly definitions
with few call sites — a library or schema module.

---

## The runner

The reference runner ships here as `ratios_check.py` (pure stdlib; it reuses
`parse_ratios` from the msdmd universal parser):

```bash
# verify one file's recorded ratios against its source
python ratios_check.py path/to/module.py

# walk a tree, verifying executable/source files and listing source gaps
python ratios_check.py --root .

# strict: files with no ratios: line also fail (CI gate)
python ratios_check.py --root . --strict
```

Exit codes: `0` all recorded ratios match and are correctly placed (gaps
allowed unless `--strict`); `1` a ratio drifted from source, a declaration was
misplaced, or — under `--strict` — a coverage gap.

## Anti-patterns

- Writing RATIOS as a fenced `# === RATIOS === … # === END RATIOS ===` block.
  It is a single `ratios:` line; the block form was a mistake.
- Recording a ratio by hand instead of recomputing it. The point is that the
  file measures itself; a hand-typed value is a contract that drifts.
- Placing the line anywhere but the file's first and last line. The first/last
  placement is the convention; a mid-file `ratios:` line defeats the
  at-a-glance reading and fails the placement gate.
- Counting a `ratios:` line in its own ratio. Always self-exclude.
- Inventing ratio ids whose computer does not exist and recording a number
  for them. If there's no computer, the value cannot be verified — record
  `hmmm` until a computer is registered.
- Introducing a parser dialect for ratios. The single-line reader is an msdmd
  extension (`parse_ratios`); if richer syntax is needed, extend msdmd, do
  not fork it.

## Completion criteria

A run is complete when every covered executable/source file carries a correctly placed `ratios:`
line on its first and last line, the registry's three computers
(`loc_comments`, `imports_exports`, `calls_definitions`) recompute each
recorded value with no drift, and any unresolved ratio is recorded as `hmmm`
rather than guessed.

hmmm
- the reference computers implement the Python counting rules; language-aware
  computers for TypeScript/other markers are a documented extension point, not
  yet implemented in `ratios_check.py`
- whether ratios verification joins CI beside the other msdmd checks
- calls_definitions: whether lambda assignments count as definitions
- imports_exports: whether re-exported names from `__init__.py` aggregate
  files count once or per-name

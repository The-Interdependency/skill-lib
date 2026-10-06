# msdmd runner configuration guidance

Use this guidance before adding a collector, visualizer, or compliance gate.
Read `msdmd/SKILL.md`, `msdmd/readers.py`, and
`msdmd/references/metadata-conventions.md`; evaluate required information at
its owning scope without requiring duplicate blocks.

## Shipped schema-2 collector scope

`python -m msdmd.collect` defaults to the schema-2 native-and-supplemental
collector. It reads supported native conventions through the versioned reader
registry in `msdmd/readers.py`, also consumes supplemental MSDMD blocks, and
emits the `msdmd/collection.ts` shape. It never imports inspected code, executes
scripts, loads plugins, follows network references, or treats declarations as
verified behavior.

The explicit legacy/block path remains available for old consumers and for an
explicit block-adoption inventory. Legacy/block output cannot silently represent
native facts. Inspect the reader registry and default directory skips at the
pinned commit; do not maintain a second extension list.

The implemented schema-2 subset includes fixture-backed readers for source and
structured standards, including language-aware source/comment attachment,
structured docstrings, manifests and lockfiles, CODEOWNERS, SPDX/REUSE/CITATION,
OpenAPI/JSON Schema, SARIF/JUnit, SBOM, and in-toto/DSSE evidence surfaces.
Unsupported, ambiguous, unreadable, invalid, dynamic, or out-of-scope inputs must
remain visible findings rather than being converted into missing-block gaps.

Usage for a schema-2 collection:

```bash
python -m pip install -r .agents/skills/msdmd/requirements.txt
npm ci --ignore-scripts --prefix .agents/skills/msdmd
python -m msdmd.collect --root . --repo example --out example_msdmd.ts
python -m msdmd.visualize example_msdmd.ts --out example_msdmd.mmd
```

Runners must install both native runtimes first. Exit codes: 1 drift under
`--check`; 2 error diagnostics under `--strict`; 3 missing native reader runtime
(opt-out `--allow-missing-reader-runtimes`, which writes `runtime-unavailable`
output and warns); 4 schema helper older than the output
(`MSDMD_COLLECTION_HELPER_VERSION`; propagate the skill or opt out with
`--legacy-blocks-only`); 5 git cannot list visible files (git missing from
PATH, corrupt index, broken `.git`) or the root is git-ignored by an enclosing
repository (no opt-out; `--check` reports 5, not drift). Exits 3, 4 and 5 write
nothing and are reported together, with precedence 5, then 3, then 4.
Use `--print-generator-identity` as the generator fingerprint.

These commands implement the shipped reader matrix, not every possible metadata
standard. A complete compliance verdict still depends on the declared repository
scope, required facts, supported readers, unresolved inputs, exclusions, and
consumer-specific obligations.

## Shipped Python module-projection scope

`python -m msdmd.module_projection` is a separate, partial native reader for
Python source. It uses `ast` and `tokenize` without importing inspected modules.
It emits one deterministic `.msdmd.jsonl` sidecar per `.py` file under the output
directory, using `msdmd/module-projection.schema.json`. Symbol identities use
qualified declarations rather than line numbers; leading comments attach to the
immediately following declaration at the same lexical depth, other interior
comments attach to the nearest enclosing declaration, and docstrings attach to
their native AST owner. Trailing indented suite comments remain with that lexical
owner until dedent. The projection header binds the executing Python version and
AST grammar; malformed MSDMD fences (interrupted, unclosed, name-mismatched or
nested-opening `msdmd_fence_mismatched`, and unmatched-close
`msdmd_fence_unmatched_close`) emit diagnostics rather than spanning code. This
fence validation is stricter than the universal block parser, which matches each
block name independently. Span byte offsets index the UTF-8 re-encoding of the
decoded text and differ from raw file offsets for BOM or non-UTF-8 sources.
Decorator-region comments attach to the decorated declaration, source lines split
only at Python newlines, and sidecars are written as exact LF-terminated UTF-8
bytes.

```bash
python -m msdmd.module_projection --root . --repo example/repo \
  --revision <exact-revision> --out-dir .msdmd/modules --write
python -m msdmd.module_projection --root . --repo example/repo \
  --revision <exact-revision> --out-dir .msdmd/modules --check
```

Complete-tree writes/checks own the entire output directory and therefore prune
or reject unexpected projection files. A run with one or more repeatable
`--source` arguments owns only those selected sidecars and leaves all others
alone. Writes publish each file by atomic replacement. An omitted revision is
recorded as `hmmm`; syntax or tokenization failures produce diagnostics and make
the check fail.

This runner does not parse imports, call graphs, dynamic exports, docstring field
dialects, manifests, CODEOWNERS, non-Python files, or the complete discovery and
exclusion denominator. It does not replace the schema-2 collection point. Treat
its output as a source-bound per-module projection, not as a repository-wide
coverage verdict.

## Native discovery contract

A native-capable consumer must inventory the declared repository scope before
choosing readers. The shipped collector implements supported subsets; it does not
license a silent complete-coverage claim over unsupported standards.
Inventory eligible inputs even when no line-comment marker or reader exists:

- source files and tests, including signatures, docstrings, and annotations;
- package/workspace manifests, lockfiles, build and tool configuration;
- provider-specific CODEOWNERS, OWNERS, and other governance declarations;
- documentation, instruction files, frontmatter, schemas, and permitted reports;
- extensionless files such as Dockerfile, Makefile, and LICENSE;
- unsupported or ambiguous formats, unreadable paths, and authorized artifacts.

Pin the repository revision, dirty input identity when applicable, scope rules,
configuration, reader versions, supported subsets, and disclosure limits.
Collecting grants no authority to execute inspected code, follow external
references, or disclose secrets. An inventory is not an extraction success.

## Exclusions and denominator

Every exclusion remains visible with its path or pattern, resolved scope or
unresolved count, reason, and governing policy. Typical candidates include
`.git/`, vendored `.agents/skills/`, dependencies, caches, generated outputs,
historical archives, frozen research artifacts, and read-only upstream mirrors.
Their category alone does not authorize silent removal from scope accounting.
Resolve whether each has an applicable information obligation before excluding it.

Report separately:

- discovered scope and eligibility rules;
- supported extraction and provided required information;
- genuinely missing information after capable inspection;
- unsupported, ambiguous, invalid, unreadable, and dynamic/unresolved inputs;
- exclusions and not-applicable scope with reasons;
- MSDMD-block adoption and independently verified behavior.

A complete-coverage claim requires completed inspection of eligible sources with
capable readers. Required unresolved scope or conflicts block a strict verdict.
Optional unknowns remain visible. Content/spec repos can lack executable-module
obligations while still having documentation, ownership, or other obligations;
do not label the entire repository N/A merely because it contains no code.

Example exclusion record for a consuming implementation (illustrative policy
data, not input accepted as a coverage claim by itself):

```json
{
  "path": ".agents/skills/",
  "status": "excluded",
  "reason": "Vendored upstream skills; excluded from local-module obligations.",
  "policy": "repo-local live-module scope",
  "resolved_file_count": "hmmm"
}
```

An unknown count stays unresolved; the illustrative record earns no completeness
claim. Generated projections remain consumers of source declarations, not
independent evidence about their own inputs.

## Planning and supplemental blocks

Start new-module work with source-linked native manifests, schemas, and design
records. Purpose, surfaces, boundaries, tests, rollout, and rollback remain
required. Use supplemental `MODULE_BUILD` entries for otherwise unexpressed
information. Preserve existing native owners without demanding a second copy.

The same rule applies to `BOUNDARIES`, `CAPABILITIES`, `CONTRACTS` / `CHECKS`,
`DOCS`, `LLMS`, and `OWNERS`: each application's semantic obligations remain,
while block absence alone is an adoption observation. Unsupported extraction is
`hmmm`, not absence. Keep declared controls separate from verified enforcement
and CODEOWNERS review assignment separate from operational ownership. Preserve
the independent RATIOS syntax and consuming-repo dialect boundaries.

## Collection point and verification

Generate `<reponame>_msdmd.ts` through the owning collector and export
`defineMsdmdCollection(...)`. Edit source declarations first; never maintain the
projection as a second doctrine owner. A provisional seed must retain its
`hmmm` regeneration gap until replaced with verified generator output.

For skill-lib's exact command and replay check, see
`ORG_DISTRIBUTION.md#collection-points`. Bind source and generator identities to
the resulting Git commit and compare a fresh render byte-for-byte. Report this
as schema-2 projection consistency, separately from native-reader acceptance
outside the implemented subset.

## hmmm

Cross-source semantic reconciliation, build/compiler context, arbitrary language
completeness, independent signature verification, full discovery and exclusion
receipts beyond the implemented subset, and broader executable acceptance
fixtures remain separate implementation work. This policy is not an executable
configuration format. The schema-2 collector and Python projection remain usable
only within their disclosed scopes.
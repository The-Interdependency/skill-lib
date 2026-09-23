# msdmd runner configuration guidance

Use this guidance before adding a collector, visualizer, or compliance gate.
Read `msdmd/SKILL.md` and `msdmd/references/metadata-conventions.md`; evaluate
required information at its owning scope without requiring duplicate blocks.

## Shipped block-helper scope

`python -m msdmd.collect` is a runnable **block-only** helper. It uses
`msdmd/parsers/universal.py`'s `COMMENT_MARKERS` registry and default directory
skips. Inspect those definitions at the pinned commit; do not maintain a second
extension list. The CLI accepts `--block` and `--expected-block`, but does not
accept `--config`, per-repo skip lists, or ratio dialect configuration.

The helper does not discover native metadata in manifests, CODEOWNERS, Markdown,
or extensionless files. It does not publish an exclusion/read-failure ledger,
validate duplicate IDs, qualify edge identities, or distinguish block examples
inside strings from real source comments. Its output is a lexical block
inventory; graphs remain prototypes. `--expected-block` measures block adoption
within this filtered scan, not missing required native information. Without
that option, an empty `gaps` array establishes no coverage result.

Usage for an explicitly block-scoped inventory:

```bash
python -m msdmd.collect --root . --repo example --out example_msdmd.ts
python -m msdmd.visualize example_msdmd.ts --out example_msdmd.mmd
```

These commands implement neither the native discovery contract below nor a
complete compliance verdict. Unsupported required scope stays `hmmm`.

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
AST grammar; malformed MSDMD fences emit diagnostics rather than spanning code.

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
exclusion denominator. It does not feed the legacy TypeScript collection or
visualizer. Treat its output as a source-bound per-module projection, not as a
repository-wide coverage verdict.

## Native discovery contract

A native-capable consumer must inventory the declared repository scope before
choosing readers. The complete form remains a contract for implementation, not
a capability of the partial Python command.
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
data, **not** input accepted by the current collector):

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
as block-projection consistency, separately from native-reader acceptance.

## hmmm

Readers beyond the partial Python slice, unified native-capable schema migration,
qualified block-edge identities, duplicate-ID validation, full discovery and
exclusion receipts, and broader executable acceptance fixtures remain separate
implementation work. This policy is not an executable configuration format.
Existing block helpers and the Python projection remain usable only within their
disclosed scopes.

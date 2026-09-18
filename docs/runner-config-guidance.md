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

## Native discovery contract

A native-capable consumer must inventory the declared repository scope before
choosing readers. This is a contract for implementation, not a shipped command.
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

Native readers, native-capable schema migration, qualified edge identities,
duplicate-ID validation, syntax-aware extraction, discovery/exclusion receipts,
and executable native acceptance fixtures remain separate implementation work.
This policy is not an executable configuration format. Existing block helpers
remain usable within their disclosed scope.

# Changelog

Notable changes to shipped skill behaviour that consumers must act on. Newest
first. Propagation PRs cite the skill-lib commit; this file explains why.

## Unreleased: msdmd collector consumer review (skill-lib #118)

Consumers re-syncing past `9867ab3` must:

- **Install the native reader runtimes** where the collector runs:
  `python -m pip install -r .agents/skills/msdmd/requirements.txt` and
  `npm ci --ignore-scripts --prefix .agents/skills/msdmd` (Node required).
  A missing runtime now exits **3** without writing. Opt-out:
  `--allow-missing-reader-runtimes` writes output marked `runtime-unavailable`
  with error diagnostics and still warns.
- **Propagate the current `msdmd/collection.ts` helper.** Schema-2 output now
  requires `MSDMD_COLLECTION_HELPER_VERSION` >= 1 in the helper named by
  `--import-path`; an older or schema-1 helper exits **4** without writing.
  Opt-out: `--legacy-blocks-only` for explicit schema-1 block-only output.
  When `--out` is outside the repository (for example a CI file under /tmp),
  the helper is located from the repository root.
- **Run the collector inside a usable git checkout.** If git cannot list the
  visible files (git missing from PATH, a corrupt index, a broken `.git`
  marker) or the root is ignored by an enclosing repository, the collector
  prints an ERROR and exits **5** without writing. There is no opt-out; collect
  from a checkout git can read. `--check` reports 5, not drift (1).
  Exit 3, 4 and 5 problems are reported together; precedence is 5, then 3,
  then 4.
- **Use `--print-generator-identity`** (add `--json` for components) as the
  freshness fingerprint. It covers all collector sources, the TypeScript worker
  and lock file, the Python minor, reader package, Node and TypeScript
  versions, and digests of the reader modules that actually resolve (a
  shadowing module on PYTHONPATH changes it).

Behaviour changes:

- The collector never reads its own output, sibling temp/candidate outputs, or
  a redirected stdout file; differently named runs render identical bytes.
- In git checkouts only tracked and untracked-not-ignored files are read. A git
  listing failure or a root ignored by an enclosing repository exits 5. Submodules are excluded ledger entries that
  record their pinned commit.
- Retained source bytes have an aggregate budget (`--max-total-bytes`, default
  256 MiB, must be positive); overflow is an error diagnostic and a warning.
- Redaction covers camel/PascalCase secret names whose final word is sensitive
  (`authorization` added), systemd URL credentials and credential directives,
  SVG metadata and raw DSSE payloads. A DSSE payload that is not an in-toto
  Statement is diagnosed and kept as a decoded `signed-payload` fact.
- Requirements files: unnamed URL/VCS/path/Windows-path entries stay `hmmm`;
  continuations are joined as pip does (comment lines never continue) and a
  trailing continuation at end of file is diagnosed.
- ratios semantic graphs resolve schema-2 addresses and never count an
  ambiguous or unresolved target as resolved.

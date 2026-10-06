# Changelog

Notable changes to shipped skill behaviour that consumers must act on. Newest
first. Propagation PRs cite the skill-lib commit; this file explains why.

## Unreleased: msdmd TypeScript reader failures fail closed

Consumers re-syncing past `3fa40b9` get:

- **Every TypeScript worker failure exits 3** and writes nothing (opt-out
  unchanged: `--allow-missing-reader-runtimes`). A nonzero exit, exit 0
  without a complete JSON result, or node rejecting `--jitless` (Node too old)
  is `typescript_reader_failed`; before, these were error diagnostics that
  exited 0 without `--strict`, or a `native_reader_error`, so TypeScript facts
  could silently go missing. Worker stderr is still never published.
- **New `--typescript-timeout SECONDS`** (default 120, positive and finite)
  bounds each worker and the identity probe. A worker past it is killed and
  reported as `typescript_reader_timeout` (exit 3); a probe past it exits 3
  with no identity.
- **`--print-generator-identity` exits 3, not a `PermissionError`
  traceback,** when the collector sources or a typescript package on the
  worker's resolution path (`node_modules` from the skill directory upward)
  cannot be read. Before, an untraversable `node_modules/typescript` crashed
  the probe, and an untraversable `node_modules` reported TypeScript as
  `absent`. Installed trees (`node_modules`, `__pycache__`, `references`) are
  no longer walked for the source digest; the identity bytes are unchanged
  for the same sources.

## Unreleased: msdmd Node runs jitless; signal deaths exit 3

Consumers re-syncing past `38c6433` get:

- **Node always runs with `--jitless`** in the TypeScript worker and in the
  generator-identity probe. V8's JIT needs writable-then-executable memory,
  which systemd `MemoryDenyWriteExecute=yes` forbids; Node then died with a V8
  fatal error (SIGTRAP, shell exit 133). Output is byte-identical; extraction
  is slower. Sandboxed workers can keep `MemoryDenyWriteExecute=yes`.
- **A Node worker killed by a signal is a missing runtime.** It yields the
  `node_runtime_unavailable` diagnostic, so the CLI exits **3** and writes
  nothing (opt-out unchanged: `--allow-missing-reader-runtimes`). Before, it
  was a `typescript_reader_failed` error that exited 0 without `--strict`, so
  TypeScript facts silently went missing.
- **`--print-generator-identity` exits 3 with no output** when its Node probe
  is killed by a signal, exits nonzero, cannot be spawned, or prints
  unexpected output. Before, it reported Node and TypeScript as `absent` and
  exited 0. Node missing from PATH is still recorded as `absent`.
  Runners must treat a nonzero exit as "no identity", never as an empty one.


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

# OpenBao native MSDMD adoption

GPT generated; context, prompt Erin Spencer.

## Transition and authority

From an uninstrumented OpenBao fork to reproducible, native-first MSDMD
collection with Go source and module metadata. `skill-lib` owns reader code,
schemas and fixtures. `The-Interdependency/openbao` owns its adoption policy,
source declarations and generated inventory. Upstream `openbao/openbao` remains
the source of the vault implementation; no contribution is submitted upstream.

Starting identities: skill-lib `e46accffcb67a10630516d486c89e67f6ad19c7a`;
fork and upstream source `5486582884a420dbd5a42e37125b59f312db7552`.
The consumer's checked-in work graph will pin the resulting producer commit.
Source extraction transfers no operational, security, certification or runtime
proof. No credentials, vault data, or deployed services are in this work.

## File plan and boundaries

| Owner/path | Change | Risk | Required evidence |
| --- | --- | --- | --- |
| skill-lib/msdmd/go_code.py | Go grammar reader: qualified declarations, comments, imports, tags and inert directives | Wrong attachment or executing directives | Native-only, ambiguous, invalid, same-name, raw-string and no-execution fixtures |
| skill-lib/msdmd/go_modules.py | Module/workspace/sum declarations, with unresolved resolution explicit | Flattening directives or false dependency claims | Quoting, blocks, replacements, unknown directives, malformed input fixtures |
| skill-lib/msdmd/readers.py, collect.py | Register readers, bind implementation identity, use actual comments for blocks/ratios | False declarations from strings or missing runtimes | End-to-end collection and missing-runtime fixtures |
| skill-lib/msdmd/requirements.txt, references, SKILL.md | Pin grammar; disclose exact supported subset | Overclaiming full language semantics | Reader regression suite and editorial gates |
| openbao/.agents/skills | Consume an exact canonical subset | Copy drift or executing vendored examples | Byte-level propagation verification |
| openbao/scripts, docs, AGENTS.md, README.md | Reproducible collection, fork policy, provenance and usage | Claiming inventory is security verification | Real fork collection, deterministic replay, visible exclusions/errors |

## Done and failure

Done when the canonical Go readers have adversarial fixture evidence, the fork
consumes their exact commit, and real-source collection is repeatable with every
excluded or unsupported scope visible. Parser, required-source, runtime, identity
or drift failures invalidate the affected coverage claim. A successful metadata
run never asserts that OpenBao is secure, deployable or behaviorally verified.

Roll out reader registration in schema 2, then propagate only after tests. Roll
back by reverting adoption and the canonical reader change; OpenBao runtime code,
data and its upstream-compatible Go module paths remain untouched.

## Usage guidance

Install `msdmd/requirements.txt` and `npm ci --ignore-scripts --prefix msdmd`.
Run `python -m unittest tests.test_go_metadata`, followed by the native-reader
regressions. The fork's `docs/MSDMD.md` will own its exact invocation and coverage
report. Required information is selected explicitly; optional unknown scope is
never silently promoted by a zero exit status.

## Source trial

The immutable fork baseline contains 1,538 Go files and 19 Go module/checksum
files. A read-only sweep completed with tree-sitter 0.25.2 and tree-sitter-go
0.25.0. Six source files retain grammar diagnostics around newer `new(value)`
forms; upstream's root module declares Go 1.27.0. This is a reader limit, not
a compile result. The consumer report must keep these diagnostics visible.
Tree-sitter 0.26.0 crashed during native node traversal on this corpus, so the
shared runtime is pinned to the version exercised by the source sweep and
existing Rust/Java/C/C++ fixture suite. No inspected program was executed.

## hmmm

Build configuration, type checking, module resolution, generated code execution,
runtime tests and vault deployment are outside metadata extraction. Real-source
reader limits and generated output size must be measured before publishing.

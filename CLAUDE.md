# CLAUDE.md — skill-lib

AI-assistant guidance for `The-Interdependency/skill-lib`.

## Core facts

- `skill-lib` is the canonical organization-wide source for reusable agent skills.
- Other The Interdependency repos vendor repo-local copies from here.
- Edit skills here first; propagate later with the source commit SHA.
- License: Apache 2.0.
- Entry points: `README.md`, `AGENTS.md`, `skills.json`, `ORG_DISTRIBUTION.md`, each `<skill>/SKILL.md`.
- No package manifest, Makefile, package.json, pyproject.toml, or CI is declared here.
- Validation here is editorial plus optional pure-stdlib helper scripts in `tools/`.

## Layout

```text
README.md              # human-facing overview and skill index
AGENTS.md              # agent-facing entry point
ORG_DISTRIBUTION.md    # canonical-source rule, target repos, propagation rule
skills.json            # machine-readable skill index
CLAUDE.md              # assistant guidance
LICENSE                # Apache 2.0
tools/README.md        # local maintenance helper documentation
tools/*.py             # pure-stdlib helper scripts
<skill-name>/SKILL.md  # required skill spec
<skill-name>/<helpers> # optional parsers, runners, examples
```

## Skills

| Skill | Kind | Depends on | Purpose |
|---|---|---|---|
| `msdmd/` | metadata-block | — | Module Self-Declared Metadata Markdown. Foundational comment-block syntax, parser contract, runner protocol, reserved fields, visible gap reporting, reference parsers. |
| `doc-build/` | metadata-block | `msdmd` | Documentation coverage through `DOCS` blocks; verifies paths and anchors; reports stale docs and visible gaps. |
| `cap-build/` | metadata-block | `msdmd` | Capability inventory through `CAPABILITIES` blocks; verifies exposed surfaces and duplicates. |
| `test-build/` | metadata-block | `msdmd` | Contract tests through `CONTRACTS` blocks in source modules; runner discovers contracts and reports gaps. |
| `meta-module-build/` | metadata-block | `msdmd` | Metadata-first module scaffolding through `MODULE_BUILD`; surfaces, boundaries, tests, rollout, rollback. |
| `risk-boundary-build/` | metadata-block | `msdmd`, `meta-module-build` | Runtime boundaries through `BOUNDARIES`; auth, storage, network, user-data, admin, operational effects. |
| `ratios/` | metadata-block | `msdmd` | Module composition ratios; comments/code, imports/exports, calls/definitions; recompute and drift-check. |
| `canon/` | procedural | — | Canonical-source and doctrine maintenance; separates declared, implemented, repo-local, inferred, desired, and `hmmm`. |
| `visitor-intro/` | procedural | — | Newcomer orientation for any org repo without inventing org-level facts. |
| `char-compress/` | procedural | — | Bone/flesh context compression. Carry flesh, frozen bones, transforms, and `hmmm`; drop only safely regenerable scaffold. No UCNS-A theorem transfer; no edcmbone metric claim. |
| `manifest/` | metadata-block | `msdmd` | Living-spec generator; derives repo facts from pyproject/tree and splices a machine-owned block into `CLAUDE.md` in consuming repos. |

## Skill anatomy

Every skill directory contains at least `SKILL.md` with YAML frontmatter:

```yaml
---
name: <slug>
description: <load-bearing trigger paragraph>
---
```

The `description` is the loading contract. Keep it specific. List triggers. Do not bury operative conditions in prose.

Two kinds:

- **Metadata-block skills:** define a block schema and executor pattern over `msdmd` parser output.
- **Procedural skills:** define agent behavior, doctrine, output shape, and hmmm; no block schema required.

## msdmd block syntax

```python
# === <BLOCK_NAME> ===
# id: <unique_snake_case_id>
#   <field>: <value>
#   <field>: <value>
# === END <BLOCK_NAME> ===
```

Flesh to preserve:

- comment marker is language-idiomatic;
- fence text and field structure are identical across languages;
- `BLOCK_NAME` is uppercase snake case;
- every entry begins with stable `id:`;
- field lines are indented beneath the id;
- files may contain multiple blocks;
- parsers concatenate matching entries;
- unknown fields stay visible as `hmmm` where the skill requires it.

Reference parsers:

```text
msdmd/parsers/universal.py  # Python stdlib
msdmd/parsers/universal.ts  # Node stdlib
```

Parser contract:

- pure functions over file text;
- no non-stdlib dependencies;
- auto-detect comment marker by extension;
- return entries, not interpreted semantics;
- return empty list when no matching block exists;
- runners must report gap lists visibly.

## Maintenance tools

```bash
python tools/check_skill_lib_drift.py
python tools/char_compress_check.py
python tools/propagate_skills.py ../target-repo          # dry-run
python tools/propagate_skills.py ../target-repo --apply  # local copy
```

Tool boundaries:

- `check_skill_lib_drift.py` checks editorial agreement among skill directories, `skills.json`, `README.md`, `ORG_DISTRIBUTION.md`, `AGENTS.md`, and `CLAUDE.md`.
- `char_compress_check.py` runs preservation fixtures from `char-compress/fixtures.json`; it is not a full natural-language codec.
- `propagate_skills.py` copies canonical skill directories into a checked-out target repo; it does not commit, push, open pull requests, or contact GitHub.

## Consumption and propagation

- Canonical install path inside consuming repos: `.agents/skills/<skill-name>/`.
- Other paths may work only if the harness walks them.
- Copy skill directories verbatim.
- Add or preserve a target `.agents/skills/README.md` citing this repo and source commit SHA.
- Repo-local copies are never the source of truth.
- Target repos are listed in `ORG_DISTRIBUTION.md`.

## Editing doctrine

1. Edit here first.
2. Keep `skills.json`, `README.md`, `ORG_DISTRIBUTION.md`, `AGENTS.md`, and `CLAUDE.md` synchronized when adding, renaming, or removing a skill.
3. Preserve load-bearing descriptions.
4. Mark unknowns as `hmmm`; do not guess.
5. New module work in consuming repos should start with `MODULE_BUILD`.
6. Contracts belong in source modules, not test files.
7. Do not fork parser dialects; propose an `msdmd` extension instead.
8. Do not invent undeclared package/build commands for this repo.
9. Apply `char-compress` when compressing repo context: carry flesh, frozen bones, transforms, and hmmm; drop only safely regenerable scaffold.
10. Do not claim UCNS-A theorem support or edcmbone metric status for `char-compress` unless a future implementation and tests explicitly establish that boundary.

## hmmm

- no CI currently runs the helper tools automatically
- propagation still requires review, commit, and pull request work in target repos
- `char_compress_check.py` is deterministic fixture support, not a full codec

# skill-lib tools

Small pure-stdlib helpers for maintaining this content repository.

These tools do not introduce an external build system. They are local editorial
checks, copy helpers, launchers, installers, and generated-file drift gates. The
small `llms/` package exists only to expose `python -m llms.build`.

## Gonol authority gate

```bash
bash tools/check_gonol_authority.sh
```

Fails if active skill-lib doctrine drifts back to assigning gonol/text
construction authority to EDCM. The active split is:

```text
UCNS  = gonol objects, constructors, geometry
Stack = active language-gonol construction research
EDCM  = measurement/evaluation only
```

## Canonical `ai.sh` and `work.sh` launchers

`tools/ai.sh` is the canonical Termux-side launcher for the coding-agent CLIs on
the `a0` VM. It uses the SSH host alias `a0` and owns the remote tmux session
layout (`0:shell`, `1:grok`, `2:codex`, `3:deepcode`), real pane/process status,
explicit restart, `remain-on-exit`, and persistent VM logs under
`~/.local/state/a0/logs`.

`tools/work.sh` is the parent menu for that unchanged AI route and Google Cloud
CLI inside Ubuntu. See [WORK.md](WORK.md) for prerequisites, repository-managed
updates, failure handling, and rollback.

Install both stable commands into the caller PATH:

```bash
bash tools/install_ai.sh
```

On Termux the installer symlinks both canonical sources into `$PREFIX/bin`,
which is already on PATH. Elsewhere it uses `~/.local/bin` and adds one
idempotent login-shell PATH line only when required. No independent launcher
copies are installed; repository updates flow through the links.

Examples:

```bash
work.sh
work.sh cloud
work.sh ai status
ai.sh
ai.sh status
ai.sh restart deepcode
ai.sh logs deepcode
ai.sh codex
```

Provider credentials remain the responsibility of the VM/provider CLIs.
`ai.sh keys` only copies already-present VM login-environment values into the
remote tmux environment so restarted CLIs can see them; it prints only
`present`/`missing` and never stores or displays key values.

## Drift checker

```bash
python tools/check_skill_lib_drift.py
python tools/check_skill_lib_drift.py --json
python tools/check_skill_lib_drift.py --warnings-fail
```

Checks that:

- every root directory with `SKILL.md` appears in `skills.json`;
- every `skills.json` entry has a matching `<skill>/SKILL.md` path;
- `README.md` lists every indexed skill;
- `ORG_DISTRIBUTION.md` lists every indexed skill;
- `AGENTS.md` and `CLAUDE.md` mention every indexed skill.

## Skill compliance checker

```bash
python tools/check_skill_compliance.py
python tools/check_skill_compliance.py --json
python tools/check_skill_compliance.py --warnings-fail
```

Checks baseline `skill-build` invariants for every `SKILL.md`: frontmatter
name, explicit load/use trigger text, `skills.json` registration, and visible
`hmmm` boundary, and one top-level workflow (fenced examples are excluded).
It reports softer shape guidance as warnings so historical
skills can be normalized one family at a time.

## Propagation helper

Dry-run by default:

```bash
python tools/propagate_skills.py ../target-repo
```

Apply copy:

```bash
python tools/propagate_skills.py ../target-repo --apply
```

Copy only selected skills:

```bash
python tools/propagate_skills.py ../target-repo --skills char-compress canon --apply
```

The helper copies canonical skill directories into:

```text
.agents/skills/<skill-name>/
```

It also carries any shared `doctrine/<file>` docs the propagated skills link to
(e.g. `msdmd`/`test-build` → `doctrine/msdmd-checks.md`) into
`.agents/skills/doctrine/`, so those relative links resolve in the vendored tree,
and writes `.agents/skills/README.md` in the target repo with the source commit
SHA. It does not commit, push, open pull requests, or contact GitHub.

## Consumer drift checker

The read-only counterpart to `propagate_skills.py`: given a checked-out consumer
repo, it reports whether that repo's vendored `.agents/skills/` subset still
matches this canonical skill-lib. This is what catches "canonical moved ahead"
drift before it accumulates between manual propagation PRs.

```bash
python tools/check_consumer_drift.py ../target-repo
python tools/check_consumer_drift.py ../target-repo --sha <skill-lib-commit>
python tools/check_consumer_drift.py ../target-repo --sha <commit> --strict-sha --json
```

The vendored subset is auto-detected (the intersection of the consumer's skill
directories with the canonical ones), so no per-repo config is needed. It:

- flags any canonical file missing from or differing in the vendored copy as
  drift (exit `1`);
- ignores repo-local additions — extra files, local runners, or repo-only
  skills beside the canonical assets;
- verifies a vendored `manifest/generate.py.sha256` still pins its `generate.py`;
- verifies any shared `doctrine/<file>` doc a vendored skill links to is present
  at `.agents/skills/doctrine/<file>` and matches canonical (a missing or stale
  referenced doctrine doc is drift);
- with `--sha`, warns when `.agents/skills/README.md` does not cite that source
  commit (an error under `--strict-sha`);
- with `--require-vendored`, fails when the repo vendors no canonical skills at
  all — used by the scheduled workflow, whose matrix is repos that must carry a
  subset, so an empty vendored set is itself a regression.

Read-only: it never writes to the consumer repo. The scheduled workflow
`.github/workflows/consumer-drift.yml` runs it against every consumer repo
weekly (and on demand); the consumer repos are public, so it checks them out
with the default `GITHUB_TOKEN` — no extra secret required.

## Org recommendation aggregator

Append repo-local `rec.md` recommendations into one org-level `rec.md` without
rewriting repo-owned reports:

```bash
python3 tools/aggregate_org_rec.py --root .. --out ../rec.md
python3 tools/aggregate_org_rec.py --root .. --out ../rec.md --append
python3 tools/aggregate_org_rec.py --root .. --out ../rec.md --strict
```

The runner discovers immediate child git checkouts, extracts the latest
`### Recommendations` section from each repo's `rec.md`, falls back to
`### Remaining` for repair-pass records, carries `### hmmm` forward, and appends
one timestamped aggregate section only when `--append` is supplied.
Repository-local `rec.md` files remain source reports; the org aggregate is a
derived index, not transferred canon.

## Org ratio comparison report

Collect shallow scalar/vector metrics across sibling repo checkouts and append
oddities into `docs.report`:

```bash
python3 tools/org_ratio_compare.py --root ..
python3 tools/org_ratio_compare.py --root .. --out ../docs.report --append
python3 tools/org_ratio_compare.py --root .. --json
```

The runner skips vendored `.agents`, dependency folders, build outputs, and
caches by default. Large text files are counted by bytes but not fully
line-counted past the configured byte ceiling; the report carries those limits
as `hmmm` instead of spending unbounded scan resources.

## llms-build runner

Dry-run generated root instructions:

```bash
python -m llms.build --root . --out llms.txt
```

Write the generated file:

```bash
python -m llms.build --root . --out llms.txt --apply
```

Check committed drift:

```bash
python -m llms.build --root . --out llms.txt --check
```

The runner parses `LLMS` blocks, ignores Markdown fenced-code examples, emits
unknowns as `hmmm`, and generates the canonical root `llms.txt` shape declared
in `llms-build/SKILL.md`.

## char-compress fixtures

```bash
python tools/char_compress_check.py
python tools/char_compress_check.py --json
```

Runs the preservation fixtures in:

```text
char-compress/fixtures.json
```

This is not a full natural-language compressor. It is a guardrail runner for
minimum preservation claims: negation, quantifier, order, values, statuses,
secrets, `hmmm`, and no UCNS-A / edcmbone status leakage.

## CI

`.github/workflows/ci.yml` runs the repo verification stack on pull requests and
pushes to `main`: unit tests, gonol-authority gate, skill drift, skill
compliance, ratios strict gate, llms-build drift, RepoLOTO audit, and RepoLOTO
checks.

`.github/workflows/consumer-drift.yml` runs `check_consumer_drift.py` against
every consumer repo on a weekly schedule (and on demand) to detect vendored-copy
drift. The consumer repos are public, so it uses the default `GITHUB_TOKEN` — no
extra secret required.

## hmmm

- `consumer-drift.yml` only *detects* drift; re-propagation still requires a
  human or agent to run `propagate_skills.py --apply`, review, commit, and open PRs
- `char_compress_check.py` verifies preservation fixtures but is not yet a complete codec
- third-party coding CLI command names and authentication methods can change;
  `tools/ai.sh` exposes command overrides rather than pretending those interfaces
  are permanent

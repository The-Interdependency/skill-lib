# CLAUDE.md — skill-lib

Assistant guidance for `The-Interdependency/skill-lib` (MPL-2.0).

## Entry points & delegation

- [`AGENTS.md`](AGENTS.md) — **authoritative agent entry point**: binding
  agent-context and resource-run invariants, skill-loading protocol, repo
  editing doctrine, and per-skill routing.
- [`README.md`](README.md) — human overview, `What's inside` skill summaries,
  Codex plugin install, `msdmd` block syntax, and `ai.sh` / `work.sh` launcher
  overview ([`tools/WORK.md`](tools/WORK.md), [`tools/A0-VAULT.md`](tools/A0-VAULT.md)).
- [`ORG_DISTRIBUTION.md`](ORG_DISTRIBUTION.md) — `.agents/skills/<skill-name>/`
  install convention, target repos, and propagation contract.
- [`tools/README.md`](tools/README.md) — pure-stdlib helpers (`propagate_skills.py`,
  `check_consumer_drift.py`, `check_skill_lib_drift.py`, `check_skill_compliance.py`,
  `ratios_check.py`, `char_compress_check.py`, `build_codex_plugin_skills.py`).
- `llms/` — stdlib `python -m llms.build` runner (`llms-build/SKILL.md`).

## Skill index

Every skill in [`skills.json`](skills.json) (see `README.md` for descriptions and `AGENTS.md` for loading triggers):

- **metadata-block**: `msdmd`, `doc-build`, `cap-build`, `deps-build`,
  `owner-build`, `test-build`, `meta-module-build`, `risk-boundary-build`,
  `ratios`, `manifest`, `llms-build`, `typed-meta-frontend`.
- **procedural**: `canon`, `domain-claims`, `visitor-intro`,
  `adaptive-elicitation`, `char-compress`, `agent-instantiation`, `a0p-instancing`,
  `plain-lens`, `thought-lens`, `gonol-build` (Stack language-construction research discipline),
  `ucns-option-selection`, `epac-selection-display`, `meta`, `the-interdependency`,
  `interdependent-work-graph`, `stack-update`, `project-incubation-graduation`,
  `distributed-publication`, `website-builder-journal`, `loop-eng`, `agent-ops`,
  `pstack-orchestration`, `fresh-making`, `action-calibration`, `wdll`,
  `repo-audit-repair`, `github-tests`, `skill-build`, `skill-usage`,
  `ssh-automation`, `vm-mcp`, `sql-queries`, `statistical-analysis`,
  `explore-data`, `validate-data`, `data-visualization`.

## Verification & runtime boundaries

- **No invented build commands**: There is no root `package.json`,
  `pyproject.toml`, or `Makefile`. CI runs `.github/workflows/ci.yml`,
  `hygiene.yml` (no tracked Python bytecode), and scheduled `consumer-drift.yml`
  (public repos via `GITHUB_TOKEN`).
- **Native-reader deps for full `msdmd` collection**: `msdmd/parsers/universal.{py,ts}`
  are pure stdlib; full schema-2 collection (`msdmd/collect.py`) also needs
  `python -m pip install -r msdmd/requirements.txt` and `npm ci --ignore-scripts --prefix msdmd`.
  With `--strict`, exit 0 validates only implemented required scope; unsupported
  conventions stay visible as `hmmm`.
- **Core gates** (see `.github/workflows/ci.yml` for exact flags):
  ```bash
  python -m msdmd.collect --root . --repo The-Interdependency/skill-lib --snapshot-identity --import-path ./msdmd/collection --out skill-lib_msdmd.ts --strict --check
  node msdmd/node_modules/typescript/bin/tsc --noEmit --strict --skipLibCheck --target ES2022 --module commonjs msdmd/collection.ts skill-lib_msdmd.ts
  python -m unittest discover -s tests
  bash tools/check_gonol_authority.sh
  python tools/check_skill_lib_drift.py --warnings-fail
  python tools/check_skill_compliance.py --warnings-fail
  python tools/build_codex_plugin_skills.py --check
  python ratios/ratios_check.py --strict
  python -m llms.build --root . --out llms.txt --check
  python tests/test_repo_loto.py --audit && python tests/test_repo_loto.py
  ```
- **Runner sections** in application `SKILL.md` files are contracts for consuming
  repos unless a helper file ships under that skill or package.

## hmmm

- propagation still requires review, commit, and pull request work in target repos
- `char_compress_check.py` is deterministic fixture support, not the full Unit Circle Number System compression engine
- provider-specific SSH wrappers must be rechecked against their current evaluated configuration rather than assumed to preserve OpenSSH defaults

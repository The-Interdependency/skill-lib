# skill-lib production readiness

`skill-lib` is production-ready as a canonical source of skill doctrine when the
repo can answer four questions without guessing:

1. What skills exist?
2. Where are they documented?
3. How are they propagated?
4. What remains unresolved?

## Current completed surface

- `README.md` indexes the skill set.
- `skills.json` is the machine-readable skill index.
- `AGENTS.md`, `CLAUDE.md`, and `llms.txt` provide agent-facing entry points.
- `ORG_DISTRIBUTION.md` names target repos and the canonical propagation rule.
- `msdmd/parsers/universal.py` and `.ts` provide reference parsers.
- `msdmd/collect.py`, `msdmd/collection.ts`, and `msdmd/visualize.py` provide
  the collection-point/graph pathway.
- `ratios/ratios_check.py` provides the canonical ratios gate.
- `tools/check_skill_lib_drift.py` and `tools/check_skill_compliance.py` provide
  editorial checks.

## Remaining work that should not be hidden

1. **CI coverage:** `hygiene.yml` checks bytecode only. The editorial tests and
   helper tools still need a CI workflow.
2. **Collection automation:** `skill-lib_msdmd.ts` is seeded as a root collection
   point; a local run of `python -m msdmd.collect ...` should replace or refresh
   it.
3. **Runner config:** artifact-aware skip lists are documented, but
   `msdmd/collect.py` does not yet accept a config file.
4. **Target propagation:** consuming repos still need collection points and
   repo-local verification PRs.
5. **Executor validation:** the org audit measures block presence, not
   required-field validity or contract execution.

## Production gate

Before tagging a release or calling a skill change propagated:

```bash
python -m unittest discover -s tests
python tools/check_skill_lib_drift.py
python tools/check_skill_compliance.py
python ratios/ratios_check.py --strict
python -m llms.build --root . --out llms.txt --check
```

## hmmm

This document records the boundary between doctrine-complete and automation-
complete. The doctrine is usable now. Full production automation still requires
CI wiring, collector config support, and target-repo propagation PRs.

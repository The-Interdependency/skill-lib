# skill-lib propagation checklist

This checklist is the org-standard path for moving a `skill-lib` change from the
canonical repo into a consuming repository.

## 1. Source change

1. Edit `The-Interdependency/skill-lib` first.
2. Keep these synchronized when a skill is added, renamed, removed, or materially
   changed:
   - `README.md`
   - `AGENTS.md`
   - `CLAUDE.md`
   - `ORG_DISTRIBUTION.md`
   - `skills.json`
   - generated `llms.txt` when an `LLMS` block changes
3. Run, in a local checkout:

```bash
python -m unittest discover -s tests
python tools/check_skill_lib_drift.py
python tools/check_skill_compliance.py
python ratios/ratios_check.py --strict
python -m llms.build --root . --out llms.txt --check
```

If one cannot be run, record that as `hmmm` in the PR body rather than claiming
it passed.

## 2. Propagate to a target repo

From a checkout of `skill-lib`:

```bash
python tools/propagate_skills.py ../target-repo          # inspect dry-run
python tools/propagate_skills.py ../target-repo --apply  # copy skill dirs
```

Then in the target repo:

1. Add or update `.agents/skills/README.md`.
2. Record the `skill-lib` source commit SHA.
3. Do not hand-edit copied skill files unless the edit is a repo-local patch
   clearly marked as such.
4. Prefer a separate target-repo PR per propagation batch.

## 3. Target repo verification

Minimum target checks:

```bash
python .agents/skills/manifest/generate.py --check
python -m msdmd.collect --root . --repo <repo> --out <repo>_msdmd.ts
```

Run any target-local checks named in `CLAUDE.md`, `AGENTS.md`, or
`.agents/skills/README.md`.

For ratios, use the target's sanctioned seal:

- new repos: canonical named `ratios:` line;
- `a0`: compact `N:M C:D I:O` dialect, enforced by `a0/scripts/annotate.py`;
- `a0-betatest`: read-only mirror; observe only.

## 4. PR body requirements

Every propagation PR should say:

- source repo: `The-Interdependency/skill-lib`;
- source commit SHA;
- target repo;
- exact skills copied;
- checks run;
- checks not run, with `hmmm`;
- whether generated files changed;
- whether target-local doctrine differs from canonical skill-lib doctrine.

## 5. Hard stops

Do not propagate into:

- `a0-betatest` directly; it is an observe-only mirror.
- archived repos unless the PR is explicitly historical/documentation-only.
- repos whose local doctrine contradicts the skill change, until the contradiction
  is named and resolved.

## hmmm

This checklist does not perform GitHub commits or PR creation. The local helper
copies files only; humans or repo agents still review, commit, push, and open the
target PR.

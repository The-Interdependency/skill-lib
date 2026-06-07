# skill-lib tools

Small pure-stdlib helpers for maintaining this content repository.

These tools do not make `skill-lib` a package and do not introduce a build
system. They are local editorial checks and copy helpers.

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

It also writes `.agents/skills/README.md` in the target repo with the source
commit SHA. It does not commit, push, open pull requests, or contact GitHub.

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

## hmmm

- no CI currently runs these tools automatically
- propagation still requires a human or agent to review, commit, and open PRs in target repos
- `char_compress_check.py` verifies preservation fixtures but is not yet a complete codec

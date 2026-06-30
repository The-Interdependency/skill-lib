# skill-lib tools

Small pure-stdlib helpers for maintaining this content repository.

These tools do not introduce an external build system. They are local editorial
checks, copy helpers, and generated-file drift gates. The small `llms/` package
exists only to expose `python -m llms.build`.

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
`hmmm` boundary. It reports softer shape guidance as warnings so historical
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

It also writes `.agents/skills/README.md` in the target repo with the source
commit SHA. It does not commit, push, open pull requests, or contact GitHub.

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

## hmmm

- no CI currently runs these tools automatically
- propagation still requires a human or agent to review, commit, and open PRs in target repos
- `char_compress_check.py` verifies preservation fixtures but is not yet a complete codec

# ratios: loc_comments=111:12 imports_exports=8:10 calls_definitions=53:12
"""Check baseline SKILL.md compliance for skill-lib.

This checker intentionally enforces only repo-wide invariants that are already
canon in AGENTS.md and skill-build/SKILL.md. It reports softer section-shape
recommendations as warnings so historical skills can be normalized family by
family without doctrinal churn.

Usage: python tools/check_skill_compliance.py --warnings-fail
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Finding:
    level: str
    skill: str
    code: str
    message: str


FRONTMATTER_RE = re.compile(r"\A---\n(?P<body>.*?)\n---\n", re.DOTALL)


def load_index(root: Path = ROOT) -> dict:
    return json.loads((root / "skills.json").read_text(encoding="utf-8"))


def skill_paths(root: Path = ROOT) -> list[Path]:
    return sorted(path for path in root.glob("*/SKILL.md") if path.is_file())


def frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    data: dict[str, str] = {}
    for raw in match.group("body").splitlines():
        if ":" not in raw or raw.startswith(" "):
            continue
        key, value = raw.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def frontmatter_text(text: str) -> str:
    match = FRONTMATTER_RE.match(text)
    return match.group("body") if match else ""


def _heading_names(text: str) -> Iterable[str]:
    """Yield ATX level-two names outside recognized fences.

    Accept zero to three spaces, space/tab separators and optional closing hashes.
    This lexical scan does not parse Markdown HTML blocks or container nesting.
    """
    fence = ""
    for line in text.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if marker:
            token, suffix = marker.groups()
            if not fence:
                if token[0] == "~" or "`" not in suffix:
                    fence = token
            elif token[0] == fence[0] and len(token) >= len(fence) and not suffix.strip(" \t"):
                fence = ""
            continue
        heading = re.match(r"^ {0,3}##[ \t]+(.*)$", line)
        if not fence and heading:
            yield re.sub(r"[ \t]+#+[ \t]*$", "", heading.group(1)).strip(" \t").lower()


def _matches_heading(heading: str, name: str) -> bool:
    wanted = name.lower()
    return heading == wanted or heading.startswith(f"{wanted}:")


def has_heading(text: str, *names: str) -> bool:
    return any(_matches_heading(heading, name) for heading in _heading_names(text) for name in names)


def workflow_count(text: str) -> int:
    """Count plain or titled workflow headings using the same presence rules."""
    return sum(_matches_heading(heading, "workflow") for heading in _heading_names(text))


def check_skill(path: Path, indexed: dict[str, dict]) -> list[Finding]:
    name = path.parent.name
    text = path.read_text(encoding="utf-8")
    fm = frontmatter(text)
    fm_text = frontmatter_text(text)
    findings: list[Finding] = []

    if workflow_count(text) > 1:
        findings.append(Finding("error", name, "duplicate_workflow", "consolidate competing Workflow sections; preserve distinct obligations at their execution points"))

    if fm.get("name") != name:
        findings.append(Finding("error", name, "frontmatter_name", f"frontmatter name must be {name!r}"))

    desc = fm.get("description", "")
    if "Load this when" not in desc and "Use this when" not in desc:
        if "Load this when" not in fm_text and "Use this when" not in fm_text:
            findings.append(Finding("error", name, "load_trigger", "description must include explicit Load this when / Use this when trigger text"))

    if name not in indexed:
        findings.append(Finding("error", name, "missing_index", "skill directory is absent from skills.json"))

    if "hmmm" not in text:
        findings.append(Finding("error", name, "missing_hmmm", "skill must preserve an explicit hmmm boundary"))

    kind = indexed.get(name, {}).get("kind", "hmmm")
    if kind == "metadata-block":
        if "Runner" not in text and "runner" not in text:
            findings.append(Finding("warning", name, "runner_guidance", "metadata-block skill should explain runner or consuming-repo contract guidance"))
        if "required" not in text.lower() and "Required" not in text:
            findings.append(Finding("warning", name, "field_requirements", "metadata-block skill should identify required vs optional fields or explain why not applicable"))
    elif kind == "procedural":
        if not has_heading(text, "workflow", "make-fresh workflow", "canonization workflow", "compression procedure", "instancing sequence (dependency order — follow it top to bottom)", "instantiation sequence (dependency order — follow it top to bottom)", "compliance workflow for existing skills"):
            findings.append(Finding("warning", name, "workflow_shape", "procedural skill should expose an ordered workflow, sequence, or procedure heading"))

    if "Anti-pattern" not in text and "anti-pattern" not in text:
        findings.append(Finding("warning", name, "anti_patterns", "skill should name common anti-patterns or explain why none are useful"))

    return findings


def collect_findings(root: Path = ROOT) -> list[Finding]:
    index = load_index(root)
    indexed = {entry.get("name", ""): entry for entry in index.get("skills", []) if isinstance(entry, dict)}
    findings: list[Finding] = []
    for path in skill_paths(root):
        findings.extend(check_skill(path, indexed))
    return findings


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check baseline skill-build compliance for SKILL.md files.")
    parser.add_argument("--json", action="store_true", help="Emit findings as JSON.")
    parser.add_argument("--warnings-fail", action="store_true", help="Treat warnings as failures.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    findings = collect_findings()
    errors = [f for f in findings if f.level == "error"]
    warnings = [f for f in findings if f.level == "warning"]

    if args.json:
        print(json.dumps([f.__dict__ for f in findings], indent=2, sort_keys=True))
    else:
        for f in findings:
            print(f"{f.level}: {f.skill}: {f.code}: {f.message}")
        status = "pass" if not errors and not (args.warnings_fail and warnings) else "fail"
        print(f"skill compliance: {status} ({len(errors)} errors, {len(warnings)} warnings)")

    return 1 if errors or (args.warnings_fail and warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
# ratios: loc_comments=111:12 imports_exports=8:10 calls_definitions=53:12

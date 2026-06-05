#!/usr/bin/env python3
"""Editorial drift checker for The-Interdependency/skill-lib.

Checks that the canonical skill directories, skills.json, README.md,
ORG_DISTRIBUTION.md, AGENTS.md, and CLAUDE.md agree about installed skills.
Pure stdlib. No network access.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Set

ROOT = Path(__file__).resolve().parents[1]
SKILLS_JSON = ROOT / "skills.json"
README = ROOT / "README.md"
ORG = ROOT / "ORG_DISTRIBUTION.md"
AGENTS = ROOT / "AGENTS.md"
CLAUDE = ROOT / "CLAUDE.md"

IGNORE_DIRS = {".git", ".github", "tools", "__pycache__"}


@dataclass
class Finding:
    severity: str
    code: str
    message: str


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def skill_dirs(root: Path = ROOT) -> Set[str]:
    out = set()
    for child in root.iterdir():
        if not child.is_dir() or child.name in IGNORE_DIRS or child.name.startswith("."):
            continue
        if (child / "SKILL.md").is_file():
            out.add(child.name)
    return out


def load_index(path: Path = SKILLS_JSON) -> Dict[str, Mapping[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    skills = data.get("skills", [])
    if not isinstance(skills, list):
        raise ValueError("skills.json must contain a skills list")
    indexed: Dict[str, Mapping[str, Any]] = {}
    for entry in skills:
        if not isinstance(entry, Mapping):
            continue
        name = str(entry.get("name", ""))
        if name:
            indexed[name] = entry
    return indexed


def names_in_readme(text: str) -> Set[str]:
    return set(re.findall(r"\[`([^`/]+)/`\]\([^)]*?/SKILL\.md\)", text))


def names_in_org(text: str) -> Set[str]:
    return set(re.findall(r"\* `([^`/]+)/` —", text))


def has_mention(text: str, skill: str) -> bool:
    return skill in text or f"`{skill}`" in text or f"`{skill}/`" in text


def check() -> List[Finding]:
    findings: List[Finding] = []
    dirs = skill_dirs()
    index = load_index()
    index_names = set(index)
    readme_names = names_in_readme(read(README))
    org_names = names_in_org(read(ORG))
    agents_text = read(AGENTS)
    claude_text = read(CLAUDE)

    for name in sorted(dirs - index_names):
        findings.append(Finding("error", "missing_index_entry", f"{name} has SKILL.md but is absent from skills.json"))
    for name in sorted(index_names - dirs):
        findings.append(Finding("error", "missing_skill_dir", f"{name} is in skills.json but {name}/SKILL.md is missing"))

    for name, entry in sorted(index.items()):
        expected_path = f"{name}/SKILL.md"
        actual_path = str(entry.get("path", ""))
        if actual_path != expected_path:
            findings.append(Finding("error", "bad_index_path", f"{name} path is {actual_path!r}, expected {expected_path!r}"))
        if entry.get("kind") not in {"metadata-block", "procedural"}:
            findings.append(Finding("error", "bad_kind", f"{name} has invalid kind {entry.get('kind')!r}"))
        if not str(entry.get("description", "")).strip():
            findings.append(Finding("error", "missing_description", f"{name} has no description"))

    for name in sorted(index_names - readme_names):
        findings.append(Finding("error", "missing_readme_entry", f"{name} is absent from README.md skill table"))
    for name in sorted(readme_names - index_names):
        findings.append(Finding("warning", "extra_readme_entry", f"{name} appears in README.md but not skills.json"))

    for name in sorted(index_names - org_names):
        findings.append(Finding("error", "missing_org_entry", f"{name} is absent from ORG_DISTRIBUTION.md installed skills"))
    for name in sorted(org_names - index_names):
        findings.append(Finding("warning", "extra_org_entry", f"{name} appears in ORG_DISTRIBUTION.md but not skills.json"))

    for name in sorted(index_names):
        if not has_mention(agents_text, name):
            findings.append(Finding("warning", "missing_agents_mention", f"{name} is not mentioned in AGENTS.md"))
        if not has_mention(claude_text, name):
            findings.append(Finding("warning", "missing_claude_mention", f"{name} is not mentioned in CLAUDE.md"))

    return findings


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check skill-lib editorial drift.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--warnings-fail", action="store_true", help="Exit nonzero on warnings as well as errors.")
    args = parser.parse_args(argv)

    findings = check()
    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]
    status = "pass" if not errors and (not warnings or not args.warnings_fail) else "fail"

    if args.json:
        print(json.dumps({
            "status": status,
            "errors": [f.__dict__ for f in errors],
            "warnings": [f.__dict__ for f in warnings],
        }, indent=2, sort_keys=True))
    else:
        print(f"skill-lib drift: {status} ({len(errors)} errors, {len(warnings)} warnings)")
        for finding in findings:
            print(f"{finding.severity.upper()} {finding.code}: {finding.message}")

    return 1 if status == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())

# ratios: loc_comments=218:48 imports_exports=9:11 calls_definitions=80:15
"""Detect drift between a consumer repo's vendored skills and canonical skill-lib.

Given a checked-out consumer repository, for every skill directory it vendors
under ``.agents/skills/`` that also exists in this canonical ``skill-lib``, verify
the canonical files match verbatim. The vendored subset is auto-detected as the
intersection of the consumer's skill directories with the canonical ones, so no
per-repo configuration is required.

Rules (matching org propagation doctrine):

* A canonical file that is missing from, or differs in, the vendored copy is
  ``drift`` (an error). Repo-local additions -- files or directories present in
  the vendored copy but absent from canonical -- are allowed and ignored, so a
  repo may keep local runners, extra skills, or its own README beside the
  canonical assets.
* Bytecode (``__pycache__`` / ``*.pyc``) is ignored on both sides.
* When a vendored ``manifest/generate.py.sha256`` companion is present it must
  pin the vendored ``generate.py`` (``sha256sum -c`` semantics); a stale pin is
  drift.
* Any shared ``doctrine/<file>`` doc a vendored skill links to (e.g.
  ``../doctrine/msdmd-checks.md``) must be vendored at
  ``.agents/skills/doctrine/<file>`` and match canonical; a missing or stale
  referenced doctrine doc is drift too.
* With ``--sha`` given, the consumer ``.agents/skills/README.md`` should cite that
  canonical source commit; a missing/mismatched citation is a warning (an error
  under ``--strict-sha``).

Pure stdlib. No network. Read-only -- it never writes to the consumer repo.
Exit status is ``0`` when clean, ``1`` on drift (or a SHA warning under
``--strict-sha``, or zero vendored canonical skills under ``--require-vendored``),
``2`` on a usage error. ``--require-vendored`` is for callers -- like the
scheduled workflow -- whose targets are known to carry a subset, so an empty
vendored set is itself a regression.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SKILLS_REL = Path(".agents/skills")
IGNORE_PARTS = {"__pycache__"}
# GNU sha256sum output line: 64 lowercase hex, one space, one mode char
# (' ' text / '*' binary), then the filename immediately -- no other spacing.
PIN_LINE_RE = re.compile(r"^(?P<digest>[0-9a-f]{64}) [ *]generate\.py$")
# A skill file linking to a shared doctrine doc, e.g. `../doctrine/msdmd-checks.md`.
# Skills live at `.agents/skills/<skill>/`, so `../doctrine/<f>` resolves to the
# sibling `.agents/skills/doctrine/<f>` -- which must be vendored alongside them.
DOCTRINE_REF_RE = re.compile(r"(?:\.\./)?doctrine/([A-Za-z0-9][\w./-]*\.md)")
_TEXT_SUFFIXES = {".md", ".py", ".ts", ".txt"}


@dataclass
class SkillReport:
    name: str
    drift: List[str] = field(default_factory=list)  # human-readable per-file reasons

    @property
    def ok(self) -> bool:
        return not self.drift


@dataclass
class ConsumerReport:
    consumer: str
    skills: List[SkillReport] = field(default_factory=list)
    doctrine: List[str] = field(default_factory=list)  # referenced-doctrine drift reasons
    sha_warning: str | None = None

    @property
    def drifted(self) -> List[SkillReport]:
        return [s for s in self.skills if not s.ok]


def _ignored(path: Path) -> bool:
    return any(part in IGNORE_PARTS or part.endswith(".pyc") for part in path.parts)


def canon_skill_names(canon_root: Path) -> set[str]:
    return {
        child.name
        for child in canon_root.iterdir()
        if child.is_dir() and (child / "SKILL.md").is_file()
    }


def _canon_files(skill_dir: Path) -> Iterable[Path]:
    for path in sorted(skill_dir.rglob("*")):
        if path.is_file() and not _ignored(path.relative_to(skill_dir)):
            yield path


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def referenced_doctrine(skill_dir: Path) -> set[str]:
    """Shared `doctrine/<file>` docs a skill's text files link to."""
    refs: set[str] = set()
    for path in _canon_files(skill_dir):
        if path.suffix.lower() not in _TEXT_SUFFIXES:
            continue
        refs.update(DOCTRINE_REF_RE.findall(path.read_text(encoding="utf-8", errors="ignore")))
    return refs


def check_doctrine(canon_root: Path, skills_root: Path, vendored_canon: List[str]) -> List[str]:
    """Every doctrine doc referenced by a vendored skill must be present + verbatim."""
    refs: set[str] = set()
    for name in vendored_canon:
        refs.update(referenced_doctrine(canon_root / name))
    reasons: List[str] = []
    for ref in sorted(refs):
        canon_doc = canon_root / "doctrine" / ref
        if not canon_doc.is_file():
            continue  # dangling reference in canonical itself -- skill-lib's problem, not the vendor's
        vend_doc = skills_root / "doctrine" / ref
        if not vend_doc.is_file():
            reasons.append(f"missing: doctrine/{ref}")
        elif vend_doc.read_bytes() != canon_doc.read_bytes():
            reasons.append(f"differs: doctrine/{ref}")
    return reasons


def diff_skill(canon_dir: Path, vend_dir: Path) -> List[str]:
    """Canonical files that are missing from or differ in the vendored copy."""
    reasons: List[str] = []
    for canon_file in _canon_files(canon_dir):
        rel = canon_file.relative_to(canon_dir)
        vend_file = vend_dir / rel
        if not vend_file.is_file():
            reasons.append(f"missing: {rel}")
        elif vend_file.read_bytes() != canon_file.read_bytes():
            reasons.append(f"differs: {rel}")
    return reasons


def check_manifest_pin(vend_dir: Path) -> List[str]:
    """A vendored generate.py.sha256, if present, must pin generate.py.

    Mirrors ``sha256sum -c`` exactly: the pin must be a single line of the form
    ``<64-hex-lowercase> <mode>generate.py`` -- checksum, one space, one mode
    character (``' '`` text / ``'*'`` binary), then the filename immediately,
    with no extra separators, markers, or lines. A pin with the right digest but
    any deviation (wrong name, extra spaces, doubled marker, extra line) would
    make the consumer's ``sha256sum -c`` CI fail or check the wrong path, so
    ``PIN_LINE_RE`` rejects all of them as drift rather than trusting a loose
    token split.
    """
    pin = vend_dir / "generate.py.sha256"
    gen = vend_dir / "generate.py"
    if not pin.is_file():
        return []
    if not gen.is_file():
        return ["stale pin: generate.py.sha256 present but generate.py missing"]
    lines = [line for line in pin.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(lines) != 1:
        return ["malformed pin: generate.py.sha256 must hold exactly one checksum line"]
    match = PIN_LINE_RE.match(lines[0])
    if not match:
        return ["malformed pin: generate.py.sha256 is not a '<sha256>  generate.py' line"]
    if match.group("digest") != sha256_of(gen):
        return ["stale pin: generate.py.sha256 does not match generate.py"]
    return []


def check_consumer(
    consumer_root: Path,
    canon_root: Path = ROOT,
    skills_rel: Path = DEFAULT_SKILLS_REL,
    sha: str | None = None,
) -> ConsumerReport:
    report = ConsumerReport(consumer=str(consumer_root))
    skills_root = consumer_root / skills_rel
    if not skills_root.is_dir():
        report.sha_warning = f"no {skills_rel} directory (nothing vendored)"
        return report

    canon = canon_skill_names(canon_root)
    vendored = sorted(
        child.name for child in skills_root.iterdir() if child.is_dir()
    )
    vendored_canon: List[str] = []
    for name in vendored:
        if name not in canon:
            continue  # repo-local skill, not part of the canonical set
        vendored_canon.append(name)
        skill = SkillReport(name=name)
        skill.drift.extend(diff_skill(canon_root / name, skills_root / name))
        if name == "manifest":
            skill.drift.extend(check_manifest_pin(skills_root / name))
        report.skills.append(skill)

    report.doctrine.extend(check_doctrine(canon_root, skills_root, vendored_canon))

    if sha:
        readme = skills_root / "README.md"
        text = readme.read_text(encoding="utf-8") if readme.is_file() else ""
        short = sha[:7]
        if short not in text and sha not in text:
            report.sha_warning = f"README does not cite source commit {short}"
    return report


def format_report(
    report: ConsumerReport, strict_sha: bool, require_vendored: bool = False
) -> tuple[str, bool]:
    lines: List[str] = []
    checked = len(report.skills)
    drifted = report.drifted
    for skill in report.skills:
        if skill.ok:
            lines.append(f"  OK    {skill.name}")
        else:
            lines.append(f"  DRIFT {skill.name}")
            lines.extend(f"          - {reason}" for reason in skill.drift)
    for reason in report.doctrine:
        lines.append(f"  DOC   {reason}")
    if report.sha_warning:
        lines.append(f"  SHA   {report.sha_warning}")
    empty = require_vendored and checked == 0
    if empty:
        lines.append("  NONE  no canonical skills vendored (a subset was expected)")
    failed = (
        bool(drifted)
        or bool(report.doctrine)
        or empty
        or (strict_sha and report.sha_warning is not None)
    )
    status = "DRIFT" if failed else "clean"
    header = (
        f"{report.consumer}: {status} "
        f"({checked} canonical skills checked, {len(drifted)} drifted)"
    )
    return "\n".join([header, *lines]), failed


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Detect drift between a consumer repo's vendored skills and canonical skill-lib."
    )
    parser.add_argument(
        "consumer", type=Path, help="Path to a checked-out consumer repository."
    )
    parser.add_argument(
        "--canon-root",
        type=Path,
        default=ROOT,
        help="Path to canonical skill-lib (default: this repo).",
    )
    parser.add_argument(
        "--skills-rel",
        type=Path,
        default=DEFAULT_SKILLS_REL,
        help="Vendored skills root relative to the consumer (default: .agents/skills).",
    )
    parser.add_argument(
        "--sha", help="Canonical source commit the vendored copies should cite."
    )
    parser.add_argument(
        "--strict-sha",
        action="store_true",
        help="Treat a missing/mismatched README source-commit citation as drift.",
    )
    parser.add_argument(
        "--require-vendored",
        action="store_true",
        help="Fail when the consumer vendors no canonical skills (for repos that must carry a subset).",
    )
    parser.add_argument("--json", action="store_true", help="Emit a JSON report.")
    args = parser.parse_args(argv)

    consumer = args.consumer.resolve()
    if not consumer.is_dir():
        print(f"consumer repo does not exist or is not a directory: {consumer}", file=sys.stderr)
        return 2

    report = check_consumer(
        consumer, canon_root=args.canon_root.resolve(), skills_rel=args.skills_rel, sha=args.sha
    )
    text, failed = format_report(
        report, strict_sha=args.strict_sha, require_vendored=args.require_vendored
    )
    if args.json:
        payload = {
            "consumer": report.consumer,
            "drift": {s.name: s.drift for s in report.skills if not s.ok},
            "doctrine": report.doctrine,
            "checked": [s.name for s in report.skills],
            "sha_warning": report.sha_warning,
            "failed": failed,
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(text)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
# ratios: loc_comments=218:48 imports_exports=9:11 calls_definitions=80:15

# ratios: loc_comments=109:9 imports_exports=9:6 calls_definitions=50:6
"""Copy canonical skill-lib skills into a target repo working tree.

This script is intentionally local-file based. It does not push, commit, open
PRs, or contact GitHub. Run it from a checked-out skill-lib repo and point it at
a checked-out target repo. Dry-run is the default.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SKILLS_JSON = ROOT / "skills.json"
DEFAULT_INSTALL_ROOT = Path(".agents/skills")
# Skills may link to shared docs under `doctrine/` (e.g. `../doctrine/msdmd-checks.md`);
# those must be carried alongside the skills or the vendored links go dead.
DOCTRINE_REF_RE = re.compile(r"(?:\.\./)?doctrine/([A-Za-z0-9][\w./-]*\.md)")
_TEXT_SUFFIXES = {".md", ".py", ".ts", ".txt"}


def load_skill_names() -> List[str]:
    data = json.loads(SKILLS_JSON.read_text(encoding="utf-8"))
    return [str(entry["name"]) for entry in data.get("skills", [])]


def current_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "hmmm-local-sha-unavailable"


def copytree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def referenced_doctrine(skill_srcs: Iterable[Path]) -> List[str]:
    """Shared `doctrine/<file>` docs the given skill directories link to."""
    refs: set[str] = set()
    for src in skill_srcs:
        for path in src.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in _TEXT_SUFFIXES:
                continue
            refs.update(DOCTRINE_REF_RE.findall(path.read_text(encoding="utf-8", errors="ignore")))
    return sorted(ref for ref in refs if (ROOT / "doctrine" / ref).is_file())


def write_readme(target_install_root: Path, sha: str, skills: Sequence[str]) -> None:
    lines = [
        "# Local agent skills",
        "",
        "This directory contains repo-local copies of canonical skills from",
        "`The-Interdependency/skill-lib`.",
        "",
        f"Source commit: `{sha}`",
        "",
        "Repo-local copies are not the source of truth. Edit `skill-lib` first,",
        "then propagate from the canonical source.",
        "",
        "Installed skills:",
        "",
    ]
    lines.extend(f"- `{name}/`" for name in skills)
    lines.append("")
    target_install_root.mkdir(parents=True, exist_ok=True)
    (target_install_root / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Propagate skill-lib skills to a local target repo.")
    parser.add_argument("target_repo", type=Path, help="Path to a checked-out target repository.")
    parser.add_argument("--install-root", type=Path, default=DEFAULT_INSTALL_ROOT, help="Relative install root inside target repo.")
    parser.add_argument("--skills", nargs="*", help="Specific skill names to copy. Default: all skills in skills.json.")
    parser.add_argument("--apply", action="store_true", help="Actually write files. Default is dry-run.")
    args = parser.parse_args(argv)

    target_repo = args.target_repo.resolve()
    if not target_repo.exists() or not target_repo.is_dir():
        print(f"target repo does not exist or is not a directory: {target_repo}", file=sys.stderr)
        return 2

    available = set(load_skill_names())
    requested = args.skills or sorted(available)
    unknown = sorted(set(requested) - available)
    if unknown:
        print(f"unknown skills: {', '.join(unknown)}", file=sys.stderr)
        return 2

    install_root = target_repo / args.install_root
    sha = current_sha()

    actions = []
    for name in requested:
        src = ROOT / name
        dst = install_root / name
        if not (src / "SKILL.md").is_file():
            print(f"missing source skill: {src}", file=sys.stderr)
            return 2
        actions.append((src, dst))

    # Carry any shared doctrine docs the propagated skills link to.
    doc_actions = [
        (ROOT / "doctrine" / ref, install_root / "doctrine" / ref)
        for ref in referenced_doctrine(src for src, _ in actions)
    ]

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"{mode}: propagate {len(actions)} skills + {len(doc_actions)} doctrine docs to {install_root}")
    print(f"source commit: {sha}")
    for src, dst in actions:
        print(f"- {src.relative_to(ROOT)} -> {dst}")
    for src, dst in doc_actions:
        print(f"- {src.relative_to(ROOT)} -> {dst}")

    if not args.apply:
        print("No files changed. Re-run with --apply to copy.")
        return 0

    install_root.mkdir(parents=True, exist_ok=True)
    for src, dst in actions:
        copytree(src, dst)
    for src, dst in doc_actions:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    write_readme(install_root, sha, requested)
    print("Propagation complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
# ratios: loc_comments=109:9 imports_exports=9:6 calls_definitions=50:6

# ratios: loc_comments=193:14 imports_exports=9:11 calls_definitions=96:11
"""Synchronize canonical skill-lib skills into a target repo working tree.

This script is intentionally local-file based. It does not push, commit, open
PRs, or contact GitHub. Run it from a checked-out skill-lib repo and point it at
a checked-out target repo. Repo-local additions are preserved. Files retired
from canonical are removed only when the target's cited prior source commit
proves they are unchanged canonical files. Dry-run is the default.
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
SOURCE_SHA_RE = re.compile(r"Source commit:[^\n]*`([0-9a-f]{7,40})`")
SKILL_SOURCE_RE = re.compile(r"^- `([^`/]+)/`[^\n]*\[not refreshed; prior source: `([0-9a-f]{7,40}|hmmm)`\]$", re.MULTILINE)
_TEXT_SUFFIXES = {".md", ".py", ".ts", ".txt"}


def load_index() -> Mapping[str, object]:
    return json.loads(SKILLS_JSON.read_text(encoding="utf-8"))


def load_skill_names() -> List[str]:
    data = load_index()
    return [str(entry["name"]) for entry in data.get("skills", [])]


def load_superseded_names() -> List[str]:
    return sorted(
        str(entry["name"])
        for entry in load_index().get("superseded_skills", [])
        if isinstance(entry, Mapping) and entry.get("name")
    )


def current_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "hmmm-local-sha-unavailable"


def previous_source_sha(target_install_root: Path) -> str | None:
    readme = target_install_root / "README.md"
    if not readme.is_file():
        return None
    match = SOURCE_SHA_RE.search(readme.read_text(encoding="utf-8"))
    return match.group(1) if match else None


def previous_skill_source_sha(target_install_root: Path, skill_name: str) -> str | None:
    """Return a skill-local prior source recorded by an earlier partial refresh."""
    readme = target_install_root / "README.md"
    if not readme.is_file():
        return None
    text = readme.read_text(encoding="utf-8")
    for name, sha in SKILL_SOURCE_RE.findall(text):
        if name == skill_name:
            return None if sha == "hmmm" else sha
    return None


def previous_canonical_blob(sha: str, skill_name: str, relative_path: Path) -> bytes | None:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "show", f"{sha}:{skill_name}/{relative_path.as_posix()}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.stdout if result.returncode == 0 else None


def sync_tree(src: Path, dst: Path, prior_sha: str | None) -> List[Path]:
    """Update canonical files without deleting proven repo-local additions."""
    removed: List[Path] = []
    if dst.exists() and prior_sha:
        for existing in sorted(dst.rglob("*")):
            if not existing.is_file():
                continue
            relative = existing.relative_to(dst)
            if (src / relative).exists():
                continue
            prior = previous_canonical_blob(prior_sha, src.name, relative)
            if prior is not None and existing.read_bytes() == prior:
                existing.unlink()
                removed.append(relative)
        for directory in sorted(
            (path for path in dst.rglob("*") if path.is_dir()),
            key=lambda path: len(path.parts),
            reverse=True,
        ):
            if not any(directory.iterdir()):
                directory.rmdir()
    shutil.copytree(src, dst, dirs_exist_ok=True)
    return removed


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
    readme = target_install_root / "README.md"
    old_text = readme.read_text(encoding="utf-8") if readme.is_file() else ""
    old_entries = dict(re.findall(r"^(- `([^`/]+)/`[^\n]*)$", old_text, re.MULTILINE))
    # Preserve owner-written descriptions for installed but unrefreshed skills.
    by_name = {name: line for line, name in old_entries.items()}
    others = sorted(path.parent.name for path in target_install_root.glob("*/SKILL.md")
                    if path.parent.name not in skills)
    prior = previous_source_sha(target_install_root)
    canonical = set(load_skill_names())
    for name in others:
        if name in canonical and "prior source:" not in by_name.get(name, ""):
            identity = prior if name in by_name and prior else "hmmm"
            by_name[name] = by_name.get(name, f"- `{name}/`") + f" [not refreshed; prior source: `{identity}`]"
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
        "Skills refreshed from the source commit above:",
        "",
    ]
    lines.extend(f"- `{name}/`" for name in skills)
    lines.append("")
    if others:
        lines.extend([
            "Other installed skills (not refreshed by this propagation):", "",
            "Their existing files retain their own authority/provenance; the source",
            "commit above does not assert that these copies were refreshed.", "",
        ])
        lines.extend(by_name.get(name, f"- `{name}/`") for name in others)
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
    prior_sha = previous_source_sha(install_root)
    removals = [install_root / name for name in load_superseded_names() if (install_root / name).exists()]

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
    print(
        f"{mode}: propagate {len(actions)} skills + {len(doc_actions)} doctrine docs "
        f"and remove {len(removals)} superseded skills from {install_root}"
    )
    print(f"source commit: {sha}")
    for src, dst in actions:
        print(f"- {src.relative_to(ROOT)} -> {dst}")
    for src, dst in doc_actions:
        print(f"- {src.relative_to(ROOT)} -> {dst}")
    for dst in removals:
        print(f"- remove superseded {dst}")

    if not args.apply:
        print("No files changed. Re-run with --apply to copy.")
        return 0

    install_root.mkdir(parents=True, exist_ok=True)
    for dst in removals:
        shutil.rmtree(dst)
    removed_files: List[tuple[str, Path]] = []
    for src, dst in actions:
        skill_prior_sha = previous_skill_source_sha(install_root, src.name) or prior_sha
        removed_files.extend((src.name, path) for path in sync_tree(src, dst, skill_prior_sha))
    for src, dst in doc_actions:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    write_readme(install_root, sha, requested)
    for skill_name, path in removed_files:
        print(f"Removed obsolete canonical file: {skill_name}/{path}")
    print("Propagation complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
# ratios: loc_comments=193:14 imports_exports=9:11 calls_definitions=96:11
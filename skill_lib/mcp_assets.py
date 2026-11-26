# ratios: loc_comments=75:3 imports_exports=6:2 calls_definitions=39:8
"""List and read the exact, packaged, skill-local supporting documents over MCP."""

from hashlib import sha256
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import subprocess

from .mcp_catalog import CatalogError, SkillCatalog

MANIFEST = Path(__file__).with_name("mcp_assets.json")
_DIRS = {"references", "templates", "examples", "assets", "scripts"}
_EXTENSIONS = {".md", ".txt", ".json", ".toml", ".yaml", ".yml", ".csv", ".tsv",
               ".py", ".js", ".ts", ".sh", ".sql"}
_ROOT_FILES = {"fixtures.json", "visual-grammar.json", "STACK_SOURCE_FIXTURE.json"}


def _admissible(relative: str) -> bool:
    # Only exact, portable POSIX spellings enter a record or reach the filesystem.
    if not isinstance(relative, str) or not relative or "\\" in relative:
        return False
    path = PurePosixPath(relative)
    if (path.is_absolute() or path.as_posix() != relative or PureWindowsPath(relative).drive
            or any(not part or part.startswith(".") or ":" in part for part in path.parts)):
        return False
    if len(path.parts) == 1:
        return (relative.endswith((".md", ".schema.json")) and relative != "SKILL.md"
                or relative in _ROOT_FILES)
    return path.parts[0] in _DIRS and path.suffix in _EXTENSIONS


def _bytes(root: Path, name: str, relative: str) -> bytes:
    path = root / name / relative
    if (not _admissible(relative) or path.resolve() != path or not path.is_file()):
        raise CatalogError("skill support file unavailable")
    return path.read_bytes()


def source_assets(root: Path, names) -> dict:
    """Regenerate the distribution inventory from tracked, regular support files."""
    root = root.resolve()
    names = set(names)
    listed = subprocess.check_output(["git", "-C", str(root), "ls-files", "--stage", "-z"])
    skills = {}
    for entry in listed.split(b"\0"):
        if not entry:
            continue
        metadata, full_path = entry.split(b"\t", 1)
        mode, _, stage = metadata.split()
        if mode not in (b"100644", b"100755") or stage != b"0":
            continue
        name, _, relative = full_path.decode("utf-8").partition("/")
        if name in names and _admissible(relative):
            data = _bytes(root, name, relative)
            data.decode("utf-8")
            skills.setdefault(name, {})[relative] = sha256(data).hexdigest()
    return {"schema": 1, "skills": skills}


class SkillAssets:
    def __init__(self, root: Path, catalog: SkillCatalog):
        self._catalog = catalog
        self._root = Path(root).resolve()
        manifest = json.loads(MANIFEST.read_bytes())
        if manifest["schema"] != 1 or not isinstance(manifest["skills"], dict):
            raise CatalogError("unsupported skill support inventory")
        self._skills = manifest["skills"]

    def list_files(self, name: str) -> list[dict]:
        self._catalog.read(name)
        return [{"name": name, "path": path, "sha256": digest,
                 "uri": f"skill-lib://support/{name}/{digest}"}
                for path, digest in sorted(self._skills.get(name, {}).items())]

    def read_file(self, name: str, path: str) -> dict:
        rows = self.list_files(name)
        row = next((item for item in rows if item["path"] == path), None)
        if row is None:
            raise CatalogError("unknown skill support file")
        data = _bytes(self._root, name, row["path"])
        if sha256(data).hexdigest() != row["sha256"]:
            raise CatalogError("skill support revision differs from packaged inventory")
        return {**row, "text": data.decode("utf-8")}

    def read_digest(self, name: str, sha256: str) -> str:
        rows = self.list_files(name)
        if not isinstance(sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", sha256):
            raise CatalogError("invalid skill support digest")
        for row in rows:
            if row["sha256"] == sha256:
                return self.read_file(name, row["path"])["text"]
        raise CatalogError("unknown skill support revision")
# ratios: loc_comments=75:3 imports_exports=6:2 calls_definitions=39:8

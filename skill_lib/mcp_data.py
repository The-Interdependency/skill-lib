# ratios: loc_comments=22:3 imports_exports=2:1 calls_definitions=13:1
"""Locate the catalog owned by this checkout or the installed MCP distribution."""

from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path


_PROJECT = "interdependency-skill-lib-mcp"
_INDEX = Path("share", _PROJECT, "skills.json")
_SOURCE_MARKERS = ("skills.json", "pyproject.toml", "setup.py", "msdmd/SKILL.md")


def catalog_root() -> Path:
    """Find the canonical source or installed catalog independently of the working directory."""
    source = Path(__file__).resolve().parent.parent
    if all((source / marker).is_file() for marker in _SOURCE_MARKERS):
        return source
    try:
        installed = distribution(_PROJECT)
    except PackageNotFoundError as exc:
        raise FileNotFoundError("cannot locate the installed skill-lib catalog") from exc
    # pip --target moves wheel data beside the dist-info directory.
    target_index = Path(installed.locate_file(_INDEX))
    if target_index.is_file():
        return target_index.resolve().parent
    for entry in installed.files or ():
        if entry.parts[-len(_INDEX.parts):] == _INDEX.parts:
            index = Path(entry.locate())
            if index.is_file():
                return index.resolve().parent
    raise FileNotFoundError("the installed skill-lib distribution is missing its catalog data")
# ratios: loc_comments=22:3 imports_exports=2:1 calls_definitions=13:1

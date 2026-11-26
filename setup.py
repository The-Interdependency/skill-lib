# ratios: loc_comments=32:2 imports_exports=5:1 calls_definitions=21:1
"""Build the wheel and source archive from the catalog's canonical source files."""

from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path

from setuptools import setup


DATA_DIR = Path("share/interdependency-skill-lib-mcp")
ROOT = Path(__file__).resolve().parent


def catalog_files():
    """Install the indexed definitions and pinned supporting files together."""
    index = json.loads((ROOT / "skills.json").read_bytes())
    assets = json.loads((ROOT / "skill_lib/mcp_assets.json").read_bytes())
    files = defaultdict(list)
    files[str(DATA_DIR)].append("skills.json")
    indexed = {skill["name"] for skill in index["skills"]}
    if assets["schema"] != 1 or not assets["skills"].keys() <= indexed:
        raise ValueError("unsupported or unowned skill support manifest")
    for skill in index["skills"]:
        name = skill["name"]
        definition = f"{name}/SKILL.md"
        if Path(name).name != name or name in {".", ".."} or skill["path"] != definition:
            raise ValueError(f"invalid catalog source: {name}")
        members = {"SKILL.md": None, **assets["skills"].get(name, {})}
        for rel, digest in members.items():
            path = ROOT / name / rel
            if (Path(rel).is_absolute() or ".." in Path(rel).parts or path.resolve() != path
                    or not path.is_file()):
                raise ValueError(f"invalid source for {name}: {rel}")
            if digest is not None and sha256(path.read_bytes()).hexdigest() != digest:
                raise ValueError(f"skill support digest mismatch: {name}/{rel}")
            source = path.relative_to(ROOT)
            files[str(DATA_DIR / source.parent)].append(str(source))
    return sorted(files.items())


setup(data_files=catalog_files())
# ratios: loc_comments=32:2 imports_exports=5:1 calls_definitions=21:1

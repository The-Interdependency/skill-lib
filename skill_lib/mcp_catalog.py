# ratios: loc_comments=145:11 imports_exports=7:2 calls_definitions=78:13
"""A process-local snapshot of skill-lib's catalog, exact instructions and load rules."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re


class CatalogError(ValueError):
    """A skill or its required inputs could not be admitted."""


_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
_SHA = re.compile(r"[0-9a-f]{64}")


def _name(value: object) -> str:
    if not isinstance(value, str) or not _NAME.fullmatch(value):
        raise CatalogError("invalid skill name")
    return value


def _unique(items):
    result = {}
    for key, value in items:
        if key in result:
            raise CatalogError(f"duplicate catalog field: {key}")
        result[key] = value
    return result


def _source(root: Path, relative: str) -> bytes:
    path = root / relative
    if path.resolve() != path or not path.is_file():
        raise CatalogError(f"expected a regular catalog file: {relative}")
    return path.read_bytes()


@dataclass(frozen=True)
class _Skill:
    name: str
    description: str
    sha256: str
    instructions: str
    edges: tuple[tuple[str, str], ...]

    def summary(self):
        return {"name": self.name, "description": self.description, "sha256": self.sha256}


def _skill(root, row):
    if not isinstance(row, dict):
        raise CatalogError("invalid skill entry")
    name = _name(row.get("name"))
    path = f"{name}/SKILL.md"
    if row.get("path") != path:
        raise CatalogError(f"unexpected instruction path for {name}")
    description = row.get("description")
    if not isinstance(description, str) or not description.strip():
        raise CatalogError(f"missing description for {name}")
    edges = []
    for kind in ("depends_on", "load_with"):
        values = row.get(kind, [])
        if not isinstance(values, list):
            raise CatalogError(f"{kind} must be an array of skill names")
        names = [_name(value) for value in values]
        if name in names or len(set(names)) != len(names):
            raise CatalogError(f"self or duplicate relation in {name}.{kind}")
        edges.extend((kind, target) for target in names)
    data = _source(root, path)
    try:
        instructions = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CatalogError(f"invalid UTF-8 instructions for {name}") from exc
    return _Skill(name, description, sha256(data).hexdigest(), instructions, tuple(edges))


def _order(skills, selected):
    """Schedule prerequisites first; directed co-loads share the resulting bundle."""
    remaining = set(selected)
    ordered = []
    while remaining:
        ready = sorted(n for n in remaining if all(
            target not in remaining for kind, target in skills[n].edges if kind == "depends_on"))
        if not ready:
            raise CatalogError("hard prerequisite cycle in skill catalog")
        # A soft cycle can share an activation. Prefer fully satisfied nodes
        # when there is a choice between equally valid prerequisite orders.
        node = next((n for n in ready if all(t not in remaining for _, t in skills[n].edges)), ready[0])
        ordered.append(node)
        remaining.remove(node)
    return ordered


class SkillCatalog:
    """Load once so every response serves hashes and text from the same snapshot."""

    def __init__(self, root: Path, *, allowed: Iterable[str] | None = None):
        root = Path(root).resolve()
        raw = _source(root, "skills.json")
        index = json.loads(raw, object_pairs_hook=_unique)
        if (not isinstance(index, dict) or type(index.get("version")) is not int
                or index["version"] != 1 or index.get("repo") != "The-Interdependency/skill-lib"
                or not isinstance(index.get("skills"), list)):
            raise CatalogError("unsupported skill-lib catalog")
        superseded = index.get("superseded_skills", [])
        if not isinstance(superseded, list) or any(not isinstance(row, dict) for row in superseded):
            raise CatalogError("invalid superseded skill declarations")
        retired = {_name(row.get("name")) for row in superseded}
        self._skills = {}
        for row in index["skills"]:
            skill = _skill(root, row)
            if skill.name in self._skills or skill.name in retired:
                raise CatalogError(f"ambiguous or retired skill: {skill.name}")
            self._skills[skill.name] = skill
        for skill in self._skills.values():
            for kind, target in skill.edges:
                if target not in self._skills:
                    raise CatalogError(f"unresolved {kind} declaration in {skill.name}")
        _order(self._skills, self._skills)
        if isinstance(allowed, (str, bytes)):
            raise CatalogError("allowed must be a collection of skill names")
        self._allowed = frozenset(self._skills if allowed is None else (_name(n) for n in allowed))
        if not self._allowed <= self._skills.keys():
            raise CatalogError("invalid visible skill set")
        # Bind the index bytes and named exact body digests using unambiguous JSON.
        identity = {"index_sha256": sha256(raw).hexdigest(),
                    "skills": {n: s.sha256 for n, s in self._skills.items()}}
        self.catalog_sha256 = sha256(json.dumps(identity, sort_keys=True,
                                               separators=(",", ":")).encode()).hexdigest()

    def discover(self) -> list[dict]:
        return [self._skills[name].summary() for name in sorted(self._allowed)]

    def read(self, name: str) -> dict:
        if _name(name) not in self._allowed:
            raise CatalogError("skill unavailable in this catalog scope")
        skill = self._skills[name]
        return {**skill.summary(), "instructions": skill.instructions}

    def activate(self, roots: Sequence[str], retained: Mapping[str, str] | None = None) -> dict:
        """Return each active skill once, with all directed inclusion reasons.

        The caller may acknowledge exact body revisions present in its current
        model context. Missing or superseded revision digests receive full text.
        """
        if not isinstance(roots, Sequence) or isinstance(roots, (str, bytes)) or not roots:
            raise CatalogError("activation requires a nonempty list of skill names")
        requested = sorted({_name(n) for n in roots})
        if not self._allowed.issuperset(requested):
            raise CatalogError("skill unavailable in this catalog scope")
        if retained is None:
            retained = {}
        if not isinstance(retained, Mapping) or not all(
                _name(n) and isinstance(h, str) and _SHA.fullmatch(h) for n, h in retained.items()):
            raise CatalogError("retained revisions must map skill names to SHA-256 digests")
        reasons = {n: [{"kind": "requested", "source": n}] for n in requested}
        queue = list(requested)
        while queue:
            owner = queue.pop()
            for kind, target in self._skills[owner].edges:
                if target not in self._allowed:
                    raise CatalogError("a required skill is unavailable in this catalog scope")
                if target not in reasons:
                    reasons[target] = []
                    queue.append(target)
                reasons[target].append({"kind": kind, "source": owner})
        rows = []
        for n in _order(self._skills, reasons):
            skill = self._skills[n]
            row = {"name": n, "sha256": skill.sha256,
                   "reasons": sorted(reasons[n], key=lambda r: (r["source"], r["kind"]))}
            if retained.get(n) == skill.sha256:
                row["instructions_retained"] = True
            else:
                row["instructions"] = skill.instructions
            rows.append(row)
        return {"catalog_sha256": self.catalog_sha256, "roots": requested, "skills": rows}
# ratios: loc_comments=145:11 imports_exports=7:2 calls_definitions=78:13

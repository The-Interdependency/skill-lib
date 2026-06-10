from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_JSON = ROOT / "skills.json"
ALLOWED_KINDS = {"metadata-block", "procedural"}


def frontmatter_for(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    _, frontmatter, _ = text.split("---\n", 2)
    data: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


class SkillIndexSemanticsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.index = json.loads(SKILLS_JSON.read_text(encoding="utf-8"))
        self.skills = self.index["skills"]
        self.names = [skill["name"] for skill in self.skills]

    def test_skill_names_are_unique_and_match_directory_names(self) -> None:
        self.assertEqual(len(self.names), len(set(self.names)))
        for skill in self.skills:
            path = Path(skill["path"])
            self.assertEqual("SKILL.md", path.name)
            self.assertEqual(skill["name"], path.parent.name)

    def test_index_names_match_frontmatter_names(self) -> None:
        for skill in self.skills:
            frontmatter = frontmatter_for(ROOT / skill["path"])
            self.assertEqual(skill["name"], frontmatter["name"], skill["path"])

    def test_index_and_frontmatter_descriptions_are_present(self) -> None:
        for skill in self.skills:
            frontmatter = frontmatter_for(ROOT / skill["path"])
            self.assertTrue(skill["description"].strip(), skill["name"])
            self.assertTrue(frontmatter["description"].strip(), skill["name"])
            self.assertGreaterEqual(len(skill["description"].split()), 8, skill["name"])
            self.assertGreaterEqual(len(frontmatter["description"].split()), 8, skill["name"])

    def test_kind_is_known_and_dependencies_match_kind(self) -> None:
        names = set(self.names)
        for skill in self.skills:
            self.assertIn(skill["kind"], ALLOWED_KINDS, skill["name"])
            depends_on = skill.get("depends_on", [])
            self.assertIsInstance(depends_on, list, skill["name"])
            for dependency in depends_on:
                self.assertIn(dependency, names, f"{skill['name']} depends on missing {dependency}")

            if skill["kind"] == "metadata-block" and skill["name"] != "msdmd":
                self.assertIn("msdmd", depends_on, skill["name"])
            if skill["kind"] == "procedural":
                self.assertNotIn("depends_on", skill, skill["name"])

    def test_foundational_and_procedural_skill_positions_are_stable(self) -> None:
        self.assertEqual("msdmd", self.skills[0]["name"])
        self.assertIn("canon", self.names)
        self.assertIn("visitor-intro", self.names)
        self.assertIn("char-compress", self.names)
        self.assertIn("manifest", self.names)
        self.assertGreater(self.names.index("canon"), self.names.index("ratios"))

    def test_repo_metadata_is_canonical(self) -> None:
        self.assertEqual(1, self.index["version"])
        self.assertEqual("The-Interdependency/skill-lib", self.index["repo"])
        self.assertEqual(".agents/skills/<skill-name>/", self.index["install_path"])


if __name__ == "__main__":
    unittest.main()

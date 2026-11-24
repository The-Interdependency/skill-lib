from __future__ import annotations

import json
import unittest
from pathlib import Path

from frontmatter import frontmatter_for


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "project-incubation-graduation" / "SKILL.md"
INDEX = ROOT / "skills.json"
ADAPTER = ROOT / "skills" / "project-incubation-graduation" / "SKILL.md"


class ProjectIncubationGraduationSkillTest(unittest.TestCase):
    def setUp(self) -> None:
        self.text = SKILL.read_text(encoding="utf-8")
        self.frontmatter = frontmatter_for(SKILL)
        self.index = json.loads(INDEX.read_text(encoding="utf-8"))
        self.adapter = ADAPTER.read_text(encoding="utf-8")

    def test_registered_as_procedural_and_adapter_loads_canonical_skill(self) -> None:
        record = next(
            skill for skill in self.index["skills"]
            if skill["name"] == "project-incubation-graduation"
        )
        self.assertEqual(record["path"], "project-incubation-graduation/SKILL.md")
        self.assertEqual(record["kind"], "procedural")
        self.assertEqual(record["description"], self.frontmatter["description"])
        self.assertIn("Read and follow `../../project-incubation-graduation/SKILL.md`", self.adapter)

if __name__ == "__main__":
    unittest.main()

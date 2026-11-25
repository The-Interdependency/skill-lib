from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "website-builder-journal" / "SKILL.md"
INDEX = ROOT / "skills.json"


class WebsiteBuilderJournalSkillTest(unittest.TestCase):
    def setUp(self) -> None:
        self.text = SKILL.read_text(encoding="utf-8")
        self.index = json.loads(INDEX.read_text(encoding="utf-8"))

    def test_registered_as_procedural_with_exact_trigger(self) -> None:
        record = next(skill for skill in self.index["skills"] if skill["name"] == "website-builder-journal")
        self.assertEqual(record["path"], "website-builder-journal/SKILL.md")
        self.assertEqual(record["kind"], "procedural")
        self.assertIn("Load this when any modification to The-Interdependency/The-Interdependency.github.io is planned or underway", record["description"])
        self.assertIn("Do not load for read-only inspection", record["description"])

if __name__ == "__main__":
    unittest.main()

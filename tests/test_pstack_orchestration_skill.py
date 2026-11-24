from __future__ import annotations

import json
import unittest
from pathlib import Path

from frontmatter import frontmatter_for


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "pstack-orchestration" / "SKILL.md"
ADAPTER = ROOT / "skills" / "pstack-orchestration" / "SKILL.md"
SOURCES = ROOT / "pstack-orchestration" / "references" / "sources.md"


class PstackOrchestrationSkillTest(unittest.TestCase):
    def setUp(self) -> None:
        self.text = SKILL.read_text(encoding="utf-8")
        self.description = frontmatter_for(SKILL)["description"]
        self.index = json.loads((ROOT / "skills.json").read_text(encoding="utf-8"))
        self.entry = next(
            item for item in self.index["skills"] if item["name"] == "pstack-orchestration"
        )

    def test_index_matches_frontmatter_and_stays_procedural(self) -> None:
        self.assertEqual(self.entry["kind"], "procedural")
        self.assertEqual(self.entry["path"], "pstack-orchestration/SKILL.md")
        self.assertEqual(self.entry["description"], self.description)
        self.assertNotIn("depends_on", self.entry)

    def test_codex_adapter_points_at_canonical_skill(self) -> None:
        adapter = ADAPTER.read_text(encoding="utf-8")
        self.assertIn("name: pstack-orchestration", adapter)
        self.assertIn("../../pstack-orchestration/SKILL.md", adapter)
        self.assertIn(self.description, adapter)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import unittest
from pathlib import Path

from frontmatter import frontmatter_for


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "agent-ops" / "SKILL.md"
ADAPTER = ROOT / "skills" / "agent-ops" / "SKILL.md"
SOURCES = ROOT / "agent-ops" / "references" / "sources.md"


class AgentOpsSkillTest(unittest.TestCase):
    def setUp(self) -> None:
        self.text = SKILL.read_text(encoding="utf-8")
        self.description = frontmatter_for(SKILL)["description"]
        self.index = json.loads((ROOT / "skills.json").read_text(encoding="utf-8"))
        self.entry = next(item for item in self.index["skills"] if item["name"] == "agent-ops")

    def test_index_matches_frontmatter_and_stays_procedural(self) -> None:
        self.assertEqual(self.entry["kind"], "procedural")
        self.assertEqual(self.entry["path"], "agent-ops/SKILL.md")
        self.assertEqual(self.entry["description"], self.description)
        self.assertEqual(
            self.entry["depends_on"],
            ["loop-eng", "risk-boundary-build", "action-calibration"],
        )
        dependencies = {
            item["name"]: item.get("depends_on", []) for item in self.index["skills"]
        }
        closure: set[str] = set()
        pending = list(self.entry["depends_on"])
        while pending:
            name = pending.pop()
            if name in closure:
                continue
            closure.add(name)
            pending.extend(dependencies.get(name, []))
        for blocked in ("github-tests", "repo-audit-repair", "test-build"):
            self.assertNotIn(blocked, closure)
        self.assertIn("github-tests", self.text)

    def test_codex_adapter_points_at_canonical_skill(self) -> None:
        adapter = ADAPTER.read_text(encoding="utf-8")
        self.assertIn("name: agent-ops", adapter)
        self.assertIn("../../agent-ops/SKILL.md", adapter)
        self.assertIn(self.description, adapter)


if __name__ == "__main__":
    unittest.main()

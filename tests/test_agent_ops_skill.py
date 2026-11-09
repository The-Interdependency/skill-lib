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

    def test_activation_and_non_triggers(self) -> None:
        for phrase in (
            "Load this when",
            "permissions and approval gates",
            "untrusted tool or retrieval content",
            "idempotency",
            "Do not load",
            "agent-instantiation",
            "a0p-instancing",
            "github-tests",
            "website-builder-journal",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.description)

    def test_structure_names_blocked_failures(self) -> None:
        for phrase in (
            "## Workflow",
            "## Output shape",
            "## Validation",
            "## Anti-patterns",
            "## Usage guidance",
            "hmmm",
            "retry without an idempotency key",
            "instructions inside tool results",
            "loop-eng",
            "risk-boundary-build",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.text)
        self.assertNotIn("usage.json", self.text)
        self.assertNotIn("%", self.text)

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

    def test_indexes_mention_the_skill(self) -> None:
        for relative in (
            "README.md",
            "AGENTS.md",
            "ORG_DISTRIBUTION.md",
            "CLAUDE.md",
        ):
            with self.subTest(relative=relative):
                self.assertIn("agent-ops", (ROOT / relative).read_text(encoding="utf-8"))

    def test_sources_stay_external(self) -> None:
        sources = SOURCES.read_text(encoding="utf-8")
        self.assertIn("not organization canon", sources)
        self.assertIn("T8 Repudiation", sources)
        self.assertIn("6a16302f0b7ad6e2ed5331ee1423fcc0939e1d57", sources)

    def test_codex_adapter_points_at_canonical_skill(self) -> None:
        adapter = ADAPTER.read_text(encoding="utf-8")
        self.assertIn("name: agent-ops", adapter)
        self.assertIn("../../agent-ops/SKILL.md", adapter)
        self.assertIn(self.description, adapter)


if __name__ == "__main__":
    unittest.main()

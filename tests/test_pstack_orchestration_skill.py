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

    def test_activation_and_non_triggers(self) -> None:
        for phrase in (
            "Load this when",
            "GitHub repo",
            "task contract",
            "PASS/FAIL/NOT_RUN",
            "autonomy gates",
            "Do not load",
            "agent-ops",
            "github-tests",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.description)

    def test_structure_names_blocked_failures(self) -> None:
        for phrase in (
            "## Workflow",
            "### 1. task.contract",
            "### 2. skill.dispatch",
            "### 3. verifier.resolve",
            "### 4. baseline.capture",
            "### 6. proof.match",
            "### 7. evidence.record",
            "### 8. repair.loop",
            "### 9. Recurrence control",
            "### 10. review.output",
            "### 11. autonomy.gate",
            "## Output shape",
            "## Validation",
            "## Anti-patterns",
            "## Usage guidance",
            "hmmm",
            "Demonstrated-need",
            "An agent's say-so is never approval",
            "verified head SHA",
            "owner's explicit go-ahead",
            "agent-ops",
            "github-tests",
            "Patching before reproducing",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.text)
        self.assertNotIn("usage.json", self.text)

    def test_index_matches_frontmatter_and_stays_procedural(self) -> None:
        self.assertEqual(self.entry["kind"], "procedural")
        self.assertEqual(self.entry["path"], "pstack-orchestration/SKILL.md")
        self.assertEqual(self.entry["description"], self.description)
        self.assertNotIn("depends_on", self.entry)

    def test_indexes_mention_the_skill(self) -> None:
        for relative in (
            "README.md",
            "AGENTS.md",
            "ORG_DISTRIBUTION.md",
            "CLAUDE.md",
        ):
            with self.subTest(relative=relative):
                self.assertIn("pstack-orchestration", (ROOT / relative).read_text(encoding="utf-8"))

    def test_sources_credit_pstack_and_remain_external(self) -> None:
        sources = SOURCES.read_text(encoding="utf-8")
        self.assertIn("not organization canon", sources)
        self.assertIn("https://github.com/cursor/plugins/tree/main/pstack", sources)
        self.assertIn("MIT, Copyright (c) 2026 Lauren Tan", sources)
        self.assertIn("https://github.com/ThewindMom/grok-pstack", sources)
        self.assertIn("https://x.com/0xChonsy/status/2121730042099306942", sources)
        self.assertIn("does not copy substantial pstack skill text", sources)

    def test_codex_adapter_points_at_canonical_skill(self) -> None:
        adapter = ADAPTER.read_text(encoding="utf-8")
        self.assertIn("name: pstack-orchestration", adapter)
        self.assertIn("../../pstack-orchestration/SKILL.md", adapter)
        self.assertIn(self.description, adapter)


if __name__ == "__main__":
    unittest.main()

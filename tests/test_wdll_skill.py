from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "wdll" / "SKILL.md"
SKILL_BUILD = ROOT / "skill-build" / "SKILL.md"


class WDLLSkillTest(unittest.TestCase):
    def test_executive_contract_and_ownership(self):
        text = SKILL.read_text(encoding="utf-8")
        for required in (
            "Load this when",
            "## Workflow",
            "spawn or newly scoped",
            "FROM → TO",
            "DONE WHEN",
            "PROVEN BY",
            "FAILS IF",
            "within authority",
            "Read-only/audit tasks remain read-only",
            "msdmd/SKILL.md",
            "## Anti-patterns",
            "CHANGED",
            "PROOF",
            "NEXT",
            "hmmm",
        ):
            with self.subTest(required=required):
                self.assertIn(required, text)

    def test_instantiation_declares_wdll_dependency(self):
        index = json.loads((ROOT / "skills.json").read_text(encoding="utf-8"))
        item = next(s for s in index["skills"] if s["name"] == "agent-instantiation")
        self.assertIn("wdll", item["depends_on"])

    def test_skill_build_owns_narrative_compression(self):
        text = SKILL_BUILD.read_text(encoding="utf-8")
        self.assertIn("Narrative compression invariant", text)
        self.assertIn("each concept one authoritative home", text.lower())
        self.assertIn("Repeat a concept only when the repetition changes execution", text)


if __name__ == "__main__":
    unittest.main()

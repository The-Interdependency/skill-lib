from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "wdll" / "SKILL.md"
SKILL_BUILD = ROOT / "skill-build" / "SKILL.md"


class WDLLSkillTest(unittest.TestCase):
    def test_wdll_has_executive_completion_contract(self):
        text = SKILL.read_text(encoding="utf-8")
        for required in (
            "Select the job",
            "FROM → TO",
            "DONE WHEN:",
            "PROVEN BY:",
            "FAILS IF:",
            "MSDMD compliance",
            "Verify final reality",
            "CHANGED",
            "PROOF",
            "NEXT",
            "hmmm",
        ):
            self.assertIn(required, text)

    def test_skill_build_owns_narrative_compression(self):
        text = SKILL_BUILD.read_text(encoding="utf-8")
        self.assertIn("Narrative compression invariant", text)
        self.assertIn("each concept one authoritative home", text.lower())
        self.assertIn("Repeat a concept only when the repetition changes execution", text)


if __name__ == "__main__":
    unittest.main()

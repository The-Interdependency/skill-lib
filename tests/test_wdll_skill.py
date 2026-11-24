from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "wdll" / "SKILL.md"
SKILL_BUILD = ROOT / "skill-build" / "SKILL.md"


class WDLLSkillTest(unittest.TestCase):
    def test_instantiation_declares_wdll_dependency(self):
        index = json.loads((ROOT / "skills.json").read_text(encoding="utf-8"))
        item = next(s for s in index["skills"] if s["name"] == "agent-instantiation")
        self.assertIn("wdll", item["depends_on"])

if __name__ == "__main__":
    unittest.main()

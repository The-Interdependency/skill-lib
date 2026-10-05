"""Regression checks for the interdependent work-graph reference boundary."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "interdependent-work-graph" / "SKILL.md"


class InterdependentWorkGraphContractTests(unittest.TestCase):
    def test_hmmm_boundary_is_visible_even_when_no_material_unknown_remains(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        reference = text.split("The first executable reference shape is:", 1)[1].split("The digest is SHA-256", 1)[0]
        self.assertNotIn('"hmmm": []', reference)
        self.assertIn("non-empty list of non-empty strings", text)
        self.assertIn("considered and currently empty", text)
        self.assertIn("No unresolved boundary in this graph;", text)


if __name__ == "__main__":
    unittest.main()

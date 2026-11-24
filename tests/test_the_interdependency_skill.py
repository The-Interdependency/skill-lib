"""Regression guards for the canonical ``the-interdependency`` workflow skill.

Usage guidance:
    Focused: ``python -m unittest tests.test_the_interdependency_skill``
    Full repo: ``python -m unittest discover -s tests``

The focused test protects the scoped operator-workflow contract, the exact
cross-repository authority identities for the vm-mcp/stack topology, and the
rule that runtime host facts such as ``a0`` cannot become unconditional
organization authority. It also guards against reintroducing a mutating
one-shot write-back workflow into the skill.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "the-interdependency" / "SKILL.md"


class TheInterdependencySkillTest(unittest.TestCase):
    def setUp(self) -> None:
        self.text = SKILL.read_text(encoding="utf-8")
        self.compact = " ".join(self.text.split())

    def test_runtime_topology_does_not_become_org_authority(self) -> None:
        patterns = (
            r"a0.{0,100}\b(?:primary|authoritative|default|required)\b.{0,100}\b(?:development|workspace|host|routing)\b",
            r"\b(?:primary|authoritative|default|required)\b.{0,100}\b(?:development|workspace|host|routing)\b.{0,100}a0",
        )
        lowered = self.text.lower()
        for pattern in patterns:
            self.assertIsNone(re.search(pattern, lowered, flags=re.DOTALL), pattern)
        self.assertIn(
            'A statement like "use `a0`" is therefore a runtime/operator decision backed by current deployment evidence',
            self.text,
        )

if __name__ == "__main__":
    unittest.main()

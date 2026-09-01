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

    def test_operator_contract_preserves_load_bearing_rules(self) -> None:
        for phrase in (
            "Audit before assent",
            "Preserve concepts; reject bad placement",
            "Useful, good, true",
            "KISS under reality contact",
            "Prior planning before execution",
            "Complete within granted scope",
            "Usage-limit aware orchestration",
            "Purposeful functions",
            "Deprecation is removal plus replacement when capability remains required",
            "`hmmm` is mandatory honest incompletion",
        ):
            self.assertIn(phrase, self.text)

    def test_authority_topology_carries_exact_cross_repository_identities(self) -> None:
        topology = self.text.split("## Operational authority topology", 1)[1].split(
            "## METAPAT consultation test", 1
        )[0]
        for phrase in (
            "durable ownership boundaries",
            "skill-lib/vm-mcp",
            "The-Interdependency/stack",
            "Concrete host/client facts are runtime evidence",
            "Provider execution capacity is not source authority",
            "Deprecated/stale routes do not revive themselves",
            "must not elevate those transient facts into unconditional organization-wide routing doctrine",
        ):
            self.assertIn(phrase, topology)
        self.assertIn("222ba4d4348022d81950c3fad054bae7e528b6a0", topology)
        self.assertIn("22b74340d0c603883193a4ecf53e2ef3f9c3e780", topology)

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

    def test_no_mutating_one_shot_write_back_workflow_is_declared(self) -> None:
        for forbidden in (
            "interdependency-operator-repair-once",
            "one-shot write-back",
            "write-back workflow",
        ):
            self.assertNotIn(forbidden, self.text)

    def test_deprecation_replacement_is_conditional_on_needed_capability(self) -> None:
        self.assertIn(
            "provide or identify its supported replacement when the retired capability remains required",
            self.compact,
        )
        self.assertIn(
            "If the capability is intentionally retired as unnecessary, complete removal is the replacement outcome",
            self.compact,
        )


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

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
            "Complete within granted scope",
            "Usage-limit aware orchestration",
            "Deprecation is removal plus replacement",
            "`hmmm` is mandatory honest incompletion",
        ):
            self.assertIn(phrase, self.text)

    def test_runtime_topology_does_not_become_org_authority(self) -> None:
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

    def test_a0_is_explicitly_runtime_not_standing_canon(self) -> None:
        self.assertIn(
            'A statement like "use `a0`" is therefore a runtime/operator decision backed by current deployment evidence',
            self.text,
        )
        self.assertNotIn("Google Cloud `a0` VM — primary persistent development surface", self.text)


if __name__ == "__main__":
    unittest.main()

"""Regression guards for the canonical ``the-interdependency`` workflow skill.

Usage guidance:
    Focused: ``python -m unittest tests.test_the_interdependency_skill``
    Full repo: ``python -m unittest discover -s tests``

The focused test protects operator-domain semantics, the vm-mcp/stack work-graph
identity, and the rule that runtime host facts such as ``a0`` cannot become
unconditional organization authority.
"""

from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "the-interdependency" / "SKILL.md"
DOMAIN_CLAIMS = ROOT / "the-interdependency" / "operator-domain-claims.json"
WORK_GRAPH = ROOT / "docs" / "work-graphs" / "vm-mcp-stack-topology.json"


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

    def test_operator_terms_have_scoped_domain_claims(self) -> None:
        payload = json.loads(DOMAIN_CLAIMS.read_text(encoding="utf-8"))
        records = {record["surface_form"]: record for record in payload["records"]}
        for surface in (
            "Audit before assent",
            "Preserve concepts; reject bad placement",
            "Useful, good, true",
            "KISS under reality contact",
            "Prior planning before execution",
            "Complete within granted scope",
            "Usage-limit aware orchestration",
            "Purposeful functions",
            "Deprecation is removal plus replacement when capability remains required",
            "hmmm",
        ):
            record = records[surface]
            self.assertTrue(record["term_id"].startswith("the-interdependency.operator."))
            self.assertEqual(record["claiming_domain"], "The Interdependency operator workflow")
            self.assertEqual(record["status"], "ratified")
            self.assertTrue(record["scope"])
            self.assertTrue(record["excluded_uses"])
        self.assertIn("operator-domain-claims.json", self.text)

    def test_vm_mcp_stack_work_graph_is_exact_and_recomputes(self) -> None:
        payload = json.loads(WORK_GRAPH.read_text(encoding="utf-8"))
        canonical = json.dumps(
            {
                "repositories": payload["repositories"],
                "boundaries": payload["boundaries"],
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        self.assertEqual(
            hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
            payload["work_graph_sha256"],
        )
        self.assertEqual(
            [entry["commit"] for entry in payload["repositories"]],
            [
                "222ba4d4348022d81950c3fad054bae7e528b6a0",
                "22b74340d0c603883193a4ecf53e2ef3f9c3e780",
            ],
        )
        self.assertFalse(payload["boundaries"]["authority_transfer"])
        self.assertIn("vm-mcp-stack-topology.json", self.text)

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

    def test_a0_guard_rejects_equivalent_unconditional_authority_claims(self) -> None:
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

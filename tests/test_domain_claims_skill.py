from __future__ import annotations

import unittest
from pathlib import Path

from frontmatter import frontmatter_for


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "domain-claims" / "SKILL.md"


class DomainClaimsSkillTest(unittest.TestCase):
    def setUp(self) -> None:
        self.text = SKILL.read_text(encoding="utf-8")
        self.frontmatter = frontmatter_for(SKILL)

    def test_domain_claim_precedes_definition_and_provenance(self) -> None:
        doctrine = self.text.index("## Zeroth-provenance doctrine")
        domain = self.text.index("domain claim", doctrine)
        definition = self.text.index("domain-bound definition", domain)
        provenance = self.text.index("conversational/source provenance", definition)
        ratification = self.text.index("ratification status", provenance)
        encoding = self.text.index("downstream encoding or implementation", ratification)
        self.assertLess(domain, definition)
        self.assertLess(definition, provenance)
        self.assertLess(provenance, ratification)
        self.assertLess(ratification, encoding)

if __name__ == "__main__":
    unittest.main()

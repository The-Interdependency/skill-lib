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

    def test_activation_and_non_trigger_are_explicit(self) -> None:
        description = self.frontmatter["description"]
        self.assertIn("Load this when", description)
        self.assertIn("theorem term", description)
        self.assertIn("ontology primitive", description)
        self.assertIn("Do not load", description)
        self.assertIn("ordinary prose", description)

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

    def test_claim_record_and_fail_closed_collision_are_pinned(self) -> None:
        for required in (
            "surface_form:",
            "term_id:",
            "claiming_domain:",
            "claimed_sense:",
            "scope:",
            "claim_type:",
            "authority_source:",
            "included_uses:",
            "excluded_uses:",
            "known_collisions:",
            "unresolved:",
            "DOMAIN_COLLISION",
            "resolution required before canonization or encoding",
        ):
            with self.subTest(required=required):
                self.assertIn(required, self.text)

    def test_skill_refuses_global_word_ownership_and_registry_overreach(self) -> None:
        self.assertIn("does not own a word everywhere", self.text)
        self.assertIn("ordinary language remains fluid", self.text)
        self.assertIn("Creating domain claims for every ordinary word", self.text)

    def test_domain_claims_runs_before_canon(self) -> None:
        self.assertIn("Before `canon`", self.text)
        self.assertIn("`domain-claims` establishes", self.text)
        self.assertIn("`canon` then determines", self.text)

    def test_hmmm_boundary_remains_visible(self) -> None:
        self.assertIn("hmmm", self.text)
        self.assertIn("multilingual surface forms", self.text)
        self.assertIn("delegated, revoked, or shared", self.text)


if __name__ == "__main__":
    unittest.main()

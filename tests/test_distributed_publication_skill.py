from __future__ import annotations

import json
import unittest
from pathlib import Path

from frontmatter import frontmatter_for


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "distributed-publication" / "SKILL.md"
INDEX = ROOT / "skills.json"


class DistributedPublicationSkillTest(unittest.TestCase):
    def setUp(self) -> None:
        self.text = SKILL.read_text(encoding="utf-8")
        self.frontmatter = frontmatter_for(SKILL)
        self.index = json.loads(INDEX.read_text(encoding="utf-8"))

    def test_activation_and_non_trigger_are_explicit(self) -> None:
        description = self.frontmatter["description"]
        self.assertIn("Load this when", description)
        self.assertIn("ordered textbook", description)
        self.assertIn("multiple repositories", description)
        self.assertIn("Load interdependent-work-graph", description)
        self.assertIn("Do not load", description)
        self.assertIn("single-repository documentation", description)

    def test_skill_is_registered_as_procedural_and_composed_by_doctrine(self) -> None:
        record = next(skill for skill in self.index["skills"] if skill["name"] == "distributed-publication")
        self.assertEqual(record["path"], "distributed-publication/SKILL.md")
        self.assertEqual(record["kind"], "procedural")
        self.assertNotIn("depends_on", record)
        self.assertIn("Load `interdependent-work-graph/SKILL.md` first or alongside this skill", self.text)

    def test_authority_and_status_do_not_transfer(self) -> None:
        for required in (
            "one reading surface != one source authority",
            "publication order != ownership transfer",
            "authorship_transfer",
            "ownership_transfer",
            "license_transfer",
            "canonical_status_transfer",
            "proof_status_transfer",
            "certification_status_transfer",
            "measurement_status_transfer",
            "empirical_status_transfer",
            "digest_is_authentication",
        ):
            with self.subTest(required=required):
                self.assertIn(required, self.text)

    def test_reference_contract_binds_order_and_exact_source_identity(self) -> None:
        for required in (
            '"schema": "the-interdependency.distributed-publication"',
            '"order_is_load_bearing": true',
            '"position": 0',
            '"source_id"',
            '"repository"',
            '"path"',
            '"commit"',
            '"blob"',
            '"content_sha256"',
            '"correction_target"',
            '"publication_sha256"',
            "Array order is preserved and therefore part of identity",
        ):
            with self.subTest(required=required):
                self.assertIn(required, self.text)

    def test_production_fails_closed_and_degraded_mode_stays_visible(self) -> None:
        self.assertIn("Required current sources fail closed in production", self.text)
        self.assertIn("retained snapshot", self.text)
        self.assertIn("no retained copy is called current", self.text)
        self.assertIn("missing content becomes `hmmm`, not invented prose", self.text)
        self.assertIn("Allowing fallback content in a production build", self.text)

    def test_corrections_route_to_source_owners(self) -> None:
        self.assertIn("Route corrections to the source owner", self.text)
        self.assertIn("Patch source content only in its owning repository", self.text)
        self.assertIn("Fixing source prose in the publication consumer", self.text)

    def test_static_accessible_publication_surface_is_required(self) -> None:
        self.assertIn("static/no-JavaScript reading path", self.text)
        self.assertIn("automated accessibility checks pass", self.text)
        self.assertIn("manual review remains acknowledged", self.text)
        self.assertIn("public build artifact exposes every source identity", self.text)

    def test_reference_implementation_and_hmmm_remain_visible(self) -> None:
        for chapter in range(8):
            self.assertIn(f"Chapter {chapter}", self.text)
        self.assertIn("website    publication consumer", self.text)
        self.assertIn("## hmmm", self.text)
        self.assertIn("cryptographic authorship", self.text)
        self.assertIn("Mathematical notation accessibility", self.text)


if __name__ == "__main__":
    unittest.main()

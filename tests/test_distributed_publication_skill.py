from __future__ import annotations

import json
import unittest
from pathlib import Path

from frontmatter import frontmatter_for


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "distributed-publication" / "SKILL.md"
INDEX = ROOT / "skills.json"
FIXTURE = ROOT / "tests" / "fixtures" / "distributed_publication_manifest.json"


class DistributedPublicationSkillTest(unittest.TestCase):
    def setUp(self) -> None:
        self.text = SKILL.read_text(encoding="utf-8")
        self.frontmatter = frontmatter_for(SKILL)
        self.index = json.loads(INDEX.read_text(encoding="utf-8"))
        self.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_skill_is_registered_as_procedural_and_composed_by_doctrine(self) -> None:
        record = next(skill for skill in self.index["skills"] if skill["name"] == "distributed-publication")
        self.assertEqual(record["path"], "distributed-publication/SKILL.md")
        self.assertEqual(record["kind"], "procedural")
        self.assertNotIn("depends_on", record)
        self.assertIn("Load `interdependent-work-graph/SKILL.md` first or alongside this skill", self.text)

    def test_reference_contract_binds_order_identity_and_license(self) -> None:
        for required in (
            '"schema": "the-interdependency.distributed-publication"',
            '"order_is_load_bearing": true',
            '"position": 0',
            '"source_id"',
            '"repository"',
            '"path"',
            '"expected_title"',
            '"commit"',
            '"blob"',
            '"content_sha256"',
            '"license"',
            '"license_status"',
            '"correction_target"',
            '"publication_sha256"',
            "Array order is preserved and therefore part of identity",
            "neither field authorizes the consumer to relicense the source",
        ):
            with self.subTest(required=required):
                self.assertIn(required, self.text)

        for source in self.fixture["sources"]:
            self.assertTrue(source["expected_title"])
            self.assertTrue(source["license"])
            self.assertIn(source["license_status"], {"declared", "unknown", "human-review-required"})

if __name__ == "__main__":
    unittest.main()

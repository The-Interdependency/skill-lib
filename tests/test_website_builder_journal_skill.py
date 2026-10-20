from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "website-builder-journal" / "SKILL.md"
INDEX = ROOT / "skills.json"


class WebsiteBuilderJournalSkillTest(unittest.TestCase):
    def setUp(self) -> None:
        self.text = SKILL.read_text(encoding="utf-8")
        self.index = json.loads(INDEX.read_text(encoding="utf-8"))

    def test_registered_as_procedural_with_exact_trigger(self) -> None:
        record = next(skill for skill in self.index["skills"] if skill["name"] == "website-builder-journal")
        self.assertEqual(record["path"], "website-builder-journal/SKILL.md")
        self.assertEqual(record["kind"], "procedural")
        self.assertIn("Load this when any modification to The-Interdependency/The-Interdependency.github.io is planned or underway", record["description"])
        self.assertIn("Do not load for read-only inspection", record["description"])

    def test_contract_is_append_only_and_model_discretionary(self) -> None:
        for phrase in (
            "append at least one new record",
            "date",
            "time",
            "exact runtime model",
            "complete discretion over the journal entry's subject matter",
            "only as much as is required to properly explicate",
            "does not recursively require a second append",
            "Previously published entries are immutable",
            "collapsible",
            "<details>",
            "<summary>",
            "npm run check:builder -- --base <base-commit>",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.text)

    def test_truthful_unavailable_provenance_is_not_a_work_blocker(self) -> None:
        for phrase in (
            '"model": "unavailable"',
            'model_unavailable_reason',
            'unavailable marker without its reason is invalid',
            'Missing model metadata alone does not block ordinary website work',
            'Do not invent a model name or version',
            'Do not attach `model_unavailable_reason` to an exact identifier',
            'public journal must display the unavailable reason',
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.text)
        self.assertNotIn('website modification remains blocked', self.text)

    def test_requested_alias_and_claim_evidence_remain_distinct(self) -> None:
        self.assertIn('requested/configured model alias is not the actual response model', self.text)
        self.assertIn('optional `requested_model`', self.text)
        self.assertIn('Scientific or model-comparison claims', self.text)
        self.assertIn('retain their evidence requirements', self.text)

    def test_historical_entry_migration_is_fail_closed(self) -> None:
        self.assertIn("do not backfill", self.text.lower())
        self.assertIn("append-only history outranks retroactive schema neatness", self.text)


if __name__ == "__main__":
    unittest.main()

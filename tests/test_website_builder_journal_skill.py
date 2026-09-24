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
        self.assertIn("before any modification to The-Interdependency/The-Interdependency.github.io", record["description"])
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

    def test_historical_entry_migration_is_fail_closed(self) -> None:
        self.assertIn("do not backfill", self.text.lower())
        self.assertIn("append-only history outranks retroactive schema neatness", self.text)


if __name__ == "__main__":
    unittest.main()

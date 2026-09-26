"""Regression checks for native-first contracts and bounded reader disclosure.

Usage: python -m unittest discover -s tests -p 'test_msdmd_native_contract_docs.py'
The complete repository suite and generated-file gates remain separate checks.
"""
from __future__ import annotations

import json
from pathlib import Path
import unittest

from llms import build
from msdmd.collect import collect, render_typescript
from msdmd.parsers.universal import parse_file
from msdmd.visualize import load_collection
from tools.build_codex_plugin_skills import adapter, canonical_frontmatter

ROOT = Path(__file__).resolve().parents[1]
APPLICATIONS = (
    "doc-build", "cap-build", "deps-build", "owner-build", "test-build",
    "meta-module-build", "risk-boundary-build", "llms-build",
)


class NativeContractDocsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.index = json.loads((ROOT / "skills.json").read_text(encoding="utf-8"))
        self.entries = {item["name"]: item for item in self.index["skills"]}

    def test_application_contracts_and_discovery_are_native_first(self) -> None:
        for name in APPLICATIONS:
            with self.subTest(skill=name):
                entry = self.entries[name]
                path = ROOT / entry["path"]
                text = path.read_text(encoding="utf-8")
                metadata = canonical_frontmatter(path)
                self.assertIn("native", metadata["description"].lower())
                self.assertEqual(entry["description"], metadata["description"])
                self.assertIn("## Native-first coverage", text)
                self.assertIn("supplement", text.lower())
                self.assertIn("hmmm", text)
                self.assertEqual(
                    (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8"),
                    adapter(entry),
                )

    def test_retired_block_absence_rules_are_removed(self) -> None:
        retired = {
            "owner-build": (
                "Report modules without OWNERS blocks as visible stewardship gaps.",
                "GAP`: module has no OWNERS block.",
                "Recording owner only in a central CODEOWNERS-like file while omitting",
            ),
            "doc-build": (
                "Report modules with no `DOCS` block as documentation coverage gaps.",
                "GAP`: source modules with no DOCS block.",
            ),
            "cap-build": (
                "Report modules with exposed public surfaces but no CAPABILITIES block",
                "Declaring capabilities in a central registry while omitting",
            ),
            "deps-build": ("Report modules with imports/calls but no DEPENDENCIES block",),
            "meta-module-build": ("report modules without `MODULE_BUILD` as coverage gaps;",),
            "risk-boundary-build": (
                "Report modules with likely sensitive imports or filenames but no BOUNDARIES block",
            ),
            "test-build": (
                "Every module that promises behavior declares those obligations in a `CONTRACTS` block.",
            ),
        }
        for name, phrases in retired.items():
            text = " ".join((ROOT / name / "SKILL.md").read_text(encoding="utf-8").split())
            for phrase in phrases:
                with self.subTest(skill=name, phrase=phrase):
                    self.assertNotIn(phrase, text)

    def test_block_runner_and_partial_python_reader_have_distinct_scopes(self) -> None:
        entry = self.entries["msdmd"]
        self.assertEqual(entry["status"], "runnable")
        self.assertEqual(entry["runner"], "msdmd/collect.py")
        self.assertEqual(entry["runner_scope"], "msdmd-blocks-only")
        self.assertEqual(
            entry["native_ingestion"],
            {
                "status": "partial",
                "runner": "msdmd/module_projection.py",
                "scope": "python-symbol-signature-docstring-comment-projection",
                "schema": "msdmd/module-projection.schema.json",
                "manifest": "msdmd/python-module-reader.json",
            },
        )

    def test_helper_identity_limitations_are_explicit(self) -> None:
        text = (ROOT / "msdmd/SKILL.md").read_text(encoding="utf-8")
        for statement in (
            "does not diagnose duplicate IDs",
            "edge `from` and `source_id`",
            "bare entry IDs",
            "### Shipped helper limitations",
            "emitted without diagnostics",
            "does not repair\nthe collector or visualizer runtime",
        ):
            self.assertIn(statement, text)
        self.assertNotIn("collection addresses additionally\nqualify", text)

    def test_llm_publication_matches_owning_sources(self) -> None:
        source = (ROOT / "llms/metadata.py").read_text(encoding="utf-8")
        entries = build.parse_text(source, source=Path("llms/metadata.py"))
        definitions = next(entry.fields for entry in entries if entry.id == "key_definitions")
        self.assertIn("native-first", definitions["msdmd"])
        self.assertIn("collector remains block-only", definitions["msdmd"])
        self.assertIn("partial Python reader", definitions["msdmd"])
        self.assertNotIn("each source module declares", source)
        generated = build.generate(build.collect(ROOT), self.index["repo"].split("/")[-1])
        self.assertEqual((ROOT / "llms.txt").read_text(encoding="utf-8"), generated)

    def test_native_ingestion_preserves_evidence_and_authority_boundaries(self) -> None:
        evidence = (ROOT / "test-build/SKILL.md").read_text(encoding="utf-8")
        ownership = (ROOT / "owner-build/SKILL.md").read_text(encoding="utf-8")
        for statement in (
            "CONTRACTS are obligations.",
            "CHECKS are accountable witnesses.",
            "Source modules own promises. Test modules own evidence.",
            "Native contract/witness readers",
        ):
            self.assertIn(statement, evidence)
        self.assertIn("CODEOWNERS review assignment does not automatically", ownership)
        self.assertIn("operational-owner obligation", ownership)

    def test_repository_collection_replays_from_owning_blocks(self) -> None:
        path = ROOT / "skill-lib_msdmd.ts"
        generated = render_typescript(
            collect(ROOT, self.index["repo"]), import_path="./msdmd/collection",
        )
        self.assertEqual(path.read_text(encoding="utf-8"), generated)
        collection = load_collection(path)
        for block, entry_id in (
            ("DOCS", "msdmd_foundational_contract"),
            ("CAPABILITIES", "repo_collection_generator"),
        ):
            with self.subTest(block=block):
                source = next(
                    item for item in parse_file(ROOT / "msdmd/collect.py", block)
                    if item["id"] == entry_id
                )
                declaration = next(
                    item for item in collection["declarations"]
                    if (item["file"], item["block"], item["id"])
                    == ("msdmd/collect.py", block, entry_id)
                )
                self.assertEqual(
                    declaration["fields"],
                    {key: value for key, value in source.items() if key != "id"},
                )
        self.assertEqual([], collection["gaps"])


if __name__ == "__main__":
    unittest.main()

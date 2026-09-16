"""Regression checks for native-first contracts and shipped reader discovery.

Usage: python -m unittest discover -s tests -p 'test_msdmd_native_contract_docs.py'
The complete repository suite and generated-file gates remain separate checks.
"""
from __future__ import annotations

import json
from pathlib import Path
import unittest

from llms import build
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

    def test_native_runner_and_exact_reader_subset_are_discoverable(self) -> None:
        entry = self.entries["msdmd"]
        self.assertEqual(entry["status"], "runnable")
        self.assertEqual(entry["runner"], "msdmd/collect.py")
        self.assertEqual(entry["runner_scope"], "native-and-msdmd-blocks")
        self.assertEqual(entry["collection_schema"], "2.0.0")
        self.assertEqual(entry["native_ingestion"]["status"], "runnable")
        self.assertEqual(entry["native_ingestion"]["runner"], "msdmd/collect.py")
        self.assertEqual(
            {
                "python-ast", "msdmd-ratios", "json-stdlib", "toml-stdlib", "markdown-frontmatter",
                "yaml-safe-subset", "typescript-static", "github-codeowners", "shell-static", "systemd-unit",
                "gitignore-lines", "python-requirements", "license-text", "svg-metadata", "llms-text",
            },
            set(entry["native_ingestion"]["readers"]),
        )

    def test_identity_repairs_and_remaining_boundaries_are_explicit(self) -> None:
        text = (ROOT / "msdmd/SKILL.md").read_text(encoding="utf-8")
        for statement in (
            "Schema 2 diagnoses duplicate IDs",
            "qualifies declaration and source-edge",
            "Ambiguous bare target references remain visible",
            "### Shipped reader boundary",
            "YAML and JavaScript/TypeScript readers are explicitly partial",
            "coverage.verified_behavior",
        ):
            self.assertIn(statement, text)
        self.assertNotIn("does not diagnose duplicate IDs", text)

    def test_llm_publication_matches_owning_sources(self) -> None:
        source = (ROOT / "llms/metadata.py").read_text(encoding="utf-8")
        entries = build.parse_text(source, source=Path("llms/metadata.py"))
        definitions = next(entry.fields for entry in entries if entry.id == "key_definitions")
        self.assertIn("native-first", definitions["msdmd"])
        self.assertIn("schema-2", definitions["msdmd"])
        self.assertIn("tested static readers", definitions["msdmd"])
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


if __name__ == "__main__":
    unittest.main()

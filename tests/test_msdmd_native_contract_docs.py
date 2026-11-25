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

    def test_llm_publication_matches_owning_sources(self) -> None:
        source = (ROOT / "llms/metadata.py").read_text(encoding="utf-8")
        entries = build.parse_text(source, source=Path("llms/metadata.py"))
        definitions = next(entry.fields for entry in entries if entry.id == "key_definitions")
        self.assertIn("native-first", definitions["msdmd"])
        self.assertIn("schema-2 collector integrates", definitions["msdmd"])
        self.assertIn("shared Python comment attachment", definitions["msdmd"])
        self.assertNotIn("each source module declares", source)
        generated = build.generate(build.collect(ROOT), self.index["repo"].split("/")[-1])
        self.assertEqual((ROOT / "llms.txt").read_text(encoding="utf-8"), generated)

    def test_repository_collection_replays_from_owning_blocks(self) -> None:
        path = ROOT / "skill-lib_msdmd.ts"
        generated = render_typescript(
            collect(ROOT, self.index["repo"], snapshot_identity=True), import_path="./msdmd/collection",
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

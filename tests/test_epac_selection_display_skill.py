from __future__ import annotations

import json
import unittest
from pathlib import Path

from frontmatter import frontmatter_for


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "epac-selection-display" / "SKILL.md"
SOURCE_FIXTURE = ROOT / "epac-selection-display" / "STACK_SOURCE_FIXTURE.json"
ADAPTER = ROOT / "skills" / "epac-selection-display" / "SKILL.md"
INDEX = ROOT / "skills.json"
STACK_SOURCE_COMMIT = "5b24db9a7fe40df4b2791e1137ade5de01c78942"
STACK_SOURCE_PATH = "research/epac/README.md"
STACK_SOURCE_BLOB = "a1f1dd6a50252349797806b2dc59897f1fb3a991"


class EpacSelectionDisplaySkillTest(unittest.TestCase):
    def setUp(self) -> None:
        self.text = SKILL.read_text(encoding="utf-8")
        self.compact = " ".join(self.text.split())
        self.frontmatter = frontmatter_for(SKILL)

    def test_activation_and_nontrigger_are_discriminating(self) -> None:
        description = self.frontmatter["description"]
        for phrase in (
            "EPAC element, molecule, construction receipt, comparison result",
            "selectable WebMCP skill",
            "missing or invented geometry",
            "refused or downgraded to verified source-backed output",
            "Do not load to select EPAC or a UCNS candidate as canon",
            "unrelated WebMCP catalogue changes",
        ):
            self.assertIn(phrase, description)
        self.assertNotIn("Do not load to select EPAC or a UCNS candidate as canon, invent missing geometry", description)

    def test_display_selection_never_promotes_status(self) -> None:
        for phrase in (
            "display selection != canon selection",
            "A display preference cannot ratify a candidate",
            "selection_effect",
            "not organization canon",
        ):
            self.assertIn(phrase, self.text)

    def test_handle_and_provisional_source_boundaries_are_explicit(self) -> None:
        self.assertIn("The EPAC handle is despecified here", self.text)
        self.assertIn("no independent authoritative source repository", self.compact)
        self.assertIn("base commit plus content digests", self.compact)
        self.assertIn(STACK_SOURCE_COMMIT, self.text)

    def test_provisional_source_pin_has_immutable_stack_fixture(self) -> None:
        fixture = json.loads(SOURCE_FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual("the-interdependency.epac-selection-display-source-fixture", fixture["schema"])
        self.assertEqual("1.0.0", fixture["version"])
        self.assertEqual("The-Interdependency/stack", fixture["source"]["repository"])
        self.assertEqual(STACK_SOURCE_COMMIT, fixture["source"]["commit"])
        self.assertEqual(STACK_SOURCE_PATH, fixture["source"]["path"])
        self.assertEqual(STACK_SOURCE_BLOB, fixture["source"]["git_blob_sha"])
        self.assertIn(fixture["source"]["commit"], self.text)
        self.assertEqual("provisional stack-local EPAC research scaffold", fixture["standing"])
        for field in (
            "authority_transfer",
            "canon_status_transfer",
            "proof_status_transfer",
            "measurement_status_transfer",
            "empirical_status_transfer",
        ):
            self.assertFalse(fixture["boundaries"][field])
        self.assertTrue(fixture["usage"])
        self.assertTrue(fixture["hmmm"])

    def test_target_receipt_and_representation_are_verified(self) -> None:
        for phrase in (
            "Selection record",
            "Resolve the user-facing target to one exact registered identifier",
            "independently replay it",
            "receipt-backed summary rather than inventing a visual projection",
            "Emit the evidence packet beside the display",
            "display_mode: summary | text | svg | receipt-json | comparison | hmmm",
        ):
            self.assertIn(phrase, self.text)

    def test_audience_and_destination_survive_output(self) -> None:
        self.assertIn("audience\ndestination", self.text)
        output = self.text.split("## Output shape", 1)[1]
        self.assertGreaterEqual(output.count("- Audience:"), 2)
        self.assertGreaterEqual(output.count("- Destination:"), 2)

    def test_webmcp_remains_a_read_only_handoff(self) -> None:
        for phrase in (
            "require repository selection before skill selection",
            "require an explicit Send",
            "remote MCP server remains a read-only registry",
            "separately authorized tools",
        ):
            self.assertIn(phrase, self.text)

    def test_sealed_comparison_and_invented_geometry_are_blocked(self) -> None:
        self.assertIn("construction remains blind to sealed known-shape labels", self.compact)
        self.assertIn("must not infer positions, couplings", self.compact)
        self.assertIn("Opening sealed comparison labels during construction", self.text)
        self.assertIn("load-to-refuse case", self.text)

    def test_index_and_adapter_expose_the_canonical_skill(self) -> None:
        index = json.loads(INDEX.read_text(encoding="utf-8"))
        entry = next(item for item in index["skills"] if item["name"] == "epac-selection-display")
        self.assertEqual("procedural", entry["kind"])
        self.assertEqual(self.frontmatter["description"], entry["description"])

        adapter = ADAPTER.read_text(encoding="utf-8")
        self.assertIn("Generated by tools/build_codex_plugin_skills.py", adapter)
        self.assertIn("../../epac-selection-display/SKILL.md", adapter)
        self.assertEqual(self.frontmatter["description"], frontmatter_for(ADAPTER)["description"])


if __name__ == "__main__":
    unittest.main()

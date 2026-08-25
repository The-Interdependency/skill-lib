from __future__ import annotations

import unittest
from pathlib import Path

from frontmatter import frontmatter_for


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "gonol-build" / "SKILL.md"
ADAPTER = ROOT / "skills" / "gonol-build" / "SKILL.md"


class GonolBuildSkillTest(unittest.TestCase):
    def setUp(self) -> None:
        self.text = SKILL.read_text(encoding="utf-8")
        self.compact = " ".join(self.text.split())
        self.frontmatter = frontmatter_for(SKILL)

    def test_activation_contract_is_concrete(self) -> None:
        description = self.frontmatter["description"]
        for phrase in (
            "character, word, definition, or recursive-relation gonols",
            "UCNS owns geometry; EDCM owns text construction",
            "characters -> words -> definitions -> recursive gonol relations",
            "Pronunciation is not required",
            "Do not load",
        ):
            self.assertIn(phrase, description)

    def test_authority_split_is_minimal(self) -> None:
        for phrase in (
            "UCNS = geometry",
            "EDCM = text-domain gonol construction",
            "skill-lib = construction/replay discipline",
            "Do not move text semantics into UCNS",
            "invent geometry in EDCM",
        ):
            self.assertIn(phrase, self.compact)

    def test_edcm_skeleton_requires_words(self) -> None:
        self.assertIn(
            "characters -> words -> definitions -> recursive gonol relations",
            self.compact,
        )
        self.assertNotIn("characters -> definitions -> recursive gonol relations", self.compact)
        self.assertIn("This order is load-bearing", self.compact)
        self.assertIn("Ordered character gonols close into a word gonol", self.compact)

    def test_closed_words_promote_atomically(self) -> None:
        for phrase in (
            "A closed word gonol is atomic at the consuming scale",
            "constituent identities, order, multiplicity, source positions, and provenance remain recoverable",
            "Definition gonols are constructed from the applicable closed word gonols",
            "Recursive relations are constructed from already-closed gonols",
        ):
            self.assertIn(phrase, self.compact)

    def test_no_undeclared_intermediate_stage(self) -> None:
        self.assertIn(
            "Do not insert another required stage into this sequence unless the governing contract is explicitly changed",
            self.compact,
        )

    def test_pronunciation_is_inert_by_default(self) -> None:
        for phrase in (
            "Pronunciation is not required for this construction",
            "must not alter gonol identity, closure, ordering, or relations",
            "Source pronunciation data may remain source metadata",
            "It is not a dependency of the current build",
        ):
            self.assertIn(phrase, self.compact)

    def test_construction_invariant_preserves_identity_and_provenance(self) -> None:
        for phrase in (
            "ordered eligible gonols",
            "authorized UCNS geometric relation/application",
            "deterministic identity + provenance receipt",
            "Preserve exact source identity, occurrence order, multiplicity, and provenance",
            "Do not normalize, deduplicate, infer relations",
        ):
            self.assertIn(phrase, self.compact)

    def test_unresolved_geometry_stays_hmmm(self) -> None:
        self.assertIn("preserve that boundary as `hmmm`", self.text)
        self.assertIn("do not fill it with an invented rule", self.compact)

    def test_completion_requires_full_scope_and_replay(self) -> None:
        for phrase in (
            "preflight the resources required to finish it",
            "Do not add arbitrary wall-clock limits",
            "the complete declared source scope",
            "deterministic construction receipts",
            "independent complete replay",
            "Replay establishes reproducibility of that construction only",
        ):
            self.assertIn(phrase, self.compact)

    def test_workflow_and_anti_patterns_are_named(self) -> None:
        self.assertIn("## Workflow", self.text)
        self.assertIn("## Anti-patterns", self.text)
        self.assertIn("Resolve the current UCNS and EDCM authorities before building", self.compact)
        self.assertIn("Moving text semantics into UCNS or inventing geometry in EDCM", self.compact)

    def test_usage_guidance_repeats_operational_contract(self) -> None:
        self.assertIn("For text construction, start in EDCM and consume current UCNS geometry", self.compact)
        self.assertIn("When a word closes, use that word gonol atomically at the next scale", self.compact)
        self.assertIn("Ignore pronunciation unless a future explicit construction says otherwise", self.compact)

    def test_codex_adapter_points_to_canonical_skill(self) -> None:
        text = ADAPTER.read_text(encoding="utf-8")
        self.assertIn("Generated by tools/build_codex_plugin_skills.py", text)
        self.assertIn("../../gonol-build/SKILL.md", text)


if __name__ == "__main__":
    unittest.main()

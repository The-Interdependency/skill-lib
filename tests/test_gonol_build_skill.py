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
            "no universal adjacent-scale ladder is required",
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

    def test_scale_options_are_owned_by_edcm(self) -> None:
        self.assertIn("`docs/GONOL_LANGUAGE_BOUNDARY.md`", self.text)
        self.assertIn("`edcm/gonol.py`", self.text)
        self.assertIn("not a mandatory ladder", self.compact)
        self.assertIn("character-to-definition construction must not be rejected", self.compact)
        self.assertNotIn("This order is load-bearing", self.compact)

    def test_closed_words_promote_atomically(self) -> None:
        for phrase in (
            "Any closed gonol is atomic at an admissible consuming scale",
            "constituent identities, order, multiplicity, source positions, and provenance remain recoverable",
            "Definition gonols use eligible closed participants",
            "Recursive relations are constructed from already-closed gonols",
        ):
            self.assertIn(phrase, self.compact)

    def test_no_undeclared_intermediate_stage(self) -> None:
        self.assertIn(
            "Do not invent participant eligibility or another required stage",
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
            "Before launching a construction or replay run whose completion materially depends on scarce resources",
            "preflight the resources required to finish it",
            "do not start the compute run",
            "Do not add arbitrary wall-clock limits",
            "the complete declared source scope",
            "deterministic construction receipts",
            "independent complete replay where replay is required by the governing protocol",
            "Replay establishes reproducibility of that construction only",
        ):
            self.assertIn(phrase, self.compact)

    def test_workflow_preflights_before_compute_and_replays_conditionally(self) -> None:
        workflow = self.text.split("## Workflow", 1)[1].split("## Authority", 1)[0]
        for phrase in (
            "Before launching construction or replay whose completion materially depends on scarce resources",
            "preflight the resources required to finish the declared scope",
            "Replay the complete declared scope only where replay is required by the governing protocol",
        ):
            self.assertIn(phrase, workflow)
        self.assertLess(
            workflow.index("Before launching construction or replay"),
            workflow.index("Resolve the EDCM constructor's declared scale option set"),
        )
        self.assertNotIn(
            "Preflight resources before a completion claim, then replay the complete declared scope",
            workflow,
        )

    def test_workflow_and_anti_patterns_are_named(self) -> None:
        self.assertIn("## Workflow", self.text)
        self.assertIn("## Anti-patterns", self.text)
        self.assertIn("Resolve the current UCNS and EDCM authorities before building", self.compact)
        self.assertIn("Moving text semantics into UCNS or inventing geometry in EDCM", self.compact)

    def test_anti_patterns_preserve_explicit_contract_exceptions(self) -> None:
        anti_patterns = self.text.split("## Anti-patterns", 1)[1].split("## hmmm", 1)[0]
        self.assertIn(
            "unless a later explicitly declared experiment makes phonology part of its construction",
            anti_patterns,
        )
        self.assertIn(
            "unless the active contract explicitly authorizes it",
            anti_patterns,
        )

    def test_usage_guidance_repeats_operational_contract(self) -> None:
        self.assertIn("For text construction, start in EDCM and consume current UCNS geometry", self.compact)
        self.assertIn("When a gonol closes, use it atomically at any admissible consuming scale", self.compact)
        self.assertIn("Ignore pronunciation unless a future explicit construction says otherwise", self.compact)

    def test_codex_adapter_points_to_canonical_skill(self) -> None:
        text = ADAPTER.read_text(encoding="utf-8")
        self.assertIn("Generated by tools/build_codex_plugin_skills.py", text)
        self.assertIn("../../gonol-build/SKILL.md", text)


if __name__ == "__main__":
    unittest.main()

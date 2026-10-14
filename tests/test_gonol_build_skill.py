from __future__ import annotations

import unittest
from pathlib import Path

from frontmatter import frontmatter_for


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "gonol-build" / "SKILL.md"
ADAPTER = ROOT / "skills" / "gonol-build" / "SKILL.md"
WITNESS = ROOT / "tools" / "check_gonol_authority.sh"


class GonolBuildSkillTest(unittest.TestCase):
    def setUp(self) -> None:
        self.text = SKILL.read_text(encoding="utf-8")
        self.compact = " ".join(self.text.split())
        self.frontmatter = frontmatter_for(SKILL)

    def test_activation_contract_is_concrete(self) -> None:
        description = self.frontmatter["description"]
        for phrase in (
            "UCNS gonol objects",
            "Stack owns active construction research",
            "EDCM owns measurement/evaluation only",
            "no universal adjacent-scale ladder is required",
            "Pronunciation is not required",
            "Do not load",
        ):
            self.assertIn(phrase, description)

    def test_authority_split_is_current(self) -> None:
        for phrase in (
            "UCNS = gonol objects, constructors, and underlying geometry",
            "Stack = active language-gonol construction research workspaces",
            "EDCM = measurement and evaluation of constructed outputs",
            "skill-lib = construction/replay discipline",
        ):
            self.assertIn(phrase, self.compact)
        self.assertNotIn("EDCM = text-domain gonol construction", self.compact)
        self.assertNotIn("EDCM owns the admissible scale options", self.compact)

    def test_active_construction_resolves_stack_workspace(self) -> None:
        self.assertIn("research/english-gonol/", self.text)
        self.assertIn("research/python-gonol/", self.text)
        self.assertIn("Do not start in EDCM", self.text)
        self.assertIn("Historical EDCM constructor names", self.text)
        self.assertNotIn("`edcm/gonol.py`", self.text)

    def test_gonol_object_authority_remains_ucns(self) -> None:
        for phrase in (
            "Consume UCNS gonol constructors and geometry",
            "Defining a competing gonol object",
            "consume UCNS construction authority",
        ):
            self.assertIn(phrase, self.compact)

    def test_closed_gonols_participate_atomically(self) -> None:
        for phrase in (
            "Any closed gonol is atomic at an admissible consuming scale",
            "constituent identities, order, multiplicity, source positions, relations, and provenance remain recoverable",
            "Constitutive relationships belong inside the construction",
            "Recursive relations consume already-closed gonols",
        ):
            self.assertIn(phrase, self.compact)

    def test_no_undeclared_intermediate_or_substitute_representation(self) -> None:
        for phrase in (
            "Do not invent participant eligibility, a required intermediate stage",
            "Do not normalize, deduplicate, infer relations",
            "tokens, AST nodes, compiler objects, embeddings, hashes, or metadata",
        ):
            self.assertIn(phrase, self.compact)

    def test_pronunciation_is_inert_by_default(self) -> None:
        for phrase in (
            "Pronunciation is not required by default",
            "must not alter gonol identity, closure, ordering, or relations",
            "Source pronunciation data may remain evidence or metadata",
            "only under an explicit source/admission contract",
        ):
            self.assertIn(phrase, self.compact)

    def test_construction_invariant_preserves_identity_relation_and_provenance(self) -> None:
        for phrase in (
            "ordered eligible closed gonols",
            "constitutive relation declared by the owning workspace",
            "UCNS gonol construction / authorized geometric application",
            "deterministic identity + provenance receipt",
            "Preserve exact source identity, occurrence order, multiplicity, relation identity, and provenance",
        ):
            self.assertIn(phrase, self.compact)

    def test_unresolved_geometry_stays_hmmm(self) -> None:
        self.assertIn("preserve that boundary as `hmmm`", self.text)
        self.assertIn("do not fill it with an invented rule", self.compact)

    def test_local_authority_gate_is_named(self) -> None:
        self.assertTrue(WITNESS.is_file())
        self.assertIn("bash tools/check_gonol_authority.sh", self.text)

    def test_completion_preserves_resource_and_replay_boundary(self) -> None:
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

    def test_workflow_preflights_before_constructor_resolution_and_replays_conditionally(self) -> None:
        workflow = self.text.split("## Workflow", 1)[1].split("## Authority", 1)[0]
        for phrase in (
            "Before launching construction or replay whose completion materially depends on scarce resources",
            "preflight the resources required to finish the declared scope",
            "Resolve the owning Stack workspace's declared source/admission profile",
            "Replay the complete declared scope only where replay is required by the governing protocol",
        ):
            self.assertIn(phrase, workflow)
        self.assertLess(
            workflow.index("Before launching construction or replay"),
            workflow.index("Resolve the owning Stack workspace's declared source/admission profile"),
        )

    def test_workflow_and_anti_patterns_are_named(self) -> None:
        self.assertIn("## Workflow", self.text)
        self.assertIn("## Anti-patterns", self.text)
        self.assertIn("Resolve the exact UCNS authority and the exact owning Stack research workspace", self.compact)
        self.assertIn("Assigning active gonol or language construction authority to EDCM", self.compact)

    def test_anti_patterns_preserve_explicit_contract_exceptions(self) -> None:
        anti_patterns = self.text.split("## Anti-patterns", 1)[1].split("## hmmm", 1)[0]
        self.assertIn(
            "unless an explicit construction admits it",
            anti_patterns,
        )
        self.assertIn(
            "unless explicitly authorized",
            anti_patterns,
        )

    def test_usage_guidance_and_owning_sections_preserve_contract(self) -> None:
        self.assertIn("start in the owning research workspace inside `The-Interdependency/stack`", self.compact)
        self.assertIn("Do not start in EDCM", self.compact)
        self.assertIn("Close each completed gonol before it participates atomically at an admissible consuming scale", self.compact)
        self.assertIn("must not alter gonol identity, closure, ordering, or relations unless the owning construction explicitly admits phonology", self.compact)

    def test_codex_adapter_points_to_canonical_skill(self) -> None:
        text = ADAPTER.read_text(encoding="utf-8")
        self.assertIn("Generated by tools/build_codex_plugin_skills.py", text)
        self.assertIn("../../gonol-build/SKILL.md", text)
        self.assertIn("EDCM owns measurement/evaluation only", text)
        self.assertNotIn("EDCM owns text construction", text)


if __name__ == "__main__":
    unittest.main()

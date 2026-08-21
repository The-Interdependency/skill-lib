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

    def test_activation_and_nontrigger_are_concrete(self) -> None:
        description = self.frontmatter["description"]
        for phrase in (
            "character, definition, punctuation-function",
            "recursive textual gonols",
            "attempts to introduce morphology",
            "Do not load",
            "ordinary prose editing",
        ):
            self.assertIn(phrase, description)

    def test_routes_authority_across_metapat_ucns_edcm(self) -> None:
        for phrase in (
            "METAPAT -> conceptual meaning of affixiation",
            "UCNS -> gonol geometry",
            "EDCM -> text-domain admission, definitions, functions, and recursive relations",
            "skill-lib -> construction, evidence, replay",
            "Resolve the current commits or PR heads",
        ):
            self.assertIn(phrase, self.compact)

    def test_every_character_is_edcm_domain_rule(self) -> None:
        self.assertIn("Every admitted character is a gonol", self.text)
        self.assertIn("EDCM owns what counts as an admitted character", self.compact)
        self.assertIn("UCNS geometrically realizes admitted participants", self.compact)

    def test_edcm_skeleton_has_no_morphology_layer(self) -> None:
        self.assertIn("characters -> definitions -> recursive gonol relations", self.compact)
        self.assertIn("Linguistic morphology is not a privileged construction layer", self.compact)
        self.assertIn("does not create a morphology stage", self.compact)
        self.assertNotIn("characters -> morphology", self.compact)
        self.assertNotIn("complete English morphology law", self.compact)

    def test_conventional_linguistic_categories_are_not_privileged_scales(self) -> None:
        for phrase in (
            "words, roots, stems, affixes, lemmas, tokens",
            "mandatory gonol scales",
            "one sourced relation among gonols, not a privileged layer",
            "never promote the category into a scale",
        ):
            self.assertIn(phrase, self.compact)

    def test_affixiation_authority_is_not_redefined_downstream(self) -> None:
        self.assertIn("METAPAT defines affixiation conceptually", self.compact)
        self.assertIn("UCNS owns the exact geometric realization", self.compact)
        self.assertIn("EDCM applies affixiation to text-domain gonols", self.compact)
        self.assertIn("does not define affixiation", self.compact)

    def test_closure_and_atomic_promotion_are_preserved(self) -> None:
        for phrase in (
            "relation enters the construction",
            "closure with source identity and receipt",
            "atomic participant at another declared scale",
            "atomic for participation at the consuming scale",
            "Do not materialize an all-pairs relationship graph",
        ):
            self.assertIn(phrase, self.compact)

    def test_dependency_complete_construction_rejects_reduced_substitutes(self) -> None:
        for phrase in (
            "Do not optimize for the smallest executable implementation",
            "dependency-complete and architecture- preserving",
            "toy, proxy, MVP, stub",
            "Do not add arbitrary wall-clock limits",
        ):
            self.assertIn(phrase, self.compact)

    def test_function_application_refuses_semantic_inference(self) -> None:
        for phrase in (
            "EDCM may apply only Public Gonol operations geometrically authorized by UCNS",
            "Never infer syntax, precedence, grammatical role",
            "Unicode names, dictionary glosses",
        ):
            self.assertIn(phrase, self.compact)

    def test_completion_requires_full_run_and_replay(self) -> None:
        for phrase in (
            "Admit the complete declared source",
            "Independently reconstruct or replay",
            "Compare byte-for-byte",
            "Replay establishes reproducibility of that candidate only",
        ):
            self.assertIn(phrase, self.compact)

    def test_historical_gonal_morphology_cannot_return(self) -> None:
        self.assertIn("deprecated omega/phi/psi cores", self.compact)
        self.assertIn("bone/flesh categories", self.compact)
        self.assertIn("historical fixed morphology weights", self.compact)
        self.assertIn("carrier-LCM language doctrine", self.compact)

    def test_hmmm_and_claim_boundaries_are_required(self) -> None:
        self.assertIn("claims not supported:", self.text)
        self.assertIn("hmmm:", self.text)
        self.assertIn("SURVIVED` does not mean proved or canonical", self.text)
        self.assertIn("block unqualified promotion, not declared candidate construction", self.compact)

    def test_codex_adapter_points_to_canonical_skill(self) -> None:
        text = ADAPTER.read_text(encoding="utf-8")
        self.assertIn("Generated by tools/build_codex_plugin_skills.py", text)
        self.assertIn("../../gonol-build/SKILL.md", text)


if __name__ == "__main__":
    unittest.main()

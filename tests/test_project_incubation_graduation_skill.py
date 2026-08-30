from __future__ import annotations

import json
import unittest
from pathlib import Path

from frontmatter import frontmatter_for


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "project-incubation-graduation" / "SKILL.md"
INDEX = ROOT / "skills.json"
ADAPTER = ROOT / "skills" / "project-incubation-graduation" / "SKILL.md"


class ProjectIncubationGraduationSkillTest(unittest.TestCase):
    def setUp(self) -> None:
        self.text = SKILL.read_text(encoding="utf-8")
        self.frontmatter = frontmatter_for(SKILL)
        self.index = json.loads(INDEX.read_text(encoding="utf-8"))
        self.adapter = ADAPTER.read_text(encoding="utf-8")

    def test_activation_and_non_trigger_are_explicit(self) -> None:
        description = self.frontmatter["description"]
        self.assertIn("Load this when", description)
        self.assertIn("compose into a new candidate capability", description)
        self.assertIn("become its own repository/package", description)
        self.assertIn("publishing the extracted project", description)
        self.assertIn("making the former incubator consume the released artifact", description)
        self.assertIn("Do not load", description)
        self.assertIn("ordinary new repository", description)
        self.assertIn("routine package release", description)

    def test_registered_as_procedural_and_adapter_loads_canonical_skill(self) -> None:
        record = next(
            skill for skill in self.index["skills"]
            if skill["name"] == "project-incubation-graduation"
        )
        self.assertEqual(record["path"], "project-incubation-graduation/SKILL.md")
        self.assertEqual(record["kind"], "procedural")
        self.assertEqual(record["description"], self.frontmatter["description"])
        self.assertIn("Read and follow `../../project-incubation-graduation/SKILL.md`", self.adapter)

    def test_lifecycle_and_reconsumption_gate_are_explicit(self) -> None:
        for state in (
            "incubating",
            "stabilizing",
            "qualified",
            "extracted",
            "released",
            "reconsumed",
            "graduated",
        ):
            with self.subTest(state=state):
                self.assertIn(state, self.text)
        self.assertIn("The forge proves the separation is real", self.text)
        self.assertIn("Sever the old implementation path", self.text)
        self.assertIn("graduation is complete only after the forge reconsumes", self.text)

    def test_external_mutations_require_explicit_authorization(self) -> None:
        self.assertIn("## Assessment versus execution", self.text)
        self.assertIn("Assessment is read-only", self.text)
        self.assertIn("explicit authorization required", self.text)
        self.assertIn("does not authorize repository creation", self.text)
        for action in (
            "create repository",
            "reserve or publish package name",
            "mutate forge dependency/imports",
            "sever incubated implementation",
            "transfer implementation authority",
        ):
            with self.subTest(action=action):
                self.assertIn(action, self.text)

    def test_release_authority_unknowns_block_qualification(self) -> None:
        self.assertIn("license_distribution_rights", self.text)
        self.assertIn("release_ownership_authority", self.text)
        self.assertIn("hard gates", self.text)
        self.assertIn("`hmmm` means **not qualified**", self.text)
        self.assertIn("license/distribution rights and release ownership are resolved, not `hmmm`", self.text)

    def test_exact_candidate_is_verified_before_stable_publication(self) -> None:
        self.assertIn("A stable public release must not be the first forge-compatibility test", self.text)
        self.assertIn("Install **that same exact candidate artifact** in the forge", self.text)
        self.assertIn("before stable publication", self.text)
        self.assertIn("do not publish it as a stable public release", self.text)
        self.assertIn("Publish the already-verified candidate bytes", self.text)

    def test_artifact_identity_is_immutable_not_version_only(self) -> None:
        self.assertIn("A human-readable version is not an immutable artifact identity", self.text)
        self.assertIn("candidate_immutable_identity", self.text)
        self.assertIn("published_immutable_identity", self.text)
        self.assertIn("published_matches_verified_candidate", self.text)
        self.assertIn("version/tag immutable evidence", self.text)
        self.assertIn("artifact digest or equivalent registry identity", self.text)

    def test_authority_transition_is_scoped_between_work_graph_snapshots(self) -> None:
        self.assertIn("the-interdependency.project-graduation-transition", self.text)
        self.assertIn("implementation_public_contract_authority_transfer: true", self.text)
        for non_transfer in (
            "semantic_authority_transfer: false",
            "theorem_status_transfer: false",
            "proof_status_transfer: false",
            "certification_status_transfer: false",
            "measurement_status_transfer: false",
            "empirical_status_transfer: false",
        ):
            with self.subTest(non_transfer=non_transfer):
                self.assertIn(non_transfer, self.text)
        self.assertIn("Do **not** encode this graduation by setting an existing work-graph `authority_transfer` field to true", self.text)
        self.assertIn("before", self.text)
        self.assertIn("after", self.text)
        self.assertIn("work_graph_sha256", self.text)

    def test_hmmm_remains_visible_but_blocking_unknowns_do_not_pass(self) -> None:
        self.assertIn("## hmmm", self.text)
        self.assertIn("blocking unresolveds do not masquerade as passed gates", self.text)
        self.assertIn("Unknown non-blocking facts remain `hmmm`", self.text)


if __name__ == "__main__":
    unittest.main()

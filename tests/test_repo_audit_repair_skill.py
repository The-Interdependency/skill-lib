from __future__ import annotations

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from frontmatter import frontmatter_for

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "repo-audit-repair" / "SKILL.md"


class RepoAuditRepairSkillTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = SKILL.read_text(encoding="utf-8")
        cls.normalized = " ".join(cls.text.split())
        cls.description = frontmatter_for(SKILL)["description"]

    def test_activation_is_broad_audit_not_ordinary_edit(self) -> None:
        self.assertIn("audit and repair an existing code repository", self.description)
        self.assertIn("Do not load for an ordinary fixed-scope edit", self.description)

    def test_audit_does_not_grant_repair_authority(self) -> None:
        self.assertIn("Treat audit-only requests as read-only", self.text)
        self.assertIn("An `audit and repair` request permits", self.text)
        self.assertIn("not unrelated cleanup", self.text)

    def test_findings_preserve_causal_classification(self) -> None:
        self.assertIn("Split compound failures into separate findings first", self.normalized)
        for finding_class in ("`DEFECT`", "`ENVIRONMENT`", "`EXTERNAL`", "`POLICY`", "`HMMM`"):
            with self.subTest(finding_class=finding_class):
                self.assertIn(finding_class, self.text)
        self.assertIn("Do not repair `ENVIRONMENT`, `EXTERNAL`, or `POLICY`", self.text)

    def test_checks_are_claim_driven_not_universal_ritual(self) -> None:
        self.assertIn("Do not impose one universal checklist", self.text)
        self.assertIn("For every selected surface, identify the claim", self.text)
        self.assertIn("do not manufacture tests merely to populate the table", self.text)

    def test_false_green_and_partial_remote_input_are_blocked(self) -> None:
        self.assertIn("A green check is evidence only for what it actually executes", self.text)
        self.assertIn("Placeholder", self.text)
        self.assertIn("Partial retrieval must fail closed or become explicit", self.text)

    def test_repairs_stay_at_the_owning_layer(self) -> None:
        self.assertIn("Repair the owning layer", self.text)
        self.assertIn("fixes its renderer", self.normalized)
        self.assertIn("does not edit the source repository's valid prose", self.normalized)

    def test_completion_distinguishes_delivery_states(self) -> None:
        self.assertIn("State `reviewed-at-head`, `merged`, `released`, and `deployed`", self.text)
        self.assertIn("Never infer one from another", self.normalized)
        self.assertIn("authoritative checks settle", self.text)

    def test_merge_admission_is_exact_revision_and_fail_closed(self) -> None:
        self.assertIn("conjunctive exact-revision", self.text)
        self.assertIn("current PR head SHA and base SHA", self.normalized)
        self.assertIn("no unresolved merge-blocking finding", self.normalized)
        self.assertIn("no unresolved review thread remains", self.normalized)
        self.assertIn("P0/P1/P2", self.text)
        self.assertIn("complete effective, non-dismissed `APPROVED` review set", self.normalized)
        self.assertIn("approval count, reviewer role, and eligibility constraint", self.normalized)
        self.assertIn("Any head or base movement invalidates", self.normalized)
        self.assertIn("expected-head/SHA", self.text)
        self.assertIn("provider's strongest guarded merge path", self.normalized)
        merge_start = self.text.index("- Use the provider's strongest guarded merge path")
        merge_end = self.text.index("- If deployment or release follows", merge_start)
        guarded_merge = " ".join(self.text[merge_start:merge_end].split())
        self.assertIn("repository policy the provider declares required", guarded_merge)
        self.assertIn("protected-branch checks, approvals, conversation resolution", guarded_merge)
        self.assertIn("task-local admission evidence", guarded_merge)
        self.assertIn("Re-read that receipt immediately before merge", guarded_merge)
        self.assertIn("current base SHA or validated merge candidate", guarded_merge)
        self.assertIn("provider mergeability to be recomputed against that same base", guarded_merge)
        self.assertIn("Base movement invalidates the receipt", guarded_merge)
        self.assertIn("Do not bypass those controls", guarded_merge)
        self.assertIn("reviewed-at-head — exact head SHA + base SHA/validated merge candidate", self.text)

    def test_repo_loto_is_composed_not_required(self) -> None:
        self.assertIn("Use `repo_loto` when available", self.text)
        self.assertIn("not a prerequisite", self.text)

    def test_origin_is_bounded_and_hmmm_survives(self) -> None:
        self.assertIn("The-Interdependency/The-Interdependency.github.io", self.text)
        self.assertIn("238595b", self.text)
        self.assertIn("does not make its Eleventy", self.text)
        self.assertIn("## hmmm", self.text)


if __name__ == "__main__":
    unittest.main()

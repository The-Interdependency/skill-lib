from __future__ import annotations

import unittest
from pathlib import Path

from frontmatter import frontmatter_for

ROOT = Path(__file__).resolve().parents[1]


def read_skill(name: str) -> str:
    return (ROOT / name / "SKILL.md").read_text(encoding="utf-8")


class SkillSpecCoverageTest(unittest.TestCase):
    def assertContainsAll(self, text: str, required: list[str], label: str) -> None:
        for item in required:
            with self.subTest(skill=label, required=item):
                self.assertIn(item, text)

    def test_frontmatter_descriptions_include_load_triggers(self) -> None:
        for path in sorted(ROOT.glob("*/SKILL.md")):
            description = frontmatter_for(path).get("description", "")
            self.assertTrue(
                "Load this when" in description or "Use this when" in description,
                f"{path} description must include explicit load/use triggers",
            )

    def test_msdmd_foundation_spec(self) -> None:
        text = read_skill("msdmd")
        self.assertContainsAll(
            text,
            [
                "## Block syntax",
                "## The parser contract",
                "## Repo collection point and visualizer",
                "<reponame>_msdmd.ts",
                "declarations",
                "gaps",
                "MsdmdCollection",
                "## The runner protocol",
                "## Field naming conventions",
            ],
            "msdmd",
        )

    def test_doc_build_spec(self) -> None:
        text = read_skill("doc-build")
        self.assertContainsAll(
            text,
            [
                "# === DOCS ===",
                "audience",
                "source",
                "status",
                "A DOCS runner MUST",
                "PENDING",
                "GAP",
                "Implementation status:",
            ],
            "doc-build",
        )

    def test_cap_build_spec(self) -> None:
        text = read_skill("cap-build")
        self.assertContainsAll(
            text,
            [
                "# === CAPABILITIES ===",
                "exposes",
                "inputs",
                "outputs",
                "boundaries",
                "A CAPABILITIES runner MUST",
                "DUPLICATE",
                "Implementation status:",
            ],
            "cap-build",
        )

    def test_deps_build_spec(self) -> None:
        text = read_skill("deps-build")
        self.assertContainsAll(
            text,
            [
                "# === DEPENDENCIES ===",
                "imports",
                "calls",
                "requires",
                "provides",
                "external",
                "A DEPENDENCIES runner MUST",
                "CYCLE",
            ],
            "deps-build",
        )

    def test_owner_build_spec(self) -> None:
        text = read_skill("owner-build")
        self.assertContainsAll(
            text,
            [
                "# === OWNERS ===",
                "owner",
                "steward",
                "review_required_for",
                "escalation",
                "An OWNERS runner MUST",
                "REVIEW_REQUIRED",
            ],
            "owner-build",
        )

    def test_test_build_spec(self) -> None:
        text = read_skill("test-build")
        self.assertContainsAll(
            text,
            [
                "# === CONTRACTS ===",
                "given",
                "then",
                "call",
                "## Authoring a runner",
                "PASS",
                "FAIL",
                "ERROR",
            ],
            "test-build",
        )

    def test_meta_module_build_spec(self) -> None:
        text = read_skill("meta-module-build")
        self.assertContainsAll(
            text,
            [
                "# === MODULE_BUILD ===",
                "module_name",
                "module_kind",
                "auth_boundary",
                "storage_boundary",
                "network_boundary",
                "user_data_boundary",
                "admin_only",
                "## Runner behavior",
            ],
            "meta-module-build",
        )

    def test_risk_boundary_build_spec(self) -> None:
        text = read_skill("risk-boundary-build")
        self.assertContainsAll(
            text,
            [
                "# === BOUNDARIES ===",
                "auth_boundary",
                "storage_boundary",
                "network_boundary",
                "user_data_boundary",
                "admin_only",
                "A BOUNDARIES runner MUST",
                "Agent behavior",
            ],
            "risk-boundary-build",
        )

    def test_ratios_spec(self) -> None:
        text = read_skill("ratios")
        self.assertContainsAll(
            text,
            [
                "ratios: loc_comments=",
                "not a fenced block",
                "first line and its last non-blank line",
                "loc_comments",
                "imports_exports",
                "calls_definitions",
                "parse_ratios",
                "python ratios_check.py",
                "hmmm",
            ],
            "ratios",
        )

    def test_llms_build_spec(self) -> None:
        text = read_skill("llms-build")
        self.assertContainsAll(
            text,
            [
                "# === LLMS ===",
                "project_overview",
                "key_definitions",
                "architecture_summary",
                "usage_rules",
                "python -m llms.build",
                "--apply",
                "--check",
                "hmmm",
            ],
            "llms-build",
        )

    def test_canon_spec(self) -> None:
        text = read_skill("canon")
        self.assertContainsAll(
            text,
            [
                "## Canon test",
                "declared",
                "implemented",
                "repo-local",
                "inferred",
                "desired",
                "## Canonization workflow",
                "hmmm",
            ],
            "canon",
        )

    def test_visitor_intro_spec(self) -> None:
        text = read_skill("visitor-intro")
        self.assertContainsAll(
            text,
            [
                "## When to load",
                "## Org thesis",
                "## Repo map",
                "## Recommended reading order",
                "## Output shape",
                "hmmm",
            ],
            "visitor-intro",
        )


if __name__ == "__main__":
    unittest.main()

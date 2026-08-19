from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tools.build_codex_plugin_skills import canonical_frontmatter
from tools.check_skill_lib_drift import (
    duplicate_entry_findings,
    duplicate_names,
    names_in_org_list,
    names_in_readme_list,
)


class SkillLibDriftCheckerTest(unittest.TestCase):
    def test_canonical_frontmatter_supports_folded_trigger_descriptions(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "SKILL.md"
            path.write_text(
                "---\nname: folded\ndescription: >-\n  Load this when a folded\n  trigger is canonical.\n---\n",
                encoding="utf-8",
            )
            self.assertEqual(
                "Load this when a folded trigger is canonical.",
                canonical_frontmatter(path)["description"],
            )

    def test_duplicate_names_reports_each_repeated_name_once(self) -> None:
        self.assertEqual(["manifest", "msdmd"], duplicate_names(["msdmd", "manifest", "msdmd", "manifest", "canon"]))

    def test_duplicate_entry_findings_cover_index_readme_and_org(self) -> None:
        findings = duplicate_entry_findings(
            [{"name": "manifest"}, {"name": "manifest"}],
            ["manifest", "manifest"],
            ["manifest", "manifest"],
        )

        self.assertEqual(
            ["duplicate_index_entry", "duplicate_readme_entry", "duplicate_org_entry"],
            [finding.code for finding in findings],
        )
        self.assertTrue(all(finding.severity == "error" for finding in findings))

    def test_extractors_preserve_duplicates_for_duplicate_detection(self) -> None:
        readme = "\n".join([
            "| [`manifest/`](manifest/SKILL.md) | first |",
            "| [`manifest/`](manifest/SKILL.md) | second |",
        ])
        org = "\n".join([
            "* `manifest/` — first",
            "* `manifest/` — second",
        ])

        self.assertEqual(["manifest", "manifest"], names_in_readme_list(readme))
        self.assertEqual(["manifest", "manifest"], names_in_org_list(org))


if __name__ == "__main__":
    unittest.main()

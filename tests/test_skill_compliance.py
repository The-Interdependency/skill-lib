"""Compliance and bounded Markdown heading regressions.

Usage: python -m unittest tests.test_skill_compliance
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.check_skill_compliance import check_skill, collect_findings, has_heading, workflow_count


class SkillComplianceCheckerTest(unittest.TestCase):
    def test_no_skill_compliance_findings(self) -> None:
        self.assertEqual([], collect_findings())

    def test_workflow_heading_forms_share_presence_and_count_rules(self) -> None:
        for indent in ("", " ", "  ", "   "):
            for body in ("## Workflow", "## Workflow: titled", "##\tWorkflow",
                         "##  Workflow", "## WORKFLOW ###", "## Workflow: titled ##\t"):
                with self.subTest(indent=indent, body=body):
                    text = indent + body + "\n"
                    self.assertTrue(has_heading(text, "workflow"))
                    self.assertEqual(1, workflow_count(text))
                    self.assertEqual(2, workflow_count(text + "## Workflow\n"))

    def test_indented_code_and_lookalikes_are_not_workflow_headings(self) -> None:
        for prefix in ("    ", "     ", "\t", " \t", "  \t", "\t ", "\u00a0"):
            for body in ("## Workflow", "## Workflow: titled"):
                with self.subTest(prefix=prefix, body=body):
                    text = prefix + body + "\n"
                    self.assertFalse(has_heading(text, "workflow"))
                    self.assertEqual(0, workflow_count(text))
                    self.assertEqual(1, workflow_count("## Workflow\n\n" + text))
        for text in ("# Workflow", "### Workflow", "##Workflow", "##\u00a0Workflow",
                     "## Workflows", "## Workflow examples", "## Workflow###",
                     "## Workflow ###x", "## Workflow \\###", "## Workflow : title",
                     "> ## Workflow", "- ## Workflow"):
            with self.subTest(text=text):
                self.assertFalse(has_heading(text, "workflow"))
                self.assertEqual(0, workflow_count(text))

    def test_indented_fence_examples_cannot_change_fence_state(self) -> None:
        for prefix in ("    ", "\t", " \t", "  \t", "\u00a0"):
            for token in ("```", "~~~"):
                with self.subTest(prefix=prefix, token=token):
                    text = prefix + token + "\n\n## Workflow\n"
                    self.assertTrue(has_heading(text, "workflow"))
                    self.assertEqual(1, workflow_count(text))
                    fenced = token + "\n" + prefix + token + "\n## Workflow\n" + token + "\n"
                    self.assertFalse(has_heading(fenced, "workflow"))
                    self.assertEqual(0, workflow_count(fenced))

    def test_fence_types_lengths_and_suffixes_preserve_examples(self) -> None:
        for token in ("```", "~~~", "````", "~~~~"):
            for indent in ("", " ", "  ", "   "):
                with self.subTest(token=token, indent=indent):
                    text = indent + token + "text\n## Workflow: example\n" + indent + token + "\t\n"
                    self.assertFalse(has_heading(text, "workflow"))
                    self.assertEqual(1, workflow_count(text + "## Workflow\n"))
            for suffix in ("text", "\u00a0"):
                with self.subTest(token=token, suffix=suffix):
                    text = token + "text\n" + token + suffix + "\n## Workflow\n" + token + "\n"
                    self.assertEqual(0, workflow_count(text))
        for text in ("````\n```\n## Workflow\n````\n",
                     "```\n~~~\n## Workflow\n```\n",
                     "```\n## Workflow: unclosed example\n"):
            with self.subTest(text=text):
                self.assertFalse(has_heading(text, "workflow"))
                self.assertEqual(0, workflow_count(text))

    def test_backtick_info_must_not_contain_backticks(self) -> None:
        text = "```bad`info\n## Workflow\n"
        self.assertTrue(has_heading(text, "workflow"))
        self.assertEqual(1, workflow_count(text))
        self.assertEqual(0, workflow_count("~~~valid`info\n## Workflow\n~~~\n"))

    def test_alternative_workflow_names_keep_the_same_normalization(self) -> None:
        names = (
            "make-fresh workflow", "canonization workflow", "compression procedure",
            "instancing sequence (dependency order — follow it top to bottom)",
            "instantiation sequence (dependency order — follow it top to bottom)",
            "compliance workflow for existing skills",
        )
        for name in names:
            for suffix in ("", ": titled"):
                with self.subTest(name=name, suffix=suffix):
                    text = "   ##\t" + name.upper() + suffix + " ###\n"
                    self.assertTrue(has_heading(text, "absent", name))
                    self.assertEqual(0, workflow_count(text))
                    self.assertFalse(has_heading("```\n" + text + "```\n", name))

    def test_compliance_uses_only_real_normalized_workflow_sections(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "example" / "SKILL.md"
            path.parent.mkdir()
            prefix = "---\nname: example\ndescription: Load this when testing.\n---\n## Anti-patterns\nhmmm\n"
            index = {"example": {"kind": "procedural"}}
            for example in ("```\n## Workflow\n```\n", "    ## Workflow\n", "\t## Workflow: example\n"):
                with self.subTest(example=example):
                    path.write_text(prefix + example)
                    self.assertIn("workflow_shape", [f.code for f in check_skill(path, index)])
                    path.write_text(prefix + example + "   ##\tWorkflow ###\n")
                    self.assertEqual([], check_skill(path, index))
                    path.write_text(prefix + example + "   ##\tWorkflow ###\n ## Workflow: other ##\n")
                    self.assertIn("duplicate_workflow", [f.code for f in check_skill(path, index)])


if __name__ == "__main__":
    unittest.main()

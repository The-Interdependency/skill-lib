"""Conservation and decision-boundary guards for narrative migration.

Usage: python -m unittest discover -s tests -p 'test_narrative_migration.py'
These checks protect specified artifacts and decisions, not universal semantic
equivalence. The independent reader exercise is recorded in docs/narrative-migration.
"""

import contextlib
import hashlib
import io
import json
import re
import tempfile
import unittest
from pathlib import Path

from tools import check_consumer_drift, propagate_skills
from tools.build_codex_plugin_skills import canonical_frontmatter
from tools.check_skill_compliance import check_skill, workflow_count

ROOT = Path(__file__).resolve().parents[1]


def fragments(text):
    blocks = re.findall(r"(?ms)^```[^\n]*\n.*?^```\s*$", text)
    tables = re.findall(r"(?m)(?:^\|[^\n]*\n)+", text)
    return {hashlib.sha256(item.strip().encode()).hexdigest() for item in blocks + tables}


class NarrativeMigrationTests(unittest.TestCase):
    def test_inventory_covers_canonical_skills_once(self):
        inventory = json.loads((ROOT / "docs/narrative-migration/inventory.json").read_text())
        index = json.loads((ROOT / "skills.json").read_text())["skills"]
        names = [item["name"] for item in inventory["entries"]]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(set(names), {item["name"] for item in index})
        for item in inventory["entries"]:
            self.assertTrue(item["decisions"], item["name"])
            self.assertIn(item["status"], ("migrated", "reviewed-retained"))
            self.assertIn(item["family"], inventory["families"])
        self.assertTrue(inventory["hmmm"])

    def test_examples_schemas_commands_and_unresolveds_survive(self):
        fixture = json.loads((ROOT / "tests/fixtures/narrative-preservation.json").read_text())
        for name, guards in fixture["skills"].items():
            with self.subTest(skill=name):
                text = (ROOT / name / "SKILL.md").read_text()
                self.assertTrue(set(guards["fenced_and_table_sha256"]).issubset(fragments(text)))
                if guards["hmmm_tail"]:
                    self.assertIn(guards["hmmm_tail"], text)

    def test_discovery_preserves_less_obvious_activation_and_exclusions(self):
        expected = {
            "agent-instantiation": ["spawn executor", "ordinary LLM-call", "a0-betatest", "_legacy_a0"],
            "a0p-instancing": ["ordinary LLM-prompt", "pending overrides", "Mongo", "FIQ", "a0ucns"],
            "the-interdependency": ["Harrison Hovel", "interdependentway.org"],
            "visitor-intro": ["pre-task", "Do not load for in-task work by an existing contributor"],
            "plain-lens": ["Do not load to edit canon itself", "dissent"],
            "thought-lens": ["partial equations", "already-explicit claim"],
            "adaptive-elicitation": ["one-shot clarification", "non-linear recall"],
        }
        for name, clauses in expected.items():
            description = canonical_frontmatter(ROOT / name / "SKILL.md")["description"]
            for clause in clauses:
                with self.subTest(skill=name, clause=clause):
                    self.assertIn(clause, description)

    def test_lifecycle_sequence_and_permission_boundaries(self):
        a0 = (ROOT / "agent-instantiation/SKILL.md").read_text()
        sequence = a0.split("## Instantiation sequence", 1)[1].split("## Fork / merge", 1)[0]
        steps = ["Define the agent", "Boot the primary", "WDLL", "sub_agent_spawn",
                 "InstanceMerge.fork(parent)", "Execute via the spawn executor",
                 "InstanceMerge.absorb(parent, child)", "Persist on a cadence", "Gate every mutation"]
        positions = [sequence.index(step) for step in steps]
        self.assertEqual(positions, sorted(positions))
        for clause in ("require_admin", "get_approval_scope_user_id()", "Never share tensor references"):
            self.assertIn(clause, sequence)
        a0p = " ".join((ROOT / "a0p-instancing/SKILL.md").read_text().split())
        for clause in ("AgentStore.create()", "AND every `(core, seed)` pair touched",
                       "`zfae_native` refuses LLM fallback", "**halt** until approved",
                       "Never share or fork a bank", "S1–S13", "FIQ", "safetensors"):
            self.assertIn(clause, a0p)

    def test_data_verification_cannot_become_optional(self):
        text = (ROOT / "validate-data/SKILL.md").read_text()
        self.assertEqual(1, workflow_count(text))
        self.assertIn("Reproduce at least one key number independently before trusting the analysis.", text)
        self.assertIn("Seek a disconfirming cut, segment, or period.", text)
        self.assertIn("Distinguish verified, plausible, and unsupported claims", text)
        self.assertLess(text.index("Reproduce at least one"), text.index("### 8. Generate Confidence"))

    def test_duplicate_workflow_is_rejected_but_fenced_examples_are_not(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "example" / "SKILL.md"
            path.parent.mkdir()
            text = "---\nname: example\ndescription: Load this when testing.\n---\n## Workflow\nAct.\n## Anti-patterns\nhmmm\n"
            path.write_text(text + "```markdown\n## Workflow\n## Workflow: example\n```\n~~~markdown\n## Workflow\n## Workflow: example\n~~~\n\n    ## Workflow\n    ## Workflow: indented example\n")
            index = {"example": {"kind": "procedural"}}
            self.assertEqual([], check_skill(path, index))
            self.assertEqual(0, workflow_count("```text\n```python\n## Workflow\n```\n"))
            path.write_text(text + "## Workflow\nCompeting recipe.\n")
            self.assertIn("duplicate_workflow", [f.code for f in check_skill(path, index)])

    def test_titled_workflows_are_counted_and_duplicates_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "example" / "SKILL.md"
            path.parent.mkdir()
            text = "---\nname: example\ndescription: Load this when testing.\n---\n## Anti-patterns\nhmmm\n"
            index = {"example": {"kind": "procedural"}}
            for first, second in (
                ("## Workflow", "## Workflow: the five rules"),
                ("## Workflow: the five rules", "## Workflow"),
                ("## Workflow: the five rules", "## Workflow: another recipe"),
                ("## WORKFLOW: the five rules", "## Workflow"),
            ):
                with self.subTest(first=first, second=second):
                    single = text + first + "\nAct.\n"
                    path.write_text(single)
                    self.assertEqual(1, workflow_count(single))
                    self.assertEqual([], check_skill(path, index))
                    duplicate = single + second + "\nCompeting recipe.\n"
                    path.write_text(duplicate)
                    self.assertEqual(2, workflow_count(duplicate))
                    self.assertIn("duplicate_workflow", [f.code for f in check_skill(path, index)])

    def test_workflow_prefixes_and_subheadings_are_not_counted(self):
        text = "## Workflow examples\n## Workflows\n### Workflow: subheading\nWorkflow: prose\n"
        self.assertEqual(0, workflow_count(text))

    def test_conservation_guards_detect_content_loss(self):
        original = "```python\nassert authorized is True\n```\n"
        self.assertNotEqual(fragments(original), fragments(original.replace("True", "False")))
        self.assertNotEqual(fragments(original), fragments(""))

    def test_partial_install_keeps_context_and_resource_rules_available(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, propagate_skills.main([directory, "--skills", "the-interdependency", "--apply"]))
            installed = Path(directory) / ".agents/skills/the-interdependency/SKILL.md"
            text = installed.read_text()
            self.assertIn("Child/sub-agents inherit", text)
            self.assertIn("Once a healthy run begins, let it finish", text)
            self.assertIn("edge cases, limitations", text)
            self.assertNotIn("](" + "../AGENTS.md", text)

    def test_partial_lifecycle_install_keeps_routed_skill_available(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, propagate_skills.main([directory, "--skills", "agent-instantiation", "--apply"]))
            installed = Path(directory) / ".agents/skills"
            expected = {"agent-instantiation", "wdll", "a0p-instancing"}
            self.assertEqual(expected, {path.parent.name for path in installed.glob("*/SKILL.md")})
            for name in expected:
                self.assertEqual((ROOT / name / "SKILL.md").read_bytes(),
                                 (installed / name / "SKILL.md").read_bytes())
            source = installed / "agent-instantiation/SKILL.md"
            self.assertIn("](../a0p-instancing/SKILL.md)", source.read_text())
            self.assertTrue((source.parent / "../a0p-instancing/SKILL.md").resolve().is_file())
            report = check_consumer_drift.check_consumer(Path(directory), canon_root=ROOT)
            _text, failed = check_consumer_drift.format_report(report, strict_sha=False, require_vendored=True)
            self.assertFalse(failed, _text)
            (installed / "a0p-instancing/SKILL.md").unlink()
            report = check_consumer_drift.check_consumer(Path(directory), canon_root=ROOT)
            text, failed = check_consumer_drift.format_report(report, strict_sha=False, require_vendored=True)
            self.assertTrue(failed, text)
            self.assertIn("a0p-instancing", text)
            self.assertIn("missing", text)


if __name__ == "__main__":
    unittest.main()

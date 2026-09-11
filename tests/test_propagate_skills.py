from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "propagate_skills", ROOT / "tools" / "propagate_skills.py"
)
ps = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = ps
_spec.loader.exec_module(ps)


class PropagateDoctrineTest(unittest.TestCase):
    def test_partial_refresh_preserves_local_skill_index_and_description(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            root = target / ".agents/skills"
            for name in ("hmmm", "test-build"):
                path = root / name / "SKILL.md"
                path.parent.mkdir(parents=True)
                path.write_text("owner-retained content\n", encoding="utf-8")
            local_entry = "- `hmmm/` — mandatory unresolved-constraint boundary object"
            (root / "README.md").write_text(local_entry + "\n", encoding="utf-8")
            for _ in range(2):
                self.assertEqual(ps.main([str(target), "--skills", "msdmd", "--apply"]), 0)
                readme = (root / "README.md").read_text(encoding="utf-8")
                self.assertEqual(readme.count(local_entry), 1)
                self.assertIn("- `test-build/`", readme)
                self.assertIn("not refreshed by this propagation", readme)
                self.assertEqual((root / "hmmm/SKILL.md").read_text(), "owner-retained content\n")

    def test_partial_refresh_uses_annotated_skill_prior_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            root = target / ".agents/skills"
            skill = root / "test-build" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("older canonical copy\n", encoding="utf-8")
            (root / "README.md").write_text(
                "# Local agent skills\n\n"
                "Source commit: `bbbbbbb`\n\n"
                "Other installed skills (not refreshed by this propagation):\n\n"
                "- `test-build/` [not refreshed; prior source: `aaaaaaa`]\n",
                encoding="utf-8",
            )
            with patch.object(ps, "current_sha", return_value="ccccccc"), patch.object(
                ps, "sync_tree", return_value=[]
            ) as sync:
                self.assertEqual(ps.main([str(target), "--skills", "test-build", "--apply"]), 0)
            self.assertEqual(sync.call_args.args[2], "aaaaaaa")

    def test_partial_refresh_preserves_explicitly_unknown_skill_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            root = target / ".agents/skills"
            skill = root / "test-build" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("unknown-origin copy\n", encoding="utf-8")
            (root / "README.md").write_text(
                "# Local agent skills\n\n"
                "Source commit: `bbbbbbb`\n\n"
                "Other installed skills (not refreshed by this propagation):\n\n"
                "- `test-build/` [not refreshed; prior source: `hmmm`]\n",
                encoding="utf-8",
            )
            with patch.object(ps, "current_sha", return_value="ccccccc"), patch.object(
                ps, "sync_tree", return_value=[]
            ) as sync:
                self.assertEqual(ps.main([str(target), "--skills", "test-build", "--apply"]), 0)
            self.assertIsNone(sync.call_args.args[2])

    def test_referenced_doctrine_helper_finds_link(self) -> None:
        # canonical msdmd/SKILL.md links to ../doctrine/msdmd-checks.md
        refs = ps.referenced_doctrine([ROOT / "msdmd"])
        self.assertIn("msdmd-checks.md", refs)

    def test_apply_carries_referenced_doctrine(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            rc = ps.main([str(target), "--skills", "msdmd", "test-build", "--apply"])
            self.assertEqual(rc, 0)
            doc = target / ".agents/skills" / "doctrine" / "msdmd-checks.md"
            self.assertTrue(doc.is_file(), "referenced doctrine doc must be carried alongside skills")
            self.assertEqual(doc.read_bytes(), (ROOT / "doctrine" / "msdmd-checks.md").read_bytes())

    def test_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            rc = ps.main([str(target), "--skills", "msdmd"])  # no --apply
            self.assertEqual(rc, 0)
            self.assertFalse((target / ".agents/skills").exists())

    def test_apply_removes_superseded_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            stale = target / ".agents/skills/gonal-morphology/SKILL.md"
            stale.parent.mkdir(parents=True)
            stale.write_text("stale doctrine\n", encoding="utf-8")

            rc = ps.main([str(target), "--skills", "gonol-build", "--apply"])

            self.assertEqual(rc, 0)
            self.assertFalse(stale.parent.exists())
            self.assertTrue((target / ".agents/skills/gonol-build/SKILL.md").is_file())

    def test_sync_preserves_local_additions_and_removes_proven_obsolete_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "canon" / "sample"
            dst = root / "consumer" / "sample"
            src.mkdir(parents=True)
            dst.mkdir(parents=True)
            (src / "SKILL.md").write_text("current\n", encoding="utf-8")
            (dst / "SKILL.md").write_text("prior\n", encoding="utf-8")
            (dst / "runner.py").write_text("local\n", encoding="utf-8")
            (dst / "obsolete.md").write_text("old canon\n", encoding="utf-8")

            def prior_blob(_sha: str, _skill: str, path: Path) -> bytes | None:
                return b"old canon\n" if path == Path("obsolete.md") else None

            with patch.object(ps, "previous_canonical_blob", side_effect=prior_blob):
                removed = ps.sync_tree(src, dst, "abc1234")

            self.assertEqual([Path("obsolete.md")], removed)
            self.assertEqual("current\n", (dst / "SKILL.md").read_text(encoding="utf-8"))
            self.assertEqual("local\n", (dst / "runner.py").read_text(encoding="utf-8"))
            self.assertFalse((dst / "obsolete.md").exists())


if __name__ == "__main__":
    unittest.main()
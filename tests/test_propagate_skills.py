from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "propagate_skills", ROOT / "tools" / "propagate_skills.py"
)
ps = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = ps
_spec.loader.exec_module(ps)


class PropagateDoctrineTest(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()

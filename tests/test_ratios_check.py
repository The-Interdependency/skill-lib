from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

RATIOS = Path(__file__).resolve().parents[1] / "ratios"
sys.path.insert(0, str(RATIOS))

import ratios_check as R  # noqa: E402


class RatiosCheckScopeTest(unittest.TestCase):
    def test_parser_language_support_does_not_create_false_ratio_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Main.java").write_text("class Main {}\n", encoding="utf-8")
            ratio = (
                "# ratios: loc_comments=hmmm imports_exports=hmmm "
                "calls_definitions=hmmm"
            )
            (root / "tool.py").write_text(
                f"{ratio}\nprint('ok')\n{ratio}\n",
                encoding="utf-8",
            )

            report = R.run(root)
            self.assertEqual([], report["gaps"])
            self.assertEqual(["Main.java"], report["outside_computer_scope"])
            self.assertEqual(0, R.main(["--root", str(root), "--strict"]))

    def test_annotated_non_python_ratios_remain_visible_but_unverified(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "Main.java"
            ratio = (
                "// ratios: loc_comments=1:1 imports_exports=0:0 "
                "calls_definitions=0:0"
            )
            path.write_text(f"{ratio}\nclass Main {{}}\n{ratio}\n", encoding="utf-8")

            report = R.run(path)
            self.assertEqual(1, report["covered"])
            self.assertEqual([], report["misplaced"])
            self.assertEqual(0, report["verified_count"])
            self.assertEqual(6, len(report["unverifiable"]))
            self.assertTrue(
                all(item["reason"] == "no named-form computer for .java" for item in report["unverifiable"])
            )

    def test_shebang_is_the_only_allowed_opening_preamble(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tool.py"
            ratio = (
                "# ratios: loc_comments=hmmm imports_exports=hmmm "
                "calls_definitions=hmmm"
            )
            path.write_text(
                f"#!/usr/bin/env python3\n{ratio}\nprint('ok')\n{ratio}\n",
                encoding="utf-8",
            )
            report = R.run(path)
            self.assertEqual([], report["misplaced"])
            self.assertEqual(6, report["pending_count"])

            path.write_text(
                f"#!/usr/bin/env python3\n\n{ratio}\nprint('ok')\n{ratio}\n",
                encoding="utf-8",
            )
            report = R.run(path)
            self.assertEqual(
                [{"file": "tool.py", "opening": False, "closing": True}],
                report["misplaced"],
            )


if __name__ == "__main__":
    unittest.main()

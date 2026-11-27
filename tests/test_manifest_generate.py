"""Regression tests for manifest/generate.py block splicing.

Usage guidance:
    python -m unittest discover -s tests -p 'test_manifest_generate.py'
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "manifest"))
import generate  # noqa: E402


class ManifestSpliceTests(unittest.TestCase):
    def test_replaces_a_well_formed_block(self) -> None:
        text = f"intro\n{generate.BEGIN}\nold\n{generate.END}\noutro\n"
        out = generate.splice(text, f"{generate.BEGIN}\nnew\n{generate.END}")
        self.assertEqual(f"intro\n{generate.BEGIN}\nnew\n{generate.END}\noutro\n", out)

    def test_rejects_end_marker_before_begin_marker(self) -> None:
        text = f"intro\n{generate.END}\nhand-written\n{generate.BEGIN}\noutro\n"
        with self.assertRaises(generate.ManifestError):
            generate.splice(text, f"{generate.BEGIN}\nnew\n{generate.END}")

    def test_appends_when_no_block_is_present(self) -> None:
        block = f"{generate.BEGIN}\nnew\n{generate.END}"
        self.assertEqual(f"intro\n\n{block}\n", generate.splice("intro\n", block))


if __name__ == "__main__":
    unittest.main()

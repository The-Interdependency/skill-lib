from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from msdmd.parsers.universal import (
    marker_for,
    parse_file,
    parse_ratios,
    parse_text,
    ratios_placement,
    walk_tree,
)


class UniversalParserTest(unittest.TestCase):
    def test_parse_single_block_with_multiple_entries(self) -> None:
        text = """# === CONTRACTS ===
# id: first_contract
#   given: a request
#   then: a response
#
# id: second_contract
#   given: another request
#   then: another response
# === END CONTRACTS ===
"""
        self.assertEqual(
            [
                {"id": "first_contract", "given": "a request", "then": "a response"},
                {"id": "second_contract", "given": "another request", "then": "another response"},
            ],
            parse_text(text, "CONTRACTS"),
        )

    def test_parse_all_matching_blocks_not_just_first(self) -> None:
        text = """# === DOCS ===
# id: first_docs
#   summary: first
# === END DOCS ===

# === DOCS ===
# id: second_docs
#   summary: second
# === END DOCS ===
"""
        self.assertEqual(
            [
                {"id": "first_docs", "summary": "first"},
                {"id": "second_docs", "summary": "second"},
            ],
            parse_text(text, "DOCS"),
        )

    def test_parse_typescript_comment_marker(self) -> None:
        text = """// === CAPABILITIES ===
// id: browser_opens_page
//   summary: opens a page
// === END CAPABILITIES ===
"""
        self.assertEqual(
            [{"id": "browser_opens_page", "summary": "opens a page"}],
            parse_text(text, "CAPABILITIES", marker="//"),
        )

    def test_parse_sql_comment_marker(self) -> None:
        text = """-- === BOUNDARIES ===
-- id: migration_writes_storage
--   storage_boundary: migration
-- === END BOUNDARIES ===
"""
        self.assertEqual(
            [{"id": "migration_writes_storage", "storage_boundary": "migration"}],
            parse_text(text, "BOUNDARIES", marker="--"),
        )

    def test_missing_block_returns_empty_list(self) -> None:
        self.assertEqual([], parse_text("# no block here\n", "CONTRACTS"))

    def test_marker_for_known_and_unknown_extensions(self) -> None:
        self.assertEqual("#", marker_for(Path("module.py")))
        self.assertEqual("//", marker_for(Path("module.ts")))
        self.assertEqual("--", marker_for(Path("module.sql")))
        self.assertIsNone(marker_for(Path("README.md")))

    def test_parse_file_uses_extension_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "module.ts"
            path.write_text(
                """// === OWNERS ===
// id: module_owner
//   owner: platform
// === END OWNERS ===
""",
                encoding="utf-8",
            )
            self.assertEqual(
                [{"id": "module_owner", "owner": "platform"}],
                parse_file(path, "OWNERS"),
            )

    def test_walk_tree_reports_annotated_and_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            annotated = root / "annotated.py"
            gap = root / "gap.py"
            skipped_dir = root / "node_modules"
            skipped_dir.mkdir()
            skipped = skipped_dir / "ignored.py"

            annotated.write_text(
                """# === DOCS ===
# id: module_doc
#   path: docs/module.md
# === END DOCS ===
""",
                encoding="utf-8",
            )
            gap.write_text("print('gap')\n", encoding="utf-8")
            skipped.write_text("print('ignored')\n", encoding="utf-8")

            annotated_files, gap_files = walk_tree(root, "DOCS")

            self.assertEqual([(annotated, [{"id": "module_doc", "path": "docs/module.md"}])], annotated_files)
            self.assertEqual([gap], gap_files)

    def test_parse_ratios_reads_single_line_declarations(self) -> None:
        text = (
            "# ratios: loc_comments=120:40 imports_exports=4:7 calls_definitions=50:10\n"
            '"""body"""\n'
            "x = 1\n"
            "# ratios: loc_comments=120:40 imports_exports=4:7 calls_definitions=50:10\n"
        )
        entries = parse_ratios(text, "#")
        # one entry per (line x ratio token): 2 lines x 3 ratios
        self.assertEqual(6, len(entries))
        self.assertEqual({"id": "loc_comments", "value": "120:40"}, entries[0])
        self.assertEqual((True, True), ratios_placement(text, "#"))

    def test_parse_ratios_detects_misplacement(self) -> None:
        text = "x = 1\n# ratios: loc_comments=1:0 imports_exports=0:0 calls_definitions=0:0\ny = 2\n"
        # present but on neither the first nor the last non-blank line
        self.assertEqual((False, False), ratios_placement(text, "#"))
        self.assertEqual(3, len(parse_ratios(text, "#")))


if __name__ == "__main__":
    unittest.main()

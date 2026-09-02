from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from msdmd.parsers.universal import (
    direct_execution_declaration,
    direct_execution_gaps,
    has_shebang,
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

    def test_walk_tree_skips_common_vcs_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            visible = root / "visible.py"
            visible.write_text("print('visible')\n", encoding="utf-8")
            hidden_files = []
            for dirname in (".git", ".hg", ".svn", ".jj"):
                metadata = root / dirname
                metadata.mkdir()
                hidden = metadata / "metadata.py"
                hidden.write_text("print('metadata')\n", encoding="utf-8")
                hidden_files.append(hidden)

            annotated_files, gap_files = walk_tree(root, "DOCS")

            self.assertEqual([], annotated_files)
            self.assertEqual([visible], gap_files)
            for hidden in hidden_files:
                self.assertNotIn(hidden, gap_files)

    def test_walk_tree_does_not_follow_directory_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside_tmp:
            root = Path(tmp)
            outside = Path(outside_tmp)
            external_source = outside / "outside.py"
            external_source.write_text("print('outside')\n", encoding="utf-8")
            link = root / "outside-link"
            try:
                link.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("directory symlinks unavailable on this platform")

            annotated_files, gap_files = walk_tree(root, "DOCS")

            self.assertEqual([], annotated_files)
            self.assertEqual([], gap_files)

    def test_typescript_walker_declares_same_source_boundary(self) -> None:
        source = (Path(__file__).resolve().parents[1] / "msdmd" / "parsers" / "universal.ts").read_text(encoding="utf-8")
        for vcs_dir in (".git", ".hg", ".svn", ".jj"):
            self.assertIn(f'"{vcs_dir}"', source)
        self.assertIn("lstatSync", source)
        self.assertIn("st.isSymbolicLink()", source)

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

    def test_parse_ratios_allows_line_one_shebang(self) -> None:
        text = (
            "#!/usr/bin/env bash\n"
            "# ratios: loc_comments=1:1 imports_exports=0:0 calls_definitions=0:0\n"
            "echo ok\n"
            "# ratios: loc_comments=1:1 imports_exports=0:0 calls_definitions=0:0\n"
        )
        self.assertEqual((True, True), ratios_placement(text, "#"))
        self.assertEqual(6, len(parse_ratios(text, "#")))

    def test_parse_ratios_rejects_gap_after_shebang(self) -> None:
        text = (
            "#!/usr/bin/env bash\n"
            "\n"
            "# ratios: loc_comments=1:1 imports_exports=0:0 calls_definitions=0:0\n"
            "echo ok\n"
            "# ratios: loc_comments=1:1 imports_exports=0:0 calls_definitions=0:0\n"
        )
        self.assertEqual((False, True), ratios_placement(text, "#"))

    def test_parse_ratios_detects_misplacement(self) -> None:
        text = "x = 1\n# ratios: loc_comments=1:0 imports_exports=0:0 calls_definitions=0:0\ny = 2\n"
        # present but on neither the opening nor the last non-blank line
        self.assertEqual((False, False), ratios_placement(text, "#"))
        self.assertEqual(3, len(parse_ratios(text, "#")))

    def test_direct_execution_declaration_and_shebang_close(self) -> None:
        text = """#!/usr/bin/env bash
# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm
# === CAPABILITIES ===
# id: ai_session_launcher
#   summary: launches persistent agent sessions
#   exposes: command:ai
#   executable: true
# === END CAPABILITIES ===
# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm
"""
        self.assertTrue(has_shebang(text))
        self.assertEqual((True, False), direct_execution_declaration(text, "#"))
        self.assertEqual([], direct_execution_gaps(text, "#"))

    def test_direct_execution_claim_without_shebang_fails(self) -> None:
        text = """# === CONTRACTS ===
# id: launcher_direct_exec
#   given: the module is invoked directly
#   then: the declared interpreter executes it
#   executable: true
# === END CONTRACTS ===
"""
        self.assertEqual(
            ["declared_direct_execution_missing_shebang"],
            direct_execution_gaps(text, "#"),
        )

    def test_shebang_without_positive_declaration_is_gap(self) -> None:
        text = """#!/usr/bin/env bash
# === CAPABILITIES ===
# id: launcher_intent_pending
#   summary: direct execution intent is unresolved
#   exposes: command:ai
#   executable: hmmm
# === END CAPABILITIES ===
"""
        self.assertEqual((False, True), direct_execution_declaration(text, "#"))
        self.assertEqual(
            ["shebang_missing_direct_execution_declaration"],
            direct_execution_gaps(text, "#"),
        )


if __name__ == "__main__":
    unittest.main()

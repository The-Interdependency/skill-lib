# === CHECKS ===
# id: check_msdmd_python_numeric_field_contract
#   proves: msdmd_python_parser_preserves_field_names
#   call: self::test_parser_field_contract
#   requires: python3
#   timeout: 10
#   mutates: filesystem
#   cleanup: tempdir_teardown
# === END CHECKS ===
from __future__ import annotations

import re
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from msdmd.parsers.universal import (
    COMMENT_MARKERS,
    marker_for,
    parse_file,
    parse_ratios,
    parse_text,
    ratios_placement,
    walk_tree,
)

ROOT = Path(__file__).resolve().parents[1]


def test_parser_field_contract() -> None:
    """No-argument CHECKS witness, also executed by the unittest suite."""
    checks = unittest.TestCase()
    helper = ROOT / "msdmd/parsers/universal.py"
    module = parse_file(helper, "MODULE_BUILD")[0]
    checks.assertEqual("msdmd_python_reference_parser", module["id"])
    checks.assertIn("COMMENT_MARKERS", module["public_surface"].split(", "))
    checks.assertEqual("read", module["storage_boundary"])
    checks.assertEqual("read", module["user_data_boundary"])
    checks.assertEqual("msdmd_python_parser_preserves_field_names", parse_file(helper, "CONTRACTS")[0]["id"])
    with tempfile.TemporaryDirectory() as directory:
        marker = Path(directory) / "executed"
        source = Path(directory) / "inspected.py"
        text = "# === NARRATIVE ===\n# id: source_bound_narrative\n#   evidence_sha256: abc123\n# === END NARRATIVE ===\n"
        source.write_text(text + "from pathlib import Path\n" + f"Path({str(marker)!r}).write_text('executed')\n")
        expected = [{"id": "source_bound_narrative", "evidence_sha256": "abc123"}]
        checks.assertEqual(expected, parse_text(text, "NARRATIVE"))
        checks.assertEqual(expected, parse_file(source, "NARRATIVE"))
        checks.assertFalse(marker.exists(), "parsing executed inspected source")


# === CHECKS ===
# id: check_msdmd_typescript_numeric_field_contract
#   proves: msdmd_typescript_parser_preserves_field_names
#   call: self::test_typescript_parser_field_contract
#   requires: python3, node24
#   timeout: 10
#   mutates: filesystem
#   cleanup: tempdir_teardown
# === END CHECKS ===


def test_typescript_parser_field_contract() -> None:
    """Execute the actual TypeScript parser using Node's native type stripping."""
    checks = unittest.TestCase()
    helper = ROOT / "msdmd/parsers/universal.ts"
    module = parse_file(helper, "MODULE_BUILD")[0]
    checks.assertEqual("msdmd_typescript_reference_parser", module["id"])
    checks.assertEqual("msdmd_typescript_parser_preserves_field_names", parse_file(helper, "CONTRACTS")[0]["id"])
    with tempfile.TemporaryDirectory() as directory:
        marker = Path(directory) / "executed"
        source = Path(directory) / "inspected.ts"
        text = "// === NARRATIVE ===\n// id: source_bound_narrative\n//   evidence_sha256: abc123\n// === END NARRATIVE ===\n"
        source.write_text(text + 'import {writeFileSync} from "node:fs";\n' + f'writeFileSync({json.dumps(str(marker))}, "executed");\n')
        script = f"import {{parseText, parseFile}} from {json.dumps(helper.as_uri())};" + f"process.stdout.write(JSON.stringify([parseText({json.dumps(text)}, 'NARRATIVE', '//'),parseFile({json.dumps(str(source))}, 'NARRATIVE')]));"
        result = subprocess.run(["node", "--input-type=module", "--eval", script], check=True, capture_output=True, text=True)
        expected = [{"id": "source_bound_narrative", "evidence_sha256": "abc123"}]
        checks.assertEqual([expected, expected], json.loads(result.stdout))
        checks.assertFalse(marker.exists(), "TypeScript parsing executed inspected source")


class UniversalParserTest(unittest.TestCase):
    def test_typescript_numeric_field_contract(self) -> None:
        test_typescript_parser_field_contract()

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

    def test_parse_numeric_snake_case_field(self) -> None:
        test_parser_field_contract()

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
        self.assertEqual("#", marker_for(Path("module.pl")))
        self.assertEqual("//", marker_for(Path("module.ts")))
        self.assertEqual("//", marker_for(Path("module.c+")))
        self.assertEqual("//", marker_for(Path("module.c++")))
        self.assertEqual("//", marker_for(Path("module.java")))
        self.assertEqual("--", marker_for(Path("module.sql")))
        self.assertEqual("%", marker_for(Path("module.erl")))
        self.assertEqual(";", marker_for(Path("module.clj")))
        self.assertEqual("!", marker_for(Path("module.f90")))
        self.assertEqual("'", marker_for(Path("module.vb")))
        self.assertEqual("*>", marker_for(Path("module.cob")))
        # .m is ambiguous between Objective-C and MATLAB/Octave. Extension-only
        # detection must not guess; callers can use parse_text with a marker.
        self.assertIsNone(marker_for(Path("module.m")))
        self.assertIsNone(marker_for(Path("README.md")))

    def test_python_and_typescript_comment_marker_registries_match(self) -> None:
        source = (ROOT / "msdmd" / "parsers" / "universal.ts").read_text(encoding="utf-8")
        body = source.split("export const COMMENT_MARKERS", 1)[1].split("};", 1)[0]
        typescript_markers = dict(re.findall(r'"(\.[^"]+)":\s*"([^"]+)"', body))
        self.assertEqual(COMMENT_MARKERS, typescript_markers)

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

    def test_parse_file_supports_additional_language_comment_families(self) -> None:
        examples = {
            "module.pl": "#",
            "module.c+": "//",
            "module.c++": "//",
            "module.cpp": "//",
            "module.java": "//",
            "module.erl": "%",
            "module.clj": ";",
            "module.f90": "!",
            "module.vb": "'",
            "module.cob": "*>",
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for filename, marker in examples.items():
                with self.subTest(filename=filename):
                    path = root / filename
                    path.write_text(
                        f"{marker} === CAPABILITIES ===\n"
                        f"{marker} id: portable_metadata\n"
                        f"{marker}   summary: parses beside its owner\n"
                        f"{marker} === END CAPABILITIES ===\n",
                        encoding="utf-8",
                    )
                    self.assertEqual(
                        [{"id": "portable_metadata", "summary": "parses beside its owner"}],
                        parse_file(path, "CAPABILITIES"),
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

    def test_parse_ratios_allows_valid_line_one_shebang(self) -> None:
        text = (
            "#!/usr/bin/env perl\n"
            "# ratios: loc_comments=1:1 imports_exports=0:0 calls_definitions=0:0\n"
            "print qq(ok);\n"
            "# ratios: loc_comments=1:1 imports_exports=0:0 calls_definitions=0:0\n"
        )
        self.assertEqual((True, True), ratios_placement(text, "#"))

    def test_parse_ratios_allows_node_shebang_before_slash_marker(self) -> None:
        text = (
            "#!/usr/bin/env node\n"
            "// ratios: loc_comments=1:1 imports_exports=0:0 calls_definitions=0:0\n"
            "console.log('ok');\n"
            "// ratios: loc_comments=1:1 imports_exports=0:0 calls_definitions=0:0\n"
        )
        self.assertEqual((True, True), ratios_placement(text, "//"))

    def test_parse_ratios_rejects_invalid_or_gapped_shebang_preamble(self) -> None:
        ratio = "# ratios: loc_comments=1:1 imports_exports=0:0 calls_definitions=0:0"
        self.assertEqual(
            (False, True),
            ratios_placement(f"#!\n{ratio}\nprint('ok')\n{ratio}\n", "#"),
        )
        self.assertEqual(
            (False, True),
            ratios_placement(
                f"#!/usr/bin/env python3\n\n{ratio}\nprint('ok')\n{ratio}\n",
                "#",
            ),
        )
        self.assertEqual(
            (False, True),
            ratios_placement(
                f"{ratio}\n#!/usr/bin/env python3\nprint('ok')\n{ratio}\n",
                "#",
            ),
        )

    def test_parse_ratios_detects_misplacement(self) -> None:
        text = "x = 1\n# ratios: loc_comments=1:0 imports_exports=0:0 calls_definitions=0:0\ny = 2\n"
        # present but on neither the first nor the last non-blank line
        self.assertEqual((False, False), ratios_placement(text, "#"))
        self.assertEqual(3, len(parse_ratios(text, "#")))


if __name__ == "__main__":
    unittest.main()
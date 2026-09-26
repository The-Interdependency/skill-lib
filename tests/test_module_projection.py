# ratios: loc_comments=97:629 imports_exports=9:11 calls_definitions=316:41
# === CHECKS ===
# id: check_module_projection_line_shift_stability
#   proves: module_projection_line_shift_stability
#   call: self::test_line_insertions_preserve_symbol_identity_and_attachment
#   requires: python3
#   timeout: 10
#   mutates: filesystem
#   cleanup: tempdir_teardown
#
# id: check_module_projection_never_executes_source
#   proves: module_projection_never_executes_source
#   call: self::test_projection_does_not_execute_inspected_source
#   requires: python3
#   timeout: 10
#   mutates: filesystem
#   cleanup: tempdir_teardown
#
# id: check_module_projection_freshness_binds_source_and_reader
#   proves: module_projection_freshness_binds_source_and_reader
#   call: self::test_freshness_key_changes_with_source_or_reader
#   requires: python3
#   timeout: 10
#   mutates: filesystem
#   cleanup: tempdir_teardown
# === END CHECKS ===
"""Tests for deterministic Python module metadata projections.

Usage: ``python -m unittest tests.test_module_projection``.
"""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from msdmd.module_projection import (
    SCHEMA_ID,
    _signature,
    check_projections,
    project_python_module,
    project_tree,
    render_jsonl,
    write_projections,
)


def _metadata_subjects(records: list[dict]) -> dict[str, tuple[str, str]]:
    return {
        record["text"]: (record["subject"], record["attachment"])
        for record in records
        if record["record_type"] == "metadata"
    }


def _symbol_ids(records: list[dict]) -> dict[str, str]:
    return {
        record["qualified_name"]: record["id"]
        for record in records
        if record["record_type"] == "symbol"
    }


class ModuleProjectionTests(unittest.TestCase):
    def test_structural_comment_attachment_uses_leading_and_enclosing_owners(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "module.py"
            source.write_text(
                '''# module header

# public function purpose
def public(value: int) -> int:
    """Return the supplied value."""
    # inside public
    return value

def outer():
    # nested purpose
    def inner():
        return 1
    # after nested definition
    return inner()
''',
                encoding="utf-8",
            )

            records = project_python_module(source, root=root, repo="example/repo")
            symbols = _symbol_ids(records)
            metadata = _metadata_subjects(records)

            self.assertEqual(
                ("python:example/repo:module.py::<module>", "module_scope"),
                metadata["module header"],
            )
            self.assertEqual(
                (symbols["public"], "leading_trivia"),
                metadata["public function purpose"],
            )
            self.assertEqual(
                (symbols["public"], "nearest_enclosing_symbol"),
                metadata["inside public"],
            )
            self.assertEqual(
                (symbols["outer.inner"], "leading_trivia"),
                metadata["nested purpose"],
            )
            self.assertEqual(
                (symbols["outer"], "nearest_enclosing_symbol"),
                metadata["after nested definition"],
            )
            self.assertEqual(
                (symbols["public"], "native_docstring"),
                metadata["Return the supplied value."],
            )

    def test_line_insertions_preserve_symbol_identity_and_attachment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "module.py"
            original = '''# purpose
def compute(value: int) -> int:
    # implementation note
    return value * 2
'''
            shifted = '''


# purpose
def compute(value: int) -> int:

    # implementation note
    return value * 2
'''
            source.write_text(original, encoding="utf-8")
            before = project_python_module(source, root=root, repo="example/repo")
            source.write_text(shifted, encoding="utf-8")
            after = project_python_module(source, root=root, repo="example/repo")

            self.assertEqual(_symbol_ids(before), _symbol_ids(after))
            for text in ("purpose", "implementation note"):
                self.assertEqual(_metadata_subjects(before)[text], _metadata_subjects(after)[text])
            before_symbol = next(record for record in before if record["record_type"] == "symbol")
            after_symbol = next(record for record in after if record["record_type"] == "symbol")
            self.assertNotEqual(
                before_symbol["source_span"]["start"]["line"],
                after_symbol["source_span"]["start"]["line"],
            )

    def test_decorator_and_method_leading_comments_attach_to_the_declaration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "module.py"
            source.write_text(
                '''def marker(value):
    return value

# decorated purpose
@marker
def decorated():
    return None

class Example:
    # method purpose
    async def method(self):
        return None
''',
                encoding="utf-8",
            )
            records = project_python_module(source, root=root, repo="example/repo")
            symbols = _symbol_ids(records)
            metadata = _metadata_subjects(records)

            self.assertEqual((symbols["decorated"], "leading_trivia"), metadata["decorated purpose"])
            self.assertEqual((symbols["Example.method"], "leading_trivia"), metadata["method purpose"])
            decorated = next(
                record
                for record in records
                if record.get("qualified_name") == "decorated"
            )
            self.assertEqual(5, decorated["source_span"]["start"]["line"])

    def test_definitions_inside_control_flow_keep_their_lexical_owner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "module.py"
            source.write_text(
                '''def outer(enabled):
    if enabled:
        # conditional helper
        def helper():
            return True
    return helper
''',
                encoding="utf-8",
            )

            records = project_python_module(source, root=root, repo="example/repo")
            symbols = _symbol_ids(records)
            metadata = _metadata_subjects(records)
            helper = next(
                record
                for record in records
                if record.get("qualified_name") == "outer.helper"
            )

            self.assertEqual(symbols["outer"], helper["parent"])
            self.assertEqual(
                (symbols["outer.helper"], "leading_trivia"),
                metadata["conditional helper"],
            )

    def test_definitions_inside_match_cases_and_except_handlers_are_discovered(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "module.py"
            source.write_text(
                '''def outer(value):
    match value:
        case 1:
            # match helper
            def matched():
                return True
    try:
        raise ValueError
    except ValueError:
        # exception helper
        def handled():
            return False
    return matched, handled
''',
                encoding="utf-8",
            )

            records = project_python_module(source, root=root, repo="example/repo")
            symbols = _symbol_ids(records)
            metadata = _metadata_subjects(records)

            self.assertIn("outer.matched", symbols)
            self.assertIn("outer.handled", symbols)
            self.assertEqual(
                (symbols["outer.matched"], "leading_trivia"),
                metadata["match helper"],
            )
            self.assertEqual(
                (symbols["outer.handled"], "leading_trivia"),
                metadata["exception helper"],
            )

    def test_trailing_suite_comments_remain_on_the_lexical_owner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "module.py"
            source.write_text(
                '''def function():
    value = 1
    # trailing invariant

# module note
''',
                encoding="utf-8",
            )

            records = project_python_module(source, root=root, repo="example/repo")
            symbols = _symbol_ids(records)
            metadata = _metadata_subjects(records)

            self.assertEqual(
                (symbols["function"], "nearest_enclosing_symbol"),
                metadata["trailing invariant"],
            )
            self.assertEqual(
                (records[0]["module_id"], "module_scope"),
                metadata["module note"],
            )

    def test_special_file_conventions_remain_module_scoped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "module.py"
            source.write_text(
                '''# ratios: loc_comments=1:1 imports_exports=0:0 calls_definitions=0:1
# === DOCS ===
# id: module_docs
#   summary: module documentation
# === END DOCS ===
def function():
    return None
''',
                encoding="utf-8",
            )
            records = project_python_module(source, root=root, repo="example/repo")
            module_id = records[0]["module_id"]
            special = [
                record
                for record in records
                if record["record_type"] == "metadata"
                and record["metadata_kind"] in {"msdmd_ratios", "msdmd_block"}
            ]
            self.assertEqual(2, len(special))
            self.assertTrue(all(record["subject"] == module_id for record in special))
            self.assertTrue(all(record["attachment"] == "module_convention" for record in special))

    def test_interrupted_and_unclosed_msdmd_fences_emit_diagnostics(self) -> None:
        cases = {
            "interrupted": (
                "# === DOCS ===\nvalue = 1\n# id: later\n# === END DOCS ===\n",
                "msdmd_fence_interrupted",
            ),
            "unclosed": (
                "# === DOCS ===\n# id: unfinished\n",
                "msdmd_fence_unclosed",
            ),
        }
        for name, (text, code) in cases.items():
            with self.subTest(case=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                source = root / "module.py"
                source.write_text(text, encoding="utf-8")

                records = project_python_module(source, root=root, repo="example/repo")
                diagnostics = [
                    record for record in records if record["record_type"] == "diagnostic"
                ]
                blocks = [
                    record["text"]
                    for record in records
                    if record["record_type"] == "metadata"
                    and record["metadata_kind"] == "msdmd_block"
                ]

                self.assertEqual("invalid", records[0]["status"])
                self.assertIn(code, {record["code"] for record in diagnostics})
                self.assertFalse(
                    any("=== DOCS ===" in block and "=== END DOCS ===" in block for block in blocks)
                )

    def test_only_python_recognized_encoding_cookie_is_module_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "module.py"
            source.write_text(
                "value = 1\n"
                "# coding: this is a design note\n"
                "def function():\n"
                "    return value\n",
                encoding="utf-8",
            )

            records = project_python_module(source, root=root, repo="example/repo")
            symbols = _symbol_ids(records)
            metadata = _metadata_subjects(records)

            self.assertEqual(
                (symbols["function"], "leading_trivia"),
                metadata["coding: this is a design note"],
            )
            self.assertNotIn(
                "encoding_cookie",
                {
                    record.get("metadata_kind")
                    for record in records
                    if record["record_type"] == "metadata"
                },
            )

    def test_generic_type_parameters_are_rendered_in_signatures(self) -> None:
        function = ast.parse("def ident(value: T) -> T:\n    return value\n").body[0]
        function.type_params = [ast.Name(id="T")]
        generic_class = ast.parse("class Box:\n    pass\n").body[0]
        generic_class.type_params = [ast.Name(id="T")]

        self.assertEqual("def ident[T](value: T) -> T", _signature(function)[0])
        self.assertEqual("class Box[T]", _signature(generic_class)[0])

    def test_projection_does_not_execute_inspected_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker = root / "executed"
            source = root / "module.py"
            source.write_text(
                "from pathlib import Path\n"
                f"Path({str(marker)!r}).write_text('executed')\n"
                "def safe():\n"
                "    return True\n",
                encoding="utf-8",
            )

            records = project_python_module(source, root=root, repo="example/repo")

            self.assertEqual("complete", records[0]["status"])
            self.assertFalse(marker.exists())

    def test_freshness_key_changes_with_source_or_reader(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "module.py"
            source.write_text("def value():\n    return 1\n", encoding="utf-8")
            first = project_python_module(source, root=root, repo="example/repo")[0]
            source.write_text("def value():\n    return 2\n", encoding="utf-8")
            changed_source = project_python_module(source, root=root, repo="example/repo")[0]
            with mock.patch("msdmd.module_projection._reader_sha256", return_value="f" * 64):
                changed_reader = project_python_module(source, root=root, repo="example/repo")[0]
            with mock.patch(
                "msdmd.module_projection._runtime_identity",
                return_value={
                    "python_implementation": "test-python",
                    "python_version": "99.0.0",
                    "ast_feature_version": "99.0",
                },
            ):
                changed_runtime = project_python_module(source, root=root, repo="example/repo")[0]
            changed_revision = project_python_module(
                source,
                root=root,
                repo="example/repo",
                revision="revision-two",
            )[0]

            self.assertNotEqual(first["freshness_key_sha256"], changed_source["freshness_key_sha256"])
            self.assertNotEqual(
                changed_source["freshness_key_sha256"],
                changed_reader["freshness_key_sha256"],
            )
            self.assertNotEqual(
                changed_source["freshness_key_sha256"],
                changed_runtime["freshness_key_sha256"],
            )
            self.assertNotEqual(
                changed_source["freshness_key_sha256"],
                changed_revision["freshness_key_sha256"],
            )
            self.assertEqual("revision-two", changed_revision["source_revision"])
            self.assertEqual("utf-8", changed_revision["source_encoding"])
            self.assertEqual([], changed_revision["hmmm"])
            self.assertRegex(changed_revision["python_version"], r"^\d+\.\d+\.\d+$")
            self.assertRegex(changed_revision["ast_feature_version"], r"^\d+\.\d+$")
            msdmd_dir = Path(__file__).resolve().parents[1] / "msdmd"
            self.assertEqual(
                hashlib.sha256((msdmd_dir / "module-projection.schema.json").read_bytes()).hexdigest(),
                changed_revision["schema_sha256"],
            )
            self.assertEqual(
                hashlib.sha256((msdmd_dir / "python-module-reader.json").read_bytes()).hexdigest(),
                changed_revision["reader_manifest_sha256"],
            )

    def test_render_and_freshness_check_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            out = Path(tmp) / "generated"
            root.mkdir()
            (root / "a.py").write_text("def a():\n    return 1\n", encoding="utf-8")
            projections = project_tree(root, "example/repo")

            written = write_projections(out, projections)

            self.assertEqual([out / "a.py.msdmd.jsonl"], written)
            self.assertEqual([], check_projections(out, projections))
            records = [json.loads(line) for line in written[0].read_text(encoding="utf-8").splitlines()]
            self.assertEqual(SCHEMA_ID, records[0]["schema"])
            self.assertEqual(render_jsonl(records), written[0].read_text(encoding="utf-8"))

            (root / "a.py").write_text("def a():\n    return 2\n", encoding="utf-8")
            stale = project_tree(root, "example/repo")
            self.assertEqual(["stale:a.py.msdmd.jsonl"], check_projections(out, stale))

    def test_corrupt_non_utf8_sidecar_is_stale_and_repairable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            out = Path(tmp) / "generated"
            root.mkdir()
            (root / "a.py").write_text("def a():\n    return 1\n", encoding="utf-8")
            projections = project_tree(root, "example/repo")
            target = write_projections(out, projections)[0]
            target.write_bytes(b"\xff\xfe corrupt")

            self.assertEqual(
                ["stale:a.py.msdmd.jsonl"],
                check_projections(out, projections),
            )
            write_projections(out, projections)
            self.assertEqual(projections["a.py.msdmd.jsonl"].encode("utf-8"), target.read_bytes())

    def test_selected_write_and_check_do_not_prune_or_reject_other_modules(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            out = Path(tmp) / "generated"
            root.mkdir()
            first = root / "a.py"
            second = root / "b.py"
            first.write_text("def a():\n    return 1\n", encoding="utf-8")
            second.write_text("def b():\n    return 2\n", encoding="utf-8")
            write_projections(out, project_tree(root, "example/repo"), prune=True)

            first.write_text("def a():\n    return 3\n", encoding="utf-8")
            selected = project_tree(root, "example/repo", sources=[first])
            write_projections(out, selected)

            self.assertTrue((out / "b.py.msdmd.jsonl").exists())
            self.assertEqual([], check_projections(out, selected))
            self.assertEqual(
                ["unexpected:b.py.msdmd.jsonl"],
                check_projections(out, selected, check_unexpected=True),
            )

    def test_projection_paths_cannot_escape_the_output_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "generated"
            projections = {"../escaped.msdmd.jsonl": "{}\n"}

            with self.assertRaisesRegex(ValueError, "escapes output directory"):
                write_projections(out, projections)
            with self.assertRaisesRegex(ValueError, "escapes output directory"):
                check_projections(out, projections)
            self.assertFalse((Path(tmp) / "escaped.msdmd.jsonl").exists())

    def test_unicode_ast_columns_are_normalized_to_character_and_byte_offsets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "module.py"
            source.write_text('def value(name="café"):\n    return name\n', encoding="utf-8")

            symbol = next(
                record
                for record in project_python_module(source, root=root, repo="example/repo")
                if record["record_type"] == "symbol"
            )
            end = symbol["source_span"]["end"]

            self.assertEqual(len("    return name"), end["column"])
            self.assertEqual(len(source.read_bytes()) - 1, end["byte"])

    def test_invalid_python_is_visible_and_fails_freshness_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            out = Path(tmp) / "generated"
            root.mkdir()
            source = root / "broken.py"
            source.write_text("def broken(:\n", encoding="utf-8")

            records = project_python_module(source, root=root, repo="example/repo")
            projections = {"broken.py.msdmd.jsonl": render_jsonl(records)}
            write_projections(out, projections)

            self.assertEqual("invalid", records[0]["status"])
            self.assertEqual("diagnostic", records[1]["record_type"])
            self.assertEqual(
                ["invalid:broken.py.msdmd.jsonl"],
                check_projections(out, projections),
            )

    def test_write_emits_exact_lf_utf8_bytes_and_repairs_crlf_sidecars(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            out = Path(tmp) / "generated"
            root.mkdir()
            (root / "a.py").write_text(
                "# café note\ndef a():\n    return 1\n",
                encoding="utf-8",
            )
            projections = project_tree(root, "example/repo")
            expected = projections["a.py.msdmd.jsonl"].encode("utf-8")
            real_named_temporary_file = tempfile.NamedTemporaryFile

            def windows_text_translation(*args, **kwargs):
                # Simulate Windows text-mode newline translation: any text-mode
                # writer that does not disable translation emits CRLF.
                mode = kwargs.get("mode", args[0] if args else "w+b")
                if "b" not in mode and kwargs.get("newline") is None:
                    kwargs["newline"] = "\r\n"
                return real_named_temporary_file(*args, **kwargs)

            with mock.patch(
                "msdmd.module_projection.tempfile.NamedTemporaryFile",
                side_effect=windows_text_translation,
            ):
                target = write_projections(out, projections)[0]

            self.assertEqual(expected, target.read_bytes())
            self.assertNotIn(b"\r", target.read_bytes())
            self.assertEqual([], check_projections(out, projections))

            target.write_bytes(expected.replace(b"\n", b"\r\n"))
            self.assertEqual(["stale:a.py.msdmd.jsonl"], check_projections(out, projections))
            with mock.patch(
                "msdmd.module_projection.tempfile.NamedTemporaryFile",
                side_effect=windows_text_translation,
            ):
                write_projections(out, projections)
            self.assertEqual(expected, target.read_bytes())
            self.assertEqual([], check_projections(out, projections))

    def test_decorator_region_comments_attach_to_the_decorated_symbol(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "module.py"
            source.write_text(
                """def first(value):
    return value

def second(*args):
    return lambda value: value

# before decorators
@first
# between decorators
@second(
    # inside decorator expression
    1,
)  # trailing decorator
def decorated():
    return None

class Example:
    # before method decorator
    @staticmethod
    # between method decorator and def
    def method():
        return None
""",
                encoding="utf-8",
            )
            records = project_python_module(source, root=root, repo="example/repo")
            symbols = _symbol_ids(records)
            metadata = _metadata_subjects(records)

            self.assertEqual("complete", records[0]["status"])
            self.assertEqual(
                (symbols["decorated"], "leading_trivia"),
                metadata["before decorators"],
            )
            for text in (
                "between decorators",
                "inside decorator expression",
                "trailing decorator",
            ):
                with self.subTest(comment=text):
                    self.assertEqual(
                        (symbols["decorated"], "nearest_enclosing_symbol"),
                        metadata[text],
                    )
            self.assertEqual(
                (symbols["Example.method"], "leading_trivia"),
                metadata["before method decorator"],
            )
            self.assertEqual(
                (symbols["Example.method"], "nearest_enclosing_symbol"),
                metadata["between method decorator and def"],
            )

    def test_mismatched_msdmd_fences_emit_diagnostics_and_invalidate(self) -> None:
        cases = {
            "closing_name_differs": (
                "# === DOCS ===\n# id: entry\n# === END CHECKS ===\n",
                "msdmd_fence_mismatched",
            ),
            "opening_inside_open_block": (
                "# === DOCS ===\n# === CHECKS ===\n# id: entry\n# === END CHECKS ===\n",
                "msdmd_fence_mismatched",
            ),
            "closing_without_opening": (
                "value = 1\n# === END DOCS ===\n",
                "msdmd_fence_unmatched_close",
            ),
        }
        for name, (text, code) in cases.items():
            with self.subTest(case=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / "repo"
                out = Path(tmp) / "generated"
                root.mkdir()
                (root / "module.py").write_text(text, encoding="utf-8")

                records = project_python_module(root / "module.py", root=root, repo="example/repo")
                codes = {
                    record["code"] for record in records if record["record_type"] == "diagnostic"
                }

                self.assertEqual("invalid", records[0]["status"])
                self.assertIn(code, codes)
                self.assertIn("MSDMD comment fence is malformed", records[0]["hmmm"])
                projections = project_tree(root, "example/repo")
                write_projections(out, projections)
                self.assertEqual(
                    ["invalid:module.py.msdmd.jsonl"],
                    check_projections(out, projections),
                )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "module.py").write_text(
                "# === DOCS ===\n# id: entry\n# === END DOCS ===\n",
                encoding="utf-8",
            )
            records = project_python_module(root / "module.py", root=root, repo="example/repo")
            self.assertEqual("complete", records[0]["status"])
            self.assertFalse(any(record["record_type"] == "diagnostic" for record in records))

    def test_unicode_line_separators_do_not_split_python_source_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            out = Path(tmp) / "generated"
            root.mkdir()
            source = root / "module.py"
            source.write_bytes(
                'NOTE = "a\u2028b\u2029c\x85d\x0ce\x1cf"  # sep\u2028note\n'
                "\n"
                "def after():\n"
                "    # inside after\n"
                "    return 1\n".encode("utf-8")
            )
            raw = source.read_bytes()

            records = project_python_module(source, root=root, repo="example/repo")
            symbol = next(record for record in records if record.get("qualified_name") == "after")
            inside = next(record for record in records if record.get("text") == "inside after")
            trailing = next(record for record in records if record.get("text") == "sep\u2028note")

            self.assertEqual("complete", records[0]["status"])
            self.assertEqual(3, symbol["source_span"]["start"]["line"])
            self.assertEqual(raw.index(b"def after"), symbol["source_span"]["start"]["byte"])
            self.assertEqual(len(raw) - 1, symbol["source_span"]["end"]["byte"])
            self.assertEqual(4, inside["source_span"]["start"]["line"])
            self.assertEqual(raw.index(b"# inside after"), inside["source_span"]["start"]["byte"])
            self.assertEqual(symbol["id"], inside["subject"])
            self.assertEqual(1, trailing["source_span"]["start"]["line"])
            self.assertEqual(raw.index(b"# sep"), trailing["source_span"]["start"]["byte"])

            projections = project_tree(root, "example/repo")
            write_projections(out, projections)
            self.assertEqual([], check_projections(out, projections))

    def test_cr_only_source_keeps_offsets_attachment_and_convergence(self) -> None:
        text = (
            "#!/usr/bin/env python\r"
            "# -*- coding: utf-8 -*-\r"
            "# lead for f\r"
            "def f(x):\r"
            "    # inside f\r"
            "    return x\r"
            "\r"
            "class C:\r"
            "    @staticmethod\r"
            "    # between\r"
            "    def m():\r"
            "        return 1\r"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            out = Path(tmp) / "generated"
            root.mkdir()
            source = root / "module.py"
            source.write_bytes(text.encode("utf-8"))
            raw = source.read_bytes()

            records = project_python_module(source, root=root, repo="example/repo")
            symbols = _symbol_ids(records)
            metadata = _metadata_subjects(records)
            by_text = {
                record["text"]: record for record in records if record["record_type"] == "metadata"
            }
            function = next(record for record in records if record.get("qualified_name") == "f")
            method = next(record for record in records if record.get("qualified_name") == "C.m")

            self.assertEqual("complete", records[0]["status"])
            self.assertEqual("encoding_cookie", by_text["-*- coding: utf-8 -*-"]["metadata_kind"])
            self.assertEqual(2, by_text["-*- coding: utf-8 -*-"]["source_span"]["start"]["line"])
            self.assertEqual((symbols["f"], "leading_trivia"), metadata["lead for f"])
            self.assertEqual((symbols["f"], "nearest_enclosing_symbol"), metadata["inside f"])
            self.assertEqual((symbols["C.m"], "nearest_enclosing_symbol"), metadata["between"])
            self.assertEqual(4, function["source_span"]["start"]["line"])
            self.assertEqual(raw.index(b"def f"), function["source_span"]["start"]["byte"])
            self.assertEqual(raw.index(b"    @staticmethod") + 4, method["source_span"]["start"]["byte"])
            self.assertEqual(len(raw) - 1, method["source_span"]["end"]["byte"])
            for comment, needle in (("inside f", b"# inside f"), ("between", b"# between")):
                with self.subTest(comment=comment):
                    self.assertEqual(
                        raw.index(needle),
                        by_text[comment]["source_span"]["start"]["byte"],
                    )

            projections = project_tree(root, "example/repo")
            write_projections(out, projections)
            self.assertEqual([], check_projections(out, projections))
            write_projections(out, project_tree(root, "example/repo"))
            self.assertEqual([], check_projections(out, project_tree(root, "example/repo")))

    def test_projection_schema_declares_all_record_types(self) -> None:
        schema_path = Path(__file__).resolve().parents[1] / "msdmd" / "module-projection.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.assertEqual(SCHEMA_ID, schema["$id"])
        self.assertEqual(
            {"module", "symbol", "metadata", "diagnostic"},
            set(schema["$defs"]) & {"module", "symbol", "metadata", "diagnostic"},
        )

    def test_reader_manifest_discloses_the_partial_supported_subset(self) -> None:
        manifest_path = Path(__file__).resolve().parents[1] / "msdmd" / "python-module-reader.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        self.assertEqual("the-interdependency.msdmd.python-ast-tokenize", manifest["reader_id"])
        self.assertEqual("partial", manifest["status"])
        self.assertIn("docstring", " ".join(manifest["supported_subset"]))
        self.assertIn("imports and dependency edges", manifest["limitations"])
        self.assertEqual(
            ["python_implementation", "python_version", "ast_feature_version"],
            manifest["supported_grammar"]["projection_fields"],
        )
        self.assertFalse(manifest["safety"]["executes_inspected_code"])


if __name__ == "__main__":
    unittest.main()
# ratios: loc_comments=97:629 imports_exports=9:11 calls_definitions=316:41

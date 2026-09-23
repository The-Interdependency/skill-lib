# ratios: loc_comments=84:266 imports_exports=8:8 calls_definitions=145:26
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

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from msdmd.module_projection import (
    SCHEMA_ID,
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
                changed_revision["freshness_key_sha256"],
            )
            self.assertEqual("revision-two", changed_revision["source_revision"])
            self.assertEqual("utf-8", changed_revision["source_encoding"])
            self.assertEqual([], changed_revision["hmmm"])
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
        self.assertFalse(manifest["safety"]["executes_inspected_code"])


if __name__ == "__main__":
    unittest.main()
# ratios: loc_comments=84:266 imports_exports=8:8 calls_definitions=145:26

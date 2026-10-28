# ratios: loc_comments=78:138 imports_exports=14:3 calls_definitions=98:18
"""Go reader acceptance: python -m unittest tests.test_go_metadata.

Fixtures are inert source, not compiled or executed. These checks cover native
metadata extraction and failure disclosure; they do not verify Go behavior.
"""
# === CHECKS ===
# id: check_go_source_inert
#   proves: go_native_source_is_inert, go_native_scope_is_preserved, go_reader_failure_is_visible
#   call: self::test_go_source_contract
#   mutates: filesystem
#   cleanup: tempdir_teardown
# id: check_go_module_scope
#   proves: go_module_declarations_preserve_scope, go_module_unknowns_fail_required_coverage
#   call: self::test_go_module_contract
#   mutates: filesystem
#   cleanup: tempdir_teardown
# === END CHECKS ===
from __future__ import annotations

import builtins
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from msdmd.collect import collect, collection_errors, runtime_unavailable
from msdmd.readers import implementation_digest


def _collect(files: dict[str, str | bytes], **options) -> dict:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        for name, content in files.items():
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content.encode() if isinstance(content, str) else content)
        return collect(root, "example/go", source_commit="a" * 40, **options)


def _facts(result: dict, kind: str) -> list[dict]:
    return [f for f in result["facts"] if f["kind"] == kind]


class GoMetadataTests(unittest.TestCase):
    def test_large_source_walk_finishes_in_a_subprocess(self):
        # Keep native runtime faults isolated from unittest's own process.
        script = '''
from pathlib import Path
from msdmd.readers import read_native
source = "package stress\\n" + "".join(
    f"// Function{i} documents a declaration.\\nfunc Function{i}() int {{ // body\\n return {i}\\n}}\\n"
    for i in range(700))
for _ in range(8):
    readers, facts, edges, diagnostics = read_native(Path("stress.go"), source.encode(), {
        "repo": "example/stress", "revision": "a" * 40, "file": "stress.go",
        "content_sha256": "b" * 64})
    assert not diagnostics, diagnostics
    assert sum(f["kind"] == "symbol-declaration" for f in facts) == 700
'''
        result = subprocess.run([sys.executable, "-X", "faulthandler", "-c", script],
                                text=True, capture_output=True, check=False)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_native_only_symbols_comments_receivers_tags_and_directives(self):
        source = '''//go:build linux && amd64

// Package vault documents a package.
package vault
import alias "example.org/library"
// Client holds a value.
type Client[T any] struct {
    // Value is serialized.
    Value string `json:"value" custom:"tag"`
}
// Read returns it.
//go:noinline
func (c *Client[T]) Read() string { return c.Value }
//go:generate sh -c "touch MUST_NOT_EXIST"
// detached comment

func Other() {}
'''
        result = _collect({"vault.go": source}, required_sources=["*.go"])
        self.assertFalse(collection_errors(result), result["diagnostics"])
        self.assertEqual([], result["declarations"])
        symbols = {f["subject"]["identity"]: f for f in _facts(result, "symbol-declaration")}
        self.assertIn("vault.Client.Read", symbols)
        self.assertIn('custom:"tag"', symbols["vault.Client.Value"]["native"]["value"]["struct_tag_literal"])
        self.assertNotIn("return c.Value", symbols["vault.Client.Read"]["native"]["value"]["signature"])
        docs = {f["subject"]["identity"] for f in _facts(result, "documentation-comment")}
        self.assertTrue({"vault", "vault.Client", "vault.Client.Value", "vault.Client.Read"} <= docs)
        self.assertNotIn("vault.Other", docs)
        self.assertEqual({"go:build", "go:noinline", "go:generate"}, {f["native"]["value"]["name"] for f in _facts(result, "source-directive")})
        self.assertTrue(all(f["native"]["value"]["execution"] == "not-performed" for f in _facts(result, "source-directive")))
        self.assertEqual("alias", _facts(result, "import-declaration")[0]["native"]["value"]["alias"])

    def test_strings_do_not_declare_blocks_or_ratios(self):
        source = '''package example
const fake = `
// === DOCS ===
// id: fake
// === END DOCS ===
// ratios: loc_comments=1:1 imports_exports=1:1 calls_definitions=1:1
`
// === DOCS ===
// id: actual
//   summary: real comment
// === END DOCS ===
func Real() {}
'''
        result = _collect({"a.go": source})
        self.assertFalse(collection_errors(result), result["diagnostics"])
        self.assertEqual(["actual"], [d["id"] for d in result["declarations"]])
        self.assertEqual([], _facts(result, "ratio-declaration"))
        self.assertFalse(any(f["convention"]["namespace"] == "msdmd.ratios-line" for f in result["facts"]))

    def test_groups_trailing_comments_and_multiple_names_survive(self):
        result = _collect({"a.go": '''package p
// Constants document the group.
const (
    // Pair docs.
    A, B = 1, 2 // trailing pair comment
)
type X struct {
    V int // trailing field comment
    // W docs.
    W string
}
'''})
        docs = _facts(result, "documentation-comment")
        self.assertTrue(any(f["subject"]["scope"] == "declaration-group" for f in docs))
        self.assertTrue(any(f["subject"]["identity"] == "p.A,B" for f in docs))
        self.assertTrue(any(f["subject"]["identity"] == "p.X.V" and f["native"]["value"]["attachment"] == "trailing-comment"
                            for f in _facts(result, "comment")))
        self.assertTrue(any(f["subject"]["identity"] == "p.X.W" for f in docs))

    def test_source_identity_distinguishes_packages_and_ignores_line_shift(self):
        one = _collect({"a/a.go": "package a\nfunc Same() {}\n", "b/b.go": "package b\nfunc Same() {}\n"})
        two = _collect({"a/a.go": "\n\npackage a\nfunc Same() {}\n", "b/b.go": "package b\nfunc Same() {}\n"})
        self.assertEqual([f["address"] for f in _facts(one, "symbol-declaration")], [f["address"] for f in _facts(two, "symbol-declaration")])
        self.assertEqual(2, len({f["address"] for f in _facts(one, "symbol-declaration")}))
        self.assertNotEqual(one["source"]["snapshot_sha256"], two["source"]["snapshot_sha256"])

    def test_invalid_input_is_not_complete_coverage(self):
        for source in (b"package p\nfunc Broken( {", b"package p\n\xff", b"// no package"):
            result = _collect({"a.go": source}, required_sources=["a.go"])
            self.assertTrue(collection_errors(result), result)

    def test_newer_go_syntax_is_a_visible_grammar_limit(self):
        # Go 1.26 permits new(value); this grammar does not cover all such forms.
        result = _collect({"a.go": 'package p\nvar V = new("value")\n'}, required_sources=["a.go"])
        self.assertTrue(collection_errors(result))
        diagnostic = next(d for d in result["diagnostics"] if d["code"] == "go_grammar_error")
        self.assertIn("not a compiler verdict", diagnostic["message"])

    def test_missing_go_runtime_cannot_certify_comment_candidates(self):
        original = builtins.__import__

        def importing(name, *args, **kwargs):
            if name == "tree_sitter_go":
                raise ImportError("fixture missing grammar")
            return original(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=importing):
            result = _collect({"a.go": "package p\n// === DOCS ===\n// id: candidate\n// === END DOCS ===\n"}, required_sources=["*.go"])
        self.assertTrue(runtime_unavailable(result))
        self.assertTrue(collection_errors(result))
        self.assertEqual([], result["declarations"])
        self.assertIn("supplemental_comment_extraction_unavailable", {d["code"] for d in result["diagnostics"]})

    def test_go_module_requirements_replacements_and_nested_scopes(self):
        result = _collect({"go.mod": '''module example.org/root
go 1.24.0
require (
 example.org/a v1.2.3
 "example.org/b" v2.0.0 // indirect
)
replace example.org/a v1.2.3 => ../a
exclude example.org/old v0.1.0
retract [v1.0.0, v1.1.0]
tool example.org/tool
''', "api/go.mod": "module example.org/root/api\nrequire example.org/a v1.3.0\n",
            "go.work": 'go 1.24.0\nuse (\n .\n "./api"\n)\n'}, required_sources=["go.mod", "api/go.mod", "go.work"])
        self.assertFalse(collection_errors(result), result["diagnostics"])
        dependencies = _facts(result, "dependency")
        self.assertEqual(3, len(dependencies))
        self.assertEqual({"direct", "indirect"}, {f["native"]["value"]["class"] for f in dependencies})
        self.assertEqual({"go.mod", "api/go.mod"}, {f["source"]["file"] for f in dependencies})
        self.assertEqual(["../a"], _facts(result, "module-replacement")[0]["native"]["value"]["to"])
        self.assertEqual(2, len(_facts(result, "workspace-member")))

    def test_go_quoted_strings_and_redaction_preserve_raw_source(self):
        result = _collect({"go.mod": 'module "example.org/\\x61"\nreplace example.org/a => "https://user:password@example.org/a"\n'})
        self.assertFalse(collection_errors(result))
        self.assertEqual("example.org/a", _facts(result, "package-identity")[0]["native"]["value"]["module"])
        self.assertNotIn("user:password", json.dumps(result))
        self.assertIn("\\x61", _facts(result, "module-directive")[0]["native"]["value"]["raw_tokens"][1])

    def test_unknown_and_invalid_module_metadata_remain_visible(self):
        for source, code in (("module example.org/a\nfuture x\n", "unknown_go_module_directive"),
            ("require (\nexample.org/a v1\n", "unclosed_go_module_block"),
            ("replace a =>\n", "invalid_go_module_directive"),
            ('module "bad\\q"\n', "invalid_go_module_tokens")):
            result = _collect({"go.mod": source}, required_sources=["go.mod"])
            self.assertTrue(collection_errors(result))
            self.assertIn(code, {d["code"] for d in result["diagnostics"]})

    def test_checksums_are_reported_without_verification(self):
        checksum = "h1:" + "A" * 43 + "="
        result = _collect({"go.sum": f"example.org/a v1.0.0 {checksum}\n"}, required_sources=["go.sum"])
        self.assertFalse(collection_errors(result))
        self.assertEqual("not-performed", _facts(result, "recorded-checksum")[0]["native"]["value"]["verification"])
        conflict = _collect({"go.sum": f"example.org/a v1.0.0 {checksum}\nexample.org/a v1.0.0 h1:{'B' * 43}=\n"})
        self.assertIn("conflicting_go_checksums", {d["code"] for d in collection_errors(conflict)})

    def test_go_implementation_is_bound_into_reader_identity(self):
        original = Path.read_bytes
        before = implementation_digest()
        implementation_digest.cache_clear()

        def reading(path):
            data = original(path)
            return data + b"\n# identity fixture\n" if path.name == "go_code.py" else data

        try:
            with patch.object(Path, "read_bytes", reading):
                self.assertNotEqual(before, implementation_digest())
        finally:
            implementation_digest.cache_clear()


def test_go_source_contract():
    suite = unittest.TestSuite(GoMetadataTests(name) for name in unittest.defaultTestLoader.getTestCaseNames(GoMetadataTests)
        if "module" not in name and "checksum" not in name and "quoted" not in name)
    result = unittest.TestResult()
    suite.run(result)
    assert result.wasSuccessful(), (result.errors, result.failures)


def test_go_module_contract():
    suite = unittest.TestSuite(GoMetadataTests(name) for name in unittest.defaultTestLoader.getTestCaseNames(GoMetadataTests)
        if "module" in name or "checksum" in name or "quoted" in name)
    result = unittest.TestResult()
    suite.run(result)
    assert result.wasSuccessful(), (result.errors, result.failures)
# ratios: loc_comments=78:138 imports_exports=14:3 calls_definitions=98:18

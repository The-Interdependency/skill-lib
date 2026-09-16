"""Executable acceptance fixtures for the MSDMD native collection contract.

Usage: python -m unittest tests.test_native_collection
These tests exercise static extraction only; they never execute fixture code.
"""
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from msdmd.collect import SCHEMA_VERSION, collect, collection_errors

ROOT = Path(__file__).resolve().parents[1]


class NativeCollectionTest(unittest.TestCase):
    def test_native_only_repository_needs_no_msdmd_redeclarations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "example.py").write_text(
                '''"""Example package."""
from pathlib import Path

__all__ = ["double"]

def double(value: int) -> int:
    """Return twice the supplied value."""
    return value * 2
''',
                encoding="utf-8",
            )
            (root / "pyproject.toml").write_text(
                '''[project]
name = "example"
version = "1.0.0"
released = 2026-09-16
dependencies = ["httpx>=1"]

[build-system]
requires = ["hatchling"]
''',
                encoding="utf-8",
            )
            (root / ".github").mkdir()
            (root / ".github" / "CODEOWNERS").write_text("/src/example/ @example/maintainers\n", encoding="utf-8")
            (root / "SKILL.md").write_text("---\nname: example\ndescription: Example skill.\n---\n", encoding="utf-8")
            (root / "package.json").write_text(json.dumps({"name": "example-ui", "api_token": "do-not-publish", "dependencies": {"react": "^19"}}), encoding="utf-8")
            (root / "workflow.yml").write_text("name: checks\non:\n  push:\njobs:\n  test:\n    steps:\n      - run: python -m unittest\n", encoding="utf-8")
            (root / "api.ts").write_text('/** Return a greeting.\n * @param name recipient\n */\nexport function greet(name: string): string { return `hello ${name}`; }\nimport { readFileSync } from "node:fs";\n', encoding="utf-8")
            (root / "run.sh").write_text("#!/bin/sh\n# shellcheck shell=sh\nexit 0\n", encoding="utf-8")
            (root / "example.service").write_text("[Service]\nExecStart=/usr/bin/example\nEnvironment=A=1\nEnvironment=B=2\n", encoding="utf-8")
            (root / ".gitignore").write_text("build/\n!important.txt\n", encoding="utf-8")
            (root / "requirements.txt").write_text(
                "httpx>=1\nprivate-lib @ https://user:token@example.invalid/private.whl\n",
                encoding="utf-8",
            )
            (root / "LICENSE").write_text("Mozilla Public License Version 2.0\n", encoding="utf-8")
            (root / "icon.svg").write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><title>Example</title><desc>Fixture icon.</desc></svg>\n',
                encoding="utf-8",
            )
            (root / "llms.txt").write_text("# Example\n- **Source** = repository\n", encoding="utf-8")

            collection = collect(root, "example", source_commit="a" * 40)

        self.assertEqual(SCHEMA_VERSION, collection["schema_version"])
        self.assertEqual([], collection["declarations"])
        self.assertFalse(collection_errors(collection))
        namespaces = {fact["convention"]["namespace"] for fact in collection["facts"]}
        self.assertTrue({"python.pep257", "python.source-metadata", "python.pyproject", "github.codeowners", "markdown.yaml-frontmatter", "npm.package-json", "yaml.document", "typescript.source-metadata", "typescript.documentation-comment", "posix.shebang", "systemd.unit", "git.ignore", "python.requirements-file", "license.text", "svg.document-metadata", "llms.txt"}.issubset(namespaces))
        symbol = next(fact for fact in collection["facts"] if fact["kind"] == "callable-declaration")
        self.assertEqual("double", symbol["subject"]["identity"])
        self.assertEqual("syntactically-observed", symbol["standing"])
        self.assertEqual("behavior not inferred", symbol["projection"]["loss"])
        ownership = next(fact for fact in collection["facts"] if fact["kind"] == "review-ownership")
        self.assertEqual("review-assignment-only", ownership["native"]["value"]["authority"])
        pyproject = next(fact for fact in collection["facts"] if fact["convention"]["namespace"] == "python.pyproject" and fact["kind"] == "structured-document")
        self.assertEqual({"$type": "toml-date", "value": "2026-09-16"}, pyproject["native"]["value"]["project"]["released"])
        serialized = json.dumps(collection, sort_keys=True)
        self.assertNotIn("do-not-publish", serialized)
        self.assertNotIn("user:token", serialized)
        self.assertIn("sensitive_fields_redacted", {item["code"] for item in collection["diagnostics"]})
        self.assertEqual(0, collection["coverage"]["unsupported_files"])
        self.assertEqual("not-evaluated", collection["coverage"]["verified_behavior"])

    def test_qualified_sources_and_duplicate_identity_diagnostics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("a.py", "b.py"):
                (root / name).write_text(
                    "# === DOCS ===\n# id: shared\n#   summary: first\n# === END DOCS ===\n",
                    encoding="utf-8",
                )
            with (root / "a.py").open("a", encoding="utf-8") as handle:
                handle.write("# === DOCS ===\n# id: shared\n#   summary: conflicting\n# === END DOCS ===\n")

            collection = collect(root, "example", block_names=("DOCS",), source_commit="b" * 40)

        addresses = [item["address"] for item in collection["declarations"]]
        self.assertEqual(3, len(addresses))
        self.assertNotEqual(addresses[0], addresses[2])
        self.assertEqual(addresses[0], addresses[1])
        errors = collection_errors(collection)
        self.assertEqual(["duplicate_block_id"], [item["code"] for item in errors])
        self.assertEqual("identity-conflict", collection["conflicts"][0]["kind"])

    def test_same_symbol_name_in_two_packages_stays_distinct(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for package in ("alpha", "beta"):
                directory = root / package
                directory.mkdir()
                (directory / "math.py").write_text("def parse(value: str) -> str:\n    return value\n", encoding="utf-8")

            collection = collect(root, "example", source_commit="9" * 40)

        facts = [item for item in collection["facts"] if item["kind"] == "callable-declaration"]
        self.assertEqual(["parse", "parse"], [item["subject"]["identity"] for item in facts])
        self.assertEqual(2, len({item["subject"]["address"] for item in facts}))

    def test_python_strings_do_not_create_block_declarations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "fixture.py").write_text(
                '''EXAMPLE = """# === DOCS ===
# id: not_a_declaration
#   summary: fixture text
# === END DOCS ==="""
''',
                encoding="utf-8",
            )

            collection = collect(root, "example", block_names=("DOCS",), source_commit="c" * 40)

        self.assertEqual([], collection["declarations"])

    def test_python_declared_encoding_and_source_lines_survive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "latin.py").write_bytes(
                b"# -*- coding: latin-1 -*-\n\ndef caf\xe9(value: int) -> int:\n    \"\"\"Doubler.\"\"\"\n    return value * 2\n"
            )

            collection = collect(root, "example", source_commit="f" * 40)

        fact = next(item for item in collection["facts"] if item["kind"] == "callable-declaration")
        self.assertEqual("caf\N{LATIN SMALL LETTER E WITH ACUTE}", fact["subject"]["identity"])
        self.assertEqual({"start_line": 3, "end_line": 5}, fact["source"]["location"])
        self.assertFalse(collection_errors(collection))

    def test_replay_is_byte_identical_for_same_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "module.py").write_text("def answer() -> int:\n    return 42\n", encoding="utf-8")
            first = collect(root, "example", source_commit="d" * 40)
            second = collect(root, "example", source_commit="d" * 40)
            next_revision = collect(root, "example", source_commit="e" * 40)

        self.assertEqual(
            json.dumps(first, sort_keys=True, separators=(",", ":")),
            json.dumps(second, sort_keys=True, separators=(",", ":")),
        )
        self.assertNotEqual(first["facts"][0]["address"], next_revision["facts"][0]["address"])

    def test_generated_collection_is_accounted_for_without_self_ingestion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "module.py").write_text("VALUE = 1\n", encoding="utf-8")
            output = root / "example_msdmd.ts"
            output.write_text("first generated value\n", encoding="utf-8")
            first = collect(root, "example", source_commit="1" * 40)
            output.write_text("different generated value\n", encoding="utf-8")
            second = collect(root, "example", source_commit="1" * 40)

        self.assertEqual(first["source"]["snapshot_sha256"], second["source"]["snapshot_sha256"])
        self.assertNotIn("example_msdmd.ts", {item["file"] for item in first["discovery"]})

    def test_invalid_native_source_stays_visible(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "broken.json").write_text('{"open": ', encoding="utf-8")
            collection = collect(root, "example", source_commit="e" * 40)

        self.assertEqual(["invalid_json"], [item["code"] for item in collection_errors(collection)])
        entry = next(item for item in collection["discovery"] if item["file"] == "broken.json")
        self.assertEqual("invalid", entry["status"])

    def test_declared_revision_must_match_available_git_head(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "module.py").write_text("VALUE = 1\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "Fixture"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "fixture@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(root), "add", "module.py"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "fixture"], check=True)

            collection = collect(root, "example", source_commit="0" * 40)

        self.assertIn("source_revision_mismatch", {item["code"] for item in collection_errors(collection)})

    def test_current_skill_lib_head_satisfies_collection_contract(self) -> None:
        revision = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

        collection = collect(ROOT, "The-Interdependency/skill-lib", source_commit=revision)

        self.assertEqual(revision, collection["source"]["revision"])
        self.assertFalse(collection_errors(collection))
        self.assertGreater(collection["coverage"]["native_facts"], 100)
        self.assertGreater(collection["coverage"]["supplemental_declarations"], 10)
        self.assertIn("json.schema", {fact["convention"]["namespace"] for fact in collection["facts"]})
        applied = {run["reader_id"] for run in collection["reader_runs"] if run["status"] == "applied"}
        self.assertTrue({"python-ast", "json-stdlib", "markdown-frontmatter", "yaml-safe-subset", "typescript-static", "shell-static", "systemd-unit", "gitignore-lines", "python-requirements", "license-text", "svg-metadata", "llms-text"}.issubset(applied))
        self.assertEqual(0, collection["coverage"]["unsupported_files"])
        self.assertFalse(any(item["id"] == "project_overview" and item["file"] == "tests/test_llms_build.py" for item in collection["declarations"]))


if __name__ == "__main__":
    unittest.main()

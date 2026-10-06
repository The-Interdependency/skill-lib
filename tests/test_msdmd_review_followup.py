"""Regressions for the Review findings on skill-lib #118 (msdmd consumer review).

Usage: python -m unittest tests.test_msdmd_review_followup
Each test names the finding it closes. Fixtures are parsed statically.
"""
from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from msdmd.collect import collect, collection_errors, generator_identity, generator_identity_components, runtime_unavailable
from msdmd.native_code import read_typescript

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ratios"))
import harmonics as H  # noqa: E402


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid", *args],
        check=True, capture_output=True, text=True,
    ).stdout.strip()


def committed_repo(root: Path, files: dict[str, str]) -> str:
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    git(root, "init", "-q")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "fixture")
    return git(root, "rev-parse", "HEAD")


def run_cli(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "msdmd.collect", *args], cwd=ROOT,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)


def current_helper() -> str:
    return (ROOT / "msdmd" / "collection.ts").read_text(encoding="utf-8")


def unversioned_schema_two_helper() -> str:
    """A 9867ab3-era helper: exports defineMsdmdCollectionV2 but predates the version constant."""
    text = current_helper()
    start = text.index("/**\n * Schema-2 shape revision")
    end = text.index("export type JsonPrimitive")
    return (text[:start] + text[end:]).replace(' | "runtime-unavailable"', "")


def docstring_parser_shim(tmp: Path) -> dict[str, str]:
    shim = tmp / "shim"
    shim.mkdir()
    (shim / "docstring_parser.py").write_text("raise ImportError('blocked for test')\n", encoding="utf-8")
    return dict(os.environ, PYTHONPATH=os.pathsep.join([str(shim), str(ROOT)]))


def requirement_facts(text: str) -> tuple[list[dict], dict]:
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "requirements.txt").write_text(text, encoding="utf-8")
        result = collect(Path(tmp), "fixture")
    return [f for f in result["facts"] if f["kind"] == "dependency"], result


class RequirementLineTests(unittest.TestCase):
    """Review 1: readers.py ~847 (P2) and ~823 (P3)."""

    def test_comment_ending_in_backslash_does_not_swallow_next_requirement(self) -> None:
        deps, _ = requirement_facts("# pinned for CI \\\nflask==3.0\ndjango==5 \\\n  # trailing note\nzipp>=3\n")
        self.assertEqual(["flask", "django", "zipp"], [f["native"]["value"]["name"] for f in deps])
        self.assertEqual("django==5 ", deps[1]["native"]["value"]["requirement"] + " ")  # comment not appended
        self.assertEqual({"start_line": 3, "end_line": 4},
                         {k: deps[1]["source"]["location"][k] for k in ("start_line", "end_line")})

    def test_trailing_backslash_at_end_of_file_is_diagnosed(self) -> None:
        deps, result = requirement_facts("requests==2.32.0 \\")
        self.assertEqual(["requests"], [f["native"]["value"]["name"] for f in deps])
        self.assertIn("dangling_requirement_continuation", {d["code"] for d in result["diagnostics"]})

    def test_windows_paths_are_not_packages(self) -> None:
        deps, result = requirement_facts("C:\\src\\pkg\nD:/x\nc:\\wheels\\winpkg-1.0-py3-none-any.whl\nrequests\n")
        self.assertEqual(["hmmm", "hmmm", "hmmm", "requests"], [f["native"]["value"]["name"] for f in deps])
        targets = {e["to"] for e in result["edges"] if e["to"].startswith("python-package:")}
        self.assertEqual({"python-package:requests"}, targets)


class GitVisibilityTests(unittest.TestCase):
    """Review 2 (collect.py ~259) and Review 3 (collect.py ~247/~399)."""

    FILES = {"a.json": '{"a": 1}\n', ".gitignore": "local.json\n"}

    def test_ls_files_failure_inside_a_checkout_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            committed_repo(root, self.FILES)
            (root / "local.json").write_text('{"v": "ignored-local-value"}', encoding="utf-8")
            (root / ".git" / "index").write_bytes(b"not an index")
            result = collect(root, "fixture")
        text = json.dumps(result)
        self.assertNotIn("ignored-local-value", text)
        self.assertEqual([], [f for f in result["discovery"] if f.get("entry_kind", "file") == "file"])
        self.assertIn("git_visibility_unavailable", {d["code"] for d in collection_errors(result)})
        self.assertFalse(result["source"]["snapshot_complete"])

    def test_broken_git_marker_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".git").write_text("gitdir: /nonexistent/msdmd-fixture\n", encoding="utf-8")
            (root / "local.json").write_text('{"v": "unlisted-value"}', encoding="utf-8")
            result = collect(root, "fixture")
        self.assertNotIn("unlisted-value", json.dumps(result))
        self.assertIn("git_visibility_unavailable", {d["code"] for d in collection_errors(result)})
        self.assertFalse(result["source"]["snapshot_complete"])

    def test_root_inside_an_ignored_directory_is_not_a_complete_empty_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            outer = Path(tmp)
            committed_repo(outer, {".gitignore": "scratch/\n", "README.md": "outer\n"})
            stage = outer / "scratch" / "stage"
            stage.mkdir(parents=True)
            (stage / "a.json").write_text('{"a": 1}', encoding="utf-8")
            result = collect(stage, "fixture")
        self.assertIn("root_git_ignored", {d["code"] for d in collection_errors(result)})
        self.assertFalse(result["source"]["snapshot_complete"])

    def test_plain_directory_outside_git_is_still_scanned(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.json").write_text('{"a": 1}', encoding="utf-8")
            result = collect(root, "fixture")
        self.assertIn("a.json", {f["file"] for f in result["discovery"]})
        self.assertTrue(result["source"]["snapshot_complete"])


class SchemaHelperVersionTests(unittest.TestCase):
    """Review 4 (collect.py ~922) and Review 11 (combined report, relative --out)."""

    def test_unversioned_schema_two_helper_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            committed_repo(root, {"a.json": "{}\n", ".agents/skills/msdmd/collection.ts": unversioned_schema_two_helper()})
            out = root / "fixture_msdmd.ts"
            refused = run_cli("--root", str(root), "--repo", "fixture", "--out", str(out))
            self.assertEqual(4, refused.returncode, refused.stderr)
            self.assertIn("MSDMD_COLLECTION_HELPER_VERSION missing", refused.stderr)
            self.assertFalse(out.exists())
            # --out is resolved before locating the helper, so a cwd-relative path works too.
            relative = run_cli("--root", str(root), "--repo", "fixture", "--out", os.path.relpath(out, ROOT))
            self.assertEqual(4, relative.returncode, relative.stderr)
            (root / ".agents/skills/msdmd/collection.ts").write_text(current_helper(), encoding="utf-8")
            accepted = run_cli("--root", str(root), "--repo", "fixture", "--out", str(out))
            self.assertEqual(0, accepted.returncode, accepted.stderr)

    def test_runtime_and_helper_problems_are_reported_together(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            committed_repo(root, {"a.py": 'def f():\n    """Doc."""\n',
                                  ".agents/skills/msdmd/collection.ts": unversioned_schema_two_helper()})
            out = root / "repo_msdmd.ts"
            result = run_cli("--root", str(root), "--repo", "repo", "--out", str(out), env=docstring_parser_shim(Path(tmp)))
        self.assertEqual(3, result.returncode)
        self.assertIn("native reader runtime unavailable", result.stderr)
        self.assertIn("MSDMD_COLLECTION_HELPER_VERSION", result.stderr)
        self.assertIn("--allow-missing-reader-runtimes", result.stderr)
        skill = os.path.relpath(ROOT / "msdmd", ROOT)
        self.assertIn(os.path.join(skill, "requirements.txt"), result.stderr)
        self.assertIn(f"npm ci --ignore-scripts --prefix {skill}", result.stderr)


class GeneratorIdentityRuntimeTests(unittest.TestCase):
    """Review 5 (collect.py ~880)."""

    def test_identity_includes_python_package_node_and_typescript_versions(self) -> None:
        components = generator_identity_components()
        self.assertEqual(f"{sys.version_info.major}.{sys.version_info.minor}", components["python"])
        self.assertIn("docstring-parser", components["python_packages"])
        self.assertIn("tree-sitter", components["python_packages"])
        typescript = ROOT / "msdmd" / "node_modules" / "typescript" / "package.json"
        if typescript.is_file():
            self.assertEqual(json.loads(typescript.read_text())["version"], components["typescript"])
            node = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True).stdout.strip()
            self.assertEqual(node, components["node"])
        baseline = generator_identity()
        from importlib import metadata
        with patch("importlib.metadata.version", side_effect=metadata.PackageNotFoundError):
            self.assertNotEqual(baseline, generator_identity())
        with patch.dict(os.environ, {"PATH": "/nonexistent-msdmd-path"}):
            absent = generator_identity_components()
            self.assertEqual(("absent", "absent"), (absent["node"], absent["typescript"]))
            if components["node"] != "absent":
                self.assertNotEqual(baseline, generator_identity())
        cli = run_cli("--print-generator-identity", "--json")
        self.assertEqual(0, cli.returncode, cli.stderr)
        self.assertEqual(components, json.loads(cli.stdout))


class DsseSupersessionTests(unittest.TestCase):
    """Review 6 (standards.py ~206)."""

    def test_non_statement_payload_is_diagnosed_and_kept_without_raw_base64(self) -> None:
        payload_doc = {"note": "not a statement", "password": "dsse-nonstatement-secret"}
        payload = base64.b64encode(json.dumps(payload_doc).encode()).decode()
        envelope = {"payloadType": "application/vnd.in-toto+json", "payload": payload, "signatures": []}
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "att.json").write_text(json.dumps(envelope), encoding="utf-8")
            result = collect(Path(tmp), "fixture")
        text = json.dumps(result)
        self.assertNotIn(payload, text)
        self.assertNotIn("dsse-nonstatement-secret", text)
        self.assertIn("dsse_payload_not_in_toto_statement", {d["code"] for d in result["diagnostics"]})
        kinds = {f["kind"] for f in result["facts"]}
        self.assertIn("signed-payload", kinds)
        self.assertNotIn("attestation", kinds)
        payload_fact = next(f for f in result["facts"] if f["kind"] == "signed-payload")
        self.assertEqual("not a statement", payload_fact["native"]["value"]["note"])
        envelope_fact = next(f for f in result["facts"] if f["kind"] == "signed-envelope")
        self.assertEqual("structured-document", envelope_fact["projection"]["supersedes"])


class CamelRedactionFinalTokenTests(unittest.TestCase):
    """Review 8 (readers.py ~323-327)."""

    def test_only_a_final_sensitive_token_is_redacted(self) -> None:
        from msdmd.readers import _is_sensitive_key
        redact = ["accessToken", "OAuthToken", "DBPassword", "resetPasswordToken", "apiKey", "APIKey", "secretKey",
                  "signingPrivateKey", "ClientSecret", "Authorization", "authorization", "proxyAuthorization",
                  "AWS_SECRET_ACCESS_KEY", "db_password", "GITHUB_TOKEN"]
        keep = ["tokenUrl", "passwordPolicyUrl", "passwordHash", "apiKeyPrefix", "accessKeyId", "tokenCount", "tokenLimit",
                "tokenType", "secretName", "privateKeyPath", "maxTokens", "tokenizer", "csrfTokenName", "keyboard", "secretary"]
        self.assertEqual([], [k for k in redact if not _is_sensitive_key(k)])
        self.assertEqual([], [k for k in keep if _is_sensitive_key(k)])


class AmbiguousSemanticEdgeTests(unittest.TestCase):
    """Review 9 (harmonics.py ~110)."""

    def test_ambiguous_short_id_target_is_unresolved(self) -> None:
        block = "# === MODULE_BUILD ===\n# id: {id}\n#   requires: {req}\n# === END MODULE_BUILD ===\nx = 1\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.py").write_text(block.format(id="alpha", req="beta"), encoding="utf-8")
            (root / "b.py").write_text(block.format(id="beta", req="hmmm"), encoding="utf-8")
            (root / "c.py").write_text(block.format(id="beta", req="hmmm"), encoding="utf-8")
            collection = collect(root, "fixture")
            self.assertEqual(["ambiguous"], [e["target_resolution"] for e in collection["edges"] if "source_block" in e])
            files = [str((root / name).resolve()) for name in ("a.py", "b.py", "c.py")]
            report = H.semantic_file_graph(collection, root, files)
        self.assertEqual(0, report["resolved_edges"])
        self.assertEqual([], report["adjacency"][files[0]])
        self.assertEqual(1, len(report["unresolved_edges"]))
        self.assertIn("beta", report["ambiguous_ids"])


class SubmoduleLedgerTests(unittest.TestCase):
    """Review 10 (submodules)."""

    def test_submodule_is_an_excluded_pinned_ledger_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            committed_repo(root, {"a.json": "{}\n"})
            sub = root / "vendor" / "sub"
            sub_sha = committed_repo(sub, {"inner.json": '{"inner": "submodule-content"}\n'})
            git(root, "update-index", "--add", "--cacheinfo", f"160000,{sub_sha},vendor/sub")
            git(root, "commit", "-q", "-m", "pin submodule")
            result = collect(root, "fixture")
            snapshot = collect(root, "fixture", snapshot_identity=True)
        entry = next(f for f in result["discovery"] if f["file"] == "vendor/sub")
        self.assertEqual({"entry_kind": "submodule", "status": "excluded", "reason": "git-submodule", "commit": sub_sha},
                         {k: entry[k] for k in ("entry_kind", "status", "reason", "commit")})
        self.assertNotIn("submodule-content", json.dumps(result))
        self.assertFalse(any(f["file"].startswith("vendor/sub/") for f in result["discovery"]))
        self.assertTrue(result["source"]["snapshot_complete"])
        self.assertFalse(result["source"]["dirty_worktree"])
        self.assertIn("vendor/sub", {f["file"] for f in snapshot["discovery"]})


class TypeScriptWorkerFailureTests(unittest.TestCase):
    """Review 11: a nonzero worker exit is not always a missing runtime."""

    def run_worker(self, stderr: str) -> list[dict]:
        completed = subprocess.CompletedProcess(args=["node"], returncode=1, stdout="", stderr=stderr)
        context = {"repo": "fixture", "revision": "r", "file": "a.ts", "content_sha256": "0" * 64, "codeowners_source": None,
                   "configuration_sha256": "0" * 64}
        with patch("msdmd.native_code.subprocess.run", return_value=completed):
            return read_typescript(Path("a.ts"), b"export const a = 1;\n", context)[2]

    def test_missing_typescript_package_is_runtime_unavailable(self) -> None:
        diagnostics = self.run_worker("Error: Cannot find module 'typescript'\nRequire stack: ...")
        self.assertEqual(["typescript_reader_unavailable"], [d["code"] for d in diagnostics])
        self.assertTrue(runtime_unavailable({"diagnostics": diagnostics}))

    def test_other_worker_failures_are_reader_errors(self) -> None:
        diagnostics = self.run_worker("RangeError: Maximum call stack size exceeded\n    at visit (secret-source-line)")
        self.assertEqual(["typescript_reader_failed"], [d["code"] for d in diagnostics])
        self.assertEqual("error", diagnostics[0]["severity"])
        self.assertFalse(runtime_unavailable({"diagnostics": diagnostics}))
        self.assertNotIn("secret-source-line", json.dumps(diagnostics))


class BudgetVisibilityTests(unittest.TestCase):
    """Review 12."""

    def test_budget_overflow_warns_without_strict_and_flag_must_be_positive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for index in range(3):
                (root / f"doc{index}.json").write_text(json.dumps({"pad": "x" * 400}), encoding="utf-8")
            result = run_cli("--root", str(root), "--repo", "fixture", "--json", "--out", str(root / "c.json"),
                             "--max-total-bytes", "500")
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("WARNING", result.stderr)
            self.assertIn("aggregate scan budget", result.stderr)
            for value in ("0", "-5"):
                bad = run_cli("--root", str(root), "--repo", "fixture", "--max-total-bytes", value)
                self.assertEqual(2, bad.returncode)
                self.assertIn("must be a positive integer", bad.stderr)


class RenameDetectionTests(unittest.TestCase):
    """Review 13 (collect.py ~302): renames in either porcelain column carry a source path."""

    def test_worktree_rename_of_own_output_is_not_dirty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            committed_repo(root, {"collection.json": '{"generated": true}\n', "a.json": "{}\n"})
            os.replace(root / "collection.json", root / ".collection.json.bak")
            git(root, "add", "-N", ".collection.json.bak")
            status = subprocess.run(["git", "-C", str(root), "status", "--porcelain=v1"],
                                    capture_output=True, text=True, check=True).stdout
            self.assertTrue(status.startswith(" R"), status)  # rename only in the worktree (Y) column
            result = collect(root, "fixture", generated_outputs=["collection.json"])
            self.assertFalse(result["source"]["dirty_worktree"])
            os.replace(root / "a.json", root / "b.json")
            git(root, "add", "-N", "b.json")
            self.assertTrue(collect(root, "fixture", generated_outputs=["collection.json"])["source"]["dirty_worktree"])


class VisibilityExitTests(unittest.TestCase):
    """Review P2 (collect.py ~284-300, main): visibility errors stop the CLI with exit 5."""

    def test_no_git_on_path_exits_5_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            committed_repo(root, {"a.json": '{"a": 1}\n'})
            empty = Path(tmp) / "empty-bin"
            empty.mkdir()
            env = dict(os.environ, PATH=str(empty))
            out = root / "repo_msdmd.ts"
            for extra in ((), ("--legacy-blocks-only",)):
                result = run_cli("--root", str(root), "--repo", "repo", "--out", str(out), *extra, env=env)
                self.assertEqual(5, result.returncode, (extra, result.stderr))
                self.assertIn("msdmd: ERROR: git_visibility_unavailable", result.stderr)
                self.assertFalse(out.exists())

    def test_ignored_root_exits_5_and_check_is_not_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            outer = Path(tmp)
            committed_repo(outer, {".gitignore": "scratch/\n", "README.md": "outer\n"})
            stage = outer / "scratch" / "stage"
            stage.mkdir(parents=True)
            (stage / "a.json").write_text('{"a": 1}', encoding="utf-8")
            out = stage / "stage_msdmd.ts"
            base = ["--root", str(stage), "--repo", "stage", "--out", str(out)]
            written = run_cli(*base)
            self.assertEqual(5, written.returncode, written.stderr)
            self.assertIn("msdmd: ERROR: root_git_ignored", written.stderr)
            self.assertFalse(out.exists())
            strict = run_cli(*base, "--strict")
            self.assertEqual(5, strict.returncode, strict.stderr)
            check = run_cli(*base, "--check")
            self.assertEqual(5, check.returncode, check.stdout + check.stderr)
            self.assertNotIn("collection drift", check.stdout)


class OutOfTreeHelperTests(unittest.TestCase):
    """Review 11d: --out outside the tree still checks the in-tree helper."""

    def test_helper_is_found_from_root_when_out_is_outside(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as scratch:
            root = Path(tmp)
            committed_repo(root, {"a.json": "{}\n", ".agents/skills/msdmd/collection.ts": unversioned_schema_two_helper()})
            out = Path(scratch) / "fixture_msdmd.ts"
            refused = run_cli("--root", str(root), "--repo", "fixture", "--out", str(out))
            self.assertEqual(4, refused.returncode, refused.stderr)
            self.assertIn(str(root.resolve() / ".agents/skills/msdmd/collection.ts"), refused.stderr)
            self.assertFalse(out.exists())
            (root / ".agents/skills/msdmd/collection.ts").write_text(current_helper(), encoding="utf-8")
            git(root, "commit", "-qam", "current helper")
            accepted = run_cli("--root", str(root), "--repo", "fixture", "--out", str(out))
            self.assertEqual(0, accepted.returncode, accepted.stderr)
            self.assertNotIn("not found", accepted.stderr)


class ShadowedReaderModuleTests(unittest.TestCase):
    """Review B (collect.py ~986): resolved reader module files are part of the identity."""

    def test_shadowing_module_changes_identity_but_not_metadata_versions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            shim = Path(tmp) / "shim"
            shim.mkdir()
            (shim / "docstring_parser.py").write_text("def parse(text):\n    raise ValueError('shadow')\n", encoding="utf-8")
            plain = run_cli("--print-generator-identity", "--json")
            shadowed = run_cli("--print-generator-identity", "--json",
                               env=dict(os.environ, PYTHONPATH=os.pathsep.join([str(shim), str(ROOT)])))
            plain_id = run_cli("--print-generator-identity")
            shadowed_id = run_cli("--print-generator-identity",
                                  env=dict(os.environ, PYTHONPATH=os.pathsep.join([str(shim), str(ROOT)])))
        for result in (plain, shadowed, plain_id, shadowed_id):
            self.assertEqual(0, result.returncode, result.stderr)
        before, after = json.loads(plain.stdout), json.loads(shadowed.stdout)
        self.assertEqual(before["python_packages"], after["python_packages"])
        self.assertTrue(before["python_modules"]["docstring_parser"].startswith("sha256:"))
        self.assertNotEqual(before["python_modules"]["docstring_parser"], after["python_modules"]["docstring_parser"])
        self.assertIn("yaml", before["python_modules"])
        self.assertNotEqual(plain_id.stdout.strip(), shadowed_id.stdout.strip())


if __name__ == "__main__":
    unittest.main()

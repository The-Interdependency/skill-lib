"""A TypeScript reader or identity probe that cannot finish fails closed (exit 3).

Usage: python -m unittest tests.test_msdmd_reader_fail_closed
Covers nonzero worker exits, required exports, truthful opt-out diagnostics,
exit 0 without a complete JSON result, node rejecting --jitless, the worker
timeout, and an untraversable typescript package seen by the generator-identity
probe. Fake ``node`` scripts stand in
for broken runtimes; permission cases skip when run as root.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from msdmd import native_code
from msdmd.collect import GeneratorIdentityError, generator_identity_components, runtime_unavailable
from msdmd.native_code import read_typescript
from tests.test_msdmd_node_sandbox import CONTEXT, ROOT, run_cli, ts_repo

SOURCE = b"export const a = 1;\n"
VALID = {"version": "5.0.0", "declarations": [], "imports": [], "exports": [], "docs": [], "comments": [], "diagnostics": []}


def fake_node(directory: Path, body: str) -> dict[str, str]:
    """PATH whose ``node`` is a shell script with ``body``."""
    directory.mkdir(parents=True, exist_ok=True)
    node = directory / "node"
    node.write_text("#!/bin/sh\n" + body + "\n", encoding="utf-8")
    node.chmod(0o755)
    return dict(os.environ, PATH=os.pathsep.join([str(directory), os.environ.get("PATH", "")]))


def worker(returncode: int, stdout: str = "", stderr: str = "") -> list[dict]:
    completed = subprocess.CompletedProcess(args=["node"], returncode=returncode, stdout=stdout, stderr=stderr)
    with patch("msdmd.native_code.subprocess.run", return_value=completed):
        return read_typescript(Path("a.ts"), SOURCE, CONTEXT)[2]


class TypeScriptReaderFailClosedTests(unittest.TestCase):
    def assert_fails_closed(self, diagnostics: list[dict], code: str = "typescript_reader_failed") -> dict:
        self.assertEqual([code], [d["code"] for d in diagnostics])
        self.assertEqual("error", diagnostics[0]["severity"])
        self.assertTrue(runtime_unavailable({"diagnostics": diagnostics}), "must map to CLI exit 3")
        self.assertNotIn("secret-source-line", json.dumps(diagnostics))
        return diagnostics[0]

    def test_any_nonzero_worker_exit_fails_closed(self) -> None:
        for returncode in (1, 2, 9, 127, 128):
            with self.subTest(returncode=returncode):
                failure = self.assert_fails_closed(worker(returncode, stderr="RangeError at visit (secret-source-line)"))
                self.assertIn(f"status {returncode}", failure["message"])

    def test_unsupported_flag_names_jitless(self) -> None:
        failure = self.assert_fails_closed(worker(9, stderr="node: bad option: --jitless\n"))
        self.assertIn("--jitless", failure["message"])
        self.assertIn("too old", failure["message"])

    def test_exit_zero_without_a_complete_json_result_fails_closed(self) -> None:
        incomplete = dict(VALID); del incomplete["declarations"]
        malformed = dict(VALID, diagnostics=[{"code": "x"}])  # missing status and lines
        for stdout in ("", "not json", "[]", json.dumps({"version": 5}), json.dumps(incomplete),
                       json.dumps(dict(VALID, exports={})), json.dumps(malformed)):
            with self.subTest(stdout=stdout):
                self.assert_fails_closed(worker(0, stdout=stdout))
        self.assertEqual([], worker(0, stdout=json.dumps(VALID)))  # a complete empty result is still fine

    def test_spawn_errors_other_than_missing_node_fail_closed(self) -> None:
        with patch("msdmd.native_code.subprocess.run", side_effect=PermissionError(13, "denied")):
            self.assert_fails_closed(read_typescript(Path("a.ts"), SOURCE, CONTEXT)[2])
        with patch("msdmd.native_code.subprocess.run", side_effect=FileNotFoundError("node")):
            with self.assertRaises(FileNotFoundError):  # read_native: reader_dependency_unavailable
                read_typescript(Path("a.ts"), SOURCE, CONTEXT)

    def test_worker_result_requires_an_explicit_exports_list(self) -> None:
        missing_exports = dict(VALID)
        del missing_exports["exports"]
        cases = [missing_exports, *(dict(VALID, exports=value) for value in (None, {}, "", 0, False))]
        for result in cases:
            with self.subTest(result=result):
                stdout = json.dumps(result)
                self.assertIsNone(native_code._worker_result(stdout))
                self.assert_fails_closed(worker(0, stdout=stdout))
        self.assertEqual(VALID, native_code._worker_result(json.dumps(VALID)))

    def test_worker_timeout_kills_and_fails_closed(self) -> None:
        with patch("msdmd.native_code.subprocess.run", side_effect=subprocess.TimeoutExpired(["node"], 120)) as run:
            failure = self.assert_fails_closed(read_typescript(Path("a.ts"), SOURCE, CONTEXT)[2], "typescript_reader_timeout")
        self.assertEqual(native_code.TYPESCRIPT_TIMEOUT_SECONDS, run.call_args.kwargs["timeout"])
        self.assertIn("120s", failure["message"])


class CliReaderFailureTests(unittest.TestCase):
    def repo(self, body: str) -> tuple[Path, Path, dict[str, str]]:
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        root = tmp / "repo"
        ts_repo(root)
        out = root / "repo_msdmd.ts"
        out.write_text("previous good artifact\n", encoding="utf-8")
        return root, out, fake_node(tmp / "bin", body)

    def run_repo(self, body: str, *extra: str) -> tuple[subprocess.CompletedProcess, Path]:
        root, out, env = self.repo(body)
        result = run_cli("--root", str(root), "--repo", "repo", "--out", str(out), *extra, env=env)
        self.assertEqual("previous good artifact\n", out.read_text(encoding="utf-8"))
        self.assertEqual(["a.ts", "repo_msdmd.ts"], sorted(p.name for p in root.iterdir() if p.name != ".git"))
        return result, out

    def test_cli_exits_3_and_writes_nothing(self) -> None:
        missing_exports = dict(VALID)
        del missing_exports["exports"]
        cases = {
            "exit 1": ("echo 'RangeError (secret-source-line)' >&2; exit 1", "exited with status 1"),
            "non-JSON on exit 0": ("cat >/dev/null; echo not-json", "without a complete JSON result"),
            "missing exports": (f"cat >/dev/null; echo '{json.dumps(missing_exports)}'", "without a complete JSON result"),
            "unsupported flag": ("echo 'node: bad option: --jitless' >&2; exit 9", "rejected --jitless"),
            "timeout": ("exec sleep 30", "exceeded 0.5s"),
        }
        for name, (body, expected) in cases.items():
            with self.subTest(name):
                result, _ = self.run_repo(body, "--typescript-timeout", "0.5")
                self.assertEqual(3, result.returncode, result.stderr)
                self.assertIn("native reader failed: ", result.stderr)
                self.assertIn(expected, result.stderr)
                self.assertIn("was not written", result.stderr)
                self.assertNotIn("secret-source-line", result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_cli_opt_out_reports_written_incomplete_output(self) -> None:
        for destination in ("file", "stdout"):
            for strict in (False, True):
                with self.subTest(destination=destination, strict=strict):
                    root, out, env = self.repo("exit 1")
                    extra = ["--out", str(out)] if destination == "file" else []
                    if strict:
                        extra.append("--strict")
                    result = run_cli("--root", str(root), "--repo", "repo", "--json",
                                     "--allow-missing-reader-runtimes", *extra, env=env)
                    self.assertEqual(2 if strict else 0, result.returncode, result.stderr)
                    rendered = out.read_text(encoding="utf-8") if destination == "file" else result.stdout
                    collection = json.loads(rendered)
                    self.assertIn("typescript_reader_failed", [d["code"] for d in collection["diagnostics"]])
                    self.assertIn("wrote incomplete output", result.stderr)
                    self.assertNotIn("was not written", result.stderr)
                    if destination == "stdout":
                        self.assertEqual("previous good artifact\n", out.read_text(encoding="utf-8"))

    def test_cli_opt_out_check_reports_no_write(self) -> None:
        result, _ = self.run_repo("exit 1", "--allow-missing-reader-runtimes", "--json", "--check")
        self.assertEqual(1, result.returncode, result.stderr)
        self.assertIn("checking incomplete output without writing", result.stderr)
        self.assertNotIn("writing incomplete output", result.stderr)
        self.assertNotIn("wrote incomplete output", result.stderr)

    def test_cli_opt_out_does_not_claim_a_write_when_helper_blocks(self) -> None:
        root, out, env = self.repo("exit 1")
        (root / "old-collection.ts").write_text("export const MSDMD_COLLECTION_HELPER_VERSION = 0;\n", encoding="utf-8")
        result = run_cli("--root", str(root), "--repo", "repo", "--out", str(out),
                         "--import-path", "./old-collection", "--allow-missing-reader-runtimes", env=env)
        self.assertEqual(4, result.returncode, result.stderr)
        self.assertEqual("previous good artifact\n", out.read_text(encoding="utf-8"))
        self.assertIn("was not written", result.stderr)
        self.assertNotIn("writing incomplete output", result.stderr)
        self.assertNotIn("wrote incomplete output", result.stderr)

    def test_timeout_must_be_positive_and_finite(self) -> None:
        for value in ("0", "-1", "nan", "inf", "soon"):
            with self.subTest(value=value):
                result = run_cli("--print-generator-identity", "--typescript-timeout", value)
                self.assertEqual(2, result.returncode)
                self.assertIn("--typescript-timeout", result.stderr)


class GeneratorIdentityProbeFailClosedTests(unittest.TestCase):
    def base_with_typescript(self) -> Path:
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: (self.restore(tmp), shutil.rmtree(tmp)))
        base = tmp / "msdmd"
        base.mkdir()
        shutil.copy(ROOT / "msdmd" / "collect.py", base / "collect.py")
        package = base / "node_modules" / "typescript"
        package.mkdir(parents=True)
        (package / "package.json").write_text('{"name":"typescript","version":"9.9.9"}', encoding="utf-8")
        (base / "node_modules" / ".bin").mkdir()
        (base / "node_modules" / ".bin" / "tsc").symlink_to("../typescript/bin/tsc")
        return base

    @staticmethod
    def restore(tmp: Path) -> None:
        # Owner-only modes: CodeQL flags world-readable chmod in tests too.
        for directory, dirnames, _ in os.walk(tmp):
            for name in dirnames:
                os.chmod(os.path.join(directory, name), 0o700)
        for path in tmp.rglob("package.json"):
            path.chmod(0o600)

    def test_untraversable_typescript_directory_raises_not_permission_error(self) -> None:
        if shutil.which("node") is None:
            self.skipTest("node is required")
        if os.geteuid() == 0:
            self.skipTest("root bypasses directory permissions")
        base = self.base_with_typescript()
        self.assertEqual("9.9.9", generator_identity_components(base)["typescript"])
        for locked, mode in ((base / "node_modules" / "typescript", 0o000), (base / "node_modules", 0o000),
                             (base / "node_modules" / "typescript", 0o600), (base / "node_modules" / "typescript" / "package.json", 0o000)):
            with self.subTest(locked=str(locked.relative_to(base)), mode=oct(mode)):
                locked.chmod(mode)
                try:
                    with self.assertRaises(GeneratorIdentityError) as raised:
                        generator_identity_components(base)
                    self.assertIn("typescript package", str(raised.exception))
                finally:
                    self.restore(base.parent)

    def test_cli_untraversable_typescript_exits_3_without_traceback(self) -> None:
        if shutil.which("node") is None or os.geteuid() == 0:
            self.skipTest("node and a non-root user are required")
        package = ROOT / "msdmd" / "node_modules" / "typescript"
        if not (package / "package.json").is_file():
            self.skipTest("npm ci --ignore-scripts --prefix msdmd has not been run")
        mode = package.stat().st_mode & 0o7777
        package.chmod(0o000)
        try:
            result = run_cli("--print-generator-identity")
        finally:
            package.chmod(mode)
        self.assertEqual(3, result.returncode, result.stderr)
        self.assertEqual("", result.stdout)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("typescript package is not readable", result.stderr)

    def test_installed_trees_are_not_walked_and_unreadable_sources_fail_closed(self) -> None:
        if os.geteuid() == 0:
            self.skipTest("root bypasses file permissions")
        base = self.base_with_typescript()
        absent = subprocess.CompletedProcess(["node"], 0, json.dumps({"node": "v0", "typescript": "absent"}), "")
        locked = base / "node_modules" / "locked"
        locked.mkdir()
        locked.chmod(0o000)  # pruned before it is entered, so never an error
        with patch("msdmd.collect.subprocess.run", return_value=absent):
            generator_identity_components(base)
            (base / "collect.py").chmod(0o000)
            try:
                with self.assertRaises(GeneratorIdentityError) as raised:
                    generator_identity_components(base)
            finally:
                (base / "collect.py").chmod(0o644)
        self.assertIn("collector sources are not readable", str(raised.exception))

    def test_probe_rejected_flag_and_timeout_raise(self) -> None:
        rejected = subprocess.CompletedProcess(["node"], 9, "", "node: bad option: --jitless\n")
        with patch("msdmd.collect.subprocess.run", return_value=rejected):
            with self.assertRaises(GeneratorIdentityError) as raised:
                generator_identity_components()
        self.assertIn("rejected --jitless", str(raised.exception))
        with patch("msdmd.collect.subprocess.run", side_effect=subprocess.TimeoutExpired(["node"], 1)) as run:
            with self.assertRaises(GeneratorIdentityError) as raised:
                generator_identity_components()
        self.assertIn("exceeded", str(raised.exception))
        self.assertEqual(native_code.TYPESCRIPT_TIMEOUT_SECONDS, run.call_args.kwargs["timeout"])

    def test_cli_probe_timeout_exits_3(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env = fake_node(Path(tmp) / "bin", "exec sleep 30")
            result = run_cli("--print-generator-identity", "--typescript-timeout", "0.5", env=env)
        self.assertEqual(3, result.returncode, result.stderr)
        self.assertEqual("", result.stdout)
        self.assertIn("node probe exceeded 0.5s", result.stderr)


if __name__ == "__main__":
    unittest.main()

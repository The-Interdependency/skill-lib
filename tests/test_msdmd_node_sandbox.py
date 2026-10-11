"""Node under a W^X sandbox (systemd MemoryDenyWriteExecute) fails closed.

Usage: python -m unittest tests.test_msdmd_node_sandbox
Signal deaths are simulated with a fake ``node`` that kills itself or with a
mocked ``subprocess.run``. Where the kernel offers PR_SET_MDWE (Linux 6.3+),
one test also runs the real collector under the same restriction systemd uses.
"""
from __future__ import annotations

import ctypes
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from msdmd import collect as collect_module
from msdmd.collect import GeneratorIdentityError, generator_identity_components, runtime_unavailable
from msdmd.native_code import NODE_ARGV, node_signal, read_typescript

ROOT = Path(__file__).resolve().parents[1]
CONTEXT = {"repo": "fixture", "revision": "r", "file": "a.ts", "content_sha256": "0" * 64,
           "codeowners_source": None, "configuration_sha256": "0" * 64}
PR_SET_MDWE, PR_MDWE_REFUSE_EXEC_GAIN = 65, 1
TS_FIXTURE = "/** Adds one. */\nexport function inc(n: number): number {\n  return n + 1;\n}\n"


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid", *args],
                   check=True, capture_output=True)


def ts_repo(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "a.ts").write_text(TS_FIXTURE, encoding="utf-8")
    git(root, "init", "-q")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "fixture")


def self_killing_node(directory: Path, signame: str = "TRAP") -> dict[str, str]:
    """PATH with a ``node`` that dies by a signal, as V8 does under MemoryDenyWriteExecute."""
    directory.mkdir(parents=True, exist_ok=True)
    node = directory / "node"
    node.write_text(f"#!/bin/sh\nkill -{signame} $$\n", encoding="utf-8")
    node.chmod(0o755)
    return dict(os.environ, PATH=os.pathsep.join([str(directory), os.environ.get("PATH", "")]))


def run_cli(*args: str, env: dict[str, str] | None = None, preexec_fn=None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "msdmd.collect", *args], cwd=ROOT, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, text=True, env=env, preexec_fn=preexec_fn)


def _refuse_exec_gain() -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(PR_SET_MDWE, PR_MDWE_REFUSE_EXEC_GAIN, 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), "PR_SET_MDWE failed")


def _mdwe_available() -> bool:
    if not sys.platform.startswith("linux") or shutil.which("node") is None:
        return False
    try:
        probe = subprocess.run([sys.executable, "-c", "pass"], preexec_fn=_refuse_exec_gain, capture_output=True)
    except (OSError, subprocess.SubprocessError):
        return False
    return probe.returncode == 0


class NodeSignalTests(unittest.TestCase):
    def test_signal_deaths_are_named_and_ordinary_exits_are_not(self) -> None:
        self.assertEqual("SIGTRAP", node_signal(-signal.SIGTRAP))
        self.assertEqual("SIGTRAP", node_signal(128 + signal.SIGTRAP))  # shell or shim wrapper: exit 133
        self.assertEqual("SIGKILL", node_signal(-signal.SIGKILL))
        for ordinary in (0, 1, 2, 127, 128):
            self.assertIsNone(node_signal(ordinary))
        self.assertIsNone(node_signal(255))

    def test_node_always_runs_jitless(self) -> None:
        self.assertEqual(("node", "--jitless"), NODE_ARGV)
        completed = subprocess.CompletedProcess(args=["node"], returncode=0, stdout='{"node":"v0","typescript":"0"}', stderr="")
        with patch("msdmd.native_code.run_node", return_value=completed) as probe:
            generator_identity_components()
        self.assertEqual(["node", "--jitless", "-e"], probe.call_args.args[0][:3])
        failed = subprocess.CompletedProcess(args=["node"], returncode=1, stdout="", stderr="")
        with patch("msdmd.native_code.run_node", return_value=failed) as worker:
            read_typescript(Path("a.ts"), b"export const a = 1;\n", CONTEXT)
        self.assertEqual(["node", "--jitless"], worker.call_args.args[0][:2])


class TypeScriptWorkerSignalTests(unittest.TestCase):
    def test_signal_killed_worker_is_runtime_unavailable(self) -> None:
        for returncode in (-signal.SIGTRAP, 128 + signal.SIGTRAP):
            completed = subprocess.CompletedProcess(args=["node"], returncode=returncode, stdout="",
                                                    stderr="# Fatal error in , line 0\n# secret-source-line")
            with patch("msdmd.native_code.run_node", return_value=completed):
                diagnostics = read_typescript(Path("a.ts"), b"export const a = 1;\n", CONTEXT)[2]
            self.assertEqual(["node_runtime_unavailable"], [d["code"] for d in diagnostics])
            self.assertIn("SIGTRAP", diagnostics[0]["message"])
            self.assertTrue(runtime_unavailable({"diagnostics": diagnostics}))
            self.assertNotIn("secret-source-line", json.dumps(diagnostics))

    def test_cli_exits_3_and_writes_nothing_when_node_is_killed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            ts_repo(root)
            out = root / "repo_msdmd.ts"
            out.write_text("previous good artifact\n", encoding="utf-8")
            env = self_killing_node(Path(tmp) / "bin")
            result = run_cli("--root", str(root), "--repo", "repo", "--out", str(out), env=env)
            self.assertEqual(3, result.returncode, result.stderr)
            self.assertIn("killed by SIGTRAP", result.stderr)
            self.assertEqual("previous good artifact\n", out.read_text(encoding="utf-8"))
            self.assertEqual(["a.ts", "repo_msdmd.ts"], sorted(p.name for p in root.iterdir() if p.name != ".git"))
            checked = run_cli("--root", str(root), "--repo", "repo", "--out", str(out), "--check", env=env)
            self.assertEqual(3, checked.returncode, checked.stderr)


class GeneratorIdentityProbeTests(unittest.TestCase):
    def probe(self, completed: subprocess.CompletedProcess):
        with patch("msdmd.native_code.run_node", return_value=completed):
            return generator_identity_components()

    def test_failed_probe_raises_instead_of_reporting_absent(self) -> None:
        cases = {
            "killed by SIGTRAP": subprocess.CompletedProcess(["node"], -signal.SIGTRAP, "", ""),
            "killed by SIGTRAP ": subprocess.CompletedProcess(["node"], 133, "", ""),
            "exited with status 1": subprocess.CompletedProcess(["node"], 1, "", ""),
            "unexpected output": subprocess.CompletedProcess(["node"], 0, "not json", ""),
            "unexpected output ": subprocess.CompletedProcess(["node"], 0, '{"node":"v24"}', ""),
        }
        for expected, completed in cases.items():
            with self.assertRaises(GeneratorIdentityError) as raised:
                self.probe(completed)
            self.assertIn(expected.strip(), str(raised.exception))
        with patch("msdmd.native_code.run_node", side_effect=OSError(12, "Cannot allocate memory")):
            with self.assertRaises(GeneratorIdentityError):
                generator_identity_components()

    def test_node_missing_from_path_is_still_absent(self) -> None:
        with patch("msdmd.native_code.run_node", side_effect=FileNotFoundError("node")):
            components = generator_identity_components()
        self.assertEqual(("absent", "absent"), (components["node"], components["typescript"]))

    def test_cli_exits_3_without_printing_an_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env = self_killing_node(Path(tmp) / "bin")
            for extra in ((), ("--json",)):
                result = run_cli("--print-generator-identity", *extra, env=env)
                self.assertEqual(3, result.returncode, result.stderr)
                self.assertEqual("", result.stdout)
                self.assertIn("node probe was killed by SIGTRAP", result.stderr)
        self.assertIs(collect_module.GeneratorIdentityError, GeneratorIdentityError)


@unittest.skipUnless(_mdwe_available(), "PR_SET_MDWE (Linux 6.3+) and node are required")
class RealMemoryDenyWriteExecuteTests(unittest.TestCase):
    """The restriction systemd MemoryDenyWriteExecute=yes applies, set with prctl."""

    def test_jitless_collection_is_byte_identical_under_mdwe(self) -> None:
        typescript = ROOT / "msdmd" / "node_modules" / "typescript" / "package.json"
        if not typescript.is_file():
            self.skipTest("npm ci --ignore-scripts --prefix msdmd has not been run")
        jit = subprocess.run(["node", "-e", "0"], preexec_fn=_refuse_exec_gain, capture_output=True)
        self.assertIsNotNone(node_signal(jit.returncode), "a JIT node should be killed under MDWE")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            ts_repo(root)
            plain = run_cli("--root", str(root), "--repo", "repo", "--json")
            sandboxed = run_cli("--root", str(root), "--repo", "repo", "--json", preexec_fn=_refuse_exec_gain)
        self.assertEqual(0, plain.returncode, plain.stderr)
        self.assertEqual(0, sandboxed.returncode, sandboxed.stderr)
        self.assertEqual(plain.stdout, sandboxed.stdout)
        self.assertIn("typescript-compiler", plain.stdout)
        identity = run_cli("--print-generator-identity", "--json")
        identity_sandboxed = run_cli("--print-generator-identity", "--json", preexec_fn=_refuse_exec_gain)
        self.assertEqual(0, identity_sandboxed.returncode, identity_sandboxed.stderr)
        self.assertEqual(identity.stdout, identity_sandboxed.stdout)
        self.assertNotEqual("absent", json.loads(identity_sandboxed.stdout)["typescript"])


if __name__ == "__main__":
    unittest.main()

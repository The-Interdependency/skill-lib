"""Deep valid TypeScript is a per-file diagnostic; timeouts kill the whole process group.

Usage: python -m unittest tests.test_msdmd_reader_depth_and_timeout
Deep inputs (long ``+`` chains, nested ifs, object and array literals)
exhaust the recursive compiler/visitor stack under ``--jitless``. That file
gets ``typescript_input_too_deep`` and collection continues (exit 0, or 2
under ``--strict``), never exit 3. Any other worker crash still exits 3. A
timed-out worker started through a version-manager style shim must not leave
the real node (a grandchild) running.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from msdmd import native_code
from msdmd.collect import GeneratorIdentityError, generator_identity_components, runtime_unavailable
from msdmd.native_code import TOO_DEEP_CODE, read_typescript
from tests.test_msdmd_node_sandbox import CONTEXT, ROOT, git, run_cli

WORKER = ROOT / "msdmd" / "typescript-reader.cjs"
TYPESCRIPT = ROOT / "msdmd" / "node_modules" / "typescript" / "package.json"
# Far past the depths Review reproduced (about 1200-1500 chained terms, 570
# ifs, 500 objects, 650 arrays) so a larger runner stack still overflows.
DEEP = {
    "plus_chain.ts": "export const a = " + " + ".join(["1"] * 6000) + ";\n",
    "nested_ifs.ts": "export function f(x: number) {\n" + "if (x) {\n" * 3000 + "x++;\n" + "}\n" * 3000 + "}\n",
    "nested_objects.ts": "export const o = " + "{a: " * 3000 + "1" + "}" * 3000 + ";\n",
    "nested_arrays.ts": "export const r = " + "[" * 3000 + "1" + "]" * 3000 + ";\n",
}
SHALLOW = "/** Adds one. */\nexport function inc(n: number): number {\n  return n + 1;\n}\n"


def _real_reader_available() -> bool:
    return shutil.which("node") is not None and TYPESCRIPT.is_file()


def _gone(pid: int) -> bool:
    """True when ``pid`` no longer exists or is only an unreaped zombie."""
    try:
        state = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
    except (FileNotFoundError, ProcessLookupError):
        return True
    return state in {"Z", "X"}


def _wait_gone(pid: int, seconds: float = 5.0) -> bool:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if _gone(pid):
            return True
        time.sleep(0.05)
    return _gone(pid)


@unittest.skipUnless(_real_reader_available(), "node and npm ci --ignore-scripts --prefix msdmd are required")
class DeepInputTests(unittest.TestCase):
    def test_each_deep_shape_is_a_per_file_diagnostic(self) -> None:
        for name, text in DEEP.items():
            with self.subTest(name):
                facts, _, diagnostics = read_typescript(Path(name), text.encode("utf-8"), dict(CONTEXT, file=name))
                self.assertEqual([], facts)
                self.assertEqual([TOO_DEEP_CODE], [d["code"] for d in diagnostics])
                self.assertEqual(("error", "unsupported"), (diagnostics[0]["severity"], diagnostics[0]["status"]))
                self.assertFalse(runtime_unavailable({"diagnostics": diagnostics}), "must not map to exit 3")

    def test_cli_collects_other_files_and_does_not_exit_3(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            for name, text in DEEP.items():
                (root / name).write_text(text, encoding="utf-8")
            (root / "shallow.ts").write_text(SHALLOW, encoding="utf-8")
            git(root, "init", "-q")
            git(root, "add", "-A")
            git(root, "commit", "-q", "-m", "fixture")
            result = run_cli("--root", str(root), "--repo", "repo", "--json")
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertNotIn("native reader failed", result.stderr)
            collection = json.loads(result.stdout)
            deep = [d for d in collection["diagnostics"] if d["code"] == TOO_DEEP_CODE]
            self.assertEqual(sorted(DEEP), sorted(d["source"]["file"] for d in deep))
            shallow = [f for f in collection["facts"] if f["source"]["file"] == "shallow.ts"
                       and f["extraction"]["reader_id"] == "typescript-compiler"]
            self.assertIn("inc", {f["native"]["value"].get("name") for f in shallow if f["kind"] == "exported-declaration"})
            strict = run_cli("--root", str(root), "--repo", "repo", "--json", "--strict")
            self.assertEqual(2, strict.returncode, strict.stderr)  # an error diagnostic, not a missing runtime

    def test_worker_rethrows_crashes_that_are_not_stack_overflow(self) -> None:
        # Run a copy of the real worker against stub compilers: only a call-stack
        # RangeError becomes a per-file diagnostic; anything else still crashes.
        cases = {
            "throw new RangeError('Maximum call stack size exceeded')": (0, TOO_DEEP_CODE),
            "throw new RangeError('Invalid array length')": (1, None),
            "throw new TypeError('compiler bug')": (1, None),
        }
        for throw, (expected_status, expected_code) in cases.items():
            with self.subTest(throw), tempfile.TemporaryDirectory() as tmp:
                base = Path(tmp)
                shutil.copy(WORKER, base / WORKER.name)
                stub = base / "node_modules" / "typescript"
                stub.mkdir(parents=True)
                (stub / "package.json").write_text('{"name":"typescript","version":"0.0.0","main":"index.js"}', encoding="utf-8")
                (stub / "index.js").write_text(
                    f"module.exports = {{version: '0.0.0', ScriptTarget: {{Latest: 99}}, createSourceFile() {{ {throw}; }}}};\n",
                    encoding="utf-8")
                done = subprocess.run([*native_code.NODE_ARGV, str(base / WORKER.name)], cwd=base, capture_output=True, text=True,
                                      input=json.dumps({"path": "a.ts", "text": "a\nb\n"}), timeout=60)
                self.assertEqual(expected_status, done.returncode, done.stderr)
                if expected_code:
                    diagnostics = json.loads(done.stdout)["diagnostics"]
                    self.assertEqual([(expected_code, "unsupported", 1, 3)],
                                     [(d["code"], d["status"], d["start_line"], d["end_line"]) for d in diagnostics])

    def test_real_worker_crash_still_exits_3(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            (root / "shallow.ts").write_text(SHALLOW, encoding="utf-8")
            git(root, "init", "-q")
            git(root, "add", "-A")
            git(root, "commit", "-q", "-m", "fixture")
            shim = Path(tmp) / "bin"
            shim.mkdir()
            node = shim / "node"
            # Real node, but the worker dies before writing a result.
            node.write_text(f"#!/bin/sh\nexec {shutil.which('node')} -e \"process.exit(7)\"\n", encoding="utf-8")
            node.chmod(0o700)
            env = dict(os.environ, PATH=os.pathsep.join([str(shim), os.environ.get("PATH", "")]))
            result = run_cli("--root", str(root), "--repo", "repo", "--json", env=env)
        self.assertEqual(3, result.returncode, result.stderr)
        self.assertIn("exited with status 7", result.stderr)


@unittest.skipUnless(os.name == "posix" and Path("/proc/self/stat").exists(), "POSIX process groups and /proc are required")
class TimeoutKillsProcessGroupTests(unittest.TestCase):
    def shim(self, tmp: Path) -> tuple[dict[str, str], Path]:
        """A ``node`` shim that, like a version manager, runs the real program as a grandchild."""
        shim = tmp / "bin"
        shim.mkdir()
        pidfile = tmp / "grandchild.pid"
        node = shim / "node"
        node.write_text(f"#!/bin/sh\nsleep 300 &\necho $! > {pidfile}\nwait\n", encoding="utf-8")
        node.chmod(0o700)
        return {"PATH": os.pathsep.join([str(shim), os.environ.get("PATH", "")])}, pidfile

    def grandchild(self, pidfile: Path) -> int:
        self.assertTrue(pidfile.is_file(), "shim did not start its grandchild")
        pid = int(pidfile.read_text().strip())
        self.addCleanup(lambda: _gone(pid) or os.kill(pid, 9))
        return pid

    def test_worker_timeout_kills_the_shims_grandchild(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env, pidfile = self.shim(Path(tmp))
            with patch.dict(os.environ, env), patch.object(native_code, "TYPESCRIPT_TIMEOUT_SECONDS", 1.0):
                started = time.monotonic()
                diagnostics = read_typescript(Path("a.ts"), b"export const a = 1;\n", CONTEXT)[2]
                elapsed = time.monotonic() - started
            self.assertEqual(["typescript_reader_timeout"], [d["code"] for d in diagnostics])
            self.assertLess(elapsed, 30, "the timeout must not wait for the grandchild")
            self.assertTrue(_wait_gone(self.grandchild(pidfile)), "grandchild node survived the timeout")

    def test_probe_timeout_kills_the_shims_grandchild(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env, pidfile = self.shim(Path(tmp))
            with patch.dict(os.environ, env), patch.object(native_code, "TYPESCRIPT_TIMEOUT_SECONDS", 1.0):
                with self.assertRaises(GeneratorIdentityError) as raised:
                    generator_identity_components()
            self.assertIn("exceeded", str(raised.exception))
            self.assertTrue(_wait_gone(self.grandchild(pidfile)), "grandchild node survived the probe timeout")

    def test_cli_timeout_leaves_no_grandchild(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env, pidfile = self.shim(Path(tmp))
            result = run_cli("--print-generator-identity", "--typescript-timeout", "1", env=dict(os.environ, **env))
            self.assertEqual(3, result.returncode, result.stderr)
            self.assertTrue(_wait_gone(self.grandchild(pidfile)), "grandchild node survived the CLI timeout")


if __name__ == "__main__":
    unittest.main()

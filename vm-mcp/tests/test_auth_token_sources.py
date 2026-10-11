"""Bearer scheme parsing, installer token/secret handling, and service token loading.

Usage: PYTHONPATH=vm-mcp python -m unittest discover -s vm-mcp/tests
Installer functions are extracted from install.sh and run without root; no
real credential is used.
"""
from __future__ import annotations

import ast
import asyncio
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from auth import BearerAuth, configured_token

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "install.sh"
TOKEN = "t" * 40


def _call(header: bytes | None) -> bool:
    called = []

    async def app(scope, receive, send):
        called.append(scope)

    async def receive():
        raise AssertionError("unauthenticated request body was read")

    async def send(message):
        pass

    headers = [] if header is None else [(b"authorization", header)]
    asyncio.run(BearerAuth(app, TOKEN.encode())({"type": "http", "headers": headers}, receive, send))
    return bool(called)


def run_installer_functions(body: str, *, env: dict[str, str] | None = None, stdin: str = "",
                            names: tuple[str, ...] = ("_resolve_auth_token", "load_auth_token",
                                                      "write_secret_file", "install_runtime")) -> subprocess.CompletedProcess:
    """Source the named install.sh functions into a fresh bash, then run body."""
    extract = "; ".join(f"source <(sed -n '/^{name}() {{/,/^}}/p' \"$1\")" for name in names)
    clean = {k: v for k, v in os.environ.items() if not k.startswith("VM_MCP_AUTH_TOKEN")}
    return subprocess.run(["bash", "-c", f"{extract}; {body}", "installer", str(INSTALLER)], input=stdin,
                          env=dict(clean, **(env or {})), capture_output=True, text=True)


class BearerSchemeTests(unittest.TestCase):
    def test_scheme_is_case_insensitive_and_token_exact(self) -> None:
        for scheme in (b"Bearer", b"bearer", b"BEARER", b"bEaReR"):
            with self.subTest(scheme=scheme):
                self.assertTrue(_call(scheme + b" " + TOKEN.encode()))
        self.assertTrue(_call(b"Bearer   " + TOKEN.encode()))  # 1*SP
        for header in (None, b"", b"Bearer", b"Bearer ", b"Basic " + TOKEN.encode(), b"Bearer" + TOKEN.encode(),
                       b"Bearer " + TOKEN.upper().encode(), b"Bearer " + TOKEN.encode() + b"x",
                       b"Bearer " + TOKEN.encode()[:-1], b"Bearers " + TOKEN.encode()):
            with self.subTest(header=header):
                self.assertFalse(_call(header))


class InstallerTokenSourceTests(unittest.TestCase):
    def resolve(self, env: dict[str, str], stdin: str = "") -> subprocess.CompletedProcess:
        return run_installer_functions('load_auth_token && printf %s "$AUTH_TOKEN"', env=env, stdin=stdin)

    def token_file(self, mode: int, content: str = TOKEN + "\n") -> Path:
        directory = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, directory)
        path = directory / "token"
        path.write_text(content, encoding="utf-8", newline="")
        path.chmod(mode)
        return path

    def test_file_stdin_and_environment_sources(self) -> None:
        cases = [
            ({"VM_MCP_AUTH_TOKEN_FILE": str(self.token_file(0o600))}, ""),
            ({"VM_MCP_AUTH_TOKEN_FILE": str(self.token_file(0o400, TOKEN))}, ""),  # no trailing newline
            ({"VM_MCP_AUTH_TOKEN_STDIN": "1"}, TOKEN + "\n"),
            ({"VM_MCP_AUTH_TOKEN": TOKEN}, ""),
        ]
        for env, stdin in cases:
            with self.subTest(env=sorted(env)):
                result = self.resolve(env, stdin)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual(TOKEN, result.stdout)

    def test_unsafe_missing_or_ambiguous_sources_fail_closed(self) -> None:
        directory = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, directory)
        link = directory / "link"
        link.symlink_to(self.token_file(0o600))
        cases = {
            "nothing": {},
            "group readable": {"VM_MCP_AUTH_TOKEN_FILE": str(self.token_file(0o640))},
            "world readable": {"VM_MCP_AUTH_TOKEN_FILE": str(self.token_file(0o604))},
            "symlink": {"VM_MCP_AUTH_TOKEN_FILE": str(link)},
            "missing file": {"VM_MCP_AUTH_TOKEN_FILE": str(directory / "absent")},
            "empty file": {"VM_MCP_AUTH_TOKEN_FILE": str(self.token_file(0o600, ""))},
            "short": {"VM_MCP_AUTH_TOKEN_FILE": str(self.token_file(0o600, "short\n"))},
            "two sources": {"VM_MCP_AUTH_TOKEN": TOKEN, "VM_MCP_AUTH_TOKEN_STDIN": "1"},
            "stdin=yes": {"VM_MCP_AUTH_TOKEN_STDIN": "yes"},
            "stdin=0 with env": {"VM_MCP_AUTH_TOKEN_STDIN": "0", "VM_MCP_AUTH_TOKEN": TOKEN},
        }
        for name, env in cases.items():
            with self.subTest(name):
                result = self.resolve(env, TOKEN + "\n")
                self.assertEqual(3, result.returncode, result.stdout)
                self.assertEqual("", result.stdout)
                self.assertNotIn(TOKEN, result.stderr)
        result = self.resolve({"VM_MCP_AUTH_TOKEN_STDIN": "yes"})
        self.assertIn("VM_MCP_AUTH_TOKEN_STDIN must be unset or 1", result.stderr)

    def test_crlf_token_file_gets_a_clear_message(self) -> None:
        result = self.resolve({"VM_MCP_AUTH_TOKEN_FILE": str(self.token_file(0o600, TOKEN + "\r\n"))})
        self.assertEqual(3, result.returncode)
        self.assertIn("CRLF", result.stderr)
        self.assertIn("LF endings", result.stderr)
        self.assertNotIn(TOKEN, result.stderr)

    def test_token_file_is_opened_once_and_checked_through_the_descriptor(self) -> None:
        text = INSTALLER.read_text(encoding="utf-8")
        body = text[text.index("_resolve_auth_token() {"):text.index("load_auth_token() {")]
        self.assertEqual(1, body.count('exec {fd}<"$file"'))
        self.assertIn('stat -L -c \'%u %a %F %d:%i\' "/dev/fd/$fd"', body)
        self.assertIn('"$path_id" != "regular_file $fd_id"', body)
        self.assertIn('read -r token <&"$fd"', body)
        self.assertNotIn('< "$file"', body)

    def test_xtrace_never_prints_the_token_and_is_restored(self) -> None:
        for env, stdin in [({"VM_MCP_AUTH_TOKEN": TOKEN}, ""),
                           ({"VM_MCP_AUTH_TOKEN_FILE": str(self.token_file(0o600))}, ""),
                           ({"VM_MCP_AUTH_TOKEN_STDIN": "1"}, TOKEN + "\n"),
                           ({"VM_MCP_AUTH_TOKEN": "short"}, "")]:
            with self.subTest(env=sorted(env)):
                result = run_installer_functions(
                    'set -x; load_auth_token; rc=$?; { set +x; } 2>/dev/null; printf "rc=%s\\n" "$rc"',
                    env=env, stdin=stdin)
                self.assertIn("+ load_auth_token", result.stderr)  # tracing was on
                self.assertNotIn(TOKEN, result.stderr, "token traced")
                self.assertIn("rc=", result.stdout)
        # The caller's xtrace state is restored after the token functions.
        result = run_installer_functions('set -x; VM_MCP_AUTH_TOKEN=' + TOKEN + ' load_auth_token; '
                                         'case $- in *x*) echo still-tracing;; esac')
        self.assertIn("still-tracing", result.stdout)
        result = run_installer_functions('load_auth_token; case $- in *x*) echo tracing;; *) echo quiet;; esac',
                                         env={"VM_MCP_AUTH_TOKEN": TOKEN})
        self.assertIn("quiet", result.stdout)

    def test_installer_writes_token_with_xtrace_off_and_not_into_the_env_file(self) -> None:
        text = INSTALLER.read_text(encoding="utf-8")
        self.assertLess(text.index("load_auth_token || exit 3"), text.index("write_secret_file /etc/vm-mcp.env"))
        self.assertIn('set +x\nprintf \'%s\\n\' "$AUTH_TOKEN" | write_secret_file "$CREDENTIAL_FILE" || exit 6\nunset AUTH_TOKEN', text)
        env_block = text[text.index("write_secret_file /etc/vm-mcp.env <<EOF || exit 6"):]
        env_block = env_block[:env_block.index("\nEOF\n")]
        self.assertNotIn("AUTH_TOKEN", env_block)
        self.assertNotIn("cat > /etc/vm-mcp.env", text)
        self.assertNotIn("chmod 0600 /etc/vm-mcp.env", text)


class InstallerSecretFileTests(unittest.TestCase):
    def test_secret_file_replaces_a_loosened_file_with_a_new_0600_inode(self) -> None:
        directory = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, directory)
        dest = directory / "vm-mcp.env"
        dest.write_text("OLD=1\n", encoding="utf-8")
        dest.chmod(0o644)
        before = dest.stat().st_ino
        result = run_installer_functions(f'umask 0022; printf "NEW=1\\n" | write_secret_file "{dest}"; '
                                         'echo "rc=$? umask=$(umask)"')
        self.assertIn("rc=0 umask=0022", result.stdout, result.stderr)
        self.assertEqual("NEW=1\n", dest.read_text(encoding="utf-8"))
        self.assertEqual(0o600, stat.S_IMODE(dest.stat().st_mode))
        self.assertNotEqual(before, dest.stat().st_ino)
        self.assertEqual(["vm-mcp.env"], sorted(p.name for p in directory.iterdir()))

    def test_failed_secret_write_leaves_no_temp_file(self) -> None:
        directory = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, directory)
        result = run_installer_functions(f'false | write_secret_file "{directory}/missing-dir/x"; echo "rc=$?"')
        self.assertNotIn("rc=0", result.stdout)
        self.assertEqual([], list(directory.iterdir()))


class InstallerUmaskTests(unittest.TestCase):
    def test_restrictive_umask_is_scoped_to_secret_writes(self) -> None:
        text = INSTALLER.read_text(encoding="utf-8")
        umask_lines = [line.strip() for line in text.splitlines() if line.strip().startswith("umask ")]
        self.assertEqual(["umask 0022", "umask 0077", "umask 0022"], umask_lines)
        secret = text[text.index("write_secret_file() {"):]
        self.assertIn("umask 0077", secret[:secret.index("\n}\n")])
        self.assertIn("  (\n    umask 0077", secret)  # subshell: does not leak
        self.assertLess(text.index("install_runtime() {"), text.index('install_runtime "$INSTALL_ROOT"'))

    @unittest.skipUnless(shutil.which("python3"), "python3 required")
    def test_venv_is_readable_and_executable_by_the_service_user_under_a_0077_shell(self) -> None:
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root)
        (root / "requirements.txt").write_text("", encoding="utf-8")
        result = run_installer_functions(f'umask 0077; install_runtime "{root}"; echo "rc=$? umask=$(umask)"',
                                         env={"PIP_NO_INDEX": "1", "PIP_DISABLE_PIP_VERSION_CHECK": "1"},
                                         names=("install_runtime",))
        self.assertIn("rc=0 umask=0077", result.stdout, result.stderr)
        venv = root / ".venv"
        for path in [venv, venv / "bin", venv / "lib", venv / "pyvenv.cfg"]:
            mode = stat.S_IMODE(path.stat().st_mode)
            with self.subTest(path=path.name):
                self.assertTrue(mode & stat.S_IROTH, oct(mode))
                if path.is_dir():
                    self.assertTrue(mode & stat.S_IXOTH, oct(mode))
        python = venv / "bin" / "python"
        self.assertTrue(stat.S_IMODE(python.stat().st_mode) & stat.S_IXOTH)
        for directory, _, files in os.walk(venv / "lib"):
            mode = stat.S_IMODE(os.stat(directory).st_mode)
            self.assertEqual(0o005, mode & 0o005, directory)
            for name in files:
                self.assertTrue(os.lstat(os.path.join(directory, name)).st_mode & stat.S_IROTH, name)


class ServiceTokenLoadingTests(unittest.TestCase):
    def run_loader(self, *, stdin, env: dict[str, str]) -> subprocess.CompletedProcess:
        code = ("import os, sys; sys.path.insert(0, sys.argv[1]); from auth import configured_token;\n"
                "token = configured_token().decode()\n"
                "print(token, 'VM_MCP_AUTH_TOKEN' in os.environ, 'VM_MCP_AUTH_TOKEN_SOURCE' in os.environ,"
                " os.path.realpath('/proc/self/fd/0'))")
        clean = {k: v for k, v in os.environ.items() if not k.startswith("VM_MCP_AUTH_TOKEN")}
        return subprocess.run([sys.executable, "-c", code, str(ROOT)], stdin=stdin, env=dict(clean, **env),
                              capture_output=True, text=True)

    def test_unit_hands_over_a_root_only_file_as_stdin(self) -> None:
        unit = (ROOT / "systemd" / "vm-mcp.service").read_text(encoding="utf-8")
        self.assertIn("StandardInput=file:/etc/credstore/vm-mcp-token", unit)
        self.assertIn("Environment=VM_MCP_AUTH_TOKEN_SOURCE=stdin", unit)
        self.assertIn("StandardOutput=journal", unit)
        self.assertNotIn("LoadCredential", unit.replace("A LoadCredential= copy", ""))
        self.assertIn("CREDENTIAL_FILE=/etc/credstore/vm-mcp-token", INSTALLER.read_text(encoding="utf-8"))

    def test_stdin_token_file_is_read_once_and_stdin_closed(self) -> None:
        with tempfile.TemporaryFile("w+") as handle:
            handle.write(TOKEN + "\n")
            handle.seek(0)
            result = self.run_loader(stdin=handle, env={"VM_MCP_AUTH_TOKEN_SOURCE": "stdin",
                                                        "VM_MCP_AUTH_TOKEN": "z" * 40})
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual([TOKEN, "False", "False", "/dev/null"], result.stdout.split())
        self.assertIn("VM_MCP_AUTH_TOKEN is ignored", result.stderr)
        self.assertNotIn(TOKEN, result.stderr)

    def test_stdin_source_rejects_pipes_bad_tokens_and_unknown_sources(self) -> None:
        result = self.run_loader(stdin=subprocess.PIPE, env={"VM_MCP_AUTH_TOKEN_SOURCE": "stdin"})
        self.assertNotEqual(0, result.returncode)
        self.assertIn("requires stdin to be the root-only token file", result.stderr)
        for content in ["", "short\n", TOKEN + "\r\n", "x" * 257]:
            with self.subTest(content=content[:8]), tempfile.TemporaryFile("w+") as handle:
                handle.write(content)
                handle.seek(0)
                result = self.run_loader(stdin=handle, env={"VM_MCP_AUTH_TOKEN_SOURCE": "stdin"})
                self.assertNotEqual(0, result.returncode)
                self.assertIn("must hold an operator-provisioned", result.stderr)
        result = self.run_loader(stdin=subprocess.DEVNULL, env={"VM_MCP_AUTH_TOKEN_SOURCE": "credential"})
        self.assertIn("must be unset or stdin", result.stderr)

    def test_environment_fallback_warns(self) -> None:
        with patch.dict(os.environ, {"VM_MCP_AUTH_TOKEN": TOKEN}), self.assertLogs("vm-mcp", "WARNING") as logs:
            os.environ.pop("VM_MCP_AUTH_TOKEN_SOURCE", None)
            self.assertEqual(TOKEN.encode(), configured_token())
            self.assertNotIn("VM_MCP_AUTH_TOKEN", os.environ)
        self.assertIn("falling back to VM_MCP_AUTH_TOKEN", logs.output[0])
        self.assertNotIn(TOKEN, logs.output[0])


class ServerDumpabilityTests(unittest.TestCase):
    def test_prctl_is_the_first_statement_before_any_heavy_import(self) -> None:
        module = ast.parse((ROOT / "server.py").read_text(encoding="utf-8"))
        body = [node for node in module.body
                if not (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant))
                and not (isinstance(node, ast.ImportFrom) and node.module == "__future__")]
        self.assertIsInstance(body[0], ast.Import)
        self.assertEqual("ctypes", body[0].names[0].name)
        self.assertIsInstance(body[1], ast.If)
        guard = ast.unparse(body[1])
        self.assertIn("prctl(4, 0, 0, 0, 0)", guard)
        self.assertIn("SystemExit", guard)


if __name__ == "__main__":
    unittest.main()

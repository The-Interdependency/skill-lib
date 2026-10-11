"""Bearer scheme parsing and installer token sources.

Usage: PYTHONPATH=vm-mcp python -m unittest discover -s vm-mcp/tests
The installer's resolve_auth_token function is extracted and run without
root; no real credential is used.
"""
from __future__ import annotations

import asyncio
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from auth import BearerAuth

ROOT = Path(__file__).resolve().parents[1]
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
        script = ("source <(sed -n '/^resolve_auth_token() {/,/^}/p' \"$1\"); "
                  "resolve_auth_token")
        clean = {k: v for k, v in os.environ.items() if not k.startswith("VM_MCP_AUTH_TOKEN")}
        return subprocess.run(["bash", "-c", script, "resolve", str(ROOT / "install.sh")], input=stdin,
                              env=dict(clean, **env), capture_output=True, text=True)

    def token_file(self, mode: int, content: str = TOKEN + "\n") -> Path:
        directory = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, directory)
        path = directory / "token"
        path.write_text(content, encoding="utf-8")
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
            "short": {"VM_MCP_AUTH_TOKEN_FILE": str(self.token_file(0o600, "short\n"))},
            "two sources": {"VM_MCP_AUTH_TOKEN": TOKEN, "VM_MCP_AUTH_TOKEN_STDIN": "1"},
        }
        for name, env in cases.items():
            with self.subTest(name):
                result = self.resolve(env, TOKEN + "\n")
                self.assertEqual(3, result.returncode, result.stdout)
                self.assertEqual("", result.stdout)
                self.assertNotIn(TOKEN, result.stderr)

    def test_installer_resolves_token_before_writing_configuration(self) -> None:
        text = (ROOT / "install.sh").read_text(encoding="utf-8")
        self.assertLess(text.index('AUTH_TOKEN="$(resolve_auth_token)" || exit 3'), text.index("cat > /etc/vm-mcp.env"))
        self.assertIn("unset VM_MCP_AUTH_TOKEN", text)


if __name__ == "__main__":
    unittest.main()

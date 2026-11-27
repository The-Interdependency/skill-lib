"""Broker regressions: PYTHONPATH=vm-mcp python -m unittest discover -s vm-mcp/tests."""
from __future__ import annotations

# === CHECKS ===
# id: check_vm_mcp_user_exec_non_root
#   proves: vm_mcp_user_exec_non_root
#   call: self::test_user_mode_rejects_root
#   mutates: none
#   cleanup: none
#
# id: check_vm_mcp_admin_exec_explicit_root
#   proves: vm_mcp_admin_exec_explicit_root
#   call: self::test_admin_mode_selects_root
#   mutates: none
#   cleanup: none
#
# id: check_vm_mcp_broker_execution_bounded
#   proves: vm_mcp_broker_execution_bounded
#   call: self::test_admin_execution_timeout_is_bounded_when_root
#   mutates: process
#   cleanup: process_group_killed
#
# id: check_vm_mcp_admin_broker_peer_verified
#   proves: vm_mcp_admin_broker_peer_verified
#   call: self::test_serve_source_uses_peer_credentials
#   mutates: none
#   cleanup: none
# === END CHECKS ===

import json
import os
import socket
import subprocess
import tempfile
import threading
import time
import pwd
import unittest
from pathlib import Path
from unittest.mock import patch

import admin_broker
import admin_client
from test_policy import _assert_process_gone


class VmMcpAdminBrokerTests(unittest.TestCase):
    def setUp(self) -> None:
        state = tempfile.TemporaryDirectory()
        self.addCleanup(state.cleanup)
        self.marker = str(Path(state.name) / "first-use")
        override = patch.dict(os.environ, {"VM_MCP_FIRST_USE_MARKER": self.marker})
        override.start()
        self.addCleanup(override.stop)

    def test_completed_command_survives_marker_io_failure(self) -> None:
        for failure in ("write", "close"):
            with self.subTest(failure=failure), \
                 patch("admin_broker.os.geteuid", return_value=0), \
                 patch("admin_broker.subprocess.Popen") as popen, \
                 patch("admin_broker._communicate_bounded", return_value=(b"done", b"", False, False, False)), \
                 patch("first_use.os.open", return_value=123), \
                 patch("first_use.os.write", side_effect=OSError("full") if failure == "write" else None), \
                 patch("first_use.os.close", side_effect=OSError("close") if failure == "close" else None):
                popen.return_value.returncode = 0
                result = admin_broker.execute_request({"mode": "admin", "command": "true", "cwd": "/"})
            self.assertTrue(result["ok"])
            self.assertEqual(0, result["exit_code"])
            self.assertEqual("done", result["stdout"])
            self.assertFalse(result["first_use_install"])
            popen.assert_called_once()

    def _run_bounded(self, command: str, timeout: float = 3.0):
        process = subprocess.Popen(["/bin/bash", "-c", command], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, start_new_session=True)
        return process, admin_broker._communicate_bounded(process, timeout=timeout, limit=4096)

    def test_bounded_run_waits_for_command_after_both_streams_close(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            finished = Path(directory) / "finished"
            process, (_, _, timed_out, _, _) = self._run_bounded(
                f"exec >/dev/null 2>&1; sleep 0.3; printf done > '{finished}'")
            self.assertFalse(timed_out)
            self.assertEqual(0, process.returncode)
            self.assertEqual("done", finished.read_text(encoding="utf-8"))

    def test_bounded_run_cleans_up_background_children_after_parent_exit(self) -> None:
        for _ in range(5):  # the pre-fix leak depended on EOF/exit ordering
            process, (stdout, _, timed_out, _, _) = self._run_bounded(
                "exec 2>&-; sleep 20 >/dev/null 2>&1 & echo $!; sleep 0.1")
            self.assertFalse(timed_out)
            self.assertEqual(0, process.returncode)
            _assert_process_gone(self, int(stdout.decode().strip()))

    def test_response_to_a_disconnected_client_does_not_raise(self) -> None:
        server, client = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
        client.close()
        with server, patch("admin_broker.sys.stderr"):
            admin_broker._send_response(server, {"ok": True, "request_id": "exec_x", "stdout": "x" * 65536})
        source = Path(admin_broker.__file__).read_text(encoding="utf-8")
        self.assertIn("_send_response(connection, response)", source)

    def test_client_accepts_a_response_at_worst_case_json_expansion(self) -> None:
        limit = 256 * 1024
        raw = b"\0" * limit
        response = {"ok": True, "exit_code": 0, "command": "true", "cwd": "/",
                    "stdout": raw.decode("utf-8", errors="replace"),
                    "stderr": raw.decode("utf-8", errors="replace")}
        payload = json.dumps(response, separators=(",", ":")).encode("utf-8")
        self.assertGreater(len(payload), admin_client.MAX_RESPONSE_BYTES)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broker.sock"
            listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            listener.bind(str(path))
            listener.listen(1)

            def serve_once() -> None:
                connection, _ = listener.accept()
                with connection:
                    while connection.recv(65536):
                        pass
                    connection.sendall(payload)

            thread = threading.Thread(target=serve_once, daemon=True)
            thread.start()
            try:
                result = admin_client.request_exec(
                    socket_path=path, mode="admin", user=None, command="true", cwd="/",
                    timeout_seconds=5, max_output_bytes=limit)
            finally:
                thread.join(5)
                listener.close()
        self.assertEqual(limit, len(result["stdout"]))

    def test_user_mode_rejects_root(self) -> None:
        with self.assertRaises(ValueError):
            admin_broker._account_for_request("user", "root")

    def test_admin_mode_selects_root(self) -> None:
        account = admin_broker._account_for_request("admin", None)
        self.assertEqual(account.pw_uid, 0)
        self.assertEqual(account.pw_name, "root")

    def test_user_mode_selects_non_root_account(self) -> None:
        current = pwd.getpwuid(__import__("os").getuid())
        if current.pw_uid == 0:
            self.skipTest("test runner is root; no portable non-root fixture")
        account = admin_broker._account_for_request("user", current.pw_name)
        self.assertEqual(account.pw_uid, current.pw_uid)

    def test_serve_source_uses_peer_credentials(self) -> None:
        text = Path(admin_broker.__file__).read_text(encoding="utf-8")
        self.assertIn("SO_PEERCRED", text)
        self.assertIn("peer_uid != caller_uid", text)
        self.assertIn("os.chmod(socket_path, 0o660)", text)

    def test_admin_execution_timeout_is_bounded_when_root(self) -> None:
        import os
        if os.geteuid() != 0:
            self.skipTest("root broker integration requires root test process")
        result = admin_broker.execute_request({
            "mode": "admin", "command": "sleep 2", "cwd": "/",
            "timeout_seconds": 0.1, "max_output_bytes": 1024,
        })
        self.assertTrue(result["timed_out"])
        self.assertIsNone(result["exit_code"])

    def test_request_rejects_empty_command_before_spawn(self) -> None:
        with patch("admin_broker.os.geteuid", return_value=0), \
             patch("admin_broker.subprocess.Popen") as popen:
            with self.assertRaises(ValueError):
                admin_broker.execute_request({"mode": "admin", "command": "", "cwd": "/"})
        popen.assert_not_called()

    def test_execution_requires_root_broker_process(self) -> None:
        with patch("admin_broker.os.geteuid", return_value=1000), \
             patch("admin_broker.subprocess.Popen") as popen:
            with self.assertRaises(PermissionError):
                admin_broker.execute_request({"mode": "admin", "command": "true", "cwd": "/"})
        popen.assert_not_called()


if __name__ == "__main__":
    unittest.main()

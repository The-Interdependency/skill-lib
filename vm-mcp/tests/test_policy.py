"""Contract tests for vm-mcp policy.

Run:
    PYTHONPATH=vm-mcp python -m unittest discover -s vm-mcp/tests -p 'test_*.py'
"""
from __future__ import annotations

import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

# === CHECKS ===
# id: check_vm_mcp_parent_escape_rejected
#   proves: vm_mcp_read_paths_confined
#   call: self::test_parent_escape_rejected
#   mutates: filesystem
#   cleanup: tempdir_teardown
#
# id: check_vm_mcp_symlink_escape_rejected
#   proves: vm_mcp_read_paths_confined
#   call: self::test_symlink_escape_rejected
#   mutates: filesystem
#   cleanup: tempdir_teardown
#
# id: check_vm_mcp_listing_symlink_not_followed
#   proves: vm_mcp_listing_symlinks_not_followed
#   call: self::test_listing_does_not_follow_symlink_metadata
#   mutates: filesystem
#   cleanup: tempdir_teardown
#
# id: check_vm_mcp_read_bounded
#   proves: vm_mcp_read_output_bounded
#   call: self::test_read_text_is_bounded
#   mutates: filesystem
#   cleanup: tempdir_teardown
#
# id: check_vm_mcp_directory_bounded
#   proves: vm_mcp_read_output_bounded
#   call: self::test_directory_listing_is_bounded
#   mutates: filesystem
#   cleanup: tempdir_teardown
#
# id: check_vm_mcp_shell_default_disabled
#   proves: vm_mcp_shell_default_disabled
#   call: self::test_shell_is_disabled_by_default
#   mutates: none
#   cleanup: none
#
# id: check_vm_mcp_shell_cwd_escape_rejected
#   proves: vm_mcp_shell_cwd_confined
#   call: self::test_shell_cwd_escape_rejected
#   mutates: filesystem
#   cleanup: tempdir_teardown
#
# id: check_vm_mcp_shell_output_bounded
#   proves: vm_mcp_shell_execution_bounded
#   call: self::test_shell_output_is_bounded_while_draining
#   mutates: process
#   cleanup: process_group_killed
#
# id: check_vm_mcp_shell_timeout
#   proves: vm_mcp_shell_execution_bounded
#   call: self::test_shell_timeout_is_enforced
#   mutates: process
#   cleanup: process_group_killed
#
# id: check_vm_mcp_background_cleanup
#   proves: vm_mcp_shell_execution_bounded
#   call: self::test_background_descendant_is_killed_before_return
#   mutates: process
#   cleanup: process_group_killed
#
# id: check_vm_mcp_environment_sanitized
#   proves: vm_mcp_credentials_not_inherited
#   call: self::test_shell_does_not_inherit_unrelated_environment
#   mutates: process_environment
#   cleanup: patch_dict_rollback
# === END CHECKS ===

from policy import (
    VmMcpConfig,
    list_directory,
    read_text,
    resolve_under_root,
    run_shell,
)


class VmMcpPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def config(self, *, shell: bool = False, output: int = 64) -> VmMcpConfig:
        return VmMcpConfig(
            root=self.root,
            shell_enabled=shell,
            max_read_bytes=64,
            max_output_bytes=output,
            max_timeout_seconds=3.0,
            max_directory_entries=10,
        )

    def test_parent_escape_rejected(self) -> None:
        with self.assertRaises(PermissionError):
            resolve_under_root(self.root, "../outside", must_exist=False)

    def test_symlink_escape_rejected(self) -> None:
        outside = self.root.parent / f"{self.root.name}-outside"
        outside.mkdir()
        try:
            (outside / "secret.txt").write_text("secret", encoding="utf-8")
            (self.root / "escape").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(PermissionError):
                read_text(self.config(), "escape/secret.txt")
        finally:
            (outside / "secret.txt").unlink(missing_ok=True)
            outside.rmdir()

    def test_listing_does_not_follow_symlink_metadata(self) -> None:
        outside = self.root.parent / f"{self.root.name}-outside"
        outside.mkdir()
        try:
            target = outside / "huge.txt"
            target.write_text("x" * 1000, encoding="utf-8")
            link = self.root / "link"
            link.symlink_to(target)
            result = list_directory(self.config(), ".")
            entry = result["entries"][0]
            self.assertEqual(entry["kind"], "symlink")
            self.assertEqual(entry["size"], link.lstat().st_size)
            self.assertNotEqual(entry["size"], target.stat().st_size)
        finally:
            target.unlink(missing_ok=True)
            outside.rmdir()

    def test_read_text_is_bounded(self) -> None:
        (self.root / "large.txt").write_text("abcdefghij", encoding="utf-8")
        result = read_text(self.config(), "large.txt", max_bytes=5)
        self.assertEqual(result["text"], "abcde")
        self.assertEqual(result["bytes_read"], 5)
        self.assertTrue(result["truncated"])

    def test_directory_listing_is_bounded(self) -> None:
        for index in range(4):
            (self.root / f"{index}.txt").write_text("x", encoding="utf-8")
        result = list_directory(self.config(), ".", max_entries=2)
        self.assertEqual(len(result["entries"]), 2)
        self.assertTrue(result["truncated"])

    def test_shell_is_disabled_by_default(self) -> None:
        with self.assertRaises(PermissionError):
            run_shell(self.config(), "true")

    def test_shell_cwd_escape_rejected(self) -> None:
        with self.assertRaises(PermissionError):
            run_shell(self.config(shell=True), "true", cwd="..")

    def test_shell_output_is_bounded_while_draining(self) -> None:
        result = run_shell(
            self.config(shell=True, output=5),
            "python3 -c 'print(\"x\" * 1000000, end=\"\")'",
        )
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["stdout"], "xxxxx")
        self.assertTrue(result["stdout_truncated"])

    def test_shell_timeout_is_enforced(self) -> None:
        started = time.monotonic()
        result = run_shell(
            self.config(shell=True),
            "sleep 2",
            timeout_seconds=0.1,
        )
        self.assertTrue(result["timed_out"])
        self.assertIsNone(result["exit_code"])
        self.assertLess(time.monotonic() - started, 1.0)

    def test_shell_does_not_inherit_unrelated_environment(self) -> None:
        with patch.dict(os.environ, {"VM_MCP_TEST_SECRET_SENTINEL": "must-not-leak"}):
            result = run_shell(
                self.config(shell=True),
                "printf '%s' \"${VM_MCP_TEST_SECRET_SENTINEL-unset}\"",
            )
        self.assertEqual(result["stdout"], "unset")

    def test_background_descendant_is_killed_before_return(self) -> None:
        result = run_shell(
            self.config(shell=True),
            "sleep 30 & child=$!; printf '%s' \"$child\"",
        )
        self.assertEqual(result["exit_code"], 0)
        pid = int(result["stdout"])
        time.sleep(0.05)
        proc = Path(f"/proc/{pid}/stat")
        if proc.exists():
            state = proc.read_text(encoding="utf-8").split()[2]
            self.assertEqual(state, "Z")


if __name__ == "__main__":
    unittest.main()

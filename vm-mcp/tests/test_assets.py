"""Static contract checks for vm-mcp deployment assets."""
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# === CHECKS ===
# id: check_vm_mcp_loopback_config
#   proves: vm_mcp_loopback_only
#   call: self::test_server_binds_loopback_only
#   mutates: none
#   cleanup: none
#
# id: check_vm_mcp_systemd_write_boundary
#   proves: vm_mcp_host_write_confined
#   call: self::test_systemd_confines_host_writes
#   mutates: none
#   cleanup: none
#
# id: check_vm_mcp_metadata_denial
#   proves: vm_mcp_metadata_credentials_blocked
#   call: self::test_systemd_blocks_cloud_metadata_address
#   mutates: none
#   cleanup: none
#
# id: check_vm_mcp_current_sdk_surface
#   proves: vm_mcp_current_sdk_surface
#   call: self::test_runtime_uses_current_v2_sdk
#   mutates: none
#   cleanup: none
# === END CHECKS ===


class VmMcpAssetTests(unittest.TestCase):
    def test_server_binds_loopback_only(self) -> None:
        text = (ROOT / "server.py").read_text(encoding="utf-8")
        self.assertIn('host="127.0.0.1"', text)
        self.assertIn('streamable_http_path="/mcp"', text)
        self.assertNotIn('host="0.0.0.0"', text)

    def test_systemd_confines_host_writes(self) -> None:
        text = (ROOT / "systemd" / "vm-mcp.service").read_text(encoding="utf-8")
        for expected in (
            "NoNewPrivileges=true",
            "ProtectSystem=strict",
            "ProtectHome=true",
            "CapabilityBoundingSet=\n",
            "AmbientCapabilities=\n",
            "ReadWritePaths=/srv/vm-mcp/workspace",
            "InaccessiblePaths=-/run/docker.sock -/var/run/docker.sock",
        ):
            self.assertIn(expected, text)

    def test_systemd_blocks_cloud_metadata_address(self) -> None:
        text = (ROOT / "systemd" / "vm-mcp.service").read_text(encoding="utf-8")
        self.assertIn("IPAddressDeny=169.254.169.254", text)

    def test_runtime_uses_current_v2_sdk(self) -> None:
        requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        server = (ROOT / "server.py").read_text(encoding="utf-8")
        self.assertIn("mcp>=2,<3", requirements)
        self.assertIn("from mcp.server import MCPServer", server)
        self.assertNotIn("from mcp.server.fastmcp", server)


if __name__ == "__main__":
    unittest.main()

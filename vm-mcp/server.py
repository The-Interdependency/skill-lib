# ratios: loc_comments=59:52 imports_exports=5:5 calls_definitions=18:7
"""MCP server for bounded agent access to a private Linux VM.

Usage guidance:
    VM_MCP_ROOT=/srv/a0/workspaces VM_MCP_SHELL_ENABLED=0 python server.py

The service binds to loopback only. Connect it through a private MCP tunnel or
other authenticated private transport; do not open its port to the public
internet. Enable ``shell_exec`` only after read-only tools work end-to-end and
the host-level systemd confinement has been installed.
"""
from __future__ import annotations

import os
from typing import Any, Callable

from mcp.server.fastmcp import FastMCP

from policy import (
    VmMcpConfig,
    list_directory as policy_list_directory,
    read_text as policy_read_text,
    run_shell as policy_run_shell,
    vm_info as policy_vm_info,
)

# === MODULE_BUILD ===
# id: vm_mcp_control_plane
#   module_name: vm_mcp_control_plane
#   module_kind: service
#   summary: exposes a loopback-only MCP control plane for bounded VM inspection and gated workspace shell execution
#   owner: skill-lib vm-mcp maintainers
#   public_surface: vm_info, list_directory, read_text, shell_exec
#   internal_surface: policy.py
#   auth_boundary: admin
#   storage_boundary: write
#   network_boundary: external
#   user_data_boundary: read
#   admin_only: true
#   tests: vm-mcp/tests/test_policy.py
#   rollout: root_installer_plus_systemd_plus_private_mcp_tunnel
#   rollback: disable_vm-mcp_service_and_remove_private_client_registration
#   feature_flag: VM_MCP_SHELL_ENABLED
#   unresolved: client_specific_private_tunnel_registration, application_layer_auth_when_not_using_a_private_tunnel
# === END MODULE_BUILD ===

# === CONTRACTS ===
# id: vm_mcp_loopback_only
#   given: the MCP server starts with its shipped runtime configuration
#   then: Streamable HTTP binds to 127.0.0.1 on /mcp rather than a public interface
#   class: security
#
# id: vm_mcp_host_write_confined
#   given: the shipped systemd service starts the MCP runtime
#   then: NoNewPrivileges is enabled, Linux capabilities are empty, and host writes are limited to the configured workspace
#   class: security
#
# id: vm_mcp_metadata_credentials_blocked
#   given: a shell command attempts to reach the standard cloud metadata-service address
#   then: the systemd network policy denies 169.254.169.254
#   class: security
#
# id: vm_mcp_production_sdk_not_prerelease
#   given: the runtime requirements are installed for production use
#   then: the MCP Python SDK is constrained to the verified stable release line and excludes prerelease v2 until GA is verified
#   class: dependency
# === END CONTRACTS ===

mcp = FastMCP(
    "vm-mcp",
    host="127.0.0.1",
    port=int(os.environ.get("VM_MCP_PORT", "8765")),
    streamable_http_path="/mcp",
    stateless_http=True,
    json_response=True,
)


def _config() -> VmMcpConfig:
    return VmMcpConfig.from_env()


def _result(call: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    try:
        return {"ok": True, **call()}
    except (OSError, ValueError, PermissionError) as exc:
        return {"ok": False, "error_type": type(exc).__name__, "error": str(exc)}


@mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": False})
def vm_info() -> dict[str, Any]:
    """Return service identity, workspace root, shell state, and configured limits."""
    return _result(lambda: policy_vm_info(_config()))


@mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": False})
def list_directory(path: str = ".", max_entries: int = 200) -> dict[str, Any]:
    """List one directory under VM_MCP_ROOT without following outside symlinks."""
    return _result(
        lambda: policy_list_directory(_config(), path, max_entries=max_entries)
    )


@mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": False})
def read_text(path: str, max_bytes: int = 65536) -> dict[str, Any]:
    """Read bounded UTF-8-compatible text from a file under VM_MCP_ROOT."""
    return _result(lambda: policy_read_text(_config(), path, max_bytes=max_bytes))


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": True,
    }
)
def shell_exec(
    command: str,
    cwd: str = ".",
    timeout_seconds: float = 60.0,
) -> dict[str, Any]:
    """Run one bounded shell command as the confined vm-mcp service user."""
    return _result(
        lambda: policy_run_shell(
            _config(), command, cwd=cwd, timeout_seconds=timeout_seconds
        )
    )


def main() -> None:
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
# ratios: loc_comments=59:52 imports_exports=5:5 calls_definitions=18:7

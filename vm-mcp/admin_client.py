# ratios: loc_comments=53:40 imports_exports=5:2 calls_definitions=19:2
"""Unix-socket client for the vm-mcp personal-console broker.

Usage guidance: call :func:`request_exec` only from the non-root MCP service.
The broker socket is local-only and must be owned by root with group access for
``vmmcp``.
"""
from __future__ import annotations

import json
import socket
from pathlib import Path
from typing import Any

# === MODULE_BUILD ===
# id: vm_mcp_admin_client
#   module_name: vm_mcp_admin_client
#   module_kind: adapter
#   summary: sends bounded personal-console execution requests from the non-root MCP service to the local root broker
#   owner: skill-lib vm-mcp maintainers
#   public_surface: request_exec
#   internal_surface: AF_UNIX JSON request/response transport
#   auth_boundary: admin
#   storage_boundary: none
#   network_boundary: local
#   user_data_boundary: read_write
#   admin_only: true
#   tests: vm-mcp/tests/test_assets.py
#   rollout: imported by policy.py only in personal-console profile
#   rollback: return deployment to workspace/read-only profile
# === END MODULE_BUILD ===

# === BOUNDARIES ===
# id: vm_mcp_admin_client_socket_boundary
#   summary: connects only to the configured local Unix-domain broker socket and sends no SSH/cloud credentials
#   auth_boundary: admin
#   storage_boundary: none
#   network_boundary: local
#   user_data_boundary: read_write
#   admin_only: true
#   side_effects: process
#   owner: skill-lib vm-mcp maintainers
# === END BOUNDARIES ===

MAX_RESPONSE_BYTES = 2 * 1024 * 1024
# json.dumps escapes each control byte (and each U+FFFD that replaces an
# undecodable byte) as a six-byte \uXXXX sequence, so a response can be up to
# six times the raw bytes it carries.
JSON_ESCAPE_FACTOR = 6
RESPONSE_ENVELOPE_BYTES = 64 * 1024


def response_limit(*, command: str, cwd: str, max_output_bytes: int) -> int:
    """Largest serialized broker response a request can legitimately produce.

    Covers both output streams at their raw limit plus the echoed command and
    working directory, each at worst-case JSON expansion, plus envelope fields.
    """
    echoed = len(command.encode("utf-8")) + len(cwd.encode("utf-8"))
    worst_case = JSON_ESCAPE_FACTOR * (2 * max(0, int(max_output_bytes)) + echoed)
    return max(MAX_RESPONSE_BYTES, worst_case + RESPONSE_ENVELOPE_BYTES)


def request_exec(
    *,
    socket_path: Path,
    mode: str,
    user: str | None,
    command: str,
    cwd: str,
    timeout_seconds: float,
    max_output_bytes: int,
) -> dict[str, Any]:
    request = {
        "mode": mode,
        "user": user,
        "command": command,
        "cwd": cwd,
        "timeout_seconds": timeout_seconds,
        "max_output_bytes": max_output_bytes,
    }
    encoded = (json.dumps(request, separators=(",", ":")) + "\n").encode("utf-8")
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.connect(str(socket_path))
        client.sendall(encoded)
        client.shutdown(socket.SHUT_WR)
        limit = response_limit(command=command, cwd=cwd, max_output_bytes=max_output_bytes)
        chunks: list[bytes] = []
        size = 0
        while True:
            chunk = client.recv(64 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > limit:
                raise RuntimeError("admin broker response exceeded client limit")
            chunks.append(chunk)
    payload = b"".join(chunks).decode("utf-8")
    response = json.loads(payload)
    if not isinstance(response, dict):
        raise RuntimeError("admin broker returned a non-object response")
    if not response.get("ok"):
        raise RuntimeError(str(response.get("error", "admin broker request failed")))
    return response
# ratios: loc_comments=53:40 imports_exports=5:2 calls_definitions=19:2

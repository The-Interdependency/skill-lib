# ratios: loc_comments=40:42 imports_exports=6:3 calls_definitions=18:6
"""HTTP caller and process isolation for the private VM control plane.

Usage: configure VM_MCP_AUTH_TOKEN through root-owned service configuration,
then wrap the MCP ASGI app with BearerAuth. Never put the token in tool arguments,
URLs, command output, or a workspace file. Call protect_process before serving
or spawning commands; Linux must deny same-UID inspection of this process.
"""
from __future__ import annotations

import ctypes
import os
import re
import secrets
from typing import Any


# === MODULE_BUILD ===
# id: vm_mcp_caller_authentication
#   module_name: vm_mcp_caller_authentication
#   module_kind: adapter
#   summary: authenticate HTTP callers and isolate service credentials from same-UID shell processes
#   owner: skill-lib vm-mcp maintainers
#   public_surface: BearerAuth, configured_token, protect_process
#   internal_surface: Linux prctl and ASGI request boundary
#   auth_boundary: admin
#   storage_boundary: none
#   network_boundary: internal
#   user_data_boundary: read
#   admin_only: true
#   tests: vm-mcp/tests/test_security_p1.py
#   rollout: reviewed source deployment plus separately authorized operator credential provisioning
#   rollback: stop vm-mcp services; retain authenticated human recovery rather than restore unauthenticated root tools
# === END MODULE_BUILD ===

# === CONTRACTS ===
# id: vm_mcp_http_caller_authenticated
#   given: an HTTP caller reaches the MCP loopback listener
#   then: a configured bearer credential is required before request parsing or tool execution
#   class: security
#
# id: vm_mcp_service_memory_isolated
#   given: untrusted shell children run under the service UID
#   then: Linux process dumpability is disabled before commands may run, denying same-UID access to service credentials
#   class: security
# === END CONTRACTS ===


def protect_process() -> None:
    """Fail closed unless Linux disables ptrace/proc-memory access by shell peers."""
    libc = ctypes.CDLL(None, use_errno=True)
    # PR_SET_DUMPABLE=0 is inherited until exec; children get sanitized env and
    # cannot read the long-running parent's memory, environ or open descriptors.
    if libc.prctl(4, 0, 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), "cannot isolate vm-mcp service process")


def configured_token() -> bytes:
    """Consume an operator-provisioned token, without exposing it to child envs."""
    token = os.environ.pop("VM_MCP_AUTH_TOKEN", "")
    if not re.fullmatch(r"[A-Za-z0-9_-]{32,256}", token):
        raise RuntimeError("VM_MCP_AUTH_TOKEN must be an operator-provisioned 32-256 character URL-safe token")
    return token.encode("ascii")


class BearerAuth:
    """Authorize before MCP parsing or routing, including direct loopback callers."""

    def __init__(self, app: Any, token: bytes) -> None:
        if not token:
            raise ValueError("HTTP bearer token is required")
        self.app = app
        self.token = token

    def _authorized(self, header: bytes) -> bool:
        """RFC 9110 credentials: the auth-scheme is case-insensitive, then 1*SP, then the token.

        Only the token is secret; it is compared in constant time.
        """
        scheme, separator, rest = header.partition(b" ")
        if not separator or scheme.lower() != b"bearer":
            return False
        return secrets.compare_digest(rest.lstrip(b" "), self.token)

    async def __call__(self, scope: dict, receive: Any, send: Any) -> None:
        if scope["type"] == "lifespan":
            await self.app(scope, receive, send)
            return
        if scope["type"] != "http":
            await send({"type": "websocket.close", "code": 1008})
            return
        headers = [value for key, value in scope.get("headers", []) if key.lower() == b"authorization"]
        if len(headers) != 1 or not self._authorized(headers[0]):
            await send({"type": "http.response.start", "status": 401, "headers": [
                (b"www-authenticate", b"Bearer"), (b"content-type", b"text/plain"), (b"cache-control", b"no-store")]})
            await send({"type": "http.response.body", "body": b"Authentication required"})
            return
        await self.app(scope, receive, send)
# ratios: loc_comments=40:42 imports_exports=6:3 calls_definitions=18:6

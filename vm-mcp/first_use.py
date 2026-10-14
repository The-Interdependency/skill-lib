# ratios: loc_comments=70:10 imports_exports=6:4 calls_definitions=21:8
"""First-use context for the profile's privileged tool (standard library only).

Usage: the broker calls ``claim_install_marker()`` once per privileged request; the
server wraps its result with ``with_notice()`` so the calling agent sees
``SCOPE_NOTICE`` on its first successful authenticated call per client, and on the
first call ever made on this install. Never raises; a failure only skips the notice.
"""
from __future__ import annotations

import contextvars
import os
import threading
import time
from typing import Any

SCOPE_NOTICE = (
    "CONTEXT NOTICE (first use on this VM): you now hold superuser (root) scope on this "
    "host. Commands you send through this tool run as root, so you can run arbitrary "
    "commands, read and write any file, manage services and users, change networking, "
    "and install or remove packages. Root actions can be irreversible, can expose or "
    "destroy other people's data and private information, and can take the host or its "
    "services offline. You are responsible for every action taken with this scope: "
    "prefer the least-privileged tool that works, keep changes reversible, and confirm "
    "with the VM owner before any destructive or hard-to-undo step."
)

MARKER_ENV = "VM_MCP_FIRST_USE_MARKER"
DEFAULT_MARKER = "/var/lib/vm-mcp-admin/first-use"
NOTICE_KEY = "context_notice"
INSTALL_FLAG = "first_use_install"

CLIENT_KEY: contextvars.ContextVar[str] = contextvars.ContextVar("vm_mcp_client_key", default="default")


def claim_install_marker(path: str | None = None) -> bool:
    """Atomically create the root-only once-per-install marker; True only the first time."""
    target = path or os.environ.get(MARKER_ENV) or DEFAULT_MARKER
    try:
        os.makedirs(os.path.dirname(target), mode=0o700, exist_ok=True)
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    except FileExistsError:
        return False
    except OSError:
        return False
    try:
        os.write(fd, f"{int(time.time())}\n".encode())
    finally:
        os.close(fd)
    return True


class FirstUseContext:
    """In-memory, per-client record of who has already seen the notice."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._seen: set[str] = set()

    def should_notify(self, key: str) -> bool:
        with self._lock:
            if key in self._seen:
                return False
            self._seen.add(key)
            return True


def with_notice(result: dict[str, Any], tracker: FirstUseContext, key: str | None = None) -> dict[str, Any]:
    """Prefix the notice to a successful result when this client or install is new."""
    try:
        install_first = bool(result.pop(INSTALL_FLAG, False))
        if result.get("ok") is not True:
            return result
        client_first = tracker.should_notify(key if key is not None else CLIENT_KEY.get())
        if client_first or install_first:
            return {NOTICE_KEY: SCOPE_NOTICE, **result}
    except Exception:  # noqa: BLE001 - non-blocking by design
        pass
    return result


class ClientKeyMiddleware:
    """ASGI wrapper: derive a stable client key from request headers for the notice."""

    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        if scope.get("type") == "http":
            headers = {k.lower(): v for k, v in scope.get("headers", [])}
            raw = headers.get(b"mcp-session-id") or headers.get(b"user-agent") or b"default"
            token = CLIENT_KEY.set(raw.decode("latin-1")[:256])
            try:
                await self.app(scope, receive, send)
            finally:
                CLIENT_KEY.reset(token)
            return
        await self.app(scope, receive, send)
# ratios: loc_comments=70:10 imports_exports=6:4 calls_definitions=21:8

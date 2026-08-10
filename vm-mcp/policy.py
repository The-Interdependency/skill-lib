# ratios: loc_comments=271:49 imports_exports=11:6 calls_definitions=86:13
"""Security policy primitives for the vm-mcp runtime.

Usage guidance:
- Construct :class:`VmMcpConfig` from the service environment.
- Route all file tools through ``resolve_under_root``.
- Keep ``shell_exec`` disabled unless the deployment explicitly opts in.
- Systemd confinement is the authoritative host write boundary; these path
  checks provide a second, tool-level boundary and clearer errors.
"""
from __future__ import annotations

import os
import pwd
import selectors
import signal
import socket
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# === CONTRACTS ===
# id: vm_mcp_read_paths_confined
#   given: a file or directory tool receives a relative path, absolute path, parent traversal, or symlink target
#   then: the resolved target must remain under VM_MCP_ROOT or the tool refuses access
#   class: security
#
# id: vm_mcp_listing_symlinks_not_followed
#   given: a directory listing encounters a symlink whose target is outside VM_MCP_ROOT
#   then: the listing reports the symlink itself and does not follow the target for file metadata
#   class: security
#
# id: vm_mcp_read_output_bounded
#   given: a requested text file or directory is larger than the configured response limit
#   then: the response is capped and reports truncation visibly
#   class: safety
#
# id: vm_mcp_shell_default_disabled
#   given: the service starts without explicit VM_MCP_SHELL_ENABLED opt-in
#   then: shell execution is refused
#   class: security
#
# id: vm_mcp_shell_cwd_confined
#   given: shell execution receives a working directory outside VM_MCP_ROOT or through an escaping symlink
#   then: execution is refused before a process is spawned
#   class: security
#
# id: vm_mcp_shell_execution_bounded
#   given: shell execution emits excessive output, exceeds its timeout, or tries to leave background descendants running
#   then: output is capped, timed-out process groups are killed, and surviving descendants are killed before return
#   class: safety
#
# id: vm_mcp_credentials_not_inherited
#   given: the MCP service process has unrelated environment variables or host credentials
#   then: shell execution receives a sanitized environment rather than the service process environment
#   class: security
# === END CONTRACTS ===

DEFAULT_ROOT = Path("/srv/vm-mcp/workspace")
DEFAULT_MAX_READ_BYTES = 256 * 1024
DEFAULT_MAX_OUTPUT_BYTES = 256 * 1024
DEFAULT_MAX_TIMEOUT_SECONDS = 300.0
DEFAULT_MAX_DIRECTORY_ENTRIES = 500
_READ_CHUNK = 64 * 1024


@dataclass(frozen=True)
class VmMcpConfig:
    root: Path
    shell_enabled: bool
    max_read_bytes: int
    max_output_bytes: int
    max_timeout_seconds: float
    max_directory_entries: int

    @classmethod
    def from_env(cls) -> "VmMcpConfig":
        return cls(
            root=Path(os.environ.get("VM_MCP_ROOT", str(DEFAULT_ROOT))).expanduser(),
            shell_enabled=_env_flag("VM_MCP_SHELL_ENABLED", default=False),
            max_read_bytes=_positive_int(
                os.environ.get("VM_MCP_MAX_READ_BYTES"), DEFAULT_MAX_READ_BYTES
            ),
            max_output_bytes=_positive_int(
                os.environ.get("VM_MCP_MAX_OUTPUT_BYTES"), DEFAULT_MAX_OUTPUT_BYTES
            ),
            max_timeout_seconds=_positive_float(
                os.environ.get("VM_MCP_MAX_TIMEOUT_SECONDS"),
                DEFAULT_MAX_TIMEOUT_SECONDS,
            ),
            max_directory_entries=_positive_int(
                os.environ.get("VM_MCP_MAX_DIRECTORY_ENTRIES"),
                DEFAULT_MAX_DIRECTORY_ENTRIES,
            ),
        )


def _env_flag(name: str, *, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _positive_int(raw: str | None, default: int) -> int:
    if raw is None:
        return default
    value = int(raw)
    if value <= 0:
        raise ValueError(f"configured integer limit must be positive: {raw!r}")
    return value


def _positive_float(raw: str | None, default: float) -> float:
    if raw is None:
        return default
    value = float(raw)
    if value <= 0:
        raise ValueError(f"configured timeout limit must be positive: {raw!r}")
    return value


def resolve_under_root(root: Path, requested: str, *, must_exist: bool = True) -> Path:
    root_resolved = root.expanduser().resolve(strict=False)
    requested_path = Path(requested).expanduser()
    candidate = (
        requested_path
        if requested_path.is_absolute()
        else root_resolved / requested_path
    ).resolve(strict=False)
    try:
        candidate.relative_to(root_resolved)
    except ValueError as exc:
        raise PermissionError(f"path escapes VM_MCP_ROOT: {requested}") from exc
    if must_exist and not candidate.exists():
        raise FileNotFoundError(candidate)
    return candidate


def vm_info(config: VmMcpConfig) -> dict[str, Any]:
    root = config.root.expanduser().resolve(strict=False)
    return {
        "hostname": socket.gethostname(),
        "user": pwd.getpwuid(os.getuid()).pw_name,
        "root": str(root),
        "root_exists": root.exists(),
        "shell_enabled": config.shell_enabled,
        "limits": {
            "max_read_bytes": config.max_read_bytes,
            "max_output_bytes": config.max_output_bytes,
            "max_timeout_seconds": config.max_timeout_seconds,
            "max_directory_entries": config.max_directory_entries,
        },
    }


def list_directory(
    config: VmMcpConfig,
    requested: str = ".",
    *,
    max_entries: int = 200,
) -> dict[str, Any]:
    directory = resolve_under_root(config.root, requested)
    if not directory.is_dir():
        raise NotADirectoryError(directory)

    limit = max(1, min(int(max_entries), config.max_directory_entries))
    entries: list[dict[str, Any]] = []
    truncated = False
    for index, child in enumerate(sorted(directory.iterdir(), key=lambda p: p.name)):
        if index >= limit:
            truncated = True
            break
        stat = child.lstat()
        if child.is_symlink():
            kind = "symlink"
        elif child.is_dir():
            kind = "directory"
        else:
            kind = "file"
        entries.append(
            {
                "name": child.name,
                "kind": kind,
                "size": stat.st_size,
                "mtime_ns": stat.st_mtime_ns,
            }
        )

    return {
        "path": str(directory),
        "entries": entries,
        "truncated": truncated,
        "limit": limit,
    }


def read_text(
    config: VmMcpConfig,
    requested: str,
    *,
    max_bytes: int = 64 * 1024,
) -> dict[str, Any]:
    path = resolve_under_root(config.root, requested)
    if not path.is_file():
        raise IsADirectoryError(path)

    limit = max(1, min(int(max_bytes), config.max_read_bytes))
    with path.open("rb") as handle:
        raw = handle.read(limit + 1)
    truncated = len(raw) > limit
    payload = raw[:limit]
    return {
        "path": str(path),
        "text": payload.decode("utf-8", errors="replace"),
        "bytes_read": len(payload),
        "truncated": truncated,
        "limit": limit,
    }


def _sanitized_subprocess_env() -> dict[str, str]:
    user = pwd.getpwuid(os.getuid())
    env = {
        "PATH": os.environ.get(
            "VM_MCP_EXEC_PATH",
            "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        ),
        "HOME": user.pw_dir,
        "USER": user.pw_name,
        "LOGNAME": user.pw_name,
        "LANG": os.environ.get("LANG", "C.UTF-8"),
        "GIT_TERMINAL_PROMPT": "0",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    if os.environ.get("LC_ALL"):
        env["LC_ALL"] = os.environ["LC_ALL"]
    return env


def _kill_group(process: subprocess.Popen[bytes]) -> None:
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def _communicate_bounded(
    process: subprocess.Popen[bytes], *, timeout: float, limit: int
) -> tuple[bytes, bytes, bool, bool, bool]:
    if process.stdout is None or process.stderr is None:  # pragma: no cover
        raise RuntimeError("stdout/stderr pipes are required")

    selector = selectors.DefaultSelector()
    streams = ((process.stdout, "stdout"), (process.stderr, "stderr"))
    for stream, name in streams:
        os.set_blocking(stream.fileno(), False)
        selector.register(stream, selectors.EVENT_READ, data=name)

    buffers = {"stdout": bytearray(), "stderr": bytearray()}
    truncated = {"stdout": False, "stderr": False}
    deadline = time.monotonic() + timeout
    timed_out = False
    descendants_cleaned = False

    try:
        while selector.get_map():
            now = time.monotonic()
            if not timed_out and now >= deadline:
                timed_out = True
                _kill_group(process)
                descendants_cleaned = True

            if process.poll() is not None and not descendants_cleaned:
                # A command such as ``sleep 60 &`` must not leave work behind
                # after the tool call returns. Kill any surviving descendants
                # in the command's dedicated process group, then drain pipes.
                _kill_group(process)
                descendants_cleaned = True

            wait = 0.05 if timed_out else max(0.0, min(0.1, deadline - now))
            events = selector.select(wait)
            for key, _ in events:
                stream = key.fileobj
                name = key.data
                try:
                    chunk = os.read(stream.fileno(), _READ_CHUNK)
                except BlockingIOError:
                    continue
                if not chunk:
                    selector.unregister(stream)
                    stream.close()
                    continue
                remaining = max(0, limit - len(buffers[name]))
                if remaining:
                    buffers[name].extend(chunk[:remaining])
                if len(chunk) > remaining:
                    truncated[name] = True

            # A killed process should close its inherited pipes promptly; this
            # guard prevents a pathological fd holder from hanging forever.
            if timed_out and time.monotonic() > deadline + 2.0:
                for key in list(selector.get_map().values()):
                    selector.unregister(key.fileobj)
                    key.fileobj.close()
    finally:
        selector.close()

    if process.poll() is None:
        _kill_group(process)
    process.wait(timeout=2.0)
    return (
        bytes(buffers["stdout"]),
        bytes(buffers["stderr"]),
        timed_out,
        truncated["stdout"],
        truncated["stderr"],
    )


def run_shell(
    config: VmMcpConfig,
    command: str,
    *,
    cwd: str = ".",
    timeout_seconds: float = 60.0,
) -> dict[str, Any]:
    if not config.shell_enabled:
        raise PermissionError("shell_exec is disabled; set VM_MCP_SHELL_ENABLED=1")
    if not command.strip():
        raise ValueError("command must not be empty")

    directory = resolve_under_root(config.root, cwd)
    if not directory.is_dir():
        raise NotADirectoryError(directory)

    timeout = max(0.1, min(float(timeout_seconds), config.max_timeout_seconds))
    process = subprocess.Popen(
        ["/bin/bash", "-lc", command],
        cwd=directory,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=_sanitized_subprocess_env(),
        start_new_session=True,
    )
    stdout, stderr, timed_out, stdout_truncated, stderr_truncated = _communicate_bounded(
        process, timeout=timeout, limit=config.max_output_bytes
    )
    return {
        "command": command,
        "cwd": str(directory),
        "exit_code": None if timed_out else process.returncode,
        "timed_out": timed_out,
        "timeout_seconds": timeout,
        "stdout": stdout.decode("utf-8", errors="replace"),
        "stderr": stderr.decode("utf-8", errors="replace"),
        "stdout_truncated": stdout_truncated,
        "stderr_truncated": stderr_truncated,
        "output_limit_bytes_per_stream": config.max_output_bytes,
    }
# ratios: loc_comments=271:49 imports_exports=11:6 calls_definitions=86:13

# vm-mcp — Security, Credential Isolation, and Yama Gate

Companion reference for [`../SKILL.md`](../SKILL.md).

## Process dumpability, fd 0 token isolation, Yama ptrace gate, and install-root boundary

The server disables Linux process dumpability as its first statement, before
importing `mcp` or `uvicorn`, and again before serving or spawning shell
commands. Right after that, still before the heavy imports, it exits if
`TracerPid` in `/proc/self/status` is nonzero, then reads the token from fd 0
and closes it. In the `workspace` and `personal-console` profiles it also
refuses a `VM_MCP_AUTH_TOKEN` environment fallback, because Yama does not gate
`/proc/<pid>/environ` reads.

Shell profiles need Yama `kernel.yama.ptrace_scope` >= 1 for the instant before
the process is non-dumpable: `pidfd_getfd` needs `PTRACE_MODE_ATTACH`, so with
scope >= 1 a same-UID `shell_exec` child (never an ancestor of the service)
cannot copy the token descriptor, even by killing the server to force a
restart. The unit's `ProcSubset=pid` hides `/proc/sys` from the server, so the
check is a root pre-start gate, `ExecStartPre=+... yama_gate.py`: the `+` runs
it as root outside the sandbox, and if it exits nonzero systemd never starts
`server.py`, so the token fd is never handed over. `StandardInput=` applies to
every executed process, `ExecStartPre=` included (systemd opens the token file
again for each one, so the gate cannot consume the server's copy); the gate
never reads fd 0 and replaces it with `/dev/null` first. All components resolve
the profile through one helper (`profiles.resolve_profile`). For shell profiles
the installer writes `kernel.yama.ptrace_scope` (1, or the existing higher
value) to `/etc/sysctl.d/99-zz-vm-mcp-ptrace.conf`, which sorts last, applies
it, warns if `systemd-sysctl --cat-config` shows a later override to 0, and
exits 7 if Yama is unavailable. `read-only` runs no shell children, so the
installer never raises the scope for it; when a host moves back to `read-only`
it deletes only its own `99-zz-vm-mcp-ptrace.conf` (a file it did not write is
kept with a warning), and only after `/etc/vm-mcp.env` is written and the
service has restarted, so a failed install never leaves the old shell-profile
config without its boot-time scope. The live value is left alone until the
next reboot or `sysctl --system`. The override warning also matches sysctl.d globs such as
`kernel.yama.* = 0`.

`VM_MCP_ROOT` is writable by the service user while root runs code from the
install root (`/opt/vm-mcp`, including the pre-start gate), so the installer
rejects a workspace that is `/`, equal to, inside, or a parent of the install
root, comparing `realpath`-resolved paths. The install root is fixed at
`/opt/vm-mcp` (both units hardcode it); `VM_MCP_INSTALL_ROOT` is no longer
read.

The server also checks the token descriptor itself (`fstat` on fd 0): it must
be a regular file owned by root with no group or other permission bits,
otherwise the service refuses to start. Same-UID shell children therefore cannot inspect its memory,
environment or descriptors to steal caller credentials. Children receive only
the sanitized execution environment. Root remains outside this protection.
The broker queries systemd for the live main-process identity on every request;
standalone personal-console launches without the managed service are refused.


# vm-mcp — Installer Upgrades, Reruns, and Real-Unit Verification

Companion reference for [`../SKILL.md`](../SKILL.md).

### Upgrading an existing install (fails closed until a token exists)

Installs from before caller authentication have no token. After this upgrade:

- the installer exits 3 without changing anything until one token source is given;
- the new `vm-mcp.service` unit does not start until
  `/etc/credstore/vm-mcp-token` exists and holds a valid token, so the MCP path
  stays down rather than open;
- updated server code under an old unit (no token file configured) falls back
  to a `VM_MCP_AUTH_TOKEN` in `/etc/vm-mcp.env` and logs a warning; with neither,
  it refuses to start. Re-running the installer removes the variable from
  `/etc/vm-mcp.env` and moves the token to the root-only file;
- clients without the `Authorization` header get `401` on every request.
- `workspace`/`personal-console` need Yama: the installer sets
  `kernel.yama.ptrace_scope` >= 1 persistently (exit 7 if Yama is missing), and
  the root pre-start gate refuses to start the service in those profiles while
  the scope is 0 or absent. A later sysctl.d file that sets it back to 0 stops
  the service rather than weakening it. Those profiles also refuse the
  `VM_MCP_AUTH_TOKEN` environment fallback; re-run the installer.

### Rerunning the installer on a VM that already has vm-mcp

- **Settings carry over.** When `/etc/vm-mcp.env` exists, `VM_MCP_ROOT`,
  `VM_MCP_PROFILE`, `VM_MCP_PORT` and `VM_MCP_ADMIN_SOCKET` default to its values
  instead of `/srv/vm-mcp/workspace`, `read-only` and `8765`. The existing profile is
  resolved with `profiles.py` (the same resolver the service uses), so a legacy
  env with only `VM_MCP_SHELL_ENABLED=1` stays `workspace` and the new env file
  records it as `VM_MCP_PROFILE=workspace`.
- **Changes are explicit.** A different workspace root or profile from the
  installed one exits 3 unless `VM_MCP_ALLOW_RECONFIGURE=1` is set (any other
  value is rejected). Restating the same values is fine.
- **Backup first.** Before anything is overwritten, the installer copies the
  previous `/opt/vm-mcp` (without `.venv`), both units, the
  `vm-mcp.service.d` drop-in, `/etc/vm-mcp.env` and the ptrace sysctl.d file into
  a new root-only (`0700`) directory under `/var/backups/vm-mcp/` and prints its
  path (also in the final summary). If the backup fails it exits 9 with nothing
  changed. Old backups are not pruned.
- **Busy service user.** `usermod` refuses a user with running processes (the
  exit 8 seen on upgrades). The installer skips `usermod` when the home is
  unchanged and otherwise stops `vm-mcp.service` and `vm-mcp-admin.service`
  first; both are restarted at the end.
- **ptrace sysctl file order.** The Yama availability check still runs before
  anything changes, but `99-zz-vm-mcp-ptrace.conf` is written only after the
  user step, and if the install then fails the file is restored to its previous
  content (or removed if this run created it). The live value is left as is.

#### One-time real-unit check on the VM (after the first install of this version)

Run as root through the human path, in the deployed profile (stack runs
`personal-console`):

1. `cat /proc/sys/kernel/yama/ptrace_scope` prints 1 or more, and
   `systemctl is-active vm-mcp.service` prints `active`;
   `journalctl -u vm-mcp.service -b | grep yama-gate` shows nothing.
2. The gate does not consume stdin: `systemctl show -p ExecStartPre vm-mcp.service`
   shows `status=0`, and an authenticated `vm_info` succeeds (the server read the
   token from its own fd 0).
3. Refusal: `sysctl -w kernel.yama.ptrace_scope=0; systemctl restart vm-mcp.service`
   fails, `journalctl -u vm-mcp.service -n 20` shows
   `vm-mcp-yama-gate: profile personal-console requires kernel.yama.ptrace_scope >= 1`,
   and no `server.py` process starts (`systemctl show -p MainPID` is 0).
4. Restore: `sysctl --system` (or `sysctl -w kernel.yama.ptrace_scope=1`), then
   `systemctl restart vm-mcp.service` and repeat step 1.

Upgrade order: (1) create the root-owned `0600` token file through the human
SSH/OS Login/IAP path; (2) re-run the installer with `VM_MCP_AUTH_TOKEN_FILE`
and the same profile and root as before; (3) add the header to the MCP client's
secure configuration; (4) verify an unauthenticated request returns `401` and an
authenticated `vm_info` succeeds; (5) delete or keep the token file under the
operator's own secret handling. Recovery while the MCP path is down uses the same
human path; never restore an unauthenticated listener to regain access.


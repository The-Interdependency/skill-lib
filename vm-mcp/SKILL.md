---
name: vm-mcp
description: Private VM control-plane skill for giving an AI/MCP client SSH-like access to a Linux or Google Compute Engine VM without handing the client an SSH private key. Load this when a user asks to connect ChatGPT, an OpenAI client, Codex, Claude, or another MCP host to a VM; expose bounded shell/file tools on a private VM; replace repeated human SSH with an auditable MCP control plane; install or audit the shipped vm-mcp runtime; or add narrowly scoped administrative actions above the workspace shell. Do not load for ordinary human-only SSH setup with no MCP/agent access.
---

# vm-mcp — private VM control plane

The transport invariant remains:

```text
human/bootstrap path: SSH / Google OS Login / IAP
model path:           MCP -> authenticated private tunnel -> bearer-authenticated loopback vm-mcp
credential boundary: SSH/cloud credentials stay outside model context
```

## Profiles

```text
read-only
  vm_info + list/read/stat

workspace
  read-only
  + write/mkdir/move/remove under VM_MCP_ROOT
  + shell_exec as confined non-root vmmcp

personal-console
  workspace
  + user_exec as any explicit local non-root account
  + admin_exec as root
```

`read-only` is the default and remains appropriate for first contact, shared
systems, or consumers that do not need mutation. `personal-console` is intended
for a **single-owner private VM** where broad administration is desired and the
owner prefers capability breadth over a narrow application API.

The personal-console rule is:

> Broad capability is allowed, but privilege transitions must remain obvious.

`user_exec` and `admin_exec` are therefore separate tools. Named convenience
tools may be added later for ergonomics, but they are not permission cages and
do not replace the general execution primitives.

## Trigger / non-trigger

Load this skill when the requested result includes one or more of:

- connect ChatGPT/OpenAI or another MCP client to a private Linux/GCE VM;
- inspect, write, or administer VM files through MCP;
- use a VM shell without placing an SSH private key in the model path;
- expose a broad personal VM console to one owner;
- install, update, audit, or troubleshoot canonical `vm-mcp`;
- distinguish ordinary non-root work from explicit root administration;
- replace repeated SSH pastes with persistent, auditable MCP contact.

Do not load it for ordinary human-only SSH setup or a generic application
deployment where no MCP/agent VM contact is wanted.

## Source of truth

Priority:

1. actual target VM facts: OS, accounts, filesystem, services, network and human recovery path;
2. this canonical `skill-lib/vm-mcp` runtime and tests;
3. current official MCP SDK/protocol documentation;
4. current target MCP client's connection, approval, and private-transport documentation;
5. `hmmm` for unresolved transport/client/host facts.

Do not copy the control plane into an application repository and let that copy
become authority. Application repos may document how they consume the service.

## Security / authority model

The non-root MCP HTTP service retains its original containment:

```text
vm-mcp.service
  user: vmmcp
  bind: 127.0.0.1 only
  NoNewPrivileges=true
  ProtectSystem=strict
  empty Linux capabilities
  Docker socket inaccessible
  cloud metadata address denied
  direct writes confined to VM_MCP_ROOT
```

Personal-console root access does **not** weaken that service. It adds a second
component:

```text
vm-mcp.service (vmmcp)
       |
       | AF_UNIX /run/vm-mcp/admin.sock
       v
vm-mcp-admin.service (root)
       |
       +-- user_exec(user, command, cwd)
       |      drops uid/gid/groups before exec
       |
       `-- admin_exec(command, cwd)
              remains uid 0 explicitly
```

The broker:

- accepts only Unix-domain connections;
- verifies the connecting process with `SO_PEERCRED` against the `vmmcp` uid and systemd's current `vm-mcp.service` MainPID; same-UID shell descendants are refused;
- creates its socket root-owned and group-accessible only to `vmmcp`;
- requires itself to be uid 0 before executing requests;
- rejects `root` through `user_exec`; root must use the visibly privileged `admin_exec` surface;
- runs commands in dedicated process groups with bounded timeout/output and descendant cleanup;
- sanitizes the command environment rather than inheriting arbitrary service secrets;
- records request id, mode, run-as user, cwd, command SHA-256, exit status, and timeout in journald;
- returns the command/output to the MCP caller but does not print arbitrary environment secrets automatically.

Every HTTP request, including direct loopback traffic, must carry the configured
`Authorization: Bearer` credential. The server refuses startup without a
32–256 character URL-safe token; operators must supply a random, high-entropy
token through the installer and the client's secure header configuration. The
installer writes it to `/etc/credstore/vm-mcp-token` (root, `0600`, new inode on
every write). systemd opens that file as root and hands it to the service as
stdin (`StandardInput=file:`); the server reads it once and replaces stdin with
`/dev/null`. The token is never in the service environment and never in a file
the `vmmcp` UID can open. (`LoadCredential=` was not used: its copy stays
readable by the service UID, so by same-UID `shell_exec` children, for the
whole service lifetime.) Tokens never belong in tool arguments, URLs,
workspace files, or chat. The installer does not generate or disclose one.
Provisioning or rotating access is a separate operator-authorized action.

The server disables Linux dumpability and checks `TracerPid` before importing
`mcp` or `uvicorn`, reads the token once from root-owned `0600` fd 0 (with
`fstat` verification), and refuses `VM_MCP_AUTH_TOKEN` env fallback in shell
profiles. `workspace` and `personal-console` require Yama
`kernel.yama.ptrace_scope >= 1` enforced via `ExecStartPre=+... yama_gate.py`
and `/etc/sysctl.d/99-zz-vm-mcp-ptrace.conf`. The installer rejects `VM_MCP_ROOT`
paths equal to, inside, or enclosing `/opt/vm-mcp`, and the broker verifies
systemd's live main-process identity on every request.
See [references/security-and-auth.md](references/security-and-auth.md) for the exact isolation, Yama, and `fstat` mechanics.

Personal-console is intentionally high authority. Anyone able to invoke
`admin_exec` effectively controls the host. Therefore it is appropriate only
when that authority matches the owner's intent and the MCP transport/account is
private and controlled by that owner.

## Tools

| Tool | read-only | workspace | personal-console | Boundary |
|---|---:|---:|---:|---|
| `vm_info` | yes | yes | yes | service/profile/limits |
| `list_directory` | yes | yes | yes | under `VM_MCP_ROOT` |
| `read_text` | yes | yes | yes | under `VM_MCP_ROOT`, bounded |
| `stat_path` | yes | yes | yes | under `VM_MCP_ROOT` |
| `write_text` | no | yes | yes | atomic UTF-8 write under root |
| `make_directory` | no | yes | yes | under root |
| `move_path` | no | yes | yes | source/destination under root |
| `remove_path` | no | yes | yes | under root; root itself refused |
| `shell_exec` | no | yes | yes | vmmcp + systemd confinement |
| `user_exec` | no | no | yes | arbitrary explicit non-root local user via broker |
| `admin_exec` | no | no | yes | root via explicit broker |

Use `shell_exec` for work that should stay inside the MCP workspace. Use
`user_exec` when repository/application ownership belongs to another local
service or human account. Use `admin_exec` for host-level operations such as
systemd, packages, mounts, ownership, PostgreSQL provisioning, or recovery.

## Installer behavior

Provision the bearer token before either installation command below. Give the
installer exactly one source:

- `VM_MCP_AUTH_TOKEN_FILE=<path>`: a regular file (not a symlink) owned by the
  installing user (root) with no group or other access (`chmod 0600`); the first
  line is the token. Preferred.
- `VM_MCP_AUTH_TOKEN_STDIN=1`: the first line of the installer's stdin (any value
  other than unset or `1` is rejected).
- `VM_MCP_AUTH_TOKEN`: the environment; avoid it where it would enter shell history.

The token file is opened once and checked through the open descriptor, so it
cannot be swapped between the check and the read; a token file with Windows
CRLF line endings is rejected with a message saying so. Token handling runs
with xtrace off, so `bash -x install.sh` never prints the token.

Use the same value in the MCP client's secure Authorization-header configuration
(`Authorization: Bearer <token>`; the scheme is case-insensitive per RFC 9110).
A tunnel by itself does not authenticate other local processes. Do not place an
actual credential in a pasted command.

Canonical install:

```bash
sudo VM_MCP_ROOT=/srv/vm-mcp/workspace \
  VM_MCP_PROFILE=read-only \
  VM_MCP_AUTH_TOKEN_FILE=/root/vm-mcp.token \
  bash vm-mcp/install.sh
```

Single-owner personal console:

```bash
sudo VM_MCP_ROOT=/srv/vm-mcp/workspace \
  VM_MCP_PROFILE=personal-console \
  VM_MCP_AUTH_TOKEN_FILE=/root/vm-mcp.token \
  bash vm-mcp/install.sh
```

Upgrades fail closed until a valid token exists; reruns carry over
`/etc/vm-mcp.env` defaults, require `VM_MCP_ALLOW_RECONFIGURE=1` to change
workspace/profile, create a `0700` backup under `/var/backups/vm-mcp/`, stop
busy service units before `usermod`, and preserve sysctl state on rollback.
See [references/installer-and-upgrade.md](references/installer-and-upgrade.md) for full upgrade order, rerun rules, and the one-time real-unit check.

Important ownership rule: if `VM_MCP_ROOT` already exists, the installer leaves
that directory's ownership unchanged. It creates/chowns the root only when the
path does not yet exist. This prevents an existing application checkout such as
`/srv/stack` from accidentally being transferred to `vmmcp` merely because it
was selected as an MCP root.

The install places immutable runtime code under `/opt/vm-mcp` (venv created
under umask `0022` so `vmmcp` can run it), non-secret configuration in
`/etc/vm-mcp.env` and the token in `/etc/credstore/vm-mcp-token` (both written
`0600` to a temp file and renamed into place), and starts `vm-mcp-admin.service` only for
`personal-console`.

## Workflow

### 1. Resolve the VM before mutation

Observe rather than infer:

```text
OS/distribution + Python
systemd availability
human SSH/OS Login recovery path
MCP private transport
intended VM_MCP_ROOT
ownership of application/repository paths
whether this is truly single-owner
current client write/destructive-operation support
```

Missing facts remain `hmmm`.

### 2. Pin canonical skill-lib

Install from an exact reviewed `The-Interdependency/skill-lib` commit. Record the
commit via `/opt/vm-mcp/SOURCE_COMMIT`.

### 3. Run canonical tests before installation

```bash
PYTHONPATH=vm-mcp python -m unittest discover -s vm-mcp/tests -p 'test_*.py'
```

When the full repository checkout is available, also run:

```bash
python tools/check_skill_compliance.py
python tools/check_skill_lib_drift.py
python ratios/ratios_check.py --root .
python tools/build_codex_plugin_skills.py --check
python -m llms.build --root . --out llms.txt --check
```

### 4. Choose the profile deliberately

Use `read-only` for first contact or shared deployments. Use `workspace` when a
confined work area and shell are enough. Use `personal-console` when the owner
explicitly wants a broad personal VM console, including root administration.

Do not silently upgrade an existing deployment from a lower authority profile.

### 5. Verify local containment

```bash
sudo systemctl --no-pager --full status vm-mcp.service
ss -ltnp | grep ':8765'
```

Expected MCP listener: `127.0.0.1:8765`.

For personal-console also verify:

```bash
sudo systemctl --no-pager --full status vm-mcp-admin.service
sudo stat -c '%U %G %a %n' /run/vm-mcp /run/vm-mcp/admin.sock
```

Expected broker boundary:

```text
broker process: root
socket transport: AF_UNIX only
/run/vm-mcp: root:vmmcp 750
admin.sock: root:vmmcp 660
```

### 6. Establish private MCP transport

Never publish raw port `8765` to the public internet. Use the current client's
authenticated private-tunnel/private-network mechanism. Client capabilities are
time-sensitive; verify current official product documentation at connection
time rather than treating this skill's historical product snapshot as current.

### 7. Exercise progressive authority

For a personal console, verify in this order:

```text
unauthenticated HTTP request -> 401
authenticated vm_info
read_text / list_directory
write_text inside disposable VM_MCP_ROOT fixture
shell_exec("id -u")
user_exec(<known non-root user>, "id -u")
admin_exec("id -u")
```

Expected final result for `admin_exec("id -u")` is `0`. Confirm the corresponding
journald broker receipt before using root for real administration.

### 8. Prefer ordinary authority when sufficient

Even in personal-console mode, use the least surprising authority that can do
the job:

```text
workspace file operation -> file tools
workspace diagnostic      -> shell_exec
repo/service-account work  -> user_exec
host administration        -> admin_exec
```

This is an observability rule, not a capability prohibition.

### 9. Keep human recovery independent

SSH/OS Login/IAP remains bootstrap, rescue, and break-glass access. Do not remove
it merely because MCP works.

## Validation

The shipped test suite and real-VM acceptance must cover path/symlink escape,
bounded output, profile defaults and backward compatibility, workspace/shell
confinement, caller auth before parsing, `SO_PEERCRED` + MainPID + non-dumpable
isolation, `user_exec`/`admin_exec` root separation, systemd hardening,
loopback/metadata denial, preserved `VM_MCP_ROOT` ownership, and real-host
restart/rollback.
See [references/validation-and-examples.md](references/validation-and-examples.md) for personal-console examples and the complete 17-item validation checklist.

## Rollback

Return to read-only without deleting human recovery access:

```bash
sudo sed -i 's/^VM_MCP_PROFILE=.*/VM_MCP_PROFILE=read-only/' /etc/vm-mcp.env
sudo systemctl disable --now vm-mcp-admin.service
sudo systemctl restart vm-mcp.service
```

Full stop:

```bash
sudo systemctl disable --now vm-mcp.service vm-mcp-admin.service
```

Disconnect the MCP client/tunnel as a separate control-plane action.

## Anti-patterns

- Putting SSH private keys, service-account keys, OAuth refresh tokens, or sudo passwords into MCP arguments or prompts.
- Opening port `8765` publicly because private transport is inconvenient.
- Running the MCP HTTP service itself as root merely to obtain admin capability.
- Hiding root execution behind a tool that looks non-privileged.
- Letting `user_exec(user="root", ...)` become an alias for root; use `admin_exec` visibly.
- Using an existing application checkout as `VM_MCP_ROOT` and changing its ownership as an installer side effect.
- Treating a loopback listener, private tunnel, or shared UID alone as caller authentication.
- Assuming `read-only` is always preferable when the owner intentionally wants a broad personal console.
- Assuming `personal-console` is appropriate for multi-user/shared systems merely because it is available.
- Treating named convenience tools as the only permissible operations in a single-owner console.
- Removing the independent SSH/OS Login recovery route after MCP contact succeeds.

## Output shape

When deploying or auditing, report:

```text
source: exact skill-lib commit
vm: observed OS/layout
profile: read-only | workspace | personal-console
workspace: exact VM_MCP_ROOT + ownership
mcp service: user/bind/hardening/status
root broker: disabled | socket/status/permissions
private transport: observed status
shell_exec: enabled/disabled
user_exec: enabled/disabled
admin_exec: enabled/disabled
validation: commands actually executed + outcomes
human recovery: observed path
hmmm: unresolved constraints
```

Never describe a command as executed when it was only derived for another
environment.

## hmmm

- Private tunnel provisioning remains client/product infrastructure and must be resolved from the current official client surface at deployment time.
- The shipped broker intentionally grants broad root administration in `personal-console`; future shared/multi-owner deployments may need a separate policy/profile rather than weakening this profile into ambiguous partial authority.
- Named convenience tools for git, systemd, PostgreSQL, fresh-making, backups, and logs are useful ergonomics but are not required for capability because `user_exec` and `admin_exec` already expose the underlying operations.

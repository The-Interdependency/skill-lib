---
name: vm-mcp
description: Private VM control-plane skill for giving an AI/MCP client SSH-like access to a Linux or Google Compute Engine VM without handing the client an SSH private key. Load this when a user asks to connect ChatGPT, an OpenAI client, Codex, Claude, or another MCP host to a VM; expose bounded shell/file tools on a private VM; replace repeated human SSH with an auditable MCP control plane; install or audit the shipped vm-mcp runtime; or add narrowly scoped administrative actions above the workspace shell. Do not load for ordinary human-only SSH setup with no MCP/agent access.
---

# vm-mcp — private VM control plane

`vm-mcp` makes a VM reachable to an MCP-capable agent without turning SSH credentials into model context. The runtime lives in this canonical `skill-lib` directory; consuming repositories may vendor the skill, but no application repository owns the control plane.

The core distinction is load-bearing:

```text
human/bootstrap path: SSH / Google OS Login / IAP
model path:           MCP -> private tunnel -> loopback vm-mcp service
credential boundary: SSH keys stay outside the model path
```

MCP is not SSH. It provides SSH-like operational contact by executing tools **on the target VM**. SSH remains the bootstrap, rescue, and break-glass path.

## Trigger / non-trigger

Load this skill when the requested result is one or more of:

- let an MCP-capable AI inspect or work in a private Linux VM;
- give ChatGPT/OpenAI a private VM tool surface;
- expose shell/file operations without exporting SSH keys or cloud credentials;
- install, update, audit, or troubleshoot `vm-mcp`;
- add a controlled admin action above the non-root workspace shell.

Do not load it for:

- ordinary human SSH key creation, `gcloud compute ssh`, or OS Login with no agent/MCP requirement;
- a public web API that does not speak MCP;
- generic application deployment where the agent does not need VM contact;
- requests to publish an unrestricted root shell to the internet.

## Kind and source of truth

This is a **procedural skill with executable helpers**. It defines no new msdmd block type. Its executable modules use existing `MODULE_BUILD`, `CONTRACTS`, and `CHECKS` declarations.

Source priority:

1. the actual target VM's operating system, filesystem layout, users, services, and network boundary;
2. this skill's runtime and tests;
3. the current stable official MCP SDK and protocol documentation;
4. the target MCP client's current official connection and permission documentation.

Client and SDK capabilities are time-sensitive. Verify them from official primary sources before deployment rather than relying on this file's historical snapshot.

## Security model

The shipped runtime has four deliberate constraints:

1. **Loopback-only transport.** `server.py` binds Streamable HTTP to `127.0.0.1` at `/mcp`. Do not create a public firewall rule for port `8765`.
2. **Non-root execution.** The service runs as `vmmcp`, with no sudo or Linux capabilities.
3. **Host writes are sandboxed.** `ProtectSystem=strict` plus a generated `ReadWritePaths=` override limits writes to `VM_MCP_ROOT`. The Docker socket is explicitly inaccessible because Docker-socket access is effectively host-root authority.
4. **Cloud credentials stay outside shell context.** `shell_exec` gets a sanitized environment, and the shipped systemd policy denies `169.254.169.254` so Google/AWS-style metadata credentials cannot be fetched through the standard link-local metadata address.

The exposed tools are:

| Tool | Default | Boundary |
|---|---|---|
| `vm_info` | enabled | service identity, root, limits; read-only |
| `list_directory` | enabled | resolved paths under `VM_MCP_ROOT`; bounded listing |
| `read_text` | enabled | resolved files under `VM_MCP_ROOT`; bounded bytes |
| `shell_exec` | **disabled** | arbitrary shell as `vmmcp`; cwd must resolve under `VM_MCP_ROOT`; systemd supplies the real host-write boundary |

`shell_exec` may read whatever the unprivileged Unix service account can legitimately read and may make outbound network requests. Do not put secrets inside `VM_MCP_ROOT` unless agent access to those secrets is intentional.

## Workflow

### 1. Inspect the target before installing

Resolve these facts from the VM, not from memory:

```text
OS/distribution and Python version
systemd availability
intended writable workspace
existing application/data directories
whether Docker/Podman sockets exist
human SSH/OS Login recovery path
MCP client and its current write-action support
private tunnel or authenticated private transport
```

Unknowns remain `hmmm`.

### 2. Pin the canonical skill-lib source

Install from an exact reviewed `The-Interdependency/skill-lib` commit or branch. Record the source commit in the VM installation. Do not copy a stale `vm-mcp` implementation out of an application repo.

### 3. Run the tests before host installation

From the `skill-lib` checkout:

```bash
PYTHONPATH=vm-mcp python -m unittest discover -s vm-mcp/tests -p 'test_*.py'
```

Also run the repository gates when the full checkout is available:

```bash
python tools/check_skill_compliance.py
python tools/check_skill_lib_drift.py
python ratios/ratios_check.py --root .
python tools/build_codex_plugin_skills.py --check
python -m llms.build --root . --out llms.txt --check
```

### 4. Install read-only first

Generic installation:

```bash
sudo VM_MCP_ROOT=/srv/vm-mcp/workspace bash vm-mcp/install.sh
```

For the current a0 VM data-disk layout:

```bash
sudo VM_MCP_ROOT=/srv/a0/workspaces bash vm-mcp/install.sh
```

The installer keeps immutable runtime code under `/opt/vm-mcp`, writable agent work under the chosen `VM_MCP_ROOT`, and starts `shell_exec` disabled.

### 5. Verify local contact

Check service state and the loopback listener before adding any remote client:

```bash
sudo systemctl --no-pager --full status vm-mcp.service
ss -ltnp | grep ':8765'
```

Expected listener address is `127.0.0.1`, not `0.0.0.0` and not the VM's external IP.

### 6. Establish the private MCP transport

For ChatGPT/OpenAI, re-check the current official custom-MCP documentation. As of 2026-08-07, OpenAI's published guidance says private-network/local MCP servers should use **Secure MCP Tunnel** rather than public exposure; full write/modify custom MCP is currently a Business/Enterprise/Edu feature, while Pro custom MCP is read/fetch only. This product boundary does not change the server's host permissions.

For other MCP hosts, use their authenticated private-tunnel/VPN/reverse-proxy mechanism. If the client cannot provide a private authenticated transport, `hmmm` the connection rather than publishing the raw service.

### 7. Exercise read-only tools end-to-end

Call, in order:

```text
vm_info
list_directory(path=".")
read_text(path=<known harmless text file>)
```

Confirm the reported root and service user before enabling any write tool.

### 8. Enable workspace shell only after the client can govern writes

When the owner explicitly wants model-side command execution and the MCP client supports appropriate write approvals:

```bash
sudo mkdir -p /etc/systemd/system/vm-mcp.service.d
printf '[Service]\nEnvironment=VM_MCP_SHELL_ENABLED=1\n' \
  | sudo tee /etc/systemd/system/vm-mcp.service.d/shell.conf
sudo systemctl daemon-reload
sudo systemctl restart vm-mcp.service
```

Disable it again with:

```bash
sudo rm -f /etc/systemd/system/vm-mcp.service.d/shell.conf
sudo systemctl daemon-reload
sudo systemctl restart vm-mcp.service
```

### 9. Add administration as named capabilities, not a root shell

If workspace shell is insufficient, do **not** make `vmmcp` passwordless root and do not expose `/run/docker.sock`. Add a root-owned broker for the smallest named operation required, for example:

```text
restart one named application service
read one service's journal
activate one reviewed release
run one reviewed backup/restore command
```

Each new admin operation needs its own arguments, permission boundary, contract, checks, rollback, and client write annotation. An unrestricted `sudo bash -c <model text>` broker is outside this skill's safe default.

## Output shape

When this skill is used for a deployment or audit, report:

```text
source: exact skill-lib commit/ref
vm: observed OS + relevant layout
workspace: exact VM_MCP_ROOT
service: installed/running/not installed
transport: loopback + private tunnel status
client: observed current MCP read/write capability
shell_exec: disabled/enabled
validation: commands actually executed + results
admin capabilities: none or exact named brokers
hmmm: unresolved constraints
```

Never describe a command as executed when it was only derived for the user to run.

## Validation

The shipped checks cover:

- `..` path escape rejection;
- symlink escape rejection;
- symlink listings without following target metadata;
- bounded text and directory output;
- shell off-by-default;
- shell cwd confinement;
- bounded/drained command output;
- timeout process-group termination;
- background-descendant cleanup;
- non-inheritance of unrelated environment secrets;
- loopback-only server configuration;
- systemd host-write/capability confinement;
- cloud metadata-address denial;
- production SDK pin excluding prerelease v2.

The test suite does **not** prove the remote client's tunnel, auth, approval UI, or account plan works. Those require end-to-end contact with the actual client.

## Anti-patterns

- Putting an SSH private key, Google service-account key, OAuth refresh token, or OS Login credential into an MCP tool argument or prompt.
- Listening on `0.0.0.0:8765` because the private tunnel is not yet configured.
- Calling a public reverse proxy "private" without authentication.
- Running the MCP service as root.
- Adding `vmmcp` to the Docker group or exposing the Docker socket.
- Treating `VM_MCP_ROOT` path checks as the only sandbox; systemd is the host-write authority boundary.
- Enabling `shell_exec` before read-only end-to-end contact works.
- Claiming ChatGPT write access when the current plan/client only exposes read/fetch.
- Keeping an SDK line after it is actually deprecated; verify current stable SDK status at deployment/update time and replace deprecated surfaces immediately.

## hmmm

- Exact Secure MCP Tunnel provisioning commands are client/product infrastructure and must be taken from current official OpenAI documentation or the actual connected product surface; do not invent them.
- Application-layer OAuth is intentionally not implemented in the loopback runtime because the default architecture assumes a private authenticated tunnel. A public-edge deployment would require a separate reviewed auth layer.
- Root-level VM maintenance is deliberately not a generic tool. Named administration brokers should be added only when concrete operations are known.
- The current stable MCP Python SDK observed on 2026-08-07 is v1.28.1 while v2.0.0b2 remains a prerelease; this skill pins the stable production line until official GA evidence changes that boundary.
- A private control plane is a door; the useful engineering question is not whether it opens, but exactly which room the hinges belong to.

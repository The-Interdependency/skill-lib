# VM provider credentials with OpenBao

GPT generated; context, prompt Erin Spencer.

## Contract and scope

`openbao/` owns a local TLS OpenBao server profile, AppRole provisioning, and
provider-specific CLI launch. `tools/ai.sh` remains the phone-side SSH/tmux
controller. Each launch authenticates, reads one KV v2 key, revokes its 60-second
vault token, then execs the CLI with that key. `--check` performs retrieval and
revocation without launching or printing the key. Authentication/read/revocation
failure blocks the launch. Existing sessions are not automatically restarted.

| CLI | KV v2 path | Child environment |
|---|---|---|
| grok | a0/data/providers/grok | XAI_API_KEY |
| codex | a0/data/providers/codex | OPENAI_API_KEY |
| deepcode | a0/data/providers/deepcode | DEEPSEEK_API_KEY |

Anthropic is not an existing ai.sh window. Add an explicit provider mapping and
policy when adding that CLI; do not hand its key to other processes.

Server: non-root `openbao`, TLS `127.0.0.1:8200`, Raft storage `/var/lib/openbao`,
audit `/var/log/openbao/audit.json`. Fresh installer refuses existing deployments,
accounts, active swap (also checked at each service start), and a binary whose SHA256 differs from the operator's
verified release digest. No downloader, dev server, public listener, root-token
file, automatic initialization, or automatic unseal is included.

AppRole credentials are private per-user files with a 30-day expiry. They remain
retrievable by processes running as that user. Provider-specific vault policies
constrain each role; they do not isolate same-UID agents from one another or from
root. The selected CLI and descendants receive the raw provider key. Stronger
isolation needs separate Unix identities or a credential-holding API proxy.

## Install and bootstrap on the actual VM

Prerequisites: verified human SSH/OS Login recovery; Linux/systemd; root install
access; Python 3, OpenSSL, coreutils; no active swap; a verified supported OpenBao
release installed root-owned at `/usr/local/bin/bao`; selected source commit.
Verify the upstream release signature/checksums independently before passing its
binary SHA256. Do not derive the expected digest from an unverified download.

Run from the chosen skill-lib checkout on the VM:

```bash
sudo bash vm-mcp/openbao/install.sh EXPECTED_VERIFIED_BINARY_SHA256
```

Installer success means service files installed, not vault ready. Inspect:

```bash
sudo systemctl is-active openbao.service
ss -ltn | grep ':820[01]'
BAO_ADDR=https://127.0.0.1:8200 BAO_CACERT=/etc/openbao/tls/cert.pem bao status
```

Status should show uninitialized/sealed on first install. All listeners must be
loopback. The self-signed TLS certificate is locally trusted through the exact
certificate file, never by disabling verification. Certificate expires in 365
days: replace certificate/key together through an authenticated operator path,
update the local trust file, restart OpenBao, and unseal/recheck before expiry.

Initialize only from a private human terminal, with pane recording disabled and
PGP encryption for initial root token and unseal shares. Use independently stored
operator-owned PGP public keys and a chosen recovery quorum:

```bash
BAO_ADDR=https://127.0.0.1:8200 BAO_CACERT=/etc/openbao/tls/cert.pem \
  bao operator init -key-shares=3 -key-threshold=2 \
  -pgp-keys=RECOVERY_ONE.asc,RECOVERY_TWO.asc,RECOVERY_THREE.asc \
  -root-token-pgp-key=OWNER.asc
```

Save encrypted recovery material outside the VM before proceeding. This example
requires three actual recovery keys; do not invent them or silently change quorum.
Decrypt shares through the owner's private recovery environment. Unseal with
interactive hidden prompts, never share values as CLI arguments or chat text:

```bash
BAO_ADDR=https://127.0.0.1:8200 BAO_CACERT=/etc/openbao/tls/cert.pem bao operator unseal
```

Repeat for the chosen threshold. Configure an operator authentication method and
verify a fresh administrative login before revoking the initial root token.
Preserve SSH and recovery independently of OpenBao. Automatic unseal is a separate
host-specific decision; this profile requires unsealing after restart.

## Provision, renew, and recover

Run each operation in a private human terminal (not a model tool). Supply a fresh
short-lived administrative token when prompted; it is revoked on successful
completion. Do not pass token/API key values in arguments, environment, or chat.
Replace `VM_USER` with the observed non-root account that owns the ai tmux session.

```bash
sudo python3 -I /opt/a0-openbao/provision.py VM_USER grok
sudo python3 -I /opt/a0-openbao/provision.py VM_USER codex
sudo python3 -I /opt/a0-openbao/provision.py VM_USER deepcode
```

Provisioning enables KV v2 at `a0/`, AppRole, a hashed audit device, and a read-only
policy per CLI with token-self-revocation. Initial key writes use CAS=0 and refuse
overwriting a stored key. Run one provisioner at a time. Credential files publish
under the target UID, never through root writes into a user-controlled home.

Renew before 30 days, or after expiry, preserving the stored provider key:

```bash
sudo python3 -I /opt/a0-openbao/provision.py VM_USER codex --renew
```

Renew publishes the new SecretID then destroys the previous accessor. If local
publication fails, it attempts to destroy the new unused SecretID. Server-side
TTL remains the backstop when cleanup itself fails. After a crash or partial
failure, inspect vault audit/role accessor state privately; never assume cleanup.
If initial provisioning stored the key but did not publish a credential, repair
the local failure then use `--resume`, which reuses the existing key. If a new
credential was published but old-accessor destruction failed, destroy that old
accessor through the admin API before accepting rotation. If final admin-token
revocation failed, revoke it explicitly. Sanitized error output cannot identify
which private step failed; audit evidence owns that determination.

Provider-key rotation is distinct: replace the key at the provider, write a new
KV version with the observed CAS version through a private administrative session,
verify retrieval, restart the affected CLI at a safe checkpoint, and revoke the
old provider key. Vault token revocation does not revoke a provider API key or
remove copies from running processes.

## Cutover and acceptance

As the actual VM_USER, verify each configured provider:

```bash
python3 -I /opt/a0-openbao/launch.py codex --check
```

A pass proves retrieval and token revocation, not provider billing/authentication.
Then update the phone checkout and its installed canonical symlinks. The updated
launcher has no legacy environment fallback. `ai.sh keys` checks all three roles;
any failure returns nonzero. Launches check retrieval before replacing a pane;
a successful tmux respawn only proves scheduling, so inspect `ai.sh status` and
the CLI's readiness after launch. Vault state can change between check and exec.

Remove provider exports from the VM login/startup files through a private edit.
Clear existing shell values, restart affected processes at checkpoints, and check
that the values have gone using presence-only output. The launcher removes these
four keys from tmux global environment and marks them removed in its session;
existing processes and other sessions still need explicit cleanup. Logs from old
sessions may contain secrets: inspect privately, rotate exposed provider keys,
and apply the owner's retention policy. Vault cannot retroactively erase them.

Target acceptance must exercise: each CLI ready with its provider; unauthorized
cross-provider read denied; invalid/revoked/expired SecretID denied; sealed vault
refuses a new launch; revoked token cannot read; no keys in tmux shared environment;
renewal invalidates old SecretID; service restart/unseal; certificate failure;
backup restore on an isolated target. Never capture key values in proof output.

## Backup, rollback, and limits

Take encrypted, access-controlled Raft snapshots through `bao operator raft
snapshot save`; record a digest and prove restore on an isolated host. Preserve
recovery material independently. Monitor audit disk space and rotate audit logs
with the supported reopen procedure for the installed OpenBao version. Disk-full
or unavailable audit devices can stop requests; do not disable auditing to hide it.

Rollback: stop new agent launches and keep existing healthy processes until a safe
checkpoint. `sudo systemctl disable --now openbao.service` stops the service while
preserving encrypted state. Retain TLS trust, encrypted snapshots, and recovery
material. Do not restore shell-export/tmux key propagation as a fallback. A failed
fresh install may leave files/accounts: inspect and complete or remove only its
new installation artifacts before rerunning; the installer refuses overwrite.

Keep vm-mcp caller authentication and human SSH/bootstrap independent of this
provider vault. Its root-only token-file/stdin boundary remains unchanged.
Never make OpenBao recovery depend on an MCP token retrievable only from the
sealed instance being recovered.

## Verification and hmmm

```bash
bash -n tools/ai.sh vm-mcp/openbao/install.sh
python -m unittest discover -s tests -p 'test_openbao*.py' -v
python -m unittest discover -s tests -p 'test_ai_launcher.py' -v
```

Offline tests establish helper error/credential boundaries and provisioning
transitions. They do not establish the deployed OpenBao version, real API policy
semantics, cloud/network identity, operator auth, unseal custody, or VM readiness.
Those remain hmmm until target acceptance. This session had no VM MCP tools or
configured a0 SSH endpoint; no live vault or provider keys were modified.

Official contracts: [AppRole](https://openbao.org/docs/auth/approle/),
[configuration](https://openbao.org/docs/configuration/),
[Raft](https://openbao.org/docs/configuration/storage/raft/).

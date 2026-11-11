# GitHub token refresh through OpenBao

GPT generated; context, prompt Erin Spencer.

## Scope and identity

The [shared manifest](github-openbao-refresh.json) pins the two input repositories
in producer-then-consumer order. Its SHA-256 is
`2e01a0ee2228fa80715fa93ea8ef5f814aada47fe2f4bb3bebada3e574b8cc28`.
These are input identities; the commits publishing each repair identify the
changed output. Repository, mathematical, empirical and certification authority
does not transfer through this integration or its fixture tests.

| Owner | Changed responsibility |
| --- | --- |
| A0 `operations/configure-vault.py` | Scoped policy, hidden operator input, authenticated/version-checked write, readback, protected CLI activation |
| skill-lib `tools/a0_vault.py` | Validated read from the pinned store, selected child delivery, stale environment removal, GitHub HTTPS credential helper |
| skill-lib `tools/ai.sh` | Direct interactive SSH entrypoint and presence/authentication checks |
| A0 `tests/reliability/check_launcher_compat.py` | Executable producer-to-consumer fixture against both exact checkouts |

## Contract and completion

The former path renewed GitHub CLI's own login and left OpenBao out of the
operation. The repaired path stores the token at KV v2 `integration/github`,
field `token`, and activates the optional CLI mapping:

```json
{"github":{"path":"integration/github","agents":["deepcode"]}}
```

A0 owns this protected configuration and its provisioning. The runtime CLI has
read-only access to the exact secret; routine replacement uses the existing
scoped application credential, never recovery/root material. Existing provider
settings remain usable before explicit GitHub activation.

Done at source level requires a hidden input route, successful authentication
before mutation, compare-and-set/write/readback, matching producer/consumer
configuration, fresh child delivery after rotation, rejection after deletion,
and redacted failures. Live completion additionally requires installation on
the existing VM, private entry of Erin's token and a real repository operation.

Fails if a credential reaches command arguments, terminal echo, a recorded
tmux pane, repository output, or a model prompt; if a rejected candidate
replaces the existing value; if stale inherited tokens override the replacement;
or if fixture evidence is represented as live VM acceptance.

The VM account and administrators remain trusted. GitHub `/user` proves
authentication only. GitHub scope/repository/organization grants remain external
authority. The shared app vault policy can read this integration, and same-user
processes are not isolated from each other by the child environment.

## Usage and rollout

Install the reviewed A0 administrative script first, then the matching phone
launcher and VM helper. Reprovision the exact read policy with `ai.sh vault setup`.
Run `ai.sh github set` directly in an interactive terminal; enter the token only
at the hidden prompt. Use `ai.sh github status` for presence and `ai.sh github check`
for GitHub authentication. Restart the selected DeepCode pane after its current
work is saved. Full instructions and rollback boundaries are in
[A0-VAULT.md](../../tools/A0-VAULT.md).

Source rollback cannot undo a GitHub revocation or a completed vault write.
Preserve protected configuration and vault history; inspect partial activation
errors before retrying. Never restore old environment tokens as fallback.

## Verification

From skill-lib:

```bash
python3 -m unittest tests.test_a0_vault tests.test_ai_launcher
bash -n tools/ai.sh
```

From the matching A0 checkout:

```bash
python3 -m unittest discover -s tests/reliability -p 'test_*.py'
python3 tests/reliability/check_launcher_compat.py ../skill-lib
```

The tests use inert credentials, local HTTP fixtures and isolated processes.
They cover successful delivery, rotation, deletion, policy/cluster failures,
CAS conflicts, hidden PTY input, refusal of noninteractive token entry,
Git credential resolution, header precedence and credential redaction.
Neither source tests nor generated metadata establish live service health.

## hmmm

This work has no live connection to the private VM. Deployment, private GitHub
token entry, actual repository permissions and physical-phone acceptance remain
separate observations. Credentials embedded in Git remote URLs, SSH remotes,
explicit later command overrides, and unseen repository-local authorization
headers require their own migration; the static launch route covers token-free
GitHub HTTPS URLs and configuration visible when the child starts.

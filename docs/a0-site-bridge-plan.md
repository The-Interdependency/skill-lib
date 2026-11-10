# A0 vault and Site connection

GPT generated; context, prompt Erin Spencer.

FROM: environment-propagating launcher and source-only console.
TO: VM-local vault-backed CLI launches, authenticated status/evidence and durable handoff inbox consumed by the private Site.

Done when: initialized/unsealed/pinned vault supplies only selected provider keys to a child process, stale keys are removed, the Site reads authenticated VM state, and repeated handoff submissions have one durable identity. Phone acceptance remains a separate claim.
Fails if: a token enters arguments/logs/browser bundles, failed vault contact triggers initialization, Site credentials authorize ordinary chat/key routes, stale evidence is called live, or receipt is called execution.

Ownership: skill-lib tools/ai.sh and tools/a0_vault.py own terminal launching. A0 operations/configure-vault.py owns bootstrap/policies/renewal; apps/server/src/reliability.js owns the bridge schema. Site lib/vm.ts and app/api/vm own consumption; app/vm-panel.tsx owns presentation.

Permissions: read-only provider CLI token separate from application/root credentials; bridge bearer authorizes status and a handoff inbox only. Secrets stay in protected VM files or Sites runtime secrets. Pairing file is an explicit owner-only secret download passed to VM over SSH stdin.

Validation: fake Bao HTTP server + subprocess credential canaries, authentication/identity/expiry failures; real Express bridge auth and duplicate inbox tests; Site adapter fixture compatibility and owner isolation. Live VM and phone results require separate receipts.

Rollout: publish producer commits, deploy A0 source and provision CLI, then pair the Site. Restart only A0 after validation; keep Bao/store/seal unchanged. Rollback: disable bridge token config, restore prior A0 release, preserve inbox/evidence; remove launcher symlink or select prior source. Never fall back to stale keys on vault failure.

## PR #137 reconciliation — 2026-11-10

The launcher input is `46ba3e680c21434dd03e79c0cbf900881829701e`.
The integration base is `8ee77a6630379e48844350d8666515389b94f4c8`
(main after agent-ops #138). Their only merge conflict is the generated
`skill-lib_msdmd.ts`; resolve it by running its owning collector on the combined
source tree. Preserve `tools/ai.sh`, `tools/a0_vault.py` and their tests byte for
byte. The collection's snapshot identity binds its inputs; the containing Git
commit and PR receipt identify this reconciliation's output.

A0 #122 is merged at `f97c7c85e31b9324caf642b41a170b7e32ee9911`.
The cross-repository fixture consumes configuration emitted by that exact A0
producer. Observed A0 main `12b64724145dac9591ca650f5d0fd3b573d4ae7d`
adds GUI repairs; `operations/`, the vault and bridge modules, and
`tests/reliability/` are unchanged from the #122 merge. This compatibility
observation does not establish GUI acceptance or authorize a later VM release.
The work graph records these distinct source roles. The private Site source
identity is carried from A0's reviewed record; its hosted deployment has not
been reverified by this reconciliation.

### Reproduce validation

Use Python 3.13, Node 24.15.0 and the reader dependencies declared by CI. From
this skill-lib checkout:

```bash
python -m unittest tests.test_a0_vault tests.test_ai_launcher -v
python -m msdmd.collect --root . --repo The-Interdependency/skill-lib --snapshot-identity --import-path ./msdmd/collection --out skill-lib_msdmd.ts --strict
python -m msdmd.collect --root . --repo The-Interdependency/skill-lib --snapshot-identity --import-path ./msdmd/collection --out skill-lib_msdmd.ts --strict --check
node msdmd/node_modules/typescript/bin/tsc --noEmit --strict --skipLibCheck --target ES2022 --module commonjs msdmd/collection.ts skill-lib_msdmd.ts
python -m unittest discover -s tests
```

Run the remaining gates in `.github/workflows/ci.yml` and `hygiene.yml`.
With the A0 checkout pinned to the #122 merge, run from that checkout:

```bash
python3 tests/reliability/check_launcher_compat.py /path/to/skill-lib
python3 -m unittest discover -s tests/reliability -p 'test_*.py'
node --test tests/reliability/bridge.test.js
```

The PR receipt records command outcomes, exact final head/base, CI runs and
fresh terminal review before the expected-head-guarded merge. Erin authorized
this conflict repair and merge after review; VM activation remains a separate
operation. The older A0 operations record's companion-merge hold is superseded
by this authorization only after those gates pass.

### Remaining integration requirements

Before activation, verify VM identity, service runtime Node >=22, existing
OpenBao store/cluster, unprivileged CLI account and recovery access. Preserve a
private checkpoint and verify an isolated restore and off-VM backup retrieval
before provisioning. Use the A0-owned checkpoint/configuration rollback; its
older source-only rollback cannot undo the credential transition. Install exact
reviewed source identities, then explicitly restart selected existing agent
panes, whose environments persist until restart. Pair the owner-private Site
over SSH stdin and retain separate runtime receipts for renewal beyond the
original token lifetime, real provider requests and physical-phone acceptance.
No provisioning, service restart, live credential retrieval, provider call or
phone acceptance is performed by this reconciliation.

hmmm: VM activation, recovery rehearsal, sustained renewal, live provider use,
hosted Site verification and physical-phone acceptance still require runtime
evidence. Source tests do not close those gates.

# vm-mcp — Personal-Console Examples and Validation Checklist

Companion reference for [`../SKILL.md`](../SKILL.md).

## Personal-console examples

Repository work as its owning service account:

```text
user_exec(
  user="stackorchestrator",
  cwd="/srv/stack",
  command="python -m frontend.cli.stackctl fresh status"
)
```

Host service inspection:

```text
admin_exec(
  cwd="/",
  command="systemctl --no-pager --full status stack-orchestrator-worker.service"
)
```

Package or host maintenance is also possible through `admin_exec`; the tool is
not artificially limited to a predefined command vocabulary. That breadth is
the point of the single-owner profile.

## Validation

The shipped suite must cover at least:

- parent/symlink path escape rejection;
- bounded file/directory/process output;
- read-only default and backward compatibility for the historical shell flag;
- workspace write gating and path confinement;
- shell cwd confinement, timeout, output bound, and environment sanitization;
- personal-console gate before broker use;
- root rejection through `user_exec`;
- root selection through `admin_exec`;
- broker root-process requirement;
- `SO_PEERCRED` UID plus current systemd MainPID verification;
- caller authentication before HTTP request parsing, including loopback callers;
- same-UID shell denial and non-dumpable service credential isolation;
- move/remove operate on final symlinks themselves, including broken links;
- root:vmmcp socket permissions;
- non-root MCP systemd hardening remaining intact;
- loopback-only MCP listener and metadata-address denial;
- installer preserving ownership of an existing `VM_MCP_ROOT`.

Actual VM acceptance must additionally exercise a real non-root `user_exec`, a
real root `admin_exec`, journald evidence, service restart, and rollback on the
target host.


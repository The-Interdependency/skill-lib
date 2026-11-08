#!/usr/bin/env python3
# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm
"""VM-local OpenBao credential boundary for ai.sh.

Usage: a0-vault status; a0-vault exec codex -- codex --yolo.
Provision /etc/a0/cli/<uid>.json with A0 operations/configure-vault.py.
Never initializes/unseals Bao. Secrets enter only the selected child environment.
The VM account and its executed CLI remain trusted; this is not a sandbox.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import stat
import sys
import urllib.error
import urllib.parse
import urllib.request

PROVIDERS = {"openai": "OPENAI_API_KEY", "xai": "XAI_API_KEY",
             "deepseek": "DEEPSEEK_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}
AGENTS = {"codex": "openai", "grok": "xai", "deepcode": "deepseek"}
SECRET_ENV = set(PROVIDERS.values()) | {"BAO_TOKEN", "VAULT_TOKEN", "BAO_TOKEN_FILE",
    "VAULT_TOKEN_FILE", "BAO_ADDR", "VAULT_ADDR", "A0_DATABASE_URL", "A0_SESSION_SECRET",
    "A0_BOOTSTRAP_CODE", "A0_BRIDGE_TOKEN"}


class BoundaryError(Exception):
    """A redacted operational failure; never carries a remote response body."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise BoundaryError("Vault/bridge redirects are refused.")


def protected_read(path: str) -> str:
    """Refuse symlinks, nonregular files and disclosure outside the account group."""
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        info = os.fstat(fd)
        if (not stat.S_ISREG(info.st_mode) or info.st_uid not in (0, os.geteuid())
                or info.st_mode & 0o027 or (info.st_mode & 0o040 and info.st_gid not in os.getgroups() + [os.getegid()])):
            raise BoundaryError("Credential file ownership/permissions must be private (0600 or root:account 0640).")
        with os.fdopen(fd, "r", encoding="utf-8", closefd=False) as stream:
            value = stream.read(32769)
        if len(value) > 32768:
            raise BoundaryError("Credential configuration is too large.")
        return value
    finally:
        os.close(fd)


def load_config(path: str) -> dict:
    data = json.loads(protected_read(path))
    if not isinstance(data, dict) or data.get("schema") != "a0.cli-vault/1":
        raise BoundaryError("Unsupported CLI vault configuration.")
    address(data.get("addr", ""))
    if not data.get("cluster_id") or not re.fullmatch(r"[A-Za-z0-9_-]+", data.get("mount", "")):
        raise BoundaryError("Pin the vault cluster identity and KV mount before use.")
    return data


def address(value: str) -> str:
    url = urllib.parse.urlsplit(value)
    if (url.username or url.password or url.query or url.fragment or url.path not in ("", "/")
            or not url.hostname or not (url.scheme == "https" or
                (url.scheme == "http" and url.hostname in ("127.0.0.1", "::1")))):
        raise BoundaryError("Use HTTPS or literal loopback HTTP without URL credentials or paths.")
    return value.rstrip("/")


def request(addr: str, path: str, token: str = "", body=None):
    headers = {"Accept": "application/json"}
    if token:
        headers["X-Vault-Token"] = token
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(address(addr) + "/v1" + path, headers=headers,
        data=None if body is None else json.dumps(body).encode())
    opener = urllib.request.build_opener(NoRedirect, urllib.request.ProxyHandler({}))
    try:
        with opener.open(req, timeout=10) as response:
            raw = response.read(262145)
            if len(raw) > 262144:
                raise BoundaryError("Vault response exceeds the protocol limit.")
            return json.loads(raw)
    except urllib.error.HTTPError as err:
        if err.code == 404:
            return None
        raise BoundaryError(f"Vault rejected the request (HTTP {err.code}); check the scoped token/policy.") from None
    except (urllib.error.URLError, TimeoutError, ValueError):
        raise BoundaryError("Vault is unreachable or returned an invalid response.") from None


def connect(config: dict) -> str:
    health = request(config["addr"], "/sys/seal-status")
    if not isinstance(health, dict) or health.get("initialized") is not True or health.get("sealed") is not False:
        raise BoundaryError("Vault must already be initialized and unsealed. No initialization was attempted.")
    if health.get("cluster_id") != config["cluster_id"]:
        raise BoundaryError("Vault cluster identity differs from the provisioned store.")
    token = protected_read(config["token_file"]).strip()
    if not token or "\n" in token:
        raise BoundaryError("Vault token file is empty or malformed.")
    info = request(config["addr"], "/auth/token/lookup-self", token)
    data = info.get("data", {}) if isinstance(info, dict) else {}
    raw_policies = data.get("policies", []) if isinstance(data, dict) else []
    if not isinstance(raw_policies, list) or any(not isinstance(p, str) for p in raw_policies):
        raise BoundaryError("Vault token lookup returned an invalid policy shape.")
    policies = set(raw_policies)
    if "a0-cli" not in policies or policies - {"a0-cli", "default"}:
        raise BoundaryError("CLI requires its dedicated a0-cli token; application/root tokens are refused.")
    return token


def key_for(config: dict, token: str, provider: str):
    result = request(config["addr"], f'/{config["mount"]}/data/provider/{provider}', token)
    if result is None:
        return None
    outer = result.get("data") if isinstance(result, dict) else None
    fields = outer.get("data") if isinstance(outer, dict) else None
    if not isinstance(fields, dict):
        raise BoundaryError("Stored provider response has an invalid shape.")
    value = fields.get("api_key") or fields.get("key")
    if value is None or value == "":
        return None
    if not isinstance(value, str) or any(c in value for c in ("\0", "\n", "\r")):
        raise BoundaryError("Stored provider credential has an invalid shape.")
    return value


def child_environment(config: dict, token: str, agent: str) -> dict:
    result = {k: v for k, v in os.environ.items() if k not in SECRET_ENV}
    provider = AGENTS[agent]
    value = key_for(config, token, provider)
    if value:
        result[PROVIDERS[provider]] = value
    elif agent != "codex":
        raise BoundaryError(f"No {provider} credential is configured in OpenBao.")
    # Codex can use its existing account login when no OpenAI API key is stored.
    return result


def site_request(config: dict, operation: str, identity: str = ""):
    bridge = config.get("bridge", {})
    token = protected_read(bridge["token_file"]).strip()
    if not re.fullmatch(r"[a-f0-9]{64}", token):
        raise BoundaryError("Site bridge credential is malformed.")
    endpoint = "handoffs/" + identity if operation == "handoff" else operation
    if operation == "handoff" and not re.fullmatch(r"[a-f0-9]{64}", identity):
        raise BoundaryError("Invalid handoff receipt ID.")
    req = urllib.request.Request(address(bridge["addr"]) + "/api/reliability/" + endpoint,
        headers={"Authorization": "Bearer " + token, "Accept": "application/json"})
    try:
        with urllib.request.build_opener(NoRedirect, urllib.request.ProxyHandler({})).open(req, timeout=15) as response:
            raw = response.read(262145)
            if len(raw) > 262144:
                raise BoundaryError("Bridge response is too large.")
            data = json.loads(raw)
    except (urllib.error.URLError, TimeoutError, ValueError):
        raise BoundaryError("VM bridge request failed; inspect pairing and the A0 service.") from None
    print(data.get("text", "") if operation == "handoff" else json.dumps(data, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=os.environ.get("A0_CLI_VAULT_CONFIG", f"/etc/a0/cli/{os.getuid()}.json"))
    commands = parser.add_subparsers(dest="action", required=True)
    commands.add_parser("status")
    site = commands.add_parser("site")
    site.add_argument("operation", choices=("status", "handoffs", "handoff"))
    site.add_argument("identity", nargs="?", default="")
    run = commands.add_parser("exec")
    run.add_argument("agent", choices=AGENTS)
    run.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    try:
        config = load_config(args.config)
        if args.action == "site":
            site_request(config, args.operation, args.identity)
            return 0
        token = connect(config)
        if args.action == "status":
            states = {p: "present" if key_for(config, token, p) else "missing" for p in PROVIDERS}
            print(json.dumps({"vault": "ready", "cluster_id": config["cluster_id"], "providers": states}))
            return 0
        command = args.command[1:] if args.command[:1] == ["--"] else args.command
        if not command:
            raise BoundaryError("Specify a coding CLI command after --.")
        env = child_environment(config, token, args.agent)
        os.execvpe(command[0], command, env)
    except BoundaryError as err:
        print(f"a0-vault: {err}", file=sys.stderr)
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        print("a0-vault: configuration, credential file or executable unavailable; run ai.sh vault status.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm

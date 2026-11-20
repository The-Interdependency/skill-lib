#!/usr/bin/env python3
# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm
"""VM-local OpenBao credential boundary for ai.sh.

Usage: a0-vault status; a0-vault check deepcode; a0-vault github status|check;
       a0-vault exec deepcode -- deepcodei.
Provision /etc/a0/cli/<uid>.json with A0 operations/configure-vault.py.
Never initializes/unseals Bao. Secrets enter only the selected child environment.
GitHub activation/rotation belongs to the operator's ai.sh github set command.
The VM account and its executed CLI remain trusted; this is not a sandbox.
"""
# === CONTRACTS ===
# id: a0_vault_selected_preflight
#   given: check AGENT with the existing pinned CLI vault configuration
#   then: apply the same selected-provider and enabled-GitHub requirements as exec; return status without dispatch, secret output or vault writes; retain Codex account-login compatibility
#   class: safety
# === END CONTRACTS ===
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

PROVIDERS = {"openai": "OPENAI_API_KEY", "xai": "XAI_API_KEY",
             "deepseek": "DEEPSEEK_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}
AGENTS = {"codex": "openai", "grok": "xai", "deepcode": "deepseek"}
GITHUB_PATH = "integration/github"
SECRET_ENV = set(PROVIDERS.values()) | {"BAO_TOKEN", "VAULT_TOKEN", "BAO_TOKEN_FILE",
    "VAULT_TOKEN_FILE", "BAO_ADDR", "VAULT_ADDR", "A0_DATABASE_URL", "A0_SESSION_SECRET",
    "A0_BOOTSTRAP_CODE", "A0_BRIDGE_TOKEN", "GH_TOKEN", "GITHUB_TOKEN"}


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
    if "github" in data:
        github = data["github"]
        if not isinstance(github, dict) or github.get("path") != GITHUB_PATH:
            raise BoundaryError("GitHub must use the provisioned integration/github path.")
        agents = github.get("agents")
        if (not isinstance(agents, list) or not agents
                or any(not isinstance(agent, str) or agent not in AGENTS for agent in agents)
                or len(set(agents)) != len(agents)):
            raise BoundaryError("GitHub must name a nonempty, unique set of supported coding agents.")
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


def github_token(config: dict, token: str):
    """Read only the selected GitHub integration; never return a cached login."""
    result = request(config["addr"], f'/{config["mount"]}/data/{GITHUB_PATH}', token)
    if result is None:
        return None
    outer = result.get("data") if isinstance(result, dict) else None
    fields = outer.get("data") if isinstance(outer, dict) else None
    if not isinstance(fields, dict):
        raise BoundaryError("Stored GitHub response has an invalid shape.")
    value = fields.get("token")
    if value is None or value == "":
        return None
    if not isinstance(value, str) or not re.fullmatch(r"[\x21-\x7e]{1,4096}", value):
        raise BoundaryError("Stored GitHub credential has an invalid shape.")
    return value


def github_identity(value: str) -> dict:
    """Authenticate at GitHub's fixed endpoint; this does not prove repo access."""
    req = urllib.request.Request("https://api.github.com/user", headers={
        "Authorization": "Bearer " + value,
        "Accept": "application/vnd.github+json", "User-Agent": "a0-vault"})
    try:
        with urllib.request.build_opener(NoRedirect, urllib.request.ProxyHandler({})).open(req, timeout=15) as response:
            raw = response.read(262145)
            if len(raw) > 262144:
                raise BoundaryError("GitHub response exceeds the protocol limit.")
            data = json.loads(raw)
    except urllib.error.HTTPError as err:
        raise BoundaryError(f"GitHub authentication failed (HTTP {err.code}); replace the token with ai.sh github set.") from None
    except (urllib.error.URLError, TimeoutError, ValueError):
        raise BoundaryError("GitHub authentication could not be checked.") from None
    login = data.get("login") if isinstance(data, dict) else None
    if not isinstance(login, str) or not re.fullmatch(r"[A-Za-z0-9-]{1,100}", login):
        raise BoundaryError("GitHub returned an invalid account identity.")
    return {"authenticated": True, "login": login}


def git_environment(result: dict) -> None:
    """Select gh for GitHub HTTPS in this child only, without storing the PAT."""
    if not shutil.which("gh", path=result.get("PATH", os.defpath)):
        raise BoundaryError("Install GitHub CLI (gh) on the VM before launching a GitHub-enabled agent.")
    count = result.get("GIT_CONFIG_COUNT", "0")
    if not re.fullmatch(r"[0-9]{1,3}", count) or int(count) > 256:
        raise BoundaryError("Inherited Git configuration count is invalid.")
    index = int(count)
    if any(f"GIT_CONFIG_KEY_{n}" not in result or f"GIT_CONFIG_VALUE_{n}" not in result for n in range(index)):
        raise BoundaryError("Inherited Git configuration entries are incomplete.")
    # Older inherited command parameters can otherwise override the new helper.
    result.pop("GIT_CONFIG_PARAMETERS", None)
    for key in ("GH_DEBUG", "GIT_TRACE_CURL", "GIT_CURL_VERBOSE"):
        result.pop(key, None)
    # HTTP options choose the most specific matching URL, before config scope.
    # Clear visible path/user-specific GitHub headers as well as the host default.
    try:
        configured = subprocess.run(
            ["git", "config", "--null", "--name-only", "--get-regexp", r"^http\..*\.extraheader$"],
            env=result, capture_output=True, timeout=10, check=False)
    except (OSError, subprocess.TimeoutExpired):
        raise BoundaryError("Git configuration could not be checked before GitHub activation.") from None
    if configured.returncode not in (0, 1) or len(configured.stdout) > 65536:
        raise BoundaryError("Git configuration could not be checked before GitHub activation.")
    header_keys = {"http.https://github.com/.extraHeader"}
    for raw in configured.stdout.split(b"\0"):
        if not raw:
            continue
        key = raw.decode("utf-8")
        scope = key[len("http."):-len(".extraheader")]
        url = urllib.parse.urlsplit(scope)
        if url.scheme == "https" and url.hostname == "github.com":
            header_keys.add(key)
    entries = [
        ("credential.https://github.com.helper", ""),
        ("credential.https://github.com.helper", "!gh auth git-credential"),
    ] + [(key, "") for key in sorted(header_keys)]
    for key, value in entries:
        result[f"GIT_CONFIG_KEY_{index}"] = key
        result[f"GIT_CONFIG_VALUE_{index}"] = value
        index += 1
    result["GIT_CONFIG_COUNT"] = str(index)
    result["GIT_TERMINAL_PROMPT"] = "0"


def github_status(config: dict, token: str, check: bool = False) -> dict:
    github = config.get("github")
    if github is None:
        if check:
            raise BoundaryError("GitHub is not enabled for this account; run ai.sh github set.")
        return {"github": "disabled", "agents": []}
    value = github_token(config, token)
    result = {"github": "present" if value else "missing", "agents": github["agents"]}
    if check:
        if not value:
            raise BoundaryError("No GitHub credential is configured in OpenBao; run ai.sh github set.")
        result.update(github_identity(value))
    return result


def child_environment(config: dict, token: str, agent: str) -> dict:
    result = {k: v for k, v in os.environ.items() if k not in SECRET_ENV}
    provider = AGENTS[agent]
    value = key_for(config, token, provider)
    if value:
        result[PROVIDERS[provider]] = value
    elif agent != "codex":
        raise BoundaryError(f"No {provider} credential is configured in OpenBao.")
    # Codex can use its existing account login when no OpenAI API key is stored.
    if agent in config.get("github", {}).get("agents", []):
        value = github_token(config, token)
        if not value:
            raise BoundaryError("No GitHub credential is configured in OpenBao; run ai.sh github set.")
        result["GH_TOKEN"] = value
        git_environment(result)
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
    preflight = commands.add_parser("check")
    preflight.add_argument("agent", choices=AGENTS)
    github = commands.add_parser("github")
    github.add_argument("operation", choices=("status", "check"))
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
        if args.action == "github":
            print(json.dumps(github_status(config, token, args.operation == "check")))
            return 0
        if args.action == "status":
            states = {p: "present" if key_for(config, token, p) else "missing" for p in PROVIDERS}
            print(json.dumps({"vault": "ready", "cluster_id": config["cluster_id"], "providers": states}))
            return 0
        if args.action == "check":
            child_environment(config, token, args.agent)
            print(json.dumps({"agent": args.agent, "preflight": "passed"}))
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

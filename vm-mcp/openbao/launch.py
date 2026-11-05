#!/usr/bin/env python3
# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm
"""Usage: python3 -I launch.py {grok,codex,deepcode} [--check | -- command]."""
# === MODULE_BUILD ===
# id: openbao_agent_launch
#   module_name: openbao_agent_launch
#   module_kind: adapter
#   summary: fetch one provider key using AppRole, revoke token, exec agent
#   owner: skill-lib
#   public_surface: launch.py agent --check or -- command
#   auth_boundary: read
#   storage_boundary: read
#   network_boundary: internal
#   user_data_boundary: read
#   admin_only: false
#   tests: tests/test_openbao_launch.py
#   rollout: install helper then provision AppRoles before updating ai.sh
#   rollback: stop new launches; retain vault and independent SSH recovery
# === END MODULE_BUILD ===
import argparse
import json
import os
from pathlib import Path
import resource
import ssl
import stat
import sys
import urllib.request

PROVIDERS = {"grok": "XAI_API_KEY", "codex": "OPENAI_API_KEY", "deepcode": "DEEPSEEK_API_KEY"}
KEYS = {*PROVIDERS.values(), "ANTHROPIC_API_KEY"}
ADDRESS = "https://127.0.0.1:8200/v1/"
CA = "/etc/openbao/tls/cert.pem"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("redirect refused")


class Client:
    def __init__(self):
        self.opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}), NoRedirect(),
            urllib.request.HTTPSHandler(context=ssl.create_default_context(cafile=CA)))

    def request(self, path, data=None, token=None):
        headers = {"Content-Type": "application/json"}
        if token:
            headers["X-Vault-Token"] = token
        req = urllib.request.Request(ADDRESS + path, headers=headers,
                                     data=None if data is None else json.dumps(data).encode())
        with self.opener.open(req, timeout=10) as response:
            raw = response.read(65537)
        if len(raw) > 65536:
            raise ValueError("oversize response")
        return json.loads(raw) if raw else {}


def credentials(agent):
    path = Path.home() / ".config/a0/openbao" / (agent + ".json")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd) as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise ValueError("credential permissions")
        data = json.loads(stream.read(16385))
    if set(data) not in ({"role_id", "secret_id"}, {"role_id", "secret_id", "secret_id_accessor"}) or not all(isinstance(v, str) and v for v in data.values()):
        raise ValueError("credential schema")
    return {k: data[k] for k in ("role_id", "secret_id")}


def retrieve(client, agent, login):
    token = client.request("auth/approle/login", login)["auth"]["client_token"]
    if not isinstance(token, str) or not token:
        raise ValueError("missing token")
    try:
        key = client.request("a0/data/providers/" + agent, token=token)["data"]["data"]["key"]
        if not isinstance(key, str) or not key or any(c in key for c in "\x00\r\n"):
            raise ValueError("invalid key")
        return key
    finally:
        # A failed revocation blocks exec; server-side TTL is the crash backstop.
        client.request("auth/token/revoke-self", {}, token)


def clean_environment(source):
    # Avoid unrelated provider credentials and shell startup injection in child.
    return {k: v for k, v in source.items() if k not in KEYS and
            not k.startswith(("BAO_", "VAULT_", "A0_", "BASH_FUNC_", "LD_", "PYTHON")) and
            k not in {"BASH_ENV", "ENV", "SHELLOPTS", "BASHOPTS"}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("agent", choices=PROVIDERS)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("command", nargs="?")
    args = parser.parse_args()
    if not args.check and not args.command:
        parser.error("command required")
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    try:
        key = retrieve(Client(), args.agent, credentials(args.agent))
        if args.check:
            print(args.agent + ": vault retrieval and token revocation passed")
            return 0
        env = clean_environment(os.environ)
        env[PROVIDERS[args.agent]] = key
        os.execve("/bin/bash", ["bash", "--noprofile", "--norc", "-c", args.command], env)
    except Exception:
        # HTTP bodies, exception strings and tracebacks may contain secrets.
        print("OpenBao launch failed; inspect vault health, role policy and credential provisioning.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm

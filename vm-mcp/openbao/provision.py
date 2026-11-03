#!/usr/bin/env python3
# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm
"""Usage: sudo python3 -I provision.py USER AGENT [--resume | --renew]. See OPENBAO.md."""
# === MODULE_BUILD ===
# id: openbao_provider_provision
#   module_name: openbao_provider_provision
#   module_kind: migration
#   summary: provision scoped roles and private credentials; resume or renew explicitly
#   owner: skill-lib
#   public_surface: provision.py USER AGENT --resume or --renew
#   auth_boundary: admin
#   storage_boundary: write
#   network_boundary: internal
#   user_data_boundary: write
#   admin_only: true
#   tests: tests/test_openbao_provision.py
#   rollout: private human terminal after initialization and unseal
#   rollback: revoke role SecretIDs; retain encrypted KV data
# === END MODULE_BUILD ===
import argparse
import getpass
import json
import os
from pathlib import Path
import pwd
import resource
import stat
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from launch import Client, PROVIDERS


def user_file(account, agent, replacement=None, expected=None):
    """All home-directory operations run after permanently dropping root."""
    read_fd, write_fd = os.pipe()
    child = os.fork()
    if child == 0:
        os.close(read_fd)
        try:
            os.setgroups([])
            os.setgid(account.pw_gid)
            os.setuid(account.pw_uid)
            directory = Path(account.pw_dir) / '.config/a0/openbao'
            directory.mkdir(parents=True, exist_ok=True, mode=0o700)
            if directory.is_symlink() or directory.stat().st_uid != account.pw_uid or directory.stat().st_mode & 0o077:
                raise ValueError('private directory required')
            path = directory / (agent + '.json')
            old = None
            if os.path.lexists(path):
                fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
                with os.fdopen(fd) as stream:
                    info = os.fstat(stream.fileno())
                    if not stat.S_ISREG(info.st_mode) or info.st_uid != account.pw_uid or info.st_mode & 0o077:
                        raise ValueError('private regular file required')
                    old = json.loads(stream.read(16385))
                if not isinstance(old.get('secret_id_accessor'), str):
                    raise ValueError('missing accessor')
            if replacement is not None:
                if old != expected:
                    raise ValueError('credential changed concurrently')
                fd, name = tempfile.mkstemp(prefix='.provision-', dir=directory)
                try:
                    with os.fdopen(fd, 'w') as stream:
                        json.dump(replacement, stream)
                        stream.flush()
                        os.fsync(stream.fileno())
                    os.replace(name, path)
                finally:
                    if os.path.exists(name):
                        os.unlink(name)
            # Small private pipe back to parent, never stdout/model output.
            payload = json.dumps(old).encode()
            os.write(write_fd, payload)
            os._exit(0)
        except Exception:
            os._exit(1)
    os.close(write_fd)
    with os.fdopen(read_fd, 'rb') as stream:
        raw = stream.read(16385)
    if os.waitpid(child, 0)[1] != 0 or len(raw) > 16384:
        raise ValueError('credential operation failed')
    return json.loads(raw)


def provision(api, agent, key, old, publish):
    """Server transaction; publish callback owns the local credential boundary."""
    mounts = api('sys/mounts')['data']
    if 'a0/' not in mounts:
        api('sys/mounts/a0', {'type': 'kv', 'options': {'version': '2'}})
    elif mounts['a0/']['type'] != 'kv' or mounts['a0/'].get('options', {}).get('version') != '2':
        raise ValueError('a0 mount conflict')
    auth = api('sys/auth')['data']
    if 'approle/' not in auth:
        api('sys/auth/approle', {'type': 'approle'})
    elif auth['approle/']['type'] != 'approle':
        raise ValueError('auth conflict')
    audits = api('sys/audit')['data']
    if 'a0-file/' not in audits:
        api('sys/audit/a0-file', {'type': 'file', 'options': {'file_path': '/var/log/openbao/audit.json'}})
    elif audits['a0-file/']['type'] != 'file' or audits['a0-file/']['options'].get('log_raw') == 'true':
        raise ValueError('audit conflict')
    role = 'a0-' + agent
    policy = ('path "a0/data/providers/' + agent + '" { capabilities = ["read"] }\n'
              'path "auth/token/revoke-self" { capabilities = ["update"] }\n')
    api('sys/policies/acl/' + role, {'policy': policy})
    api('auth/approle/role/' + role, {'token_policies': [role], 'token_no_default_policy': True,
        'token_type': 'service', 'token_num_uses': 0, 'token_ttl': '60s', 'token_max_ttl': '60s', 'token_explicit_max_ttl': '60s',
        'secret_id_ttl': '720h', 'secret_id_num_uses': 0, 'bind_secret_id': True,
        'secret_id_bound_cidrs': ['127.0.0.1/32'], 'token_bound_cidrs': ['127.0.0.1/32']})
    if key is not None:
        api('a0/data/providers/' + agent, {'options': {'cas': 0}, 'data': {'key': key}})
    else:
        # Resume/renew preserves the stored provider key and refuses a missing key.
        stored = api('a0/data/providers/' + agent)['data']['data']['key']
        if not isinstance(stored, str) or not stored:
            raise ValueError('missing key')
    role_id = api('auth/approle/role/' + role + '/role-id')['data']['role_id']
    issued = api('auth/approle/role/' + role + '/secret-id', {})['data']
    credential = {'role_id': role_id, 'secret_id': issued['secret_id'], 'secret_id_accessor': issued['secret_id_accessor']}
    try:
        publish(credential)
    except Exception:
        api('auth/approle/role/' + role + '/secret-id-accessor/destroy', {'secret_id_accessor': issued['secret_id_accessor']})
        raise
    if old:
        api('auth/approle/role/' + role + '/secret-id-accessor/destroy', {'secret_id_accessor': old['secret_id_accessor']})
    return credential['secret_id_accessor']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('user')
    parser.add_argument('agent', choices=PROVIDERS)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--resume', action='store_true')
    mode.add_argument('--renew', action='store_true')
    args = parser.parse_args()
    if os.geteuid() != 0 or not sys.stdin.isatty():
        parser.error('run as root from a private human terminal')
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    os.umask(0o077)
    try:
        account = pwd.getpwnam(args.user)
        if account.pw_uid == 0:
            raise ValueError('non-root agent account required')
        old = user_file(account, args.agent)
        if bool(old) != args.renew:
            raise ValueError('renew requires existing credential; initial/resume requires absent credential')
        token = getpass.getpass('Temporary OpenBao administrator token (revoked on success): ')
        key = None if args.resume or args.renew else getpass.getpass('Provider API key: ')
        if not token or (key is not None and (not key or any(c in key for c in '\x00\r\n'))):
            raise ValueError('invalid input')
        client = Client()
        def api(path, data=None):
            return client.request(path, data, token)
        accessor = provision(api, args.agent, key, old,
            lambda value: user_file(account, args.agent, value, old))
        api('auth/token/revoke-self', {})
        print('Provisioned ' + args.agent + '; admin token revoked; renew AppRole before 30 days.')
        return 0
    except Exception:
        print('Provisioning failed; partial state may exist. Follow OPENBAO.md recovery. No secret values printed.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm

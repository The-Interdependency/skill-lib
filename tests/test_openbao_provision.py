"""Offline provisioning transition tests; production acceptance remains separate."""
import importlib.util
from pathlib import Path
import unittest
import os
import tempfile
import types

ROOT = Path(__file__).resolve().parents[1] / 'vm-mcp/openbao'
spec = importlib.util.spec_from_file_location('provision_bao', ROOT / 'provision.py')
provision = importlib.util.module_from_spec(spec)
spec.loader.exec_module(provision)


class API:
    def __init__(self):
        self.calls = []

    def __call__(self, path, data=None):
        self.calls.append((path, data))
        if path in ('sys/mounts', 'sys/auth', 'sys/audit'):
            return {'data': {}}
        if path.endswith('/role-id'):
            return {'data': {'role_id': 'role'}}
        if path.endswith('/secret-id'):
            return {'data': {'secret_id': 'new-id', 'secret_id_accessor': 'new-accessor'}}
        if path.startswith('a0/data/') and data is None:
            return {'data': {'data': {'key': 'stored-key'}}}
        return {}


class ProvisionTests(unittest.TestCase):
    @unittest.skipUnless(os.geteuid() == 0, 'requires privilege-drop fixture')
    def test_credential_publication_drops_uid_and_renews(self):
        with tempfile.TemporaryDirectory() as home:
            try:
                os.chown(home, 65534, 65534)
            except OSError as error:
                if error.errno == 22:
                    self.skipTest("container does not map fixture UID 65534")
                raise
            account = types.SimpleNamespace(pw_uid=65534, pw_gid=65534, pw_dir=home)
            self.assertIsNone(provision.user_file(account, 'grok'))
            first = {'role_id': 'r', 'secret_id': 's', 'secret_id_accessor': 'a'}
            provision.user_file(account, 'grok', first, None)
            path = Path(home) / '.config/a0/openbao/grok.json'
            self.assertEqual(path.stat().st_uid, 65534)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(provision.user_file(account, 'grok'), first)
            second = dict(first, secret_id='s2', secret_id_accessor='a2')
            provision.user_file(account, 'grok', second, first)
            self.assertEqual(provision.user_file(account, 'grok'), second)
            with self.assertRaises(ValueError):
                provision.user_file(account, 'grok', first, first)

    def test_initial_key_write_is_no_clobber(self):
        api = API()
        published = []
        provision.provision(api, 'grok', 'key', None, published.append)
        self.assertIn(('a0/data/providers/grok', {'options': {'cas': 0}, 'data': {'key': 'key'}}), api.calls)
        self.assertEqual(published[0]['secret_id_accessor'], 'new-accessor')
        role = dict(api.calls)['auth/approle/role/a0-grok']
        self.assertEqual(role['token_explicit_max_ttl'], '60s')
        self.assertTrue(role['token_no_default_policy'])
        policy = dict(api.calls)['sys/policies/acl/a0-grok']['policy']
        self.assertNotIn('codex', policy)
        self.assertNotIn('list', policy)

    def test_renew_preserves_key_and_revokes_old_after_publish(self):
        api = API()
        def publish(credential):
            self.assertFalse(any(p.endswith('/destroy') for p, _ in api.calls))
        provision.provision(api, 'codex', None, {'secret_id_accessor': 'old-accessor'}, publish)
        self.assertEqual([data for p, data in api.calls if p == 'a0/data/providers/codex'], [None])
        self.assertEqual(api.calls[-1], ('auth/approle/role/a0-codex/secret-id-accessor/destroy', {'secret_id_accessor': 'old-accessor'}))

    def test_failed_publication_destroys_new_credential(self):
        api = API()
        def fail(credential):
            raise OSError('private publication failed')
        with self.assertRaises(OSError):
            provision.provision(api, 'grok', None, None, fail)
        self.assertEqual(api.calls[-1][1], {'secret_id_accessor': 'new-accessor'})

    def test_resume_reads_existing_key(self):
        api = API()
        provision.provision(api, 'deepcode', None, None, lambda value: None)
        self.assertIn(('a0/data/providers/deepcode', None), api.calls)
        self.assertFalse(any(p.endswith('/destroy') for p, _ in api.calls))

    def test_wrong_mount_fails_before_write(self):
        api = API()
        def conflict(path, data=None):
            if path == 'sys/mounts':
                return {'data': {'a0/': {'type': 'transit'}}}
            return api(path, data)
        with self.assertRaises(ValueError):
            provision.provision(conflict, 'grok', 'key', None, lambda value: None)
        self.assertEqual(api.calls, [])


if __name__ == '__main__':
    unittest.main()

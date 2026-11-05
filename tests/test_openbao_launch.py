"""Offline security contracts for provider-scoped launch; no production secrets."""
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import contextlib

PATH = Path(__file__).resolve().parents[1] / 'vm-mcp/openbao/launch.py'
spec = importlib.util.spec_from_file_location('bao_launch', PATH)
launch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launch)


class Fake:
    def __init__(self, fail_read=False, fail_revoke=False, key='test-only-key'):
        self.calls = []
        self.fail_read = fail_read
        self.fail_revoke = fail_revoke
        self.key = key

    def request(self, path, data=None, token=None):
        self.calls.append((path, data, token))
        if path == 'auth/approle/login':
            return {'auth': {'client_token': 'temporary-test-token'}}
        if path == 'auth/token/revoke-self':
            if self.fail_revoke:
                raise RuntimeError('secret-in-error')
            return {}
        if self.fail_read:
            raise RuntimeError('secret-in-error')
        return {'data': {'data': {'key': self.key}}}


class LaunchTests(unittest.TestCase):
    def test_provider_scope_and_revoke(self):
        for agent in launch.PROVIDERS:
            client = Fake()
            self.assertEqual(launch.retrieve(client, agent, {'role_id': 'r', 'secret_id': 's'}), 'test-only-key')
            self.assertEqual([c[0] for c in client.calls], ['auth/approle/login', 'a0/data/providers/' + agent, 'auth/token/revoke-self'])
            self.assertEqual(client.calls[1][2], 'temporary-test-token')

    def test_failed_read_revokes(self):
        client = Fake(fail_read=True)
        with self.assertRaises(RuntimeError):
            launch.retrieve(client, 'grok', {})
        self.assertEqual(client.calls[-1][0], 'auth/token/revoke-self')

    def test_failed_revoke_blocks_delivery(self):
        with self.assertRaises(RuntimeError):
            launch.retrieve(Fake(fail_revoke=True), 'codex', {})

    def test_bad_key_is_rejected_and_token_revoked(self):
        for key in ('', None, 'bad\nkey', 'bad\0key'):
            client = Fake(key=key)
            with self.assertRaises(ValueError):
                launch.retrieve(client, 'grok', {})
            self.assertEqual(client.calls[-1][0], 'auth/token/revoke-self')

    def test_credential_permissions_and_symlink(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(launch.Path, 'home', return_value=Path(temp)):
            directory = Path(temp) / '.config/a0/openbao'
            directory.mkdir(parents=True)
            path = directory / 'grok.json'
            data = {'role_id': 'r', 'secret_id': 's'}
            path.write_text(json.dumps(data))
            path.chmod(0o600)
            self.assertEqual(launch.credentials('grok'), data)
            path.chmod(0o644)
            with self.assertRaises(ValueError):
                launch.credentials('grok')
            path.unlink()
            path.symlink_to('/dev/null')
            with self.assertRaises(OSError):
                launch.credentials('grok')

    def test_child_environment_strips_other_keys_and_startup_hooks(self):
        dirty = dict.fromkeys(launch.KEYS | {'BAO_TOKEN', 'VAULT_TOKEN', 'BASH_ENV', 'ENV', 'LD_PRELOAD', 'PYTHONPATH', 'A0_KEY'}, 'secret')
        dirty['PATH'] = '/usr/bin:/bin'
        self.assertEqual(launch.clean_environment(dirty), {'PATH': '/usr/bin:/bin'})

    def test_main_execs_only_selected_key_without_login_shell(self):
        client = Fake()
        with patch.object(launch, 'Client', return_value=client), patch.object(launch, 'credentials', return_value={}), patch.object(launch.os, 'execve') as execute, patch.object(launch.sys, 'argv', ['launch.py', 'codex', '--', 'codex --yolo']), patch.object(launch.resource, 'setrlimit'), patch.dict(os.environ, {'XAI_API_KEY': 'old', 'OPENAI_API_KEY': 'old'}, clear=True):
            launch.main()
        args = execute.call_args.args
        self.assertEqual(args[1], ['bash', '--noprofile', '--norc', '-c', 'codex --yolo'])
        self.assertEqual(args[2], {'OPENAI_API_KEY': 'test-only-key'})

    def test_check_does_not_exec_or_print_key(self):
        output = io.StringIO()
        with patch.object(launch, 'Client', return_value=Fake()), patch.object(launch, 'credentials', return_value={}), patch.object(launch.os, 'execve') as execute, patch.object(launch.sys, 'argv', ['launch.py', 'grok', '--check']), patch.object(launch.resource, 'setrlimit'), contextlib.redirect_stdout(output):
            self.assertEqual(launch.main(), 0)
        execute.assert_not_called()
        self.assertNotIn('test-only-key', output.getvalue())

    def test_error_does_not_expose_body_or_launch(self):
        output = io.StringIO()
        with patch.object(launch, 'Client', return_value=Fake(fail_read=True)), patch.object(launch, 'credentials', return_value={}), patch.object(launch.os, 'execve') as execute, patch.object(launch.sys, 'argv', ['launch.py', 'grok', '--', 'grok']), patch.object(launch.resource, 'setrlimit'), contextlib.redirect_stderr(output):
            self.assertEqual(launch.main(), 1)
        execute.assert_not_called()
        self.assertNotIn('secret-in-error', output.getvalue())

    def test_redirect_denied(self):
        with self.assertRaises(ValueError):
            launch.NoRedirect().redirect_request(None, None, 307, '', {}, 'https://other.example')


if __name__ == '__main__':
    unittest.main()

"""Execute the real helper against inert HTTP fixtures; never contact a live vault."""
import contextlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

HELPER = Path(__file__).resolve().parents[1] / 'tools/a0_vault.py'
CANARY = 'fixture-provider-secret-not-for-output'


class VaultTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.paths = []
        self.sealed = False
        self.initialized = True
        self.cluster = 'fixture-cluster'
        self.policies = ['a0-cli']
        self.expired = False
        self.missing = False
        self.redirect = False
        test = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass

            def do_GET(self):
                test.paths.append(self.path)
                status = 200
                if test.redirect:
                    self.send_response(302)
                    self.send_header('Location', '/leak')
                    self.end_headers()
                    return
                if self.path == '/v1/sys/seal-status':
                    data = {'initialized': test.initialized, 'sealed': test.sealed, 'cluster_id': test.cluster}
                elif self.path == '/v1/auth/token/lookup-self':
                    status = 403 if test.expired else 200
                    data = {'data': {'policies': test.policies}, 'errors': [CANARY]}
                elif self.path.startswith('/v1/a0/data/provider/'):
                    status = 404 if test.missing else 200
                    data = {'data': {'data': {'api_key': CANARY}}}
                else:
                    status, data = 404, {}
                self.send_response(status)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        token = self.root / 'token'
        token.write_text('fixture-cli-token')
        token.chmod(0o600)
        self.config = self.root / 'config.json'
        self.config.write_text(json.dumps({'schema': 'a0.cli-vault/1', 'addr': f'http://127.0.0.1:{self.server.server_port}',
            'mount': 'a0', 'cluster_id': self.cluster, 'token_file': str(token)}))
        self.config.chmod(0o600)

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temp.cleanup()

    def invoke(self, *args, env=None):
        return subprocess.run([sys.executable, str(HELPER), '--config', str(self.config), *args],
            capture_output=True, text=True, env=env)

    def test_status_redacts_values_and_reads_exact_a0_paths(self):
        result = self.invoke('status')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(CANARY, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['providers']['deepseek'], 'present')
        self.assertIn('/v1/a0/data/provider/deepseek', self.paths)

    def test_child_gets_only_selected_provider_and_never_vault_or_app_credentials(self):
        env = {**os.environ, 'OPENAI_API_KEY': 'stale', 'XAI_API_KEY': 'stale', 'DEEPSEEK_API_KEY': 'stale',
               'BAO_TOKEN': 'root-canary', 'VAULT_TOKEN': 'root-canary', 'A0_DATABASE_URL': 'db-canary'}
        code = "import os,json; print(json.dumps({'selected':os.environ.get('OPENAI_API_KEY')=='fixture-provider-secret-not-for-output','other':any(k in os.environ for k in ['XAI_API_KEY','DEEPSEEK_API_KEY','BAO_TOKEN','VAULT_TOKEN','A0_DATABASE_URL'])}))"
        result = self.invoke('exec', 'codex', '--', sys.executable, '-c', code, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {'selected': True, 'other': False})
        self.assertEqual([p for p in self.paths if '/provider/' in p], ['/v1/a0/data/provider/openai'])

    def test_deleted_key_cannot_fall_back_to_stale_environment(self):
        self.missing = True
        result = self.invoke('exec', 'codex', '--', sys.executable, '-c', "import os; print('OPENAI_API_KEY' in os.environ)",
            env={**os.environ, 'OPENAI_API_KEY': 'stale'})
        self.assertEqual(result.stdout.strip(), 'False')
        self.assertEqual(result.returncode, 0)  # Existing Codex account login remains possible.
        self.assertNotEqual(self.invoke('exec', 'deepcode', '--', 'true').returncode, 0)

    def test_launcher_carries_login_cli_and_runtime_path_into_stale_tmux(self):
        login = self.root / 'login bin'
        login.mkdir()
        helper = self.root / 'a0-vault'
        helper.write_text(HELPER.read_text())
        helper.chmod(0o700)
        cli = login / 'fixture-cli'
        cli.write_text('#!/usr/bin/env fixture-runtime\n')
        runtime = login / 'fixture-runtime'
        runtime.write_text('''#!/bin/bash
set -eu
[[ "$2" == 'literal argument' ]]
[[ -n "$OPENAI_API_KEY" && -z "${XAI_API_KEY+x}" && -z "${BAO_TOKEN+x}" ]]
printf '%s\\n' LOGIN-PATH-AND-KEY-OK
''')
        tmux = login / 'tmux'
        tmux.write_text('''#!/bin/bash
set -eu
if [[ "$1" == respawn-pane ]]; then
  PATH=/usr/bin:/bin /bin/bash -c "$5"
fi
''')
        for file in (cli, runtime, tmux):
            file.chmod(0o700)
        script = '''source "$1" help >/dev/null
remote() { PATH="$LOGIN_PATH" /bin/bash -c "$1"; }
pipe_log() { :; }
respawn codex 'fixture-cli "literal argument"'
'''
        result = subprocess.run(['/bin/bash', '-c', script, 'fixture', str(HELPER.with_name('ai.sh'))],
            env={**os.environ, 'LOGIN_PATH': str(login) + ':' + os.environ['PATH'],
                 'A0_AI_VAULT_HELPER': str(helper), 'A0_CLI_VAULT_CONFIG': str(self.config),
                 'OPENAI_API_KEY': 'stale', 'XAI_API_KEY': 'stale', 'BAO_TOKEN': 'stale'},
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'LOGIN-PATH-AND-KEY-OK')
        self.assertNotIn(CANARY, result.stdout + result.stderr)

    def test_unavailable_identity_seal_and_root_token_never_dispatch_child(self):
        for attr, value in [('sealed', True), ('initialized', False), ('cluster', 'wrong'), ('policies', ['root']), ('expired', True), ('redirect', True)]:
            with self.subTest(attr=attr):
                old = getattr(self, attr)
                setattr(self, attr, value)
                result = self.invoke('exec', 'codex', '--', sys.executable, '-c', "print('CHILD-RAN')")
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn('CHILD-RAN', result.stdout)
                self.assertNotIn(CANARY, result.stdout + result.stderr)
                setattr(self, attr, old)
        self.assertFalse(any('/init' in p or '/unseal' in p or p == '/leak' for p in self.paths))

    def test_symlink_and_world_readable_credentials_fail_closed(self):
        token = self.root / 'token'
        token.chmod(0o644)
        self.assertNotEqual(self.invoke('status').returncode, 0)
        token.unlink()
        source = self.root / 'other'
        source.write_text('fixture-cli-token')
        source.chmod(0o600)
        token.symlink_to(source)
        self.assertNotEqual(self.invoke('status').returncode, 0)


if __name__ == '__main__':
    unittest.main()

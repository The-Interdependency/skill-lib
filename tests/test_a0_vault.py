"""Execute the real helper against inert HTTP fixtures; never contact a live vault."""
import contextlib
import hashlib
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
GITHUB_CANARY = 'fixture-github-secret-not-for-output'


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
        self.github_status = 200
        self.github_token = GITHUB_CANARY
        self.github_response = None
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
                elif self.path == '/v1/a0/data/integration/github':
                    status = test.github_status
                    data = test.github_response if test.github_response is not None else {
                        'data': {'data': {'token': test.github_token}}}
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
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        self.gh = self.bin / 'gh'
        self.gh.write_text(f'''#!{sys.executable}
import json, os, sys
from pathlib import Path
if sys.argv[1:] != ['auth', 'git-credential', 'get']:
    raise SystemExit(98)
sys.stdin.read()
if os.environ.get('FIXTURE_GH_TRACE'):
    Path(os.environ['FIXTURE_GH_TRACE']).write_text(json.dumps(sys.argv[1:]))
print('username=fixture-github')
print('password=' + os.environ.get('GH_TOKEN', 'stale-disk-cache-credential'))
''')
        self.gh.chmod(0o700)

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temp.cleanup()

    def invoke(self, *args, env=None, with_gh=True):
        child_env = {**os.environ, **(env or {})}
        if with_gh:
            child_env['PATH'] = str(self.bin) + os.pathsep + child_env.get('PATH', '')
        return subprocess.run([sys.executable, str(HELPER), '--config', str(self.config), *args],
            capture_output=True, text=True, env=child_env)

    def configure_github(self, value=None):
        config = json.loads(self.config.read_text())
        config['github'] = value if value is not None else {
            'path': 'integration/github', 'agents': ['deepcode']}
        self.config.write_text(json.dumps(config))

    def guarded_github(self, operation, *, status=200, payload=None):
        """Run the CLI with only Vault fixture traffic and a simulated GitHub response."""
        trace = self.root / 'github-network.json'
        trace.write_text('[]')
        wrapper = self.root / 'github-network-guard.py'
        fixture_origin = f'http://127.0.0.1:{self.server.server_port}/v1/'
        if payload is None:
            payload = {'login': 'fixture-owner', 'id': 17}
        wrapper.write_text(f'''import hashlib, io, json, runpy, sys, urllib.error, urllib.request
from pathlib import Path
trace = Path({str(trace)!r})
original = urllib.request.build_opener
class Reply(io.BytesIO):
    status = 200
    def getcode(self):
        return self.status
class Guard:
    def __init__(self, *args, **kwargs):
        self.inner = original(*args, **kwargs)
    def open(self, request, *args, **kwargs):
        url = request.full_url
        if url.startswith({fixture_origin!r}):
            return self.inner.open(request, *args, **kwargs)
        headers = {{key.lower(): value for key, value in request.header_items()}}
        calls = json.loads(trace.read_text())
        calls.append({{'url': url, 'method': request.get_method(),
            'authorization_ok': hashlib.sha256(headers.get('authorization', '').encode()).hexdigest() == {hashlib.sha256(('Bearer ' + self.github_token).encode()).hexdigest()!r},
            'vault_token_sent': 'x-vault-token' in headers,
            'accept': headers.get('accept'), 'user_agent': headers.get('user-agent')}})
        trace.write_text(json.dumps(calls))
        if url != 'https://api.github.com/user':
            raise AssertionError('Unexpected external network destination')
        body = json.dumps({payload!r}).encode()
        if {status} != 200:
            raise urllib.error.HTTPError(url, {status}, 'fixture failure', {{'Location': 'https://attacker.invalid/leak'}}, io.BytesIO(body))
        return Reply(body)
urllib.request.build_opener = Guard
sys.argv = [{str(HELPER)!r}, '--config', {str(self.config)!r}, 'github', {operation!r}]
runpy.run_path({str(HELPER)!r}, run_name='__main__')
''')
        result = subprocess.run([sys.executable, str(wrapper)], capture_output=True, text=True)
        return result, json.loads(trace.read_text())

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

    def test_github_enabled_child_receives_only_fresh_github_credential(self):
        self.configure_github()
        code = '''import hashlib, json, os, sys
print(json.dumps({
    'github_matches': hashlib.sha256(os.environ.get('GH_TOKEN', '').encode()).hexdigest() == sys.argv[1],
    'legacy_github_absent': 'GITHUB_TOKEN' not in os.environ,
    'selected_provider': 'DEEPSEEK_API_KEY' in os.environ,
    'other_secrets_absent': not any(k in os.environ for k in ['OPENAI_API_KEY', 'XAI_API_KEY', 'BAO_TOKEN', 'VAULT_TOKEN']),
    'token_absent_from_argv': os.environ.get('GH_TOKEN') not in '\\0'.join(sys.argv),
}))
'''
        result = self.invoke('exec', 'deepcode', '--', sys.executable, '-c', code,
            hashlib.sha256(GITHUB_CANARY.encode()).hexdigest(),
            env={'GH_TOKEN': 'stale-gh-token', 'GITHUB_TOKEN': 'stale-github-token',
                 'OPENAI_API_KEY': 'stale-openai-token', 'BAO_TOKEN': 'stale-root-token'})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {
            'github_matches': True, 'legacy_github_absent': True, 'selected_provider': True,
            'other_secrets_absent': True, 'token_absent_from_argv': True})
        self.assertEqual([path for path in self.paths if '/data/' in path], [
            '/v1/a0/data/provider/deepseek', '/v1/a0/data/integration/github'])
        self.assertNotIn(GITHUB_CANARY, result.stdout + result.stderr)

    def test_github_token_rotation_is_read_by_the_next_actual_child(self):
        self.configure_github()
        code = "import hashlib,os,sys; print(hashlib.sha256(os.environ.get('GH_TOKEN','').encode()).hexdigest() == sys.argv[1])"
        for value in (GITHUB_CANARY, 'fixture-rotated-github-secret'):
            with self.subTest(rotation=value != GITHUB_CANARY):
                self.github_token = value
                result = self.invoke('exec', 'deepcode', '--', sys.executable, '-c', code,
                    hashlib.sha256(value.encode()).hexdigest(), env={'GH_TOKEN': 'stale'})
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.strip(), 'True')
                self.assertNotIn(value, result.stdout + result.stderr)
        self.assertEqual(self.paths.count('/v1/a0/data/integration/github'), 2)

    def test_github_is_not_fetched_or_inherited_for_agents_outside_the_allowlist(self):
        self.configure_github()
        self.github_status = 403
        for agent in ('codex', 'grok'):
            with self.subTest(agent=agent):
                result = self.invoke('exec', agent, '--', sys.executable, '-c',
                    "import os; print(any(k in os.environ for k in ('GH_TOKEN','GITHUB_TOKEN')))",
                    env={'GH_TOKEN': 'stale-gh-token', 'GITHUB_TOKEN': 'stale-github-token'})
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.strip(), 'False')
        self.assertNotIn('/v1/a0/data/integration/github', self.paths)

    def test_unconfigured_github_is_not_fetched_or_inherited(self):
        result = self.invoke('exec', 'deepcode', '--', sys.executable, '-c',
            "import os; print(any(k in os.environ for k in ('GH_TOKEN','GITHUB_TOKEN')))",
            env={'GH_TOKEN': 'stale-gh-token', 'GITHUB_TOKEN': 'stale-github-token'})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'False')
        self.assertNotIn('/v1/a0/data/integration/github', self.paths)

    def test_deleted_github_token_never_dispatches_a_child_that_can_read_gh_disk_cache(self):
        self.configure_github()
        marker = self.root / 'gh-called.json'
        code = "import subprocess; subprocess.run(['gh','auth','git-credential','get'], input='protocol=https\\nhost=github.com\\n\\n', text=True, capture_output=True, check=True); print('CHILD-RAN')"
        first = self.invoke('exec', 'deepcode', '--', sys.executable, '-c', code,
            env={'FIXTURE_GH_TRACE': str(marker)})
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertTrue(marker.exists())
        marker.unlink()
        self.github_status = 404
        deleted = self.invoke('exec', 'deepcode', '--', sys.executable, '-c', code,
            env={'FIXTURE_GH_TRACE': str(marker), 'GH_TOKEN': 'stale-gh-token',
                 'GITHUB_TOKEN': 'stale-github-token'})
        self.assertNotEqual(deleted.returncode, 0)
        self.assertNotIn('CHILD-RAN', deleted.stdout)
        self.assertFalse(marker.exists(), 'Child reached gh credential-cache fallback after vault deletion')
        self.assertNotIn(GITHUB_CANARY, deleted.stdout + deleted.stderr)

    def test_github_denial_and_malformed_values_never_dispatch_child_or_print_secrets(self):
        self.configure_github()
        cases = [
            (403, {'errors': [GITHUB_CANARY]}),
            (200, []),
            (200, {'data': []}),
            (200, {'data': {'data': {'api_key': GITHUB_CANARY}}}),
        ]
        for value in ('', None, 42, {}, 'has space', 'line\nbreak', 'carriage\rreturn',
                      'nul\0byte', '\u00eb', 'a' * 4097):
            cases.append((200, {'data': {'data': {'token': value}}}))
        for index, (status, payload) in enumerate(cases):
            with self.subTest(case=index):
                self.github_status, self.github_response = status, payload
                result = self.invoke('exec', 'deepcode', '--', sys.executable, '-c', "print('CHILD-RAN')",
                    env={'GH_TOKEN': 'stale-gh-token', 'GITHUB_TOKEN': 'stale-github-token'})
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn('CHILD-RAN', result.stdout)
                self.assertNotIn(GITHUB_CANARY, result.stdout + result.stderr)

    def test_github_configuration_rejects_unknown_paths_and_invalid_agent_lists(self):
        invalid = [
            {'path': 'provider/deepseek', 'agents': ['deepcode']},
            {'path': '../integration/github', 'agents': ['deepcode']},
            {'path': '/integration/github', 'agents': ['deepcode']},
            {'path': 'https://attacker.invalid/credential', 'agents': ['deepcode']},
            {'path': 'integration/github', 'agents': ['shell']},
            {'path': 'integration/github', 'agents': ['deepcode', 'unknown']},
            {'path': 'integration/github', 'agents': ['deepcode', 'deepcode']},
            {'path': 'integration/github', 'agents': 'deepcode'},
            {'path': 'integration/github', 'agents': []},
            {'path': 'integration/github'},
            ['integration/github', 'deepcode'],
        ]
        for value in invalid:
            with self.subTest(config=value):
                self.configure_github(value)
                result = self.invoke('exec', 'deepcode', '--', sys.executable, '-c', "print('CHILD-RAN')")
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn('CHILD-RAN', result.stdout)
        self.assertEqual(self.paths, [], 'Invalid configuration must fail before requesting secrets')

    def test_enabled_github_requires_gh_before_child_dispatch(self):
        self.configure_github()
        result = self.invoke('exec', 'deepcode', '--', sys.executable, '-c', "print('CHILD-RAN')",
            env={'PATH': str(self.root / 'no-executables')}, with_gh=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('CHILD-RAN', result.stdout)
        self.assertNotIn(GITHUB_CANARY, result.stdout + result.stderr)

    def test_real_git_credential_lookup_uses_fresh_token_over_persisted_and_inherited_credentials(self):
        self.configure_github()
        import shutil
        git = shutil.which('git')
        self.assertIsNotNone(git, 'git is required to verify the credential routing contract')
        stale_marker = self.root / 'stale-helper-used'
        stale_helper = self.root / 'stale-helper'
        stale_helper.write_text(f'''#!{sys.executable}
from pathlib import Path
Path({str(stale_marker)!r}).write_text('called')
print('username=stale')
print('password=stale-persisted-credential')
''')
        stale_helper.chmod(0o700)
        config = self.root / 'gitconfig'
        config.write_text(f'''[credential "https://github.com"]
    helper = !{stale_helper}
[http "https://github.com/"]
    extraHeader = Authorization: bearer stale-persisted-header
[http "https://github.com/The-Interdependency/"]
    extraHeader = Authorization: bearer stale-persisted-path-header
''')
        code = '''import json,os,subprocess,sys
def run(*args, **kwargs):
    return subprocess.run([sys.argv[1], '-C', sys.argv[2], *args], capture_output=True, text=True, check=True, **kwargs)
result = run('credential', 'fill', input='protocol=https\\nhost=github.com\\n\\n')
credential = dict(line.split('=', 1) for line in result.stdout.splitlines() if '=' in line)
headers = run('config', '--get-all', 'http.https://github.com/.extraHeader').stdout.splitlines()
specific_headers = run('config', '--get-urlmatch', 'http.extraHeader', 'https://github.com/The-Interdependency/a0').stdout.splitlines()
print(json.dumps({
    'fresh_password': credential.get('password') == os.environ.get('GH_TOKEN'),
    'legacy_github_absent': 'GITHUB_TOKEN' not in os.environ,
    'parameters_absent': 'GIT_CONFIG_PARAMETERS' not in os.environ,
    'header_reset': bool(headers) and headers[-1] == '',
    'specific_header_reset': bool(specific_headers) and specific_headers[-1] == '',
    'benign_config_preserved': run('config', 'user.email').stdout.strip() == 'fixture@example.invalid',
}))
'''
        result = self.invoke('exec', 'deepcode', '--', sys.executable, '-c', code, git, str(self.root),
            env={'GIT_CONFIG_GLOBAL': str(config), 'GIT_CONFIG_NOSYSTEM': '1',
                 'GIT_CONFIG_COUNT': '4', 'GIT_CONFIG_KEY_0': 'user.email',
                 'GIT_CONFIG_VALUE_0': 'fixture@example.invalid',
                 'GIT_CONFIG_KEY_1': 'credential.https://github.com.helper',
                 'GIT_CONFIG_VALUE_1': '!' + str(stale_helper),
                 'GIT_CONFIG_KEY_2': 'http.https://github.com/.extraHeader',
                 'GIT_CONFIG_VALUE_2': 'Authorization: bearer stale-inherited-header',
                 'GIT_CONFIG_KEY_3': 'http.https://github.com/The-Interdependency/a0.extraHeader',
                 'GIT_CONFIG_VALUE_3': 'Authorization: bearer stale-inherited-path-header',
                 'GIT_CONFIG_PARAMETERS': "'credential.https://github.com.helper=!'",
                 'GH_TOKEN': 'stale-gh-token', 'GITHUB_TOKEN': 'stale-github-token'})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {
            'fresh_password': True, 'legacy_github_absent': True, 'parameters_absent': True,
            'header_reset': True, 'specific_header_reset': True, 'benign_config_preserved': True})
        self.assertFalse(stale_marker.exists(), 'Git reached an old credential helper')
        self.assertNotIn(GITHUB_CANARY, result.stdout + result.stderr)

    def test_github_status_reports_presence_without_github_network_or_token_output(self):
        self.configure_github()
        result, calls = self.guarded_github('status')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {'github': 'present', 'agents': ['deepcode']})
        self.assertEqual(calls, [])
        self.assertNotIn(GITHUB_CANARY, result.stdout + result.stderr)
        self.assertEqual([path for path in self.paths if '/data/' in path], ['/v1/a0/data/integration/github'])
        self.github_status = 404
        missing, calls = self.guarded_github('status')
        self.assertEqual(missing.returncode, 0, missing.stderr)
        self.assertEqual(json.loads(missing.stdout)['github'], 'missing')
        self.assertEqual(calls, [])

    def test_github_check_contacts_only_fixed_github_endpoint_and_redacts_the_secret(self):
        self.configure_github()
        result, calls = self.guarded_github('check')
        self.assertEqual(result.returncode, 0, result.stderr)
        state = json.loads(result.stdout)
        self.assertTrue(state['authenticated'])
        self.assertEqual(state['login'], 'fixture-owner')
        self.assertEqual(calls, [{
            'url': 'https://api.github.com/user', 'method': 'GET', 'authorization_ok': True,
            'vault_token_sent': False, 'accept': 'application/vnd.github+json', 'user_agent': 'a0-vault'}])
        self.assertNotIn(GITHUB_CANARY, result.stdout + result.stderr)

    def test_github_check_refuses_remote_errors_without_response_body_disclosure(self):
        self.configure_github()
        for status in (302, 401, 403, 429, 500):
            with self.subTest(status=status):
                result, calls = self.guarded_github('check', status=status,
                    payload={'message': GITHUB_CANARY})
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(len(calls), 1, 'No redirect or retry may send the secret elsewhere')
                self.assertEqual(calls[0]['url'], 'https://api.github.com/user')
                self.assertNotIn(GITHUB_CANARY, result.stdout + result.stderr)

    def test_github_check_never_contacts_github_for_missing_or_disabled_secret(self):
        disabled, calls = self.guarded_github('status')
        self.assertEqual(disabled.returncode, 0, disabled.stderr)
        self.assertEqual(json.loads(disabled.stdout), {'github': 'disabled', 'agents': []})
        self.assertEqual(calls, [])
        for enabled in (False, True):
            with self.subTest(enabled=enabled):
                if enabled:
                    self.configure_github()
                    self.github_status = 404
                result, calls = self.guarded_github('check')
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(calls, [])


if __name__ == '__main__':
    unittest.main()

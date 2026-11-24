from __future__ import annotations

import json
import os
from pathlib import Path
import pty
import shlex
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "tools" / "ai.sh"
INSTALLER = ROOT / "tools" / "install_ai.sh"
RATIO = "# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm"

# === CHECKS ===
# id: check_ai_launcher_aggregate_failure
#   proves: ai_launcher_aggregate_failure
#   call: self::test_aggregate_actions_attempt_each_agent_and_report_any_failure
#   mutates: none
#   cleanup: none
# id: check_ai_launcher_bootstrap_failure
#   proves: ai_launcher_aggregate_failure, ai_launcher_phase_failure
#   call: self::test_start_bootstrap_failure_does_not_attempt_agents
#   mutates: none
#   cleanup: none
# id: check_ai_launcher_pane_state
#   proves: ai_launcher_phase_failure
#   call: self::test_setup_or_unknown_pane_state_never_replaces_or_attaches
#   mutates: none
#   cleanup: none
# id: check_ai_launcher_preflight_preserves_pane
#   proves: ai_launcher_preflight_preserves_pane
#   call: self::test_failed_vault_preflight_preserves_the_pane_and_its_environment
#   mutates: none
#   cleanup: none
# id: check_ai_launcher_respawn_failure
#   proves: ai_launcher_phase_failure
#   call: self::test_vault_check_mask_and_respawn_errors_are_not_hidden_by_logging
#   mutates: none
#   cleanup: none
# id: check_ai_launcher_new_window_retry
#   proves: ai_launcher_new_window_retry
#   call: self::test_failed_first_launch_creates_no_placeholder_and_retries_normally
#   mutates: none
#   cleanup: none
# id: check_ai_launcher_menu_recovery
#   proves: ai_launcher_menu_recovery
#   call: self::test_menu_reports_failed_actions_and_accepts_recovery_commands
#   mutates: none
#   cleanup: none
# id: check_ai_launcher_fast_exit_diagnostics
#   proves: ai_launcher_first_launch_diagnostics
#   call: self::test_first_launch_retains_fast_failure_and_its_diagnostic
#   requires: bash, tmux
#   mutates: filesystem
#   cleanup: private_tmux_server_and_tempdir
# id: check_ai_launcher_first_launch_setup
#   proves: ai_launcher_first_launch_diagnostics
#   call: self::test_first_launch_stages_logging_and_cleans_failed_setup
#   mutates: filesystem
#   cleanup: tempdir_teardown
# === END CHECKS ===


class AILauncherTests(unittest.TestCase):
    def test_shell_syntax(self) -> None:
        for script in (LAUNCHER, INSTALLER):
            subprocess.run(["bash", "-n", str(script)], check=True)

    def test_launcher_keeps_ratio_seals_as_literal_boundaries(self) -> None:
        lines = LAUNCHER.read_text(encoding="utf-8").splitlines()
        self.assertEqual(lines[0], RATIO)
        self.assertEqual(lines[-1], RATIO)
        self.assertFalse(lines[0].startswith("#!"))

    def test_launcher_is_termux_side_remote_tmux_controller(self) -> None:
        text = LAUNCHER.read_text(encoding="utf-8")
        for phrase in (
            'HOST="${A0_AI_HOST:-a0}"',
            'SESSION="${A0_AI_SESSION:-a0}"',
            'StrictHostKeyChecking=yes',
            'ssh -tt -o StrictHostKeyChecking=yes',
            "remain-on-exit on",
            "tmux pipe-pane",
            "#{pane_dead}",
            "#{pane_current_command}",
            "tmux respawn-pane -k",
            ".local/state/a0/logs",
        ):
            self.assertIn(phrase, text)

    def test_expected_vm_window_layout_and_commands_are_pinned(self) -> None:
        text = LAUNCHER.read_text(encoding="utf-8")
        for phrase in (
            "shell) printf '0|shell|%s",
            "grok) printf '1|grok|%s",
            "codex) printf '2|codex|%s",
            "deepcode) printf '3|deepcode|%s",
            'GROK_CMD="${A0_GROK_CMD:-grok}"',
            'CODEX_CMD="${A0_CODEX_CMD:-codex --yolo}"',
            'DEEPCODE_CMD="${A0_DEEPCODE_CMD:-deepcodei}"',
        ):
            self.assertIn(phrase, text)

    def test_start_repairs_missing_or_dead_agents_without_restarting_healthy_ones(self) -> None:
        text = LAUNCHER.read_text(encoding="utf-8")
        self.assertIn('if window_exists "$name"; then', text)
        self.assertIn('elif [[ "$force" == 1 || "$dead" == 1 ]]; then', text)
        self.assertIn('respawn "$name" "$command_line"', text)

    def test_vault_launch_has_no_key_value_in_ssh_or_tmux_arguments(self) -> None:
        text = LAUNCHER.read_text(encoding="utf-8")
        self.assertNotIn("printenv", text)
        self.assertNotIn('tmux set-environment -t', text)
        self.assertIn('tmux set-environment -r -t', text)
        self.assertNotIn('tmux set-environment -g', text)
        self.assertIn('keys_status() { resolve_vault_helper || return; remote', text)
        self.assertIn('exec $(q "$VAULT_HELPER") exec', text)
        self.assertIn('exec $(q "$name") -- $command_line"', text)
        self.assertNotIn('-- bash', text)  # No shell may run after a0-vault cleans the environment.
        self.assertIn('site pair FILE', text)

    def test_installer_places_ai_sh_on_termux_path_without_copying(self) -> None:
        text = INSTALLER.read_text(encoding="utf-8")
        for phrase in (
            '$PREFIX/bin',
            'TARGET="$BIN_DIR/ai.sh"',
            'SOURCE="$SOURCE_DIR/ai.sh"',
            'ln -sfn "$SOURCE" "$TARGET"',
            'skill-lib ai launcher',
        ):
            self.assertIn(phrase, text)
        self.assertNotIn('cp "$SOURCE" "$TARGET"', text)


class AILaunchFailureTests(unittest.TestCase):
    """Run the real Bash functions with inert remote/process boundaries.

    Usage: python -m unittest discover -s tests -p test_ai_launcher.py.
    No SSH connection, tmux pane or credential is used by these fixtures.
    """

    def shell(self, script, *, input=None, **env):
        return subprocess.run(['bash', '-c',
            'source "$1" help >/dev/null\n' + script, 'fixture', str(LAUNCHER)],
            env={**os.environ, 'A0_AI_VAULT_HELPER': '/fixture helper/a0-vault', **env},
            input=input, capture_output=True, text=True, timeout=10)

    def test_aggregate_actions_attempt_each_agent_and_report_any_failure(self):
        for action, agents in (('start_all', ['grok', 'codex', 'deepcode']),
                               ('restart all', ['shell', 'grok', 'codex', 'deepcode'])):
            for failed in ['', *agents]:
                with self.subTest(action=action, failed=failed):
                    result = self.shell('''
ensure_window_shell() { :; }
ensure_agent() { printf '%s\\n' "$1"; [[ "$1" != "$FAILED" ]]; }
restart_one() { printf '%s\\n' "$1"; [[ "$1" != "$FAILED" ]]; }
if ''' + action + '''; then exit 0; else exit "$?"; fi
''', FAILED=failed)
                    self.assertEqual(result.returncode, 1 if failed else 0, result.stderr)
                    self.assertEqual(result.stdout.splitlines(), agents)

    def test_start_bootstrap_failure_does_not_attempt_agents(self):
        result = self.shell('''
ensure_window_shell() { return 23; }
ensure_agent() { printf 'AGENT-RAN'; }
if start_all; then exit 0; else exit "$?"; fi
''')
        self.assertEqual(result.returncode, 23, result.stderr)
        self.assertEqual(result.stdout, '')

    def test_setup_or_unknown_pane_state_never_replaces_or_attaches(self):
        for action in ('ensure_agent codex', 'open_agent codex'):
            for setup, lookup, state, expected in ((23, 0, '0', 23),
                                                   (0, 24, '', 24),
                                                   (0, 0, 'unknown', 1)):
                with self.subTest(action=action, setup=setup, lookup=lookup, state=state):
                    result = self.shell('''
window_exists() { return 0; }
ensure_window_shell() { return "$SETUP"; }
pane_dead() { printf '%s' "$STATE"; return "$LOOKUP"; }
respawn() { printf 'REPLACED'; }
attach_window() { printf 'ATTACHED'; }
if ''' + action + '''; then exit 0; else exit "$?"; fi
''', SETUP=str(setup), LOOKUP=str(lookup), STATE=state)
                    self.assertEqual(result.returncode, expected, result.stderr)
                    self.assertEqual(result.stdout, '')

    def test_healthy_existing_agent_is_preserved_without_credential_reads(self):
        result = self.shell('''
window_exists() { return 0; }
ensure_window_shell() { :; }
pane_dead() { printf '0'; }
respawn() { printf 'REPLACED'; return 23; }
if ensure_agent codex; then exit 0; else exit "$?"; fi
''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, '')

    def test_failed_first_launch_creates_no_placeholder_and_retries_normally(self):
        for action in ('ensure_agent codex', 'open_agent codex', 'restart_one codex'):
            with self.subTest(action=action):
                result = self.shell('''
created=0
failed=23
window_exists() { [[ "$created" == 1 ]]; }
ensure_window_shell() {
  if [[ "$created" == 0 ]]; then
    created=1
    printf 'CREATED\\n'
    [[ -n "${3:-}" ]] && printf 'LAUNCH-COMMAND\\n'
  fi
  return 0
}
pane_dead() { printf '0'; }
attach_window() { printf 'ATTACHED\\n'; }
pipe_log() { :; }
remote() {
  case "$1" in
    resolved=*) printf '/fixture cli/agent\\n/fixture runtime:/usr/bin' ;;
    *' check '*) return "$failed" ;;
    *set-environment*) return 0 ;;
    *respawn-pane*) printf 'REPLACED\\n' ;;
    *) return 99 ;;
  esac
}
if ''' + action + '''; then first=0; else first=$?; fi
printf 'first=%s created=%s\\n' "$first" "$created"
failed=0
''' + action + '''
ensure_agent codex
''')
                self.assertEqual(result.returncode, 0, result.stderr)
                lines = result.stdout.splitlines()
                self.assertEqual(lines[0], 'first=23 created=0')
                self.assertEqual(lines.count('CREATED'), 1)
                self.assertEqual(lines.count('LAUNCH-COMMAND'), 1)
                self.assertNotIn('REPLACED', lines)
                self.assertEqual(lines.count('ATTACHED'), int(action.startswith('open_agent')))

    def test_menu_reports_failed_actions_and_accepts_recovery_commands(self):
        for choice in ('1', '2', '3', '4', '5', '7', '8', '9'):
            with self.subTest(choice=choice):
                answer = choice + ('\ncodex' if choice in ('7', '8') else '') + '\n6\n0\n'
                result = self.shell('''
ensure_session() { :; }
open_agent() { return 23; }
keys_status() { return 23; }
restart() { return 23; }
logs() { return 23; }
status() { printf 'RECOVERY-STATUS\\n'; }
menu
printf 'MENU-RETURNED\\n'
''', input=answer)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('RECOVERY-STATUS', result.stdout)
                self.assertIn('MENU-RETURNED', result.stdout)
                self.assertIn('status 23', result.stderr)

    def test_failed_vault_preflight_preserves_the_pane_and_its_environment(self):
        result = self.shell('''
remote() {
  case "$1" in
    resolved=*) printf '/fixture cli/agent\\n/fixture runtime:/usr/bin' ;;
    *' check '*) return 23 ;;
    *) printf 'MUTATED'; return 0 ;;
  esac
}
pipe_log() { printf 'LOGGED'; }
if respawn codex codex; then exit 0; else exit "$?"; fi
''')
        self.assertEqual(result.returncode, 23, result.stderr)
        self.assertEqual(result.stdout, '')

    def test_vault_check_mask_and_respawn_errors_are_not_hidden_by_logging(self):
        for failed, expected in (('', 0), ('mask', 24), ('respawn', 25)):
            with self.subTest(failed=failed):
                result = self.shell('''
remote() {
  case "$1" in
    resolved=*) printf '/fixture cli/agent\\n/fixture runtime:/usr/bin' ;;
    *' check '*) printf 'check\\n' >&2 ;;
    *set-environment*) printf 'mask\\n' >&2; [[ "$FAILED" != mask ]] || return 24 ;;
    *respawn-pane*) printf 'respawn\\n' >&2; [[ "$FAILED" != respawn ]] || return 25 ;;
    *) return 99 ;;
  esac
}
pipe_log() { printf 'log\\n' >&2; }
if respawn codex codex; then exit 0; else exit "$?"; fi
''', FAILED=failed)
                self.assertEqual(result.returncode, expected, result.stderr)
                steps = ['check', 'mask', 'respawn', 'log']
                if failed:
                    steps = steps[:steps.index(failed) + 1]
                self.assertEqual(result.stderr.splitlines(), steps)
                self.assertEqual(result.stdout, '')

    def test_first_launch_stages_logging_and_cleans_failed_setup(self):
        for failed, expected in (('', 0), ('retention', 24), ('logging', 25), ('launch', 26)):
            with self.subTest(failed=failed), tempfile.TemporaryDirectory() as temp:
                result = self.shell('''
ensure_session() { :; }
window_exists() { return 1; }
tmux() {
  case "$1" in
    list-windows) return 0 ;;
    new-window)
      printf 'create\\n' >&2
      if [[ "${*: -1}" == fixture-agent-command ]]; then
        [[ -f "$FIXTURE/retention" && -f "$FIXTURE/logging" ]] || return 23
      fi
      [[ "$*" != *' -P '* ]] || printf '@1\\n'
      ;;
    set-option)
      printf 'retention\\n' >&2
      [[ "$FAILED" != retention ]] || return 24
      touch "$FIXTURE/retention"
      ;;
    pipe-pane)
      printf 'logging\\n' >&2
      [[ "$FAILED" != logging ]] || return 25
      touch "$FIXTURE/logging"
      ;;
    respawn-pane)
      [[ -f "$FIXTURE/retention" && -f "$FIXTURE/logging" ]] || return 23
      printf 'launch\\n' >&2
      [[ "$FAILED" != launch ]] || return 26
      touch "$FIXTURE/launched"
      ;;
    kill-window) touch "$FIXTURE/cleaned" ;;
    *) return 99 ;;
  esac
  return 0
}
export -f tmux
remote() { bash -c "$1"; }
REMOTE_LOG_SUBDIR="$FIXTURE_REL/logs"
if ensure_window_shell 2 codex fixture-agent-command; then exit 0; else exit "$?"; fi
''', FAILED=failed, FIXTURE=temp, FIXTURE_REL=os.path.relpath(temp, Path.home()))
                self.assertEqual(result.returncode, expected, result.stderr)
                steps = ['create', 'retention', 'logging', 'launch']
                if failed:
                    steps = steps[:steps.index(failed) + 1]
                self.assertEqual(result.stderr.splitlines(), steps)
                self.assertEqual((Path(temp) / 'launched').exists(), not failed)
                self.assertEqual((Path(temp) / 'cleaned').exists(), bool(failed))


@unittest.skipUnless(shutil.which('tmux'), 'real lifecycle witness requires tmux')
class AIRealTmuxTests(unittest.TestCase):
    """Exercise the real launcher and a private tmux server, without SSH or keys.

    Usage: install tmux, then run the normal test_ai_launcher.py suite.
    A delayed transport response makes an immediately exiting CLI deterministic.
    """

    def test_first_launch_retains_fast_failure_and_its_diagnostic(self):
        try:
            with socket.socket(socket.AF_UNIX):
                pass
        except PermissionError:
            if os.environ.get('A0_REQUIRE_REAL_TMUX') == '1':
                raise
            self.skipTest('sandbox denies Unix sockets; required hosted tmux lane remains authoritative')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            binary = shutil.which('tmux')
            socket_path = root / 'tmux.sock'
            wrapper = root / 'tmux'
            wrapper.write_text('#!/bin/sh\nexec ' + shlex.quote(binary) +
                               ' -S ' + shlex.quote(str(socket_path)) + ' -f /dev/null "$@"\n')
            wrapper.chmod(0o700)
            agent = root / 'instant-agent'
            agent.write_text('#!/bin/sh\nprintf "first-launch-diagnostic\\n"\nexit 7\n')
            agent.chmod(0o700)
            helper = root / 'a0-vault'
            helper.write_text('#!/bin/bash\ncase "$1" in\ncheck) exit 0;;\n'
                              'exec) shift 2; shift; exec "$@";;\nesac\nexit 2\n')
            helper.chmod(0o700)
            env = {**os.environ, 'PATH': str(root) + os.pathsep + os.environ['PATH'],
                   'A0_AI_SESSION': 'fixture', 'A0_CODEX_CMD': str(agent),
                   'A0_AI_VAULT_HELPER': str(helper),
                   'A0_AI_REMOTE_LOG_SUBDIR': os.path.relpath(root / 'logs', Path.home())}
            subprocess.run([str(wrapper), 'new-session', '-d', '-s', 'fixture', '-n', 'shell'],
                           env=env, check=True, capture_output=True)
            try:
                result = subprocess.run(['bash', '-c', '''
source "$1" help >/dev/null
require_remote() { :; }
remote() {
  local rc=0
  bash -c "$1" || rc=$?
  if [[ "$1" == *new-window* ]]; then sleep 0.2; fi
  return "$rc"
}
if ensure_agent codex; then exit 0; else exit "$?"; fi
''', 'fixture', str(LAUNCHER)], env=env, capture_output=True, text=True, timeout=10)
                state = subprocess.run([str(wrapper), 'display-message', '-p', '-t',
                                        'fixture:codex.0', '#{pane_dead}:#{pane_dead_status}'],
                                       env=env, capture_output=True, text=True)
                self.assertEqual(state.returncode, 0, result.stderr + state.stderr)
                self.assertEqual(state.stdout.strip(), '1:7')
                self.assertNotEqual(result.returncode, 0, result.stderr)
                log = root / 'logs' / 'codex.log'
                deadline = time.monotonic() + 2
                while time.monotonic() < deadline:
                    if log.exists() and 'first-launch-diagnostic' in log.read_text():
                        break
                    time.sleep(0.02)
                self.assertTrue(log.exists(), result.stderr)
                self.assertIn('first-launch-diagnostic', log.read_text())
            finally:
                subprocess.run([str(wrapper), 'kill-server'], env=env, capture_output=True)


class AIGitHubLauncherTests(unittest.TestCase):
    """Execute routing with inert SSH/tmux executables; never contact a VM."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.trace = self.root / 'ssh.jsonl'
        self.tmux_trace = self.root / 'tmux.jsonl'
        for command, variable in (('ssh', 'FIXTURE_SSH_TRACE'), ('tmux', 'FIXTURE_TMUX_TRACE')):
            script = self.root / command
            script.write_text(f'''#!{sys.executable}
import json, os, sys
with open(os.environ[{variable!r}], 'a') as out:
    out.write(json.dumps(sys.argv[1:]) + '\\n')
''')
            script.chmod(0o700)
        self.env = {
            **os.environ, 'PATH': str(self.root) + os.pathsep + os.environ['PATH'],
            'A0_AI_HOST': 'fixture-vm', 'A0_AI_SESSION': 'fixture-session',
            'A0_AI_VAULT_HELPER': '/fixture helper/a0-vault',
            'FIXTURE_SSH_TRACE': str(self.trace), 'FIXTURE_TMUX_TRACE': str(self.tmux_trace),
            'GH_TOKEN': 'fixture-gh-must-not-be-in-argv',
            'GITHUB_TOKEN': 'fixture-legacy-must-not-be-in-argv',
        }

    def invoke(self, *args, tty=False):
        command = ['bash', str(LAUNCHER), *args]
        if not tty:
            return subprocess.run(command, capture_output=True, text=True, env=self.env)
        master, slave = pty.openpty()
        try:
            process = subprocess.Popen(command, stdin=slave, stdout=slave, stderr=slave, env=self.env)
            os.close(slave)
            slave = None
            process.wait(timeout=10)
            output = bytearray()
            while True:
                try:
                    block = os.read(master, 65536)
                except OSError:
                    break
                if not block:
                    break
                output.extend(block)
            return subprocess.CompletedProcess(command, process.returncode, output.decode(), '')
        finally:
            os.close(master)
            if slave is not None:
                os.close(slave)

    def calls(self):
        return [json.loads(line) for line in self.trace.read_text().splitlines()] if self.trace.exists() else []

    def remote_script(self, call):
        self.assertIn('StrictHostKeyChecking=yes', call)
        self.assertIn('ForwardAgent=no', call)
        self.assertIn('fixture-vm', call)
        command = shlex.split(call[-1])
        self.assertEqual(command[:2], ['bash', '-lc'])
        self.assertEqual(len(command), 3)
        return command[2]

    def test_github_set_goes_directly_to_ssh_tty_without_tmux_logging_or_secret_arguments(self):
        result = self.invoke('github', 'set', tty=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.calls()
        self.assertEqual(len(calls), 1)
        self.assertIn('-tt', calls[0])
        script = self.remote_script(calls[0])
        self.assertEqual(shlex.split(script), [
            'sudo', '-n', 'python3', '/usr/local/lib/a0/configure-vault.py',
            '--set-github-token', '--cli-user', '$(id -un)'])
        self.assertNotIn('tmux', script)
        self.assertFalse(self.tmux_trace.exists())
        combined = json.dumps(calls) + result.stdout + result.stderr
        self.assertNotIn(self.env['GH_TOKEN'], combined)
        self.assertNotIn(self.env['GITHUB_TOKEN'], combined)

    def test_github_set_refuses_non_tty_before_ssh_can_echo_piped_input(self):
        result = self.invoke('github', 'set')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.calls(), [])
        self.assertNotIn(self.env['GH_TOKEN'], result.stdout + result.stderr)
        self.assertNotIn(self.env['GITHUB_TOKEN'], result.stdout + result.stderr)

    def test_github_status_and_check_use_ordinary_ssh_with_literal_quoted_helper(self):
        for operation in ('status', 'check'):
            with self.subTest(operation=operation):
                if self.trace.exists():
                    self.trace.unlink()
                result = self.invoke('github', operation)
                self.assertEqual(result.returncode, 0, result.stderr)
                calls = self.calls()
                self.assertEqual(len(calls), 1)
                self.assertNotIn('-tt', calls[0])
                self.assertEqual(shlex.split(self.remote_script(calls[0])), [
                    self.env['A0_AI_VAULT_HELPER'], 'github', operation])
                self.assertNotIn(self.env['GH_TOKEN'], json.dumps(calls))
                self.assertNotIn(self.env['GITHUB_TOKEN'], json.dumps(calls))

    def test_github_rejects_token_or_extra_arguments_before_ssh(self):
        for args in (('set', 'fixture-never-copy-token'), ('status', 'extra'),
                     ('check', 'extra'), ('unknown',)):
            with self.subTest(args=args):
                result = self.invoke('github', *args)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.calls(), [])
                self.assertNotIn('fixture-never-copy-token', result.stdout + result.stderr)

    def test_stale_github_variables_are_masked_in_the_a0_tmux_session(self):
        result = subprocess.run(['bash', '-c',
            'source "$1" help >/dev/null; clear_stale_keys', 'fixture', str(LAUNCHER)],
            capture_output=True, text=True, env=self.env)
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.calls()
        self.assertEqual(len(calls), 1)
        script = self.remote_script(calls[0])
        execute = subprocess.run(['bash', '-c', script], capture_output=True, text=True, env=self.env)
        self.assertEqual(execute.returncode, 0, execute.stderr)
        mutations = [json.loads(line) for line in self.tmux_trace.read_text().splitlines()]
        self.assertIn(['set-environment', '-r', '-t', 'fixture-session', 'GH_TOKEN'], mutations)
        self.assertIn(['set-environment', '-r', '-t', 'fixture-session', 'GITHUB_TOKEN'], mutations)
        self.assertTrue(all(row[:4] == ['set-environment', '-r', '-t', 'fixture-session'] for row in mutations))
        self.assertNotIn(self.env['GH_TOKEN'], json.dumps(calls + mutations))
        self.assertNotIn(self.env['GITHUB_TOKEN'], json.dumps(calls + mutations))

    def test_agent_command_overrides_must_be_plain_commands(self):
        for variable, agent in (('A0_GROK_CMD', 'grok'), ('A0_CODEX_CMD', 'codex'), ('A0_DEEPCODE_CMD', 'deepcode')):
            for value in ('cli; touch /tmp/pwned', 'cli $(id)', 'cli `id`', 'cli && x', 'cli | tee',
                          'cli > out', 'cli < in', 'cli *', 'cli ?', 'cli !x', 'cli {a,b}', 'cli \\x',
                          'cli (x)', 'cli\nid', 'cli $HOME', 'cli [ab]', 'cli a]', 'cli #rest',
                          'cli ~/x', 'cli\targ', 'cli "unbalanced', "cli 'unbalanced", 'if'):
                with self.subTest(variable=variable, value=value):
                    if self.trace.exists():
                        self.trace.unlink()
                    result = subprocess.run(['bash', '-c',
                        'source "$1" help >/dev/null; respawn "$2" "$(spec "$2" | cut -d"|" -f3-)"',
                        'fixture', str(LAUNCHER), agent],
                        capture_output=True, text=True, env={**self.env, variable: value})
                    self.assertNotEqual(result.returncode, 0)
                    self.assertRegex(result.stderr, f'ERROR: {variable} (must be a|is not a valid) plain command')
                    if len(value) > 3:
                        self.assertNotIn(value, result.stderr)  # The value itself is never echoed.
                    self.assertEqual(self.calls(), [])  # Refused before any SSH/tmux contact.
        help_text = self.invoke('help').stdout
        self.assertIn('must be plain commands', help_text)
        self.assertIn('{ } [ ] # ~, a tab or a newline', help_text)
        for value in ('grok', 'codex --yolo', 'fixture-cli "literal argument"', "cli 'two words' --flag=x"):
            with self.subTest(allowed=value):
                result = subprocess.run(['bash', '-c', 'source "$1" help >/dev/null; require_plain_command grok "$2"',
                    'fixture', str(LAUNCHER), value], capture_output=True, text=True, env=self.env)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_masked_tmux_variables_match_the_vault_secret_set(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("a0_vault_fixture", LAUNCHER.with_name("a0_vault.py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        line = next(row for row in LAUNCHER.read_text(encoding="utf-8").splitlines() if row.startswith("KEY_VARS="))
        names = line.split("=", 1)[1].strip('"').split()
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(set(names), module.SECRET_ENV)
        for name in ("A0_BRIDGE_TOKEN", "A0_SESSION_SECRET", "A0_BOOTSTRAP_CODE", "A0_DATABASE_URL", "BASH_ENV", "ENV"):
            self.assertIn(name, names)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import os
from pathlib import Path
import pty
import shlex
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "tools" / "ai.sh"
INSTALLER = ROOT / "tools" / "install_ai.sh"
RATIO = "# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm"


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
        self.assertIn('if [[ "$existed" == 0 || "$dead" == 1 ]]; then', text)
        self.assertIn('respawn "$name" "$command_line"', text)

    def test_vault_launch_has_no_key_value_in_ssh_or_tmux_arguments(self) -> None:
        text = LAUNCHER.read_text(encoding="utf-8")
        self.assertNotIn("printenv", text)
        self.assertNotIn('tmux set-environment -t', text)
        self.assertIn('tmux set-environment -r -t', text)
        self.assertNotIn('tmux set-environment -g', text)
        self.assertIn('keys_status() { resolve_vault_helper; remote', text)
        self.assertIn('exec $(q "$VAULT_HELPER") exec', text)
        self.assertIn('-- bash -c', text)
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


if __name__ == "__main__":
    unittest.main()

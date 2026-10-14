#!/usr/bin/env python3
"""Offline launcher routing regressions. Usage: python -m unittest discover -s tests -p test_work_launcher.py -v.
Mocks verify command construction, not Google/SSH/Android live access.
"""
from pathlib import Path
import json
import os
import subprocess
import tempfile
import shutil
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'tools/work.sh'
INSTALLER = ROOT / 'tools/install_ai.sh'


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='work-launcher-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.home = self.root / 'home space'
        self.bin = self.root / 'bin'
        self.home.mkdir()
        self.bin.mkdir()
        self.tools = self.root / 'repo space/tools'
        self.tools.mkdir(parents=True)
        self.script = self.tools / 'work.sh'
        shutil.copy2(SCRIPT, self.script)
        shutil.copy2(INSTALLER, self.tools / 'install_ai.sh')
        self.log = self.root / 'calls.jsonl'
        self.env = {
            **os.environ, 'HOME': str(self.home),
            'PATH': f'{self.bin}:/usr/bin:/bin', 'CALL_LOG': str(self.log),
        }
        for key in ('WORK_AI', 'WORK_DISTRO', 'MOCK_RC', 'PREFIX', 'A0_AI_BIN_DIR', 'A0_AI_PROFILE'):
            self.env.pop(key, None)

    def stub(self, name, rc=0):
        p = self.bin / name
        # Absolute interpreter prevents the test's PATH stubs affecting logging.
        p.write_text(
            '#!/usr/bin/python3\nimport json, os, sys\n'
            'with open(os.environ["CALL_LOG"], "a") as f:\n'
            '    f.write(json.dumps(sys.argv) + "\\n")\n'
            f'sys.exit({rc})\n'
        )
        p.chmod(0o700)
        return p

    def run_script(self, *args, stdin='', ubuntu=False):
        # Override only OS detection to cover both routing branches on any host.
        code = 'source "$1"; shift; is_ubuntu() { return ' + ('0' if ubuntu else '1') + '; }; main "$@"'
        return subprocess.run(
            ['/bin/bash', '-c', code, 'test', str(self.script), *args],
            input=stdin, text=True, capture_output=True, env=self.env, check=False,
        )

    def calls(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()] if self.log.exists() else []

    def make_ai(self, path=None, rc=0):
        path = path or self.tools / 'ai.sh'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f'printf "AI_ARGS:"; printf "<%s>" "$@"; printf "\\n"; exit {rc}\n')
        return path

    def test_bash_syntax(self):
        self.assertEqual(subprocess.run(['/bin/bash', '-n', str(SCRIPT)], check=False).returncode, 0)

    def test_help_needs_no_tools(self):
        p = self.run_script('help')
        self.assertEqual(p.returncode, 0)
        self.assertIn('Usage:', p.stdout)
        self.assertEqual(self.calls(), [])

    def test_menu_quit_has_no_tool_effects(self):
        self.assertEqual(self.run_script(stdin='0\n').returncode, 0)
        self.assertEqual(self.calls(), [])

    def test_menu_eof_exits(self):
        self.assertEqual(self.run_script().returncode, 0)

    def test_cloud_enters_ubuntu(self):
        self.stub('proot-distro')
        p = self.run_script('cloud')
        self.assertEqual(p.returncode, 0)
        c = self.calls()[0]
        self.assertEqual(c[1:6], ['login', 'ubuntu', '--', '/bin/bash', '-lc'])
        self.assertEqual(c[-3:], ['gcloud', 'cloud-shell', 'ssh'])
        self.assertIn('$HOME/google-cloud-sdk/bin', c[6])

    def test_distro_override_stays_one_argument(self):
        self.stub('proot-distro')
        self.env['WORK_DISTRO'] = 'ubuntu-local'
        self.run_script('cloud')
        self.assertEqual(self.calls()[0][2], 'ubuntu-local')

    def test_already_ubuntu_does_not_nest_proot(self):
        self.stub('proot-distro')
        self.stub('bash')
        p = self.run_script('cloud', ubuntu=True)
        self.assertEqual(p.returncode, 0)
        self.assertEqual(len(self.calls()), 1)
        self.assertEqual(Path(self.calls()[0][0]).name, 'bash')
        self.assertEqual(self.calls()[0][-3:], ['gcloud', 'cloud-shell', 'ssh'])

    def test_login_uses_phone_browser_flow(self):
        self.stub('proot-distro')
        self.assertEqual(self.run_script('login').returncode, 0)
        self.assertEqual(self.calls()[0][-4:], ['gcloud', 'auth', 'login', '--no-launch-browser'])

    def test_setup_explicit_only(self):
        self.stub('proot-distro')
        self.run_script('setup')
        self.assertEqual(self.calls()[0][-3:], ['gcloud', 'init', '--console-only'])

    def test_local_ubuntu_shell_not_cloud(self):
        self.stub('proot-distro')
        self.run_script('ubuntu')
        self.assertEqual(self.calls()[0][-2:], ['/bin/bash', '-i'])

    def test_arbitrary_cloud_arguments_not_reparsed(self):
        self.stub('proot-distro')
        payload = f'; touch "{self.root}/SHOULD_NOT_EXIST" #'
        self.run_script('gcloud', 'compute', 'instances', 'list', '--filter', payload)
        self.assertEqual(self.calls()[0][-6:], ['gcloud', 'compute', 'instances', 'list', '--filter', payload])
        self.assertFalse((self.root / 'SHOULD_NOT_EXIST').exists())

    def test_transport_nonzero_preserved(self):
        self.stub('proot-distro', 42)
        self.assertEqual(self.run_script('cloud').returncode, 42)

    def test_transport_not_retried(self):
        self.stub('proot-distro', 42)
        self.run_script('cloud')
        self.assertEqual(len(self.calls()), 1)

    def test_menu_survives_tool_failure(self):
        self.stub('proot-distro', 42)
        p = self.run_script(stdin='2\n0\n')
        self.assertEqual(p.returncode, 0)
        self.assertIn('status 42', p.stderr)
        self.assertEqual(p.stdout.count('Work\n'), 2)

    def test_ai_nonzero_preserved(self):
        self.make_ai(rc=23)
        self.assertEqual(self.run_script('ai', 'status').returncode, 23)

    def test_missing_ai_does_not_block_cloud(self):
        self.stub('proot-distro')
        self.assertEqual(self.run_script('ai').returncode, 127)
        self.assertEqual(self.run_script('cloud').returncode, 0)

    def test_missing_ubuntu_fails_without_installing(self):
        self.env['PATH'] = str(self.bin)
        p = self.run_script('cloud')
        self.assertEqual(p.returncode, 127)
        self.assertIn('Ubuntu unavailable', p.stderr)
        self.assertEqual(self.calls(), [])

    def test_boot_resolves_sdk_inside_child_home(self):
        self.stub('proot-distro')
        self.run_script('cloud')
        boot = self.calls()[0][6]
        self.stub('grep')  # Model Ubuntu's os-release for this boot unit test.
        sdk = self.home / 'google-cloud-sdk/bin'
        sdk.mkdir(parents=True)
        cli = sdk / 'gcloud'
        cli.write_text('#!/bin/bash\nprintf "SDK:%s\\n" "$1"\n')
        cli.chmod(0o700)
        p = subprocess.run(['/bin/bash', '-c', boot, 'work.sh', 'gcloud', 'hello'],
                           env=self.env, text=True, capture_output=True, check=False)
        self.assertEqual(p.returncode, 0)
        self.assertEqual(p.stdout.strip(), 'SDK:hello')

    def test_boot_propagates_missing_command(self):
        self.stub('proot-distro')
        self.run_script('cloud')
        boot = self.calls()[0][6]
        self.stub('grep')  # Model Ubuntu's os-release for this boot unit test.
        p = subprocess.run(['/bin/bash', '-c', boot, 'work.sh', 'definitely-absent-work-launcher-command'],
                           env=self.env, text=True, capture_output=True, check=False)
        self.assertEqual(p.returncode, 127)

    def test_unknown_command_fails(self):
        self.assertEqual(self.run_script('not-a-command').returncode, 2)

    def test_status_reports_missing_ai(self):
        self.stub('proot-distro')
        p = self.run_script('status')
        self.assertEqual(p.returncode, 127)
        self.assertIn('not a live access test', p.stdout)

    def test_status_uses_only_account_project_fields(self):
        self.make_ai()
        self.stub('proot-distro')
        self.assertEqual(self.run_script('status').returncode, 0)
        self.assertEqual(self.calls()[0][-4:], ['gcloud', 'config', 'list', '--format=text(core.account,core.project)'])

    def test_ai_does_not_enter_ubuntu(self):
        self.make_ai()
        self.stub('proot-distro')
        self.assertEqual(self.run_script('ai', 'menu').returncode, 0)
        self.assertEqual(self.calls(), [])

    def test_canonical_ai_with_spaces_preserves_arguments(self):
        self.make_ai()
        p = self.run_script('ai', 'logs', 'name with spaces')
        self.assertEqual(p.returncode, 0)
        self.assertIn('AI_ARGS:<logs><name with spaces>', p.stdout)

    def test_stale_path_and_home_copies_are_ignored(self):
        self.make_ai(self.bin / 'ai.sh', rc=71).chmod(0o700)
        self.make_ai(self.home / 'ai.sh', rc=72)
        self.env['WORK_AI'] = str(self.home / 'ai.sh')
        self.assertEqual(self.run_script('ai').returncode, 127)
        self.make_ai()
        self.assertEqual(self.run_script('ai', 'status').returncode, 0)

    def test_canonical_ai_cannot_recurse_into_work(self):
        (self.tools / 'ai.sh').symlink_to(self.script)
        self.assertEqual(self.run_script('ai').returncode, 127)

    def test_installed_symlink_resolves_canonical_sibling(self):
        self.make_ai()
        target = self.bin / 'work.sh'
        target.symlink_to(self.script)
        p = subprocess.run(['/bin/bash', str(target), 'ai', 'status'],
                           env=self.env, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertIn('AI_ARGS:<status>', p.stdout)

    def test_unexpected_arguments_are_rejected(self):
        self.stub('proot-distro')
        self.assertEqual(self.run_script('cloud', 'ignored').returncode, 2)
        self.assertEqual(self.run_script('gcloud').returncode, 2)
        self.assertEqual(self.calls(), [])

    def test_selected_environment_must_actually_be_ubuntu(self):
        self.stub('proot-distro')
        self.run_script('cloud')
        boot = self.calls()[0][6]
        self.stub('grep', 1)
        p = subprocess.run(['/bin/bash', '-c', boot, 'work.sh', '/bin/true'],
                           env=self.env, capture_output=True, text=True)
        self.assertEqual(p.returncode, 126)
        self.assertIn('not Ubuntu', p.stderr)

    def test_boot_preserves_literal_arguments_and_stdin(self):
        self.stub('proot-distro')
        self.run_script('cloud')
        boot = self.calls()[0][6]
        self.stub('grep')
        payload = '$(touch ' + str(self.root / 'NO') + ')'
        p = subprocess.run(['/bin/bash', '-c', boot, 'work.sh', '/usr/bin/python3',
                            '-c', 'import sys; print(repr(sys.argv[1:])); print(sys.stdin.read())',
                            payload, 'two words', ''],
                           input='kept stdin', env=self.env, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertIn(repr([payload, 'two words', '']), p.stdout)
        self.assertIn('kept stdin', p.stdout)
        self.assertFalse((self.root / 'NO').exists())

    def install(self):
        return subprocess.run(['/bin/bash', str(self.tools / 'install_ai.sh')],
                              env=self.env, capture_output=True, text=True)

    def test_installer_links_both_commands_and_repeat_is_safe(self):
        self.make_ai()
        self.env['PREFIX'] = str(self.root)
        for _ in range(2):
            result = self.install()
            self.assertEqual(result.returncode, 0, result.stderr)
        for name in ('ai.sh', 'work.sh'):
            self.assertTrue((self.bin / name).is_symlink())
            self.assertEqual((self.bin / name).resolve(), self.tools / name)
        self.assertFalse((self.home / '.profile').exists())
        self.assertEqual(self.calls(), [])

    def test_repository_changes_reach_installed_commands_without_copying(self):
        self.make_ai()
        self.env['PREFIX'] = str(self.root)
        self.assertEqual(self.install().returncode, 0)
        self.make_ai().write_text('printf "updated canonical source\\n"\n')
        p = subprocess.run(['/bin/bash', str(self.bin / 'work.sh'), 'ai'],
                           env=self.env, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertEqual(p.stdout.strip(), 'updated canonical source')

    def test_fallback_path_line_is_added_only_once(self):
        self.make_ai()
        for _ in range(2):
            result = self.install()
            self.assertEqual(result.returncode, 0, result.stderr)
        profile = (self.home / '.profile').read_text()
        self.assertEqual(profile.count('# skill-lib ai launcher'), 1)
        for name in ('ai.sh', 'work.sh'):
            self.assertTrue((self.home / '.local/bin' / name).is_symlink())

    def test_missing_source_fails_before_installing_either_link(self):
        self.make_ai()
        self.script.unlink()
        self.env['PREFIX'] = str(self.root)
        self.assertEqual(self.install().returncode, 2)
        self.assertFalse((self.bin / 'ai.sh').exists())
        self.assertFalse((self.bin / 'work.sh').exists())

    def test_invalid_source_does_not_replace_existing_commands(self):
        self.make_ai()
        self.script.write_text('if broken\n')
        target = self.bin / 'ai.sh'
        target.write_text('preserve me\n')
        self.env['PREFIX'] = str(self.root)
        self.assertNotEqual(self.install().returncode, 0)
        self.assertEqual(target.read_text(), 'preserve me\n')

    def test_directory_target_is_not_modified(self):
        self.make_ai()
        target = self.bin / 'work.sh'
        target.mkdir()
        self.env['PREFIX'] = str(self.root)
        self.assertEqual(self.install().returncode, 2)
        self.assertEqual(list(target.iterdir()), [])
        self.assertFalse((self.bin / 'ai.sh').exists())

    def test_install_into_source_directory_is_refused(self):
        self.make_ai()
        original = self.script.read_bytes()
        self.env['A0_AI_BIN_DIR'] = str(self.tools)
        self.assertEqual(self.install().returncode, 2)
        self.assertFalse(self.script.is_symlink())
        self.assertEqual(self.script.read_bytes(), original)

    def test_shell_syntax_and_ratio_boundaries(self):
        ratio = '# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm'
        for path in (SCRIPT, INSTALLER):
            subprocess.run(['/bin/bash', '-n', str(path)], check=True)
            lines = path.read_text().splitlines()
            self.assertEqual(lines[1], ratio)
            self.assertEqual(lines[-1], ratio)


if __name__ == '__main__':
    unittest.main()

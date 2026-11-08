from __future__ import annotations

from pathlib import Path
import subprocess
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


if __name__ == "__main__":
    unittest.main()

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
        self.assertEqual(lines[0], "#!/usr/bin/env bash")
        self.assertEqual(lines[1], RATIO)
        self.assertEqual(lines[-1], RATIO)

    def test_launcher_is_termux_side_remote_tmux_controller(self) -> None:
        text = LAUNCHER.read_text(encoding="utf-8")
        for phrase in (
            'HOST="${A0_AI_HOST:-a0}"',
            'SESSION="${A0_AI_SESSION:-a0}"',
            'ssh "$HOST"',
            'ssh -tt "$HOST"',
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

    def test_keys_use_vault_and_remove_legacy_tmux_values(self) -> None:
        text = LAUNCHER.read_text(encoding="utf-8")
        self.assertIn('/opt/a0-openbao/launch.py', text)
        self.assertIn('tmux set-environment -gu', text)
        self.assertIn('tmux set-environment -r', text)
        self.assertNotIn('printenv', text)
        self.assertNotIn('sync_keys', text)

    def test_aggregate_does_not_hide_pane_lookup_failure(self) -> None:
        source = LAUNCHER.read_text().split('case "${1:-menu}" in')[0]
        script = source + '\nwindow_exists() { return 0; }\nensure_window_shell() { return 0; }\npane_dead() { return 23; }\nif start_all; then exit 99; else exit "$?"; fi\n'
        result = subprocess.run(["bash", "-c", script], capture_output=True)
        self.assertEqual(result.returncode, 1)

    def test_failed_preflight_never_respawns_existing_pane(self) -> None:
        source = LAUNCHER.read_text().split('case "${1:-menu}" in')[0]
        script = source + '\nremote() {\n  case "$1" in\n    *\'--check\'*) return 23 ;;\n    *\'respawn-pane\'*) echo WRONG ;;\n  esac\n  return 0\n}\nif respawn codex codex; then exit 99; else exit "$?"; fi\n'
        result = subprocess.run(["bash", "-c", script], capture_output=True)
        self.assertEqual(result.returncode, 23)
        self.assertNotIn(b"WRONG", result.stdout)

    def test_respawn_transport_failure_is_preserved(self) -> None:
        source = LAUNCHER.read_text().split('case "${1:-menu}" in')[0]
        script = source + '\nclear_legacy_keys() { return 0; }\nremote() { case "$1" in *respawn-pane*) return 24 ;; esac; return 0; }\nif respawn codex codex; then exit 99; else exit "$?"; fi\n'
        result = subprocess.run(["bash", "-c", script], capture_output=True)
        self.assertEqual(result.returncode, 24)

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

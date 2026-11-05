#!/usr/bin/env bash
# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm
set -euo pipefail

# === MODULE_BUILD ===
# id: skill_lib_ai_launcher
#   module_name: ai
#   module_kind: cli
#   summary: canonical Termux-side SSH/tmux launcher for coding-agent CLIs on the a0 development VM with health, restart, OpenBao key retrieval, and persistent remote pane logs
#   owner: skill-lib
#   public_surface: ai.sh start|attach|status|restart|logs|keys|grok|codex|deepcode|shell
#   internal_surface: remote bash quoting, tmux session/window lifecycle, provider-scoped OpenBao launch
#   auth_boundary: SSH host alias and third-party CLIs own authentication; launcher never prints key values
#   storage_boundary: remote pane logs under ~/.local/state/a0/logs; no secret persistence
#   network_boundary: SSH to configured VM host only
#   user_data_boundary: provider keys enter only the selected CLI process through the VM OpenBao helper
#   admin_only: false
#   tests: tests/test_ai_launcher.py
#   rollout: explicit install via tools/install_ai.sh
#   rollback: remove installed ai.sh symlink; canonical source remains in skill-lib
#   requires: local bash + ssh; remote bash + tmux; optional remote grok/codex/deepcodei CLIs
#   since: 2026-09-12
#   unresolved: third-party CLI executable names and provider authentication methods may change
# === END MODULE_BUILD ===

HOST="${A0_AI_HOST:-a0}"
SESSION="${A0_AI_SESSION:-a0}"
REMOTE_LOG_SUBDIR="${A0_AI_REMOTE_LOG_SUBDIR:-.local/state/a0/logs}"
GROK_CMD="${A0_GROK_CMD:-grok}"
CODEX_CMD="${A0_CODEX_CMD:-codex --yolo}"
DEEPCODE_CMD="${A0_DEEPCODE_CMD:-deepcodei}"
SHELL_CMD="${A0_SHELL_CMD:-exec \"\${SHELL:-/bin/bash}\" -l}"
VAULT_HELPER="/opt/a0-openbao/launch.py"

usage() {
  cat <<'EOF'
usage: ai.sh [command]

commands:
  start                 ensure a0 tmux session and expected windows exist
  attach                attach to the a0 tmux session
  status | -list        show expected windows and actual pane/process state
  restart NAME          restart grok, codex, deepcode, shell, or all
  -restart NAME         compatibility alias for restart
  logs [NAME]           tail persistent remote pane log (default: deepcode)
  keys                  verify OpenBao retrieval per provider; print status only
  grok | -grok          ensure/select Grok and attach
  codex | -codex        ensure/select Codex and attach
  deepcode|-deepcode|-deepcodei
                        ensure/select DeepCode and attach
  shell                 ensure/select VM shell and attach
  menu                  interactive selector (default)

configuration:
  A0_AI_HOST, A0_AI_SESSION, A0_GROK_CMD, A0_CODEX_CMD,
  A0_DEEPCODE_CMD, A0_SHELL_CMD
EOF
}

q() { printf '%q' "$1"; }

remote() {
  local script="$1"
  ssh "$HOST" "bash -lc $(q "$script")"
}

remote_tty() {
  local script="$1"
  ssh -tt "$HOST" "bash -lc $(q "$script")"
}

require_remote() {
  if ! ssh -o BatchMode=yes -o ConnectTimeout=8 "$HOST" 'command -v tmux >/dev/null 2>&1'; then
    printf 'ERROR: cannot reach %s non-interactively with remote tmux available\n' "$HOST" >&2
    return 1
  fi
}

session_exists() {
  remote "tmux has-session -t $(q "$SESSION") 2>/dev/null" || return
}

window_exists() {
  local name="$1"
  session_exists && remote "tmux list-windows -t $(q "$SESSION") -F '#W' | grep -Fxq $(q "$name")"
}

pane_dead() {
  local name="$1"
  remote "tmux display-message -p -t $(q "$SESSION:$name.0") '#{pane_dead}'" || return
}

pipe_log() {
  local name="$1" target="$SESSION:$1.0" command
  command="cat >> \"\$HOME/$REMOTE_LOG_SUBDIR/$name.log\""
  remote "mkdir -p \"\$HOME/$REMOTE_LOG_SUBDIR\"; tmux pipe-pane -o -t $(q "$target") $(q "$command")" || return
}

clear_legacy_keys() {
  remote "for key in OPENAI_API_KEY XAI_API_KEY DEEPSEEK_API_KEY ANTHROPIC_API_KEY; do tmux set-environment -gu \"\$key\"; tmux set-environment -r -t $(q "$SESSION") \"\$key\"; done" || return
}

keys_status() {
  require_remote || return
  local name result=0
  for name in grok codex deepcode; do
    remote "python3 -I $(q "$VAULT_HELPER") $name --check" || result=1
  done
  return "$result"
}

ensure_session() {
  require_remote || return
  if ! session_exists; then
    remote "tmux new-session -d -s $(q "$SESSION") -n shell" || return
  fi
  remote "tmux set-option -w -t $(q "$SESSION:shell") remain-on-exit on 2>/dev/null || true; mkdir -p \"\$HOME/$REMOTE_LOG_SUBDIR\"" || return
  pipe_log shell || true
  clear_legacy_keys || return
}

spec() {
  case "$1" in
    shell) printf '0|shell|%s\n' "$SHELL_CMD" ;;
    grok) printf '1|grok|%s\n' "$GROK_CMD" ;;
    codex) printf '2|codex|%s\n' "$CODEX_CMD" ;;
    deepcode) printf '3|deepcode|%s\n' "$DEEPCODE_CMD" ;;
    *) return 2 ;;
  esac
}

ensure_window_shell() {
  local index="$1" name="$2"
  ensure_session || return
  if window_exists "$name"; then
    remote "tmux set-option -w -t $(q "$SESSION:$name") remain-on-exit on" || return
    pipe_log "$name" || true
    return 0
  fi

  local occupied
  occupied="$(remote "tmux list-windows -t $(q "$SESSION") -F '#I:#W' | grep '^${index}:' || true")"
  if [[ -n "$occupied" ]]; then
    printf 'ERROR: expected window %s at index %s, but %s occupies it\n' "$name" "$index" "$occupied" >&2
    return 3
  fi
  remote "tmux new-window -d -t $(q "$SESSION:$index") -n $(q "$name")" || return
  remote "tmux set-option -w -t $(q "$SESSION:$name") remain-on-exit on" || return
  pipe_log "$name" || true
}

respawn() {
  local name="$1" command_line="$2" binary pane_command
  binary="${command_line%% *}"
  if ! remote "command -v $(q "$binary") >/dev/null 2>&1"; then
    printf 'ERROR: %s is not installed on %s\n' "$binary" "$HOST" >&2
    return 127
  fi
  remote "python3 -I $(q "$VAULT_HELPER") $(q "$name") --check" || return
  clear_legacy_keys || return
  pane_command="exec python3 -I $(q "$VAULT_HELPER") $(q "$name") -- $(q "$command_line")"
  remote "tmux respawn-pane -k -t $(q "$SESSION:$name.0") $(q "$pane_command")" || return
  pipe_log "$name" || true
}

ensure_agent() {
  local agent="$1" row index name command_line dead existed=0
  row="$(spec "$agent")"
  IFS='|' read -r index name command_line <<<"$row"
  if window_exists "$name"; then
    existed=1
  fi
  ensure_window_shell "$index" "$name" || return
  dead="$(pane_dead "$name")" || return
  [[ "$dead" == 0 || "$dead" == 1 ]] || { printf 'ERROR: invalid pane state\n' >&2; return 1; }
  if [[ "$existed" == 0 || "$dead" == 1 ]]; then
    respawn "$name" "$command_line" || return
  fi
}

start_all() {
  ensure_window_shell 0 shell || return
  local result=0
  ensure_agent grok || result=1
  ensure_agent codex || result=1
  ensure_agent deepcode || result=1
  return "$result"
}

restart_one() {
  local agent="$1" row index name command_line
  row="$(spec "$agent")" || {
    printf 'ERROR: unknown restart target: %s\n' "$agent" >&2
    return 2
  }
  IFS='|' read -r index name command_line <<<"$row"
  ensure_window_shell "$index" "$name" || return
  if [[ "$agent" == shell ]]; then
    local pane_command
    pane_command="exec bash -lc $(q "$command_line")"
    remote "tmux respawn-pane -k -t $(q "$SESSION:$name.0") $(q "$pane_command")" || return
    pipe_log "$name" || true
  else
    respawn "$name" "$command_line" || return
  fi
}

restart() {
  local target="${1:-all}"
  case "$target" in
    all)
      local result=0
      restart_one shell || result=1
      restart_one grok || result=1
      restart_one codex || result=1
      restart_one deepcode || result=1
      return "$result"
      ;;
    grok|codex|deepcode|shell) restart_one "$target" ;;
    *) printf 'ERROR: restart target must be grok, codex, deepcode, shell, or all\n' >&2; return 2 ;;
  esac
}

status() {
  require_remote || return
  if ! session_exists; then
    printf 'session %-12s missing on %s\n' "$SESSION" "$HOST"
    return 1
  fi
  remote "tmux list-panes -s -t $(q "$SESSION") -F '#{window_index}\\t#{window_name}\\tdead=#{pane_dead}\\tpid=#{pane_pid}\\tcommand=#{pane_current_command}' | sort -n" || return
}

attach_window() {
  local name="$1"
  remote_tty "tmux select-window -t $(q "$SESSION:$name") && exec tmux attach-session -t $(q "$SESSION")"
}

open_agent() {
  local agent="$1" row index name command_line dead existed=0
  row="$(spec "$agent")"
  IFS='|' read -r index name command_line <<<"$row"
  if window_exists "$name"; then
    existed=1
  fi
  ensure_window_shell "$index" "$name" || return
  dead="$(pane_dead "$name")" || return
  [[ "$dead" == 0 || "$dead" == 1 ]] || { printf 'ERROR: invalid pane state\n' >&2; return 1; }
  if [[ "$agent" != shell && ( "$existed" == 0 || "$dead" == 1 ) ]]; then
    respawn "$name" "$command_line" || return
  fi
  attach_window "$name"
}

logs() {
  local name="${1:-deepcode}"
  case "$name" in shell|grok|codex|deepcode) ;; *) printf 'ERROR: unknown log: %s\n' "$name" >&2; return 2 ;; esac
  ensure_session || return
  remote "file=\"\$HOME/$REMOTE_LOG_SUBDIR/$name.log\"; if [[ -f \"\$file\" ]]; then tail -n ${A0_AI_LOG_LINES:-200} \"\$file\"; else printf 'no log yet: %s\\n' \"\$file\"; exit 1; fi" || return
}

menu() {
  ensure_session || return
  while true; do
    cat <<'EOF'

AI on a0:
  1) Grok
  2) Codex
  3) DeepCode
  4) Shell
  5) Keys
  6) Status
  7) Restart
  8) Logs
  0) Quit
EOF
    read -r -p '> ' choice
    case "$choice" in
      1) open_agent grok ;;
      2) open_agent codex ;;
      3) open_agent deepcode ;;
      4) open_agent shell ;;
      5) keys_status ;;
      6) status || true ;;
      7) read -r -p 'restart [grok/codex/deepcode/shell/all]: ' target; restart "${target:-all}" || true ;;
      8) read -r -p 'log [deepcode/codex/grok/shell]: ' target; logs "${target:-deepcode}" || true ;;
      0) return 0 ;;
      *) printf 'unknown choice\n' ;;
    esac
  done
}

case "${1:-menu}" in
  start) start_all ;;
  attach) ensure_session; remote_tty "exec tmux attach-session -t $(q "$SESSION")" ;;
  status|-list) status ;;
  restart) shift; restart "${1:-all}" ;;
  -restart) shift; restart "${1:-all}" ;;
  logs) shift; logs "${1:-deepcode}" ;;
  keys) keys_status ;;
  grok|-grok) open_agent grok ;;
  codex|-codex) open_agent codex ;;
  deepcode|-deepcode|-deepcodei) open_agent deepcode ;;
  shell) open_agent shell ;;
  menu) menu ;;
  -h|--help|help) usage ;;
  *) usage >&2; exit 2 ;;
esac
# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm

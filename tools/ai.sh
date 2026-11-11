# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm
set -euo pipefail

# === MODULE_BUILD ===
# id: skill_lib_ai_launcher
#   module_name: ai
#   module_kind: cli
#   summary: canonical Termux-side SSH/tmux launcher for coding-agent CLIs on the a0 development VM with health, restart, vault-backed credentials, and persistent remote pane logs
#   owner: skill-lib
#   public_surface: ai.sh start|attach|status|restart|logs|keys|vault|github|site|grok|codex|deepcode|shell
#   internal_surface: remote bash quoting, tmux session/window lifecycle, VM-local vault execution
#   auth_boundary: SSH host alias and third-party CLIs own authentication; launcher never prints key values
#   storage_boundary: owner-only remote pane logs; protected VM credential files are provisioned separately
#   network_boundary: SSH to configured VM host only
#   user_data_boundary: provider and enabled GitHub credentials are resolved by a0-vault inside the VM child environment only; GitHub input uses direct unlogged SSH terminal
#   admin_only: false
#   tests: tests/test_ai_launcher.py; tests/test_a0_vault.py
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
VAULT_HELPER="${A0_AI_VAULT_HELPER:-}"
KEY_VARS="OPENAI_API_KEY XAI_API_KEY DEEPSEEK_API_KEY ANTHROPIC_API_KEY BAO_TOKEN VAULT_TOKEN GH_TOKEN GITHUB_TOKEN"

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
  keys                  report OpenBao readiness and provider presence; never copy keys
  vault install|setup|status
                        install helper, provision via existing A0, or inspect vault
  github set|status|check
                        replace GitHub token in OpenBao, inspect presence, or verify login
  site pair FILE        send owner-downloaded Site pairing file to VM over SSH stdin
  site status|handoffs   inspect the authenticated bridge or queued handoffs
  site handoff ID        print one queued handoff for the VM coding agent
  grok | -grok          ensure/select Grok and attach
  codex | -codex        ensure/select Codex and attach
  deepcode|-deepcode|-deepcodei
                        ensure/select DeepCode and attach
  shell                 ensure/select VM shell and attach
  menu                  interactive selector (default)

configuration:
  A0_AI_HOST, A0_AI_SESSION, A0_GROK_CMD, A0_CODEX_CMD,
  A0_DEEPCODE_CMD, A0_SHELL_CMD, A0_AI_VAULT_HELPER
EOF
}

q() { printf '%q' "$1"; }

remote() {
  local script="$1"
  ssh -o StrictHostKeyChecking=yes -o ForwardAgent=no "$HOST" "bash -lc $(q "$script")"
}

remote_tty() {
  local script="$1"
  ssh -tt -o StrictHostKeyChecking=yes -o ForwardAgent=no "$HOST" "bash -lc $(q "$script")"
}

require_remote() {
  if ! ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ForwardAgent=no -o ConnectTimeout=8 "$HOST" 'command -v tmux >/dev/null 2>&1'; then
    printf 'ERROR: cannot reach %s non-interactively with remote tmux available\n' "$HOST" >&2
    return 1
  fi
}

session_exists() {
  remote "tmux has-session -t $(q "$SESSION") 2>/dev/null"
}

window_exists() {
  local name="$1"
  session_exists && remote "tmux list-windows -t $(q "$SESSION") -F '#W' | grep -Fxq $(q "$name")"
}

pane_dead() {
  local name="$1"
  remote "tmux display-message -p -t $(q "$SESSION:$name.0") '#{pane_dead}'"
}

pipe_log() {
  local name="$1" target="$SESSION:$1.0" command
  command="umask 077; cat >> \"\$HOME/$REMOTE_LOG_SUBDIR/$name.log\""
  remote "umask 077; mkdir -p \"\$HOME/$REMOTE_LOG_SUBDIR\"; chmod 700 \"\$HOME/$REMOTE_LOG_SUBDIR\"; touch \"\$HOME/$REMOTE_LOG_SUBDIR/$name.log\"; chmod 600 \"\$HOME/$REMOTE_LOG_SUBDIR/$name.log\"; tmux pipe-pane -o -t $(q "$target") $(q "$command")"
}

clear_stale_keys() {
  local script
  # Mask inherited legacy credentials in A0 only; unrelated tmux sessions are untouched.
  script="for key in $KEY_VARS; do tmux set-environment -r -t $(q "$SESSION") \"\$key\"; done"
  remote "$script"
}

resolve_vault_helper() {
  if [[ -z "$VAULT_HELPER" ]]; then
    VAULT_HELPER="$(remote 'printf "%s/.local/bin/a0-vault" "$HOME"')"
  fi
  [[ "$VAULT_HELPER" == /* && "$VAULT_HELPER" != *$'\n'* ]] || { printf 'A0_AI_VAULT_HELPER must resolve to an absolute VM path.\n' >&2; return 2; }
}

keys_status() { resolve_vault_helper; remote "$(q "$VAULT_HELPER") status"; }

vault_command() {
  case "${1:-status}" in
    status) keys_status ;;
    install)
      local source_dir helper install_script
      source_dir="$(dirname "$(readlink -f "$0")")"
      helper="$source_dir/a0_vault.py"
      [[ -f "$helper" ]] || { printf 'Missing canonical a0_vault.py beside ai.sh\n' >&2; return 1; }
      install_script="$(cat <<'REMOTE_INSTALL'
set -e
umask 077
mkdir -p "$HOME/.local/bin"
tmp=$(mktemp "$HOME/.local/bin/.a0-vault.XXXXXX")
trap 'rm -f "$tmp"' EXIT
cat > "$tmp"
python3 -c 'import ast,sys; ast.parse(open(sys.argv[1]).read())' "$tmp"
chmod 700 "$tmp"
mv "$tmp" "$HOME/.local/bin/a0-vault"
printf 'VM vault helper installed.\n'
REMOTE_INSTALL
)"
      remote "$install_script" < "$helper"
      ;;
    setup) remote 'sudo -n python3 /usr/local/lib/a0/configure-vault.py --cli-user "$(id -un)"' ;;
    *) printf 'usage: ai.sh vault install|setup|status\n' >&2; return 2 ;;
  esac
}

github_command() {
  [[ $# -le 1 ]] || { printf 'usage: ai.sh github set|status|check (never pass a token as an argument)\n' >&2; return 2; }
  case "${1:-status}" in
    set)
      [[ -t 0 && -t 1 ]] || { printf 'Run ai.sh github set directly in an interactive terminal; piped token input is refused.\n' >&2; return 2; }
      # The operator enters the token with terminal echo disabled by the root-owned
      # provisioner. Do not run this inside a logged tmux pane or capture its input.
      remote_tty 'sudo -n python3 /usr/local/lib/a0/configure-vault.py --set-github-token --cli-user "$(id -un)"'
      ;;
    status|check)
      resolve_vault_helper
      remote "$(q "$VAULT_HELPER") github $(q "${1:-status}")"
      ;;
    *) printf 'usage: ai.sh github set|status|check\n' >&2; return 2 ;;
  esac
}

site_command() {
  resolve_vault_helper
  case "${1:-status}" in
    pair)
      [[ -n "${2:-}" && -f "$2" ]] || { printf 'usage: ai.sh site pair /path/to/a0-site-connection.json\n' >&2; return 2; }
      remote 'sudo -n python3 /usr/local/lib/a0/configure-vault.py --pair-site --cli-user "$(id -un)"' < "$2"
      ;;
    status|handoffs) remote "$(q "$VAULT_HELPER") site $(q "$1")" ;;
    handoff)
      [[ "${2:-}" =~ ^[a-f0-9]{64}$ ]] || { printf 'Handoff ID must be the 64-character receipt ID.\n' >&2; return 2; }
      remote "$(q "$VAULT_HELPER") site handoff $(q "$2")"
      ;;
    *) printf 'usage: ai.sh site pair FILE|status|handoffs|handoff ID\n' >&2; return 2 ;;
  esac
}

ensure_session() {
  require_remote
  if ! session_exists; then
    remote "tmux new-session -d -s $(q "$SESSION") -n shell"
  fi
  remote "umask 077; tmux set-option -w -t $(q "$SESSION:shell") remain-on-exit on 2>/dev/null || true; mkdir -p \"\$HOME/$REMOTE_LOG_SUBDIR\""
  pipe_log shell || true
  clear_stale_keys
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
  ensure_session
  if window_exists "$name"; then
    remote "tmux set-option -w -t $(q "$SESSION:$name") remain-on-exit on"
    pipe_log "$name" || true
    return 0
  fi

  local occupied
  occupied="$(remote "tmux list-windows -t $(q "$SESSION") -F '#I:#W' | grep '^${index}:' || true")"
  if [[ -n "$occupied" ]]; then
    printf 'ERROR: expected window %s at index %s, but %s occupies it\n' "$name" "$index" "$occupied" >&2
    return 3
  fi
  remote "tmux new-window -d -t $(q "$SESSION:$index") -n $(q "$name")"
  remote "tmux set-option -w -t $(q "$SESSION:$name") remain-on-exit on"
  pipe_log "$name" || true
}

respawn() {
  resolve_vault_helper
  local name="$1" command_line="$2" binary pane_command launch_env resolved_binary runtime_path
  binary="${command_line%% *}"
  if ! launch_env="$(remote "resolved=\$(type -P $(q "$binary")) || exit 127; printf '%s\\n%s' \"\$resolved\" \"\$PATH\"")"; then
    printf 'ERROR: %s is not installed on %s\n' "$binary" "$HOST" >&2
    return 127
  fi
  resolved_binary="${launch_env%%$'\n'*}"
  runtime_path="${launch_env#*$'\n'}"
  [[ "$resolved_binary" == /* && -n "$runtime_path" && "$runtime_path" != *$'\n'* ]] || {
    printf 'ERROR: remote CLI executable/PATH could not be resolved safely\n' >&2; return 127;
  }
  # Resolve login-shell tools (including nvm runtimes) before credentials enter
  # the child. A long-lived tmux server may have an older PATH.
  command_line="$(q "$resolved_binary")${command_line#"$binary"}"
  clear_stale_keys
  pane_command="PATH=$(q "$runtime_path") exec $(q "$VAULT_HELPER") exec $(q "$name") -- bash -c $(q "$command_line")"
  remote "tmux respawn-pane -k -t $(q "$SESSION:$name.0") $(q "$pane_command")"
  pipe_log "$name" || true
}

ensure_agent() {
  local agent="$1" row index name command_line dead existed=0
  row="$(spec "$agent")"
  IFS='|' read -r index name command_line <<<"$row"
  if window_exists "$name"; then
    existed=1
  fi
  ensure_window_shell "$index" "$name"
  dead="$(pane_dead "$name")"
  if [[ "$existed" == 0 || "$dead" == 1 ]]; then
    respawn "$name" "$command_line"
  fi
}

start_all() {
  ensure_window_shell 0 shell
  ensure_agent grok || true
  ensure_agent codex || true
  ensure_agent deepcode || true
}

restart_one() {
  local agent="$1" row index name command_line
  row="$(spec "$agent")" || {
    printf 'ERROR: unknown restart target: %s\n' "$agent" >&2
    return 2
  }
  IFS='|' read -r index name command_line <<<"$row"
  ensure_window_shell "$index" "$name"
  if [[ "$agent" == shell ]]; then
    local pane_command
    pane_command="exec bash -lc $(q "$command_line")"
    remote "tmux respawn-pane -k -t $(q "$SESSION:$name.0") $(q "$pane_command")"
    pipe_log "$name" || true
  else
    respawn "$name" "$command_line"
  fi
}

restart() {
  local target="${1:-all}"
  case "$target" in
    all)
      restart_one shell || true
      restart_one grok || true
      restart_one codex || true
      restart_one deepcode || true
      ;;
    grok|codex|deepcode|shell) restart_one "$target" ;;
    *) printf 'ERROR: restart target must be grok, codex, deepcode, shell, or all\n' >&2; return 2 ;;
  esac
}

status() {
  require_remote
  if ! session_exists; then
    printf 'session %-12s missing on %s\n' "$SESSION" "$HOST"
    return 1
  fi
  remote "tmux list-panes -s -t $(q "$SESSION") -F '#{window_index}\\t#{window_name}\\tdead=#{pane_dead}\\tpid=#{pane_pid}\\tcommand=#{pane_current_command}' | sort -n"
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
  ensure_window_shell "$index" "$name"
  dead="$(pane_dead "$name")"
  if [[ "$agent" != shell && ( "$existed" == 0 || "$dead" == 1 ) ]]; then
    respawn "$name" "$command_line"
  fi
  attach_window "$name"
}

logs() {
  local name="${1:-deepcode}"
  case "$name" in shell|grok|codex|deepcode) ;; *) printf 'ERROR: unknown log: %s\n' "$name" >&2; return 2 ;; esac
  ensure_session
  remote "file=\"\$HOME/$REMOTE_LOG_SUBDIR/$name.log\"; if [[ -f \"\$file\" ]]; then tail -n ${A0_AI_LOG_LINES:-200} \"\$file\"; else printf 'no log yet: %s\\n' \"\$file\"; exit 1; fi"
}

menu() {
  ensure_session
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
  9) Vault status
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
      9) keys_status || true ;;
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
  vault) shift; vault_command "${1:-status}" ;;
  github) shift; github_command "$@" ;;
  site) shift; site_command "${1:-status}" "${2:-}" ;;
  grok|-grok) open_agent grok ;;
  codex|-codex) open_agent codex ;;
  deepcode|-deepcode|-deepcodei) open_agent deepcode ;;
  shell) open_agent shell ;;
  menu) menu ;;
  -h|--help|help) usage ;;
  *) usage >&2; exit 2 ;;
esac
# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm

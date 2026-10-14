#!/usr/bin/env bash
# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm
# === MODULE_BUILD ===
# id: skill_lib_work_launcher
#   module_name: work
#   module_kind: adapter
#   summary: repository-owned menu for the canonical ai.sh and Ubuntu-hosted Google Cloud CLI
#   owner: skill-lib
#   public_surface: work.sh [ai [ARGS...]|cloud|ubuntu|login|setup|status|gcloud ARGS...]
#   internal_surface: canonical_ai, ubuntu_run, dispatch, menu
#   auth_boundary: write
#   storage_boundary: write
#   network_boundary: external
#   user_data_boundary: hmmm
#   admin_only: false
#   tests: tests/test_work_launcher.py
#   rollout: explicit bash tools/install_ai.sh; subsequent repository pulls update linked source
#   rollback: remove the installed work.sh symlink; ai.sh remains independently usable
#   unresolved: phone runtime, endpoint trust, provider access, effects of explicitly supplied gcloud subcommands
# === END MODULE_BUILD ===
# Usage and boundaries: tools/WORK.md; work.sh --help. Child tools own credentials
# and effects. The menu itself starts no agents, login flow, or cloud session.

is_ubuntu() {
  [[ -r /etc/os-release ]] && grep -Eq '^ID="?ubuntu"?$' /etc/os-release
}

ubuntu_run() {
  local boot='if ! grep -Eq '\''^ID="?ubuntu"?$'\'' /etc/os-release; then printf "Ubuntu required; selected environment is not Ubuntu.\n" >&2; exit 126; fi; export PATH="$HOME/google-cloud-sdk/bin:$PATH"; exec "$@"'
  if is_ubuntu; then
    bash -lc "$boot" work.sh "$@"
  elif command -v proot-distro >/dev/null 2>&1; then
    proot-distro login "${WORK_DISTRO:-ubuntu}" -- /bin/bash -lc "$boot" work.sh "$@"
  else
    printf 'Ubuntu unavailable. Use your existing Termux proot-distro Ubuntu installation.\n' >&2
    return 127
  fi
}

canonical_ai() {
  local source ai
  source=$(readlink -f -- "${BASH_SOURCE[0]}") || return $?
  ai="${source%/*}/ai.sh"
  if [[ -f $ai && -r $ai && ! $ai -ef $source ]]; then
    printf '%s\n' "$ai"
  else
    printf 'Canonical sibling ai.sh missing: %s\n' "$ai" >&2
    return 127
  fi
}

usage() {
  cat <<'HELP'
Usage: work.sh [command]
  ai [ARGS...]   Canonical ai.sh menu, or e.g. ai status / ai codex
  cloud          Google Cloud Shell, reached through Ubuntu (not the a0 VM)
  ubuntu         Local Ubuntu terminal
  login          Google sign-in with a browser URL and terminal authorization code
  setup          Google's account/project initialization
  status         Canonical AI path and Google account/project configuration
  gcloud ARGS... Explicit Google Cloud CLI command inside Ubuntu
  help           Show this help
No command opens the menu. WORK_DISTRO selects your existing Ubuntu alias.
Install/update through skill-lib: bash tools/install_ai.sh. See tools/WORK.md.
No automatic installs, credential copying, project changes, or retries.
HELP
}

dispatch() {
  local cmd=${1:-help} p rc=0
  if (( $# )); then shift; fi
  case "$cmd" in
    ai|gcloud) ;;
    *) if (( $# )); then printf 'Unexpected arguments for %s\n' "$cmd" >&2; return 2; fi ;;
  esac
  case "$cmd" in
    1|ai) p=$(canonical_ai) || return $?; bash -- "$p" "$@" ;;
    2|cloud) ubuntu_run gcloud cloud-shell ssh ;;
    3|ubuntu) ubuntu_run /bin/bash -i ;;
    4|login) ubuntu_run gcloud auth login --no-launch-browser ;;
    5|setup) ubuntu_run gcloud init --console-only ;;
    6|status)
      if p=$(canonical_ai); then printf 'AI launcher: %s\n' "$p"; else rc=$?; fi
      printf 'Google configuration in Ubuntu (not a live access test):\n'
      ubuntu_run gcloud config list --format='text(core.account,core.project)' || return $?
      return "$rc" ;;
    gcloud)
      if (( $# == 0 )); then printf 'Supply a gcloud command.\n' >&2; return 2; fi
      ubuntu_run gcloud "$@" ;;
    help|-h|--help) usage ;;
    *) printf 'Unknown command: %s\n' "$cmd" >&2; usage >&2; return 2 ;;
  esac
}

menu() {
  local choice rc
  while true; do
    printf '\nWork\n  1) AI — canonical ai.sh\n  2) Google Cloud Shell\n  3) Ubuntu terminal\n  4) Google sign-in\n  5) Google setup / project selection\n  6) Paths / Google configuration\n  0) Quit\n'
    IFS= read -r -p '> ' choice || return 0
    [[ $choice == 0 ]] && return 0
    if dispatch "$choice"; then :; else
      rc=$?
      printf '\nAction exited with status %s. The menu remains available.\n' "$rc" >&2
    fi
  done
}

main() {
  if (( $# )); then dispatch "$@"; else menu; fi
}

if [[ ${BASH_SOURCE[0]} == "$0" ]]; then main "$@"; fi
# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm

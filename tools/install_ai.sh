#!/usr/bin/env bash
# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm
set -euo pipefail

# === MODULE_BUILD ===
# id: skill_lib_ai_installer
#   module_name: install_ai
#   module_kind: adapter
#   summary: links canonical tools/ai.sh and tools/work.sh into caller PATH, preferring Termux $PREFIX/bin and otherwise ~/.local/bin
#   owner: skill-lib
#   public_surface: bash tools/install_ai.sh
#   internal_surface: source preflight, PATH target selection, symlink installation
#   auth_boundary: none
#   storage_boundary: write
#   network_boundary: none
#   user_data_boundary: none
#   admin_only: false
#   tests: tests/test_ai_launcher.py, tests/test_work_launcher.py
#   rollout: explicit user invocation; see tools/WORK.md
#   rollback: remove installed ai.sh and work.sh symlinks and marked PATH line if added; repository sources remain
#   unresolved: a current shell cannot inherit a newly appended PATH line from a child process; an interrupted two-link install must be rerun
# === END MODULE_BUILD ===
# Usage: bash tools/install_ai.sh. No commands, agents, or cloud sessions start.

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
SOURCE="$SOURCE_DIR/ai.sh"
WORK_SOURCE="$SOURCE_DIR/work.sh"
PROFILE="${A0_AI_PROFILE:-$HOME/.profile}"

if [[ -n "${A0_AI_BIN_DIR:-}" ]]; then
  BIN_DIR="$A0_AI_BIN_DIR"
elif [[ -n "${PREFIX:-}" && -d "$PREFIX/bin" && -w "$PREFIX/bin" ]]; then
  BIN_DIR="$PREFIX/bin"
else
  BIN_DIR="$HOME/.local/bin"
fi

TARGET="$BIN_DIR/ai.sh"
WORK_TARGET="$BIN_DIR/work.sh"
for source in "$SOURCE" "$WORK_SOURCE"; do
  [[ -f "$source" ]] || { printf 'ERROR: canonical launcher missing: %s\n' "$source" >&2; exit 2; }
  bash -n "$source"
done
for target in "$TARGET" "$WORK_TARGET"; do
  [[ ! -d "$target" ]] || { printf 'ERROR: launcher target is a directory: %s\n' "$target" >&2; exit 2; }
done
if [[ -d "$BIN_DIR" && "$(cd "$BIN_DIR" && pwd -P)" == "$SOURCE_DIR" ]]; then
  printf 'ERROR: install directory is the source directory; refusing self-links.\n' >&2
  exit 2
fi
mkdir -p "$BIN_DIR"
chmod 0755 "$SOURCE" "$WORK_SOURCE"
ln -sfn "$SOURCE" "$TARGET"
ln -sfn "$WORK_SOURCE" "$WORK_TARGET"

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
  mkdir -p "$(dirname "$PROFILE")"
  touch "$PROFILE"
  path_line="export PATH=\"$BIN_DIR:\$PATH\" # skill-lib ai launcher"
  if ! grep -Fqx "$path_line" "$PROFILE"; then
    printf '\n%s\n' "$path_line" >> "$PROFILE"
  fi
  printf 'PATH updated for future login shells in %s\n' "$PROFILE"
  printf 'for this shell: export PATH=%q:\$PATH\n' "$BIN_DIR"
fi

printf 'installed: %s -> %s\n' "$TARGET" "$SOURCE"
printf 'installed: %s -> %s\n' "$WORK_TARGET" "$WORK_SOURCE"
bash "$TARGET" --help
bash "$WORK_TARGET" --help

# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm

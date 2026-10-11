#!/usr/bin/env bash
# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm
set -euo pipefail
# Runtime code and the venv must stay readable by the vmmcp service user; only
# secret files are written under umask 0077 (write_secret_file).
umask 0022
TRACE_INSTALL=0
[[ $- == *x* ]] && TRACE_INSTALL=1

# Install canonical vm-mcp on a Linux VM.
#
# Usage:
#   sudo VM_MCP_ROOT=/srv/vm-mcp/workspace bash vm-mcp/install.sh
#   sudo VM_MCP_PROFILE=personal-console \
#        VM_MCP_ROOT=/srv/vm-mcp/workspace bash vm-mcp/install.sh
#
# Profiles:
#   read-only        read tools only (default)
#   workspace        workspace write tools + confined shell_exec
#   personal-console workspace tools plus brokered user_exec/admin_exec
#
# The MCP HTTP service always binds to 127.0.0.1. personal-console starts a
# separate root Unix-socket broker; it does not make the MCP service root.

if [[ ${EUID} -ne 0 ]]; then
  echo "ERROR: run as root (sudo ... bash vm-mcp/install.sh)" >&2
  exit 2
fi

SOURCE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_ROOT="${VM_MCP_INSTALL_ROOT:-/opt/vm-mcp}"
WORK_ROOT="${VM_MCP_ROOT:-/srv/vm-mcp/workspace}"
PROFILE="${VM_MCP_PROFILE:-read-only}"
PORT="${VM_MCP_PORT:-8765}"
SERVICE_USER="${VM_MCP_SERVICE_USER:-vmmcp}"
SERVICE_GROUP="$SERVICE_USER"
ADMIN_SOCKET="${VM_MCP_ADMIN_SOCKET:-/run/vm-mcp/admin.sock}"
CREDENTIAL_FILE=/etc/credstore/vm-mcp-token
YAMA_SCOPE_PATH=/proc/sys/kernel/yama/ptrace_scope
PTRACE_SYSCTL_CONF=/etc/sysctl.d/99-zz-vm-mcp-ptrace.conf
# The bearer token comes from exactly one operator-provisioned source, so it
# never has to appear in a pasted command line or shell history:
#   VM_MCP_AUTH_TOKEN_FILE=/root/vm-mcp.token  regular file owned by the
#                                              installing user, no group/other access
#   VM_MCP_AUTH_TOKEN_STDIN=1                  first line of stdin
#   VM_MCP_AUTH_TOKEN=...                      environment (avoid in shell history)
# Every function that touches the token runs with xtrace off, so `bash -x`
# never prints it, and restores the caller's xtrace setting afterwards.
_resolve_auth_token() {
  local sources=0 token="" file fd owner mode raw fd_id path_id path_raw
  case "${VM_MCP_AUTH_TOKEN_STDIN-}" in
    ""|1) ;;
    *) echo "ERROR: VM_MCP_AUTH_TOKEN_STDIN must be unset or 1" >&2; return 3 ;;
  esac
  [[ -n "${VM_MCP_AUTH_TOKEN:-}" ]] && sources=$((sources + 1))
  [[ -n "${VM_MCP_AUTH_TOKEN_FILE:-}" ]] && sources=$((sources + 1))
  [[ "${VM_MCP_AUTH_TOKEN_STDIN:-}" == 1 ]] && sources=$((sources + 1))
  if (( sources > 1 )); then
    echo "ERROR: give exactly one of VM_MCP_AUTH_TOKEN_FILE, VM_MCP_AUTH_TOKEN_STDIN=1 or VM_MCP_AUTH_TOKEN" >&2
    return 3
  fi
  if [[ -n "${VM_MCP_AUTH_TOKEN_FILE:-}" ]]; then
    file="$VM_MCP_AUTH_TOKEN_FILE"
    if [[ -L "$file" || ! -f "$file" ]]; then
      echo "ERROR: VM_MCP_AUTH_TOKEN_FILE must be a regular file, not a symlink" >&2
      return 3
    fi
    # Open once, check the opened file itself (fstat through /dev/fd), and
    # require the path to still name that same inode: no check-then-read race.
    if ! exec {fd}<"$file"; then
      echo "ERROR: cannot open VM_MCP_AUTH_TOKEN_FILE" >&2
      return 3
    fi
    # %f is the raw st_mode in hex and is not locale-translated (unlike %F).
    read -r owner mode raw fd_id < <(LC_ALL=C stat -L -c '%u %a %f %d:%i' "/dev/fd/$fd")
    path_id="$(LC_ALL=C stat -c '%f %d:%i' -- "$file" 2>/dev/null || true)"
    path_raw="${path_id%% *}"
    if [[ ! "$raw" =~ ^[0-9a-f]+$ || ! "$path_raw" =~ ^[0-9a-f]+$ ]] \
        || (( (16#$raw & 16#F000) != 16#8000 || (16#$path_raw & 16#F000) != 16#8000 )) \
        || [[ "${path_id#* }" != "$fd_id" ]]; then
      exec {fd}<&-
      echo "ERROR: VM_MCP_AUTH_TOKEN_FILE is not a regular file or changed while being opened" >&2
      return 3
    fi
    if [[ "$owner" != "$EUID" ]] || (( (8#$mode & 8#077) != 0 )); then
      exec {fd}<&-
      echo "ERROR: VM_MCP_AUTH_TOKEN_FILE must be owned by the installing user with no group/other access (chmod 0600)" >&2
      return 3
    fi
    IFS= read -r token <&"$fd" || [[ -n "$token" ]]
    exec {fd}<&-
  elif [[ "${VM_MCP_AUTH_TOKEN_STDIN:-}" == 1 ]]; then
    IFS= read -r token || [[ -n "$token" ]]
  else
    token="${VM_MCP_AUTH_TOKEN:-}"
  fi
  if [[ "$token" == *$'\r' ]]; then
    echo "ERROR: the token ends in a carriage return: the token file has Windows (CRLF) line endings. Save it with LF endings (for example: sed -i 's/\r\$//' FILE) and retry" >&2
    return 3
  fi
  if [[ ! "$token" =~ ^[A-Za-z0-9_-]{32,256}$ ]]; then
    echo "ERROR: supply an operator-provisioned token (32-256 URL-safe characters) via VM_MCP_AUTH_TOKEN_FILE, VM_MCP_AUTH_TOKEN_STDIN=1 or VM_MCP_AUTH_TOKEN before installation" >&2
    return 3
  fi
  AUTH_TOKEN="$token"
}

# Usage: load_auth_token  (sets AUTH_TOKEN, or returns 3)
load_auth_token() {
  local xtrace=0 rc=0
  [[ $- == *x* ]] && xtrace=1
  set +x
  _resolve_auth_token || rc=$?
  unset VM_MCP_AUTH_TOKEN
  if (( xtrace )); then set -x; fi
  return "$rc"
}

# Usage: ... | write_secret_file DEST
# Writes stdin to a new 0600 temp file beside DEST under umask 0077, then
# renames it over DEST: an existing loosened DEST is replaced by a new inode,
# so the secret is never readable through an old mode.
write_secret_file() {
  local dest=$1 xtrace=0 rc=0
  [[ $- == *x* ]] && xtrace=1
  set +x
  # Explicit checks: errexit does not apply inside a subshell used with ||.
  (
    umask 0077
    tmp="$(mktemp "$(dirname -- "$dest")/.$(basename -- "$dest").XXXXXX")" || exit 1
    trap 'rm -f -- "$tmp"' EXIT
    cat > "$tmp" || exit 1
    chmod 0600 "$tmp" || exit 1
    if [[ $EUID -eq 0 ]]; then chown root:root "$tmp" || exit 1; fi
    mv -f -- "$tmp" "$dest" || exit 1
    trap - EXIT
  ) || rc=$?
  if (( xtrace )); then set -x; fi
  return "$rc"
}

load_auth_token || exit 3
NOLOGIN="$(command -v nologin || true)"
[[ -n "$NOLOGIN" ]] || NOLOGIN=/bin/false

case "$PROFILE" in
  read-only|workspace|personal-console) ;;
  *) echo "ERROR: VM_MCP_PROFILE must be read-only, workspace, or personal-console" >&2; exit 3 ;;
esac
case "$WORK_ROOT" in
  /*) ;;
  *) echo "ERROR: VM_MCP_ROOT must be an absolute path" >&2; exit 3 ;;
esac
case "$WORK_ROOT" in
  *$'\n'*|*$'\r'*) echo "ERROR: VM_MCP_ROOT must not contain newlines" >&2; exit 3 ;;
esac

# Usage: ensure_ptrace_scope PROFILE
# Shell profiles only: Yama ptrace_scope >= 1 stops same-UID shell_exec
# children from ptracing or pidfd_getfd-ing the service (a non-ancestor), so
# they cannot copy its token descriptor in the startup instant before it is
# non-dumpable. Keeps an existing higher value, persists it in a sysctl.d file
# that sorts last, applies it now, and warns about a later override to 0.
# read-only runs no shell children, so the host's ptrace policy is left alone.
ensure_ptrace_scope() {
  local profile=$1 current target tmp
  if [[ "$profile" == read-only ]]; then
    return 0
  fi
  if [[ ! -r "$YAMA_SCOPE_PATH" ]]; then
    echo "ERROR: kernel.yama.ptrace_scope is unavailable (Yama LSM not enabled). The $profile profile runs shell children as the service user and needs ptrace_scope >= 1 so they cannot copy the service's token descriptor. Enable Yama (security=yama / lsm=...,yama) or use VM_MCP_PROFILE=read-only" >&2
    return 7
  fi
  current="$(< "$YAMA_SCOPE_PATH")"
  if [[ ! "$current" =~ ^[0-3]$ ]]; then
    echo "ERROR: unexpected kernel.yama.ptrace_scope value" >&2
    return 7
  fi
  target=$(( current > 1 ? current : 1 ))
  tmp="$(mktemp "$(dirname -- "$PTRACE_SYSCTL_CONF")/.vm-mcp-ptrace.XXXXXX")" || return 7
  printf '# Written by vm-mcp/install.sh: same-UID processes may not ptrace or\n# pidfd_getfd non-descendants such as vm-mcp.service.\nkernel.yama.ptrace_scope = %s\n' "$target" > "$tmp" \
    && chmod 0644 "$tmp" && mv -f -- "$tmp" "$PTRACE_SYSCTL_CONF" || { rm -f -- "$tmp"; return 7; }
  if (( current < 1 )); then
    if ! sysctl -q -w "kernel.yama.ptrace_scope=$target" >/dev/null; then
      echo "ERROR: could not set kernel.yama.ptrace_scope=$target" >&2
      return 7
    fi
  fi
  current="$(< "$YAMA_SCOPE_PATH")"
  if (( current < 1 )); then
    echo "ERROR: kernel.yama.ptrace_scope is still $current after applying $PTRACE_SYSCTL_CONF" >&2
    return 7
  fi
  warn_ptrace_override
}

# Usage: warn_ptrace_override
# Warn when the merged sysctl.d configuration's last kernel.yama.ptrace_scope
# assignment comes from another file and is 0 (it would apply at next boot;
# the pre-start gate would then refuse to start the service).
warn_ptrace_override() {
  local tool line file="" last_file="" last_value=""
  tool="$(command -v systemd-sysctl || true)"
  for candidate in /usr/lib/systemd/systemd-sysctl /lib/systemd/systemd-sysctl; do
    [[ -n "$tool" ]] && break
    [[ -x "$candidate" ]] && tool="$candidate"
  done
  [[ -n "$tool" ]] || return 0
  while IFS= read -r line; do
    if [[ "$line" =~ ^#\ (/.*\.conf)$ ]]; then
      file="${BASH_REMATCH[1]}"
    elif [[ "$line" =~ ^[[:space:]]*-?kernel[./]yama[./]ptrace_scope[[:space:]]*=[[:space:]]*([0-9]+) ]]; then
      last_file="$file"
      last_value="${BASH_REMATCH[1]}"
    fi
  done < <("$tool" --cat-config 2>/dev/null || true)
  if [[ -n "$last_value" && "$last_file" != "$PTRACE_SYSCTL_CONF" && "$last_value" -lt 1 ]]; then
    echo "WARNING: $last_file sets kernel.yama.ptrace_scope = $last_value after $PTRACE_SYSCTL_CONF; at next boot vm-mcp.service will refuse to start in the $profile profile until that override is removed" >&2
  fi
}

install_python() {
  if command -v apt-get >/dev/null 2>&1; then
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -qq
    apt-get install -y -qq python3 python3-venv ca-certificates >/dev/null
  elif command -v dnf >/dev/null 2>&1; then
    dnf install -y python3 ca-certificates >/dev/null
  elif command -v yum >/dev/null 2>&1; then
    yum install -y python3 ca-certificates >/dev/null
  fi
  command -v python3 >/dev/null 2>&1 || {
    echo "ERROR: python3 is required and no supported package manager installed it" >&2
    exit 4
  }
}

systemd_quote() {
  local value=$1
  value=${value//\\/\\\\}
  value=${value//\"/\\\"}
  printf '"%s"' "$value"
}

ensure_ptrace_scope "$PROFILE" || exit 7
install_python

if ! id "$SERVICE_USER" >/dev/null 2>&1; then
  useradd --system --home "$WORK_ROOT/.vm-mcp-home" --shell "$NOLOGIN" "$SERVICE_USER"
else
  usermod --home "$WORK_ROOT/.vm-mcp-home" "$SERVICE_USER"
fi

# Existing application directories retain their existing ownership. This fixes
# the dangerous first-release behavior where selecting an existing VM_MCP_ROOT
# could transfer ownership of that directory to vmmcp.
if [[ ! -e "$WORK_ROOT" ]]; then
  install -d -o "$SERVICE_USER" -g "$SERVICE_GROUP" -m 0750 "$WORK_ROOT"
elif [[ ! -d "$WORK_ROOT" ]]; then
  echo "ERROR: VM_MCP_ROOT exists but is not a directory: $WORK_ROOT" >&2
  exit 5
fi
install -d -o "$SERVICE_USER" -g "$SERVICE_GROUP" -m 0700 "$WORK_ROOT/.vm-mcp-home"
install -d -o root -g root -m 0755 "$INSTALL_ROOT" "$INSTALL_ROOT/systemd"

for file in server.py auth.py policy.py profiles.py yama_gate.py admin_client.py admin_broker.py requirements.txt; do
  install -m 0644 "$SOURCE_ROOT/$file" "$INSTALL_ROOT/$file"
done
install -m 0644 "$SOURCE_ROOT/systemd/vm-mcp.service" "$INSTALL_ROOT/systemd/vm-mcp.service"
install -m 0644 "$SOURCE_ROOT/systemd/vm-mcp-admin.service" "$INSTALL_ROOT/systemd/vm-mcp-admin.service"

SOURCE_COMMIT=hmmm
if command -v git >/dev/null 2>&1 && git -C "$SOURCE_ROOT" rev-parse HEAD >/dev/null 2>&1; then
  SOURCE_COMMIT="$(git -C "$SOURCE_ROOT" rev-parse HEAD)"
fi
printf '%s\n' "$SOURCE_COMMIT" > "$INSTALL_ROOT/SOURCE_COMMIT"
chmod 0644 "$INSTALL_ROOT/SOURCE_COMMIT"

# Usage: install_runtime INSTALL_ROOT
# The vmmcp service user must read and exec the venv whatever umask the
# operator's shell had, so venv creation and pip always run under umask 0022.
install_runtime() {
  local root=$1
  (
    set -e
    umask 0022
    if [[ ! -x "$root/.venv/bin/python" ]]; then
      python3 -m venv "$root/.venv"
    fi
    "$root/.venv/bin/python" -m pip install --upgrade pip >/dev/null
    "$root/.venv/bin/python" -m pip install -r "$root/requirements.txt"
  )
}
install_runtime "$INSTALL_ROOT"

install -m 0644 "$SOURCE_ROOT/systemd/vm-mcp.service" /etc/systemd/system/vm-mcp.service
install -m 0644 "$SOURCE_ROOT/systemd/vm-mcp-admin.service" /etc/systemd/system/vm-mcp-admin.service
# The token goes to a root-only 0600 file that the service manager opens and
# passes as the service's stdin (see systemd/vm-mcp.service). It is never a
# service environment variable: /proc/<pid>/environ is readable by same-UID
# processes until the server is non-dumpable.
install -d -o root -g root -m 0700 "$(dirname -- "$CREDENTIAL_FILE")"
set +x
printf '%s\n' "$AUTH_TOKEN" | write_secret_file "$CREDENTIAL_FILE" || exit 6
unset AUTH_TOKEN
if (( TRACE_INSTALL )); then set -x; fi
write_secret_file /etc/vm-mcp.env <<EOF || exit 6
VM_MCP_ROOT=$(systemd_quote "$WORK_ROOT")
VM_MCP_PROFILE=$PROFILE
VM_MCP_PORT=$PORT
VM_MCP_ADMIN_SOCKET=$(systemd_quote "$ADMIN_SOCKET")
EOF

install -d -m 0755 /etc/systemd/system/vm-mcp.service.d
cat > /etc/systemd/system/vm-mcp.service.d/workspace.conf <<EOF
[Service]
ReadWritePaths=
ReadWritePaths=$WORK_ROOT
EOF
chmod 0644 /etc/systemd/system/vm-mcp.service.d/workspace.conf

systemctl daemon-reload
if [[ "$PROFILE" == personal-console ]]; then
  systemctl enable --now vm-mcp-admin.service
  systemctl restart vm-mcp-admin.service
else
  systemctl disable --now vm-mcp-admin.service >/dev/null 2>&1 || true
fi
systemctl enable --now vm-mcp.service
systemctl restart vm-mcp.service

printf '\nvm-mcp installed\n'
printf '  source commit: %s\n' "$SOURCE_COMMIT"
printf '  endpoint:      http://127.0.0.1:%s/mcp\n' "$PORT"
printf '  workspace:     %s\n' "$WORK_ROOT"
printf '  profile:       %s\n' "$PROFILE"
if [[ "$PROFILE" == personal-console ]]; then
  printf '  root broker:   %s\n' "$ADMIN_SOCKET"
  printf '  user_exec:     enabled\n'
  printf '  admin_exec:    enabled (root)\n'
else
  printf '  root broker:   disabled\n'
fi
systemctl --no-pager --full status vm-mcp.service | sed -n '1,14p'
# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm

# ratios: loc_comments=88:8 imports_exports=0:0 calls_definitions=2:0
#!/usr/bin/env bash
set -euo pipefail

# Install the canonical skill-lib vm-mcp runtime on a Linux VM.
#
# Usage:
#   sudo VM_MCP_ROOT=/srv/a0/workspaces bash vm-mcp/install.sh
#
# The installed service binds only to 127.0.0.1:8765 and starts with shell
# execution disabled. A private MCP tunnel/client is still required.

if [[ ${EUID} -ne 0 ]]; then
  echo "ERROR: run as root (sudo ... bash vm-mcp/install.sh)" >&2
  exit 2
fi

SOURCE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_ROOT="${VM_MCP_INSTALL_ROOT:-/opt/vm-mcp}"
WORK_ROOT="${VM_MCP_ROOT:-/srv/vm-mcp/workspace}"
PORT="${VM_MCP_PORT:-8765}"
SERVICE_USER="${VM_MCP_SERVICE_USER:-vmmcp}"
SERVICE_GROUP="$SERVICE_USER"
NOLOGIN="$(command -v nologin || true)"
[[ -n "$NOLOGIN" ]] || NOLOGIN=/bin/false

case "$WORK_ROOT" in
  /*) ;;
  *) echo "ERROR: VM_MCP_ROOT must be an absolute path" >&2; exit 3 ;;
esac
case "$WORK_ROOT" in
  *$'\n'*|*$'\r'*) echo "ERROR: VM_MCP_ROOT must not contain newlines" >&2; exit 3 ;;
esac

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

install_python

if ! id "$SERVICE_USER" >/dev/null 2>&1; then
  useradd --system --home "$WORK_ROOT/.vm-mcp-home" --shell "$NOLOGIN" "$SERVICE_USER"
else
  usermod --home "$WORK_ROOT/.vm-mcp-home" "$SERVICE_USER"
fi

install -d -o "$SERVICE_USER" -g "$SERVICE_GROUP" -m 0750 "$WORK_ROOT"
install -d -o "$SERVICE_USER" -g "$SERVICE_GROUP" -m 0700 "$WORK_ROOT/.vm-mcp-home"
install -d -o root -g root -m 0755 "$INSTALL_ROOT" "$INSTALL_ROOT/systemd"
install -m 0644 "$SOURCE_ROOT/server.py" "$INSTALL_ROOT/server.py"
install -m 0644 "$SOURCE_ROOT/policy.py" "$INSTALL_ROOT/policy.py"
install -m 0644 "$SOURCE_ROOT/requirements.txt" "$INSTALL_ROOT/requirements.txt"
install -m 0644 "$SOURCE_ROOT/systemd/vm-mcp.service" "$INSTALL_ROOT/systemd/vm-mcp.service"

SOURCE_COMMIT=hmmm
if command -v git >/dev/null 2>&1 && git -C "$SOURCE_ROOT" rev-parse HEAD >/dev/null 2>&1; then
  SOURCE_COMMIT="$(git -C "$SOURCE_ROOT" rev-parse HEAD)"
fi
printf '%s\n' "$SOURCE_COMMIT" > "$INSTALL_ROOT/SOURCE_COMMIT"
chmod 0644 "$INSTALL_ROOT/SOURCE_COMMIT"

if [[ ! -x "$INSTALL_ROOT/.venv/bin/python" ]]; then
  python3 -m venv "$INSTALL_ROOT/.venv"
fi
"$INSTALL_ROOT/.venv/bin/python" -m pip install --upgrade pip >/dev/null
"$INSTALL_ROOT/.venv/bin/python" -m pip install -r "$INSTALL_ROOT/requirements.txt"

install -m 0644 "$SOURCE_ROOT/systemd/vm-mcp.service" /etc/systemd/system/vm-mcp.service
cat > /etc/vm-mcp.env <<EOF
VM_MCP_ROOT=$(systemd_quote "$WORK_ROOT")
VM_MCP_PORT=$PORT
VM_MCP_SHELL_ENABLED=0
EOF
chmod 0600 /etc/vm-mcp.env

install -d -m 0755 /etc/systemd/system/vm-mcp.service.d
cat > /etc/systemd/system/vm-mcp.service.d/workspace.conf <<EOF
[Service]
ReadWritePaths=
ReadWritePaths=$WORK_ROOT
EOF
chmod 0644 /etc/systemd/system/vm-mcp.service.d/workspace.conf

systemctl daemon-reload
systemctl enable --now vm-mcp.service
systemctl restart vm-mcp.service

printf '\nvm-mcp installed\n'
printf '  source commit: %s\n' "$SOURCE_COMMIT"
printf '  endpoint:      http://127.0.0.1:%s/mcp\n' "$PORT"
printf '  workspace:     %s\n' "$WORK_ROOT"
printf '  shell_exec:    disabled\n'
systemctl --no-pager --full status vm-mcp.service | sed -n '1,14p'
# ratios: loc_comments=88:8 imports_exports=0:0 calls_definitions=2:0

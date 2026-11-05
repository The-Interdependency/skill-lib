#!/usr/bin/env bash
# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm
# Usage: sudo bash install.sh EXPECTED_BAO_SHA256; fresh install only.
# Requires an operator-verified /usr/local/bin/bao; never downloads or initializes.
set -Eeuo pipefail
[[ $EUID == 0 && ${1:-} =~ ^[a-fA-F0-9]{64}$ ]] || { echo 'root and expected bao SHA256 required' >&2; exit 2; }
source_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
for tool in openssl python3 systemctl sha256sum install useradd; do command -v "$tool" >/dev/null; done
[[ -f /usr/local/bin/bao && ! -L /usr/local/bin/bao ]]
printf '%s  /usr/local/bin/bao\n' "$1" | sha256sum --check --status
[[ $(stat -c '%u' /usr/local/bin/bao) == 0 ]]
[[ -z $(find /usr/local/bin/bao -perm /022 -print) ]]
# Integrated storage uses mmap; refuse a host with active swap before any write.
[[ $(wc -l < /proc/swaps) == 1 ]] || { echo 'active swap: resolve encrypted-memory policy before installing' >&2; exit 3; }
for path in /etc/openbao /var/lib/openbao /var/log/openbao /opt/a0-openbao /etc/systemd/system/openbao.service; do
  [[ ! -e $path && ! -L $path ]] || { echo "existing deployment: inspect before upgrade: $path" >&2; exit 4; }
done
! getent passwd openbao >/dev/null || { echo 'existing openbao account requires reviewed upgrade' >&2; exit 4; }
useradd --system --user-group --home-dir /var/lib/openbao --shell /usr/sbin/nologin openbao
install -d -o root -g openbao -m 0750 /etc/openbao/tls
install -d -o openbao -g openbao -m 0700 /var/lib/openbao /var/log/openbao
install -d -o root -g root -m 0755 /opt/a0-openbao
umask 077
openssl req -x509 -newkey rsa:3072 -nodes -days 365 -subj '/CN=a0-openbao-local' \
  -addext 'subjectAltName=IP:127.0.0.1' \
  -keyout /etc/openbao/tls/key.pem -out /etc/openbao/tls/cert.pem >/dev/null 2>&1
chown root:openbao /etc/openbao/tls/key.pem
chmod 0640 /etc/openbao/tls/key.pem
# Certificate is public trust material. Private key stays restricted.
chmod 0755 /etc/openbao /etc/openbao/tls
chmod 0644 /etc/openbao/tls/cert.pem
install -o root -g openbao -m 0640 "$source_dir/server.hcl" /etc/openbao/server.hcl
install -o root -g root -m 0644 "$source_dir/launch.py" /opt/a0-openbao/launch.py
install -o root -g root -m 0644 "$source_dir/swap_gate.py" /opt/a0-openbao/swap_gate.py
install -o root -g root -m 0644 "$source_dir/provision.py" /opt/a0-openbao/provision.py
install -o root -g root -m 0644 "$source_dir/openbao.service" /etc/systemd/system/openbao.service
systemctl daemon-reload
systemctl enable --now openbao.service
printf 'Installed, awaiting private initialization/unseal and AppRole provisioning. See OPENBAO.md.\n'
# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm

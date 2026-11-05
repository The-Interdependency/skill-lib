ui = false
disable_mlock = true
api_addr = "https://127.0.0.1:8200"
cluster_addr = "https://127.0.0.1:8201"
storage "raft" {
  path = "/var/lib/openbao"
  node_id = "a0-local"
}
listener "tcp" {
  address = "127.0.0.1:8200"
  cluster_address = "127.0.0.1:8201"
  tls_cert_file = "/etc/openbao/tls/cert.pem"
  tls_key_file = "/etc/openbao/tls/key.pem"
  tls_min_version = "tls12"
}

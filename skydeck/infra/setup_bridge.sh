#!/usr/bin/env bash
# ────────────────────────────────────────────────────────────────
# setup_bridge.sh — Squid forward-proxy on the European bridge
#
# Run on: 91.107.160.193 (EU bridge server)
# Purpose: Allow the Iranian production server (185.159.154.217)
#          to pull Docker images from registry.gitlab.com through
#          this proxy, bypassing DPI firewalls.
#
# Usage:  sudo bash setup_bridge.sh
# ────────────────────────────────────────────────────────────────
set -euo pipefail

IRAN_IP="185.159.154.217"
SQUID_PORT="3128"

echo "=== [1/4] Installing Squid ==="
apt-get update -qq
apt-get install -y -qq squid

echo "=== [2/4] Backing up original config ==="
cp /etc/squid/squid.conf /etc/squid/squid.conf.bak.$(date +%s)

echo "=== [3/4] Writing Squid config ==="
cat > /etc/squid/squid.conf << 'SQUID_EOF'
# ── SkyDeck Bridge Proxy ────────────────────────────────────
# Only the Iranian production server is allowed to connect.
# All other IPs are denied.

# ACLs
acl localnet src 185.159.154.217/32
acl SSL_ports port 443
acl Safe_ports port 80
acl Safe_ports port 443
acl CONNECT method CONNECT

# Access rules
http_access deny !Safe_ports
http_access deny CONNECT !SSL_ports
http_access allow localnet
http_access deny all

# Listener
http_port 3128

# Logging
access_log daemon:/var/log/squid/access.log squid
cache_log /var/log/squid/cache.log

# Hardening
forwarded_for delete
via off
request_header_access X-Forwarded-For deny all

# No disk cache needed — this is a pass-through proxy
cache deny all
SQUID_EOF

echo "=== [4/4] Restarting Squid ==="
systemctl enable squid
systemctl restart squid
systemctl status squid --no-pager

echo ""
echo "Done. Squid is listening on port ${SQUID_PORT}."
echo "Only ${IRAN_IP} is allowed to connect."
echo ""
echo "IMPORTANT: Ensure your firewall allows inbound TCP ${SQUID_PORT} from ${IRAN_IP}:"
echo "  ufw allow from ${IRAN_IP} to any port ${SQUID_PORT} proto tcp"

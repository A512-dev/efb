#!/usr/bin/env bash
# ────────────────────────────────────────────────────────────────
# setup_iran.sh — Configure Docker to use the EU bridge proxy
#
# Run on: 185.159.154.217 (Iranian production server)
# Purpose: Route Docker daemon's HTTP/HTTPS traffic through the
#          Squid proxy on 91.107.160.193:3128 so that image pulls
#          from registry.gitlab.com bypass DPI firewalls.
#
# Usage:  sudo bash setup_iran.sh
# ────────────────────────────────────────────────────────────────
set -euo pipefail

BRIDGE_IP="91.107.160.193"
BRIDGE_PORT="3128"
PROXY_URL="http://${BRIDGE_IP}:${BRIDGE_PORT}"
DROPIN_DIR="/etc/systemd/system/docker.service.d"
DROPIN_FILE="${DROPIN_DIR}/http-proxy.conf"

echo "=== [1/4] Creating systemd drop-in directory ==="
mkdir -p "${DROPIN_DIR}"

echo "=== [2/4] Writing proxy configuration ==="
cat > "${DROPIN_FILE}" << EOF
[Service]
Environment="HTTP_PROXY=${PROXY_URL}"
Environment="HTTPS_PROXY=${PROXY_URL}"
Environment="NO_PROXY=localhost,127.0.0.1,185.159.154.217"
EOF

echo "  Written to: ${DROPIN_FILE}"
cat "${DROPIN_FILE}"

echo ""
echo "=== [3/4] Reloading systemd ==="
systemctl daemon-reload

echo "=== [4/4] Restarting Docker ==="
systemctl restart docker
systemctl status docker --no-pager

echo ""
echo "Done. Docker now routes through ${PROXY_URL}."
echo ""
echo "Verify with:"
echo "  docker info | grep -i proxy"
echo "  docker pull hello-world"

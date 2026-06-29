#!/usr/bin/env bash
# OmniSight host discovery: Docker containers → JSON for host_agent.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v python3 >/dev/null 2>&1 && [[ -f "${SCRIPT_DIR}/host_discover.py" ]]; then
  exec python3 "${SCRIPT_DIR}/host_discover.py"
fi

if command -v python3 >/dev/null 2>&1; then
  exec python3 -
fi

HOSTNAME_FQDN="$(hostname 2>/dev/null || echo unknown)"
HOST_IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
printf '{"host":{"hostname":"%s","ip":"%s","os":"Linux"},"processes":[],"connections":[]}\n' "$HOSTNAME_FQDN" "$HOST_IP"

#!/usr/bin/env bash
set -euo pipefail

docker compose up -d --build

# Find the IPv4 address used for the default network route.
HOST_IP=$(ip -4 route get 8.8.8.8 |
    awk '{for (i=1; i<=NF; i++) if ($i=="src") {print $(i+1); exit}}')

if [[ -z "$HOST_IP" ]]; then
    echo "Could not determine the host's private IP address." >&2
    exit 1
fi

echo
echo "Woninet dashboard:"
echo "http://${HOST_IP}:8080"

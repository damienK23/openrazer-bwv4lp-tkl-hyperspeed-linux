#!/usr/bin/env bash
set -euo pipefail

KERNEL="$(uname -r)"

echo "== DKMS: rebuild openrazer-driver/3.12.2 for kernel ${KERNEL}"
dkms remove openrazer-driver/3.12.2 --all || true
dkms install openrazer-driver/3.12.2 -k "${KERNEL}" --force

echo "== Reload razerkbd module"
modprobe -r razerkbd 2>/dev/null || true
modprobe razerkbd

echo "== Check modalias for 02d2/02d4"
modinfo razerkbd | grep -iE "p000002d2|p000002d4" || true

echo "== Restart openrazer-daemon (no systemd required)"
openrazer-daemon -r || true

echo "OK"


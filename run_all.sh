#!/usr/bin/env bash
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "== OpenRazer BWV4 LP TKL HyperSpeed patch runner =="

echo "== 1) Patch DKMS sources"
sudo python3 "$here/openrazer_bwv4lp_tkl_patch.py"

echo "== 2) Rebuild DKMS"
sudo bash "$here/openrazer_bwv4lp_tkl_rebuild.sh"

echo "== 3) Patch daemon (keyboards.py)"
sudo python3 "$here/openrazer_bwv4lp_tkl_daemon_patch.py"
sudo python3 "$here/openrazer_bwv4lp_tkl_daemon_fix.py"
sudo python3 "$here/openrazer_bwv4lp_tkl_daemon_capability_fix.py"

echo "== 4) Patch udev rules + retrigger"
sudo python3 "$here/openrazer_udev_add_02d2_02d4.py"
sudo udevadm control --reload-rules
sudo udevadm trigger --action=add --subsystem-match=hid --attr-match=idVendor=1532

echo "== Done. Replug keyboard + dongle, then start daemon/Polychromatic."


# openrazer-bwv4lp-tkl-hyperspeed-linux
Patch scripts to enable OpenRazer/Polychromatic support for the Razer BlackWidow V4 Low‑Profile TKL HyperSpeed on Ubuntu/Linux (USB IDs 1532:02D2 / 1532:02D4).

This repo provides one-shot scripts to make the Razer BlackWidow V4 Low‑Profile Tenkeyless HyperSpeed work with OpenRazer + Polychromatic on Linux, when it shows as “unsupported” and the RGB is stuck in a rainbow pattern.

It targets the two USB modes:

HyperSpeed dongle: 1532:02D2
Wired keyboard: 1532:02D4
What it does
Patches OpenRazer DKMS driver (razerkbd) to add 0x02D2/0x02D4 (modalias + binding).
Patches OpenRazer daemon to recognize the device in keyboards.py.
Updates udev rules so sysfs nodes are accessible to the plugdev group.
Adds a small daemon workaround to avoid crashing on optional/unsupported sysfs capabilities.
Audience / scope note
Designed for Ubuntu/Debian systems using the packaged OpenRazer DKMS driver. It modifies system files (DKMS sources, udev rules, Python dist-packages). Use at your own risk.

Tags / topics
openrazer, razer, blackwidow, linux, ubuntu, dkms, polychromatic, rgb, keyboard

Suggested GitHub Release note (optional)
Tested: Ubuntu 24.04 (noble), OpenRazer 3.12.2, kernel 6.17.x.

#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path("/usr/src/openrazer-driver-3.12.2/driver")
C_PATH = ROOT / "razerkbd_driver.c"
H_PATH = ROOT / "razerkbd_driver.h"

WIRED_EXISTING = "case USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_TENKEYLESS_HYPERSPEED_WIRED:"
WIRELESS_EXISTING = "case USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_TENKEYLESS_HYPERSPEED_WIRELESS:"
WIRED_NEW = "case USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_LP_TENKEYLESS_HYPERSPEED_WIRED:"
WIRELESS_NEW = "case USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_LP_TENKEYLESS_HYPERSPEED_WIRELESS:"


def die(msg: str) -> None:
    print(f"ERREUR: {msg}", file=sys.stderr)
    sys.exit(1)


def ensure_defines(h: str) -> str:
    if "USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_LP_TENKEYLESS_HYPERSPEED_WIRELESS" not in h:
        anchor = "#define USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_TENKEYLESS_HYPERSPEED_WIRELESS 0x02D5\n"
        if anchor not in h:
            die("Anchor define 0x02D5 introuvable dans razerkbd_driver.h")
        h = h.replace(
            anchor,
            anchor + "#define USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_LP_TENKEYLESS_HYPERSPEED_WIRELESS 0x02D2\n",
            1,
        )
    if "USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_LP_TENKEYLESS_HYPERSPEED_WIRED" not in h:
        anchor = "#define USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_TENKEYLESS_HYPERSPEED_WIRED 0x02D7\n"
        if anchor not in h:
            die("Anchor define 0x02D7 introuvable dans razerkbd_driver.h")
        h = h.replace(
            anchor,
            "#define USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_LP_TENKEYLESS_HYPERSPEED_WIRED 0x02D4\n" + anchor,
            1,
        )
    return h


def insert_after_all(text: str, needle: str, insertion: str) -> tuple[str, int]:
    """
    For each line containing needle, insert insertion on the next line (same indentation),
    unless insertion already appears nearby.
    """
    out_lines: list[str] = []
    count = 0
    for line in text.splitlines(True):
        out_lines.append(line)
        if needle in line:
            # if the next line already is our insertion, do nothing (handled by scan)
            indent = line.split("case", 1)[0]
            ins_line = f"{indent}{insertion}\n"
            # guard: don't duplicate if already inserted immediately after
            # (we can't peek ahead easily without buffering; instead check last 2 lines)
            if len(out_lines) >= 2 and out_lines[-1] == ins_line:
                continue
            # if previous line was already insertion, skip
            if len(out_lines) >= 2 and out_lines[-2] == ins_line:
                continue
            out_lines.append(ins_line)
            count += 1
    return ("".join(out_lines), count)


def main() -> None:
    if not C_PATH.exists() or not H_PATH.exists():
        die("Sources DKMS introuvables dans /usr/src/openrazer-driver-3.12.2/driver")

    h = H_PATH.read_text(encoding="utf-8", errors="replace")
    c = C_PATH.read_text(encoding="utf-8", errors="replace")

    h2 = ensure_defines(h)

    # Expand *all* switch blocks that already support the non-low-profile TKL hyperspeed IDs.
    c2, n1 = insert_after_all(c, WIRED_EXISTING, WIRED_NEW)
    c3, n2 = insert_after_all(c2, WIRELESS_EXISTING, WIRELESS_NEW)

    H_PATH.write_text(h2, encoding="utf-8")
    C_PATH.write_text(c3, encoding="utf-8")

    print(f"OK: ajouté {n1} insertions wired + {n2} insertions wireless dans razerkbd_driver.c")


if __name__ == "__main__":
    main()


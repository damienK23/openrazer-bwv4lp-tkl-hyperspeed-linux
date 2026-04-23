#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path("/usr/src/openrazer-driver-3.12.2/driver")
H_PATH = ROOT / "razerkbd_driver.h"
C_PATH = ROOT / "razerkbd_driver.c"

NEW_DEFINES = [
    ("USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_LP_TENKEYLESS_HYPERSPEED_WIRELESS", "0x02D2"),
    ("USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_LP_TENKEYLESS_HYPERSPEED_WIRED", "0x02D4"),
]


def die(msg: str) -> None:
    print(f"ERREUR: {msg}", file=sys.stderr)
    sys.exit(1)


def require_file(p: Path) -> None:
    if not p.exists():
        die(f"Fichier introuvable: {p}")


def ensure_define(h: str, name: str, value: str) -> str:
    if name in h:
        return h

    # Insert near existing V4 TKL HyperSpeed defines to keep the file organized.
    anchor = "#define USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_TENKEYLESS_HYPERSPEED_WIRELESS 0x02D5\n"
    if anchor not in h:
        die("Anchor non trouvé dans razerkbd_driver.h (define 0x02D5). La version du driver a peut-être changé.")

    insert = anchor + f"#define {name} {value}\n"
    return h.replace(anchor, insert, 1)


def add_case_after_first(c: str, existing: str, new: str) -> str:
    if new in c:
        return c
    idx = c.find(existing)
    if idx == -1:
        die(f"Case attendu non trouvé dans razerkbd_driver.c: {existing.strip()}")
    idx_end = idx + len(existing)
    return c[:idx_end] + new + c[idx_end:]


def main() -> None:
    require_file(H_PATH)
    require_file(C_PATH)

    h = H_PATH.read_text(encoding="utf-8", errors="replace")
    c = C_PATH.read_text(encoding="utf-8", errors="replace")

    # ---- Header defines ----
    for name, value in NEW_DEFINES:
        h = ensure_define(h, name, value)

    # ---- Core wiring: mirror existing V4 TKL HyperSpeed handling ----
    # We intentionally mirror the existing family already supported in this driver:
    # USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_TENKEYLESS_HYPERSPEED_{WIRED,WIRELESS}
    c = add_case_after_first(
        c,
        "    case USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_TENKEYLESS_HYPERSPEED_WIRED:\n",
        "    case USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_LP_TENKEYLESS_HYPERSPEED_WIRED:\n",
    )
    c = add_case_after_first(
        c,
        "    case USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_TENKEYLESS_HYPERSPEED_WIRELESS:\n",
        "    case USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_LP_TENKEYLESS_HYPERSPEED_WIRELESS:\n",
    )

    # Device type strings (for sysfs / daemon visibility)
    wired_anchor = (
        "    case USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_TENKEYLESS_HYPERSPEED_WIRED:\n"
        "        device_type = \"Razer BlackWidow V4 Tenkeyless HyperSpeed (Wired)\";\n"
        "        break;\n"
    )
    if "USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_LP_TENKEYLESS_HYPERSPEED_WIRED" not in c:
        pos = c.find(wired_anchor)
        if pos == -1:
            die("Anchor non trouvé pour le device_type (wired).")
        insert = wired_anchor + (
            "    case USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_LP_TENKEYLESS_HYPERSPEED_WIRED:\n"
            "        device_type = \"Razer BlackWidow V4 Low-profile Tenkeyless HyperSpeed (Wired)\";\n"
            "        break;\n"
        )
        c = c.replace(wired_anchor, insert, 1)

    wireless_anchor = (
        "    case USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_TENKEYLESS_HYPERSPEED_WIRELESS:\n"
        "        device_type = \"Razer BlackWidow V4 Tenkeyless HyperSpeed (Wireless)\";\n"
        "        break;\n"
    )
    if "USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_LP_TENKEYLESS_HYPERSPEED_WIRELESS" not in c:
        pos = c.find(wireless_anchor)
        if pos == -1:
            die("Anchor non trouvé pour le device_type (wireless).")
        insert = wireless_anchor + (
            "    case USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_LP_TENKEYLESS_HYPERSPEED_WIRELESS:\n"
            "        device_type = \"Razer BlackWidow V4 Low-profile Tenkeyless HyperSpeed (Wireless)\";\n"
            "        break;\n"
        )
        c = c.replace(wireless_anchor, insert, 1)

    # Fn translation table block should include the new IDs.
    # We add the LP cases right next to the existing V4 TKL hyperspeed cases.
    translation_anchor = (
        "    case USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_TENKEYLESS_HYPERSPEED_WIRED:\n"
        "    case USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_TENKEYLESS_HYPERSPEED_WIRELESS:\n"
        "        translation = find_translation(chroma_keys_9, usage->code);\n"
        "        break;\n"
    )
    if (
        "USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_LP_TENKEYLESS_HYPERSPEED_WIRED" not in c
        or "USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_LP_TENKEYLESS_HYPERSPEED_WIRELESS" not in c
    ):
        if translation_anchor not in c:
            die("Anchor non trouvé pour le bloc chroma_keys_9 (traductions FN).")
        replacement = (
            "    case USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_TENKEYLESS_HYPERSPEED_WIRED:\n"
            "    case USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_TENKEYLESS_HYPERSPEED_WIRELESS:\n"
            "    case USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_LP_TENKEYLESS_HYPERSPEED_WIRED:\n"
            "    case USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_LP_TENKEYLESS_HYPERSPEED_WIRELESS:\n"
            "        translation = find_translation(chroma_keys_9, usage->code);\n"
            "        break;\n"
        )
        c = c.replace(translation_anchor, replacement, 1)

    # Device table: this is critical so the module binds (modalias).
    table_anchor = (
        "    { HID_USB_DEVICE(USB_VENDOR_ID_RAZER,USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_TENKEYLESS_HYPERSPEED_WIRED) },\n"
        "    { HID_USB_DEVICE(USB_VENDOR_ID_RAZER,USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_TENKEYLESS_HYPERSPEED_WIRELESS) },\n"
    )
    table_line_wired = "    { HID_USB_DEVICE(USB_VENDOR_ID_RAZER,USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_LP_TENKEYLESS_HYPERSPEED_WIRED) },\n"
    table_line_wireless = "    { HID_USB_DEVICE(USB_VENDOR_ID_RAZER,USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_LP_TENKEYLESS_HYPERSPEED_WIRELESS) },\n"
    if (table_line_wired not in c) or (table_line_wireless not in c):
        if table_anchor not in c:
            die("Anchor non trouvé dans razer_devices[] (V4 TKL HyperSpeed).")
        insertion = ""
        if table_line_wired not in c:
            insertion += table_line_wired
        if table_line_wireless not in c:
            insertion += table_line_wireless
        c = c.replace(table_anchor, table_anchor + insertion, 1)

    H_PATH.write_text(h, encoding="utf-8")
    C_PATH.write_text(c, encoding="utf-8")

    print("OK: patch appliqué dans /usr/src/openrazer-driver-3.12.2/driver")


if __name__ == "__main__":
    main()


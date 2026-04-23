#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import re

C_PATH = Path("/usr/src/openrazer-driver-3.12.2/driver/razerkbd_driver.c")

WIRED = "USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_LP_TENKEYLESS_HYPERSPEED_WIRED"
WIRELESS = "USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_LP_TENKEYLESS_HYPERSPEED_WIRELESS"

def main() -> None:
    s = C_PATH.read_text(encoding="utf-8", errors="replace")

    # Extract the razer_attr_read_device_type() function body and de-dupe case labels inside it.
    m = re.search(r"static\s+ssize_t\s+razer_attr_read_device_type\s*\([^)]*\)\s*\{", s)
    if not m:
        raise SystemExit("ERREUR: fonction razer_attr_read_device_type introuvable")

    start = m.start()
    # naive brace matching from function start
    i = s.find("{", m.end()-1)
    depth = 0
    end = None
    for j in range(i, len(s)):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                end = j + 1
                break
    if end is None:
        raise SystemExit("ERREUR: impossible de trouver la fin de razer_attr_read_device_type")

    pre, body, post = s[:start], s[start:end], s[end:]

    seen = set()
    out_lines = []
    removed = 0
    for line in body.splitlines(True):
        if WIRED in line or WIRELESS in line:
            key = WIRED if WIRED in line else WIRELESS
            if key in seen:
                removed += 1
                continue
            seen.add(key)
        out_lines.append(line)

    body2 = "".join(out_lines)
    if removed == 0:
        print("OK: aucun doublon device_type trouvé")
        return

    C_PATH.write_text(pre + body2 + post, encoding="utf-8")
    print(f"OK: supprimé {removed} doublon(s) dans razer_attr_read_device_type")

if __name__ == "__main__":
    main()

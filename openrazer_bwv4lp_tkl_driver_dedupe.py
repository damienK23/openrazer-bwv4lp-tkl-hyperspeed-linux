#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import re

C_PATH = Path("/usr/src/openrazer-driver-3.12.2/driver/razerkbd_driver.c")

def main() -> None:
    s = C_PATH.read_text(encoding="utf-8", errors="replace")

    # Remove consecutive duplicate case lines for our LP IDs (causes duplicate case value).
    patterns = [
        r"(\n\s*case\s+USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_LP_TENKEYLESS_HYPERSPEED_WIRED:\s*)\1+",
        r"(\n\s*case\s+USB_DEVICE_ID_RAZER_BLACKWIDOW_V4_LP_TENKEYLESS_HYPERSPEED_WIRELESS:\s*)\1+",
    ]

    before = s
    for pat in patterns:
        s = re.sub(pat, r"\1", s)

    if s == before:
        print("OK: rien à dédupliquer (pas de doublons consécutifs trouvés)")
    else:
        C_PATH.write_text(s, encoding="utf-8")
        print("OK: doublons supprimés dans razerkbd_driver.c")

if __name__ == "__main__":
    main()

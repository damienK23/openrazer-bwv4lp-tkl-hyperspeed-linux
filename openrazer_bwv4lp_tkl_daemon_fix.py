#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


TARGET = Path("/usr/lib/python3/dist-packages/openrazer_daemon/hardware/keyboards.py")


def die(msg: str) -> None:
    print(f"ERREUR: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if not TARGET.exists():
        die(f"Fichier introuvable: {TARGET}")

    s = TARGET.read_text(encoding="utf-8", errors="replace")

    # Fix the broken insertion that resulted in: "USB_PID = 0x02D5class ..."
    s2 = s.replace("USB_PID = 0x02D5class ", "USB_PID = 0x02D5\n\nclass ")
    s2 = s2.replace("USB_PID = 0x02D7class ", "USB_PID = 0x02D7\n\nclass ")

    if s2 == s:
        print("OK: rien à corriger (pattern non trouvé)")
        return

    TARGET.write_text(s2, encoding="utf-8")
    print("OK: keyboards.py réparé (saut de ligne ajouté)")


if __name__ == "__main__":
    main()


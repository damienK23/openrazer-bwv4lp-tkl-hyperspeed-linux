#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


TARGET = Path("/usr/lib/python3/dist-packages/openrazer_daemon/hardware/keyboards.py")


def die(msg: str) -> None:
    print(f"ERREUR: {msg}", file=sys.stderr)
    sys.exit(1)


PATCH_MARKER = "RazerBlackWidowV4LowProfileTenkeylessHyperSpeed"


CLASSES_SNIPPET = r'''

class RazerBlackWidowV4LowProfileTenkeylessHyperSpeedWired(RazerBlackWidowV4TenkeylessHyperSpeedWired):
    """
    Class for the Razer BlackWidow V4 Low-profile Tenkeyless HyperSpeed (Wired)
    """
    # Keep this regex intentionally broad because udev naming differs slightly across distros.
    EVENT_FILE_REGEX = re.compile(r'.*Razer_Razer_BlackWidow_V4_.*Low.*Tenkeyless_HyperSpeed(-if01)?-event-kbd')

    USB_VID = 0x1532
    USB_PID = 0x02D4


class RazerBlackWidowV4LowProfileTenkeylessHyperSpeedWireless(RazerBlackWidowV4LowProfileTenkeylessHyperSpeedWired):
    """
    Class for the Razer BlackWidow V4 Low-profile Tenkeyless HyperSpeed (Wireless / HyperSpeed dongle)
    """
    EVENT_FILE_REGEX = re.compile(r'.*Razer_Razer_BlackWidow_V4_.*Low.*Tenkeyless_HyperSpeed(_\d+)?(-if01)?-event-mouse')
    USB_PID = 0x02D2
'''.lstrip("\n")


def main() -> None:
    if not TARGET.exists():
        die(f"Fichier introuvable: {TARGET}")

    content = TARGET.read_text(encoding="utf-8", errors="replace")
    if PATCH_MARKER in content:
        print("OK: daemon déjà patché (rien à faire)")
        return

    anchor = "class RazerBlackWidowV4TenkeylessHyperSpeedWireless"
    idx = content.find(anchor)
    if idx == -1:
        die("Anchor non trouvé (classes V4 Tenkeyless HyperSpeed). La version du daemon a peut-être changé.")

    # Insert right after the existing V4 TKL HyperSpeed classes block.
    insert_pos = content.find("\n\n", idx)
    if insert_pos == -1:
        insert_pos = idx

    content = content[:insert_pos] + CLASSES_SNIPPET + content[insert_pos:]
    TARGET.write_text(content, encoding="utf-8")
    print("OK: classes clavier ajoutées dans le daemon")


if __name__ == "__main__":
    main()


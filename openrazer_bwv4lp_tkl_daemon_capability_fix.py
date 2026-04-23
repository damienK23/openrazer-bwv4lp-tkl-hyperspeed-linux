#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import sys


TARGET = Path("/usr/lib/python3/dist-packages/openrazer_daemon/hardware/keyboards.py")


def die(msg: str) -> None:
    print(f"ERREUR: {msg}", file=sys.stderr)
    sys.exit(1)


INSERT_MARKER = "# --- OpenRazer local patch: BWV4 LP TKL capabilities ---"


WIRED_CLASS = "class RazerBlackWidowV4LowProfileTenkeylessHyperSpeedWired"


OVERRIDE_BLOCK = r'''
    # --- OpenRazer local patch: BWV4 LP TKL capabilities ---
    # The driver support we added is sufficient for lighting, but some optional
    # sysfs nodes like poll_rate/charge_level might be missing or read-only.
    # Avoid crashing the daemon on startup by skipping poll-rate/battery restore.
    def restore_dpi_poll_rate(self):
        dpi_func = getattr(self, "setDPI", None)
        if dpi_func is not None:
            if self.dpi[0] > self.DPI_MAX:
                self.dpi[0] = self.DPI_MAX
            if self.dpi[1] > self.DPI_MAX:
                self.dpi[1] = self.DPI_MAX
            dpi_func(self.dpi[0], self.dpi[1])

    METHODS = [m for m in RazerBlackWidowV4TenkeylessHyperSpeedWired.METHODS
               if m not in ("get_poll_rate", "set_poll_rate", "get_supported_poll_rates", "get_battery", "is_charging")]
    POLL_RATES = []
'''.lstrip("\n")


def main() -> None:
    if not TARGET.exists():
        die(f"Fichier introuvable: {TARGET}")

    s = TARGET.read_text(encoding="utf-8", errors="replace")
    if INSERT_MARKER in s:
        print("OK: capabilities déjà patchées")
        return

    # Find wired class block start (be tolerant to whitespace / line endings).
    cls_name = "RazerBlackWidowV4LowProfileTenkeylessHyperSpeedWired"
    m = re.search(rf"^\\s*class\\s+{re.escape(cls_name)}\\s*\\(.*\\)\\s*:\\s*(?:\\r?\\n)", s, flags=re.M)
    if not m:
        # Fallback: substring search (helps when line endings / formatting are odd)
        idx = s.find(f"class {cls_name}")
        if idx == -1:
            die("Classe RazerBlackWidowV4LowProfileTenkeylessHyperSpeedWired introuvable (daemon pas patché ?).")
        # locate the end of the class line
        line_end = s.find("\n", idx)
        if line_end == -1:
            die("Fichier keyboards.py inattendu (pas de fin de ligne).")
        start = line_end + 1
    else:
        start = m.end()

    # Insert right after class docstring block end (after the first blank line following it),
    # or if no docstring, after the class line.
    # Find end of docstring (""") if present immediately.
    doc_m = re.search(r'\\A\\s+"""[\\s\\S]*?"""\\s*\\n', s[start:], flags=re.M)
    insert_at = start
    if doc_m:
        insert_at = start + doc_m.end()

    s2 = s[:insert_at] + OVERRIDE_BLOCK + s[insert_at:]
    TARGET.write_text(s2, encoding="utf-8")
    print("OK: capabilities patchées (poll_rate/battery désactivés pour ce clavier)")


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import sys


TARGET = Path("/etc/udev/rules.d/99-razer.rules")


def die(msg: str) -> None:
    print(f"ERREUR: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if not TARGET.exists():
        die(f"Fichier introuvable: {TARGET}")

    s = TARGET.read_text(encoding="utf-8", errors="replace")

    lines = s.splitlines(keepends=True)
    kb_idx = None
    for i, line in enumerate(lines):
        if line.strip() == "# Keyboards":
            kb_idx = i
            break
    if kb_idx is None:
        die("Bloc '# Keyboards' introuvable dans 99-razer.rules")

    prod_idx = None
    for j in range(kb_idx + 1, min(kb_idx + 10, len(lines))):
        if "ATTRS{idProduct}==" in lines[j]:
            prod_idx = j
            break
    if prod_idx is None:
        die("Ligne ATTRS{idProduct}== introuvable après '# Keyboards' (format inattendu).")

    m = re.search(r'ATTRS\{idProduct\}=="([^"]+)"', lines[prod_idx])
    if not m:
        die("Impossible d'extraire la liste idProduct depuis la ligne '# Keyboards'.")

    products = m.group(1).split("|")
    wanted = ["02d2", "02d4"]
    changed = False
    for w in wanted:
        if w not in products:
            products.append(w)
            changed = True

    if not changed:
        print("OK: 02d2/02d4 déjà présents dans la règle udev")
        return

    # Keep deterministic ordering (hex compare)
    products_sorted = sorted(set(products), key=lambda x: int(x, 16))
    new_list = "|".join(products_sorted)

    # Replace in-place only on that line
    lines[prod_idx] = re.sub(r'ATTRS\{idProduct\}=="[^"]+"',
                             f'ATTRS{{idProduct}}=="{new_list}"',
                             lines[prod_idx],
                             count=1)

    TARGET.write_text("".join(lines), encoding="utf-8")
    print("OK: 02d2/02d4 ajoutés à /etc/udev/rules.d/99-razer.rules")


if __name__ == "__main__":
    main()


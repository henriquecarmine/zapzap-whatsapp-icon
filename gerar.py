#!/usr/bin/env python3
"""Builds the tray icon SVG: WhatsApp mark, monochrome, with unread counter.

The counter is drawn in the SAME colour as the mark, with a gap opened in
the bubble behind it — no coloured pill. That is the whole point: on a tray
where every other icon is monochrome, one red blob is the thing your eye
keeps catching.

Digit body shrinks as digits pile up, so "999" occupies the same corner as
"1" and nothing ever leaves the frame.
"""
from pathlib import Path

AQUI = Path(__file__).resolve().parent
MODELO = AQUI / "whatsapp-symbolic-count.svg"
SIMPLES = AQUI / "whatsapp-symbolic.svg"

# Digit body and gap width, by how many digits. Measured by eye at 22 px,
# which is the size that actually matters — a tray icon that only works at
# 256 px is a drawing, not an icon.
TAMANHOS = {
    1: (112, 16),
    2: (88, 14),
}


def icone(quantidade: int = 0, cor: str = "#ffffff") -> str:
    """SVG for `quantidade` unread messages. Zero means the plain mark."""
    if quantidade <= 0:
        return SIMPLES.read_text(encoding="utf-8").replace("#ffffff", cor)

    # Capped at 9+. Rendered at 22 px and looked at: a single digit reads,
    # two digits are tight but legible, three ("999") are a smudge and the
    # gap eats half the bubble. A badge nobody can read is worse than no
    # badge — it costs the mark's legibility and returns nothing.
    texto = str(quantidade) if quantidade <= 9 else "9+"
    corpo, traco = TAMANHOS[len(texto)]

    return (MODELO.read_text(encoding="utf-8")
            .replace("{color}", cor)
            .replace("{number}", texto)
            .replace("{size}", str(corpo))
            .replace("{stroke}", str(traco)))


if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    print(icone(n, sys.argv[2] if len(sys.argv) > 2 else "#ffffff"))

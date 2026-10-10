#!/usr/bin/env python3
"""Maintainer tool: draw the gear icon used by the Settings shortcut -> assets/icons/."""
import math
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "assets" / "icons"
GOLD, DARK = (214, 176, 106, 255), (26, 22, 30, 255)


def gear(size=512, teeth=8):
    s = size * 4  # draw big, shrink down: gives smooth edges
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c, r_out, r_in, r_hub = s / 2, s * 0.46, s * 0.34, s * 0.14
    for i in range(teeth):  # teeth as rounded spokes around the rim
        a = 2 * math.pi * i / teeth
        w = s * 0.085
        pts = []
        for sign in (1, -1):
            for radius in (r_in * 0.9, r_out):
                pts.append((c + radius * math.cos(a) - sign * w * math.sin(a),
                            c + radius * math.sin(a) + sign * w * math.cos(a)))
        d.polygon([pts[0], pts[1], pts[3], pts[2]], fill=GOLD)
    d.ellipse([c - r_in, c - r_in, c + r_in, c + r_in], fill=GOLD)
    d.ellipse([c - r_hub, c - r_hub, c + r_hub, c + r_hub], fill=DARK)   # centre hole
    ring = s * 0.045
    d.ellipse([c - r_in + ring, c - r_in + ring, c + r_in - ring, c + r_in - ring], outline=DARK, width=int(s * 0.012))
    return im.resize((size, size), Image.LANCZOS)


def refresh(size=512):
    """A circular arrow, for the "update now" launcher."""
    s = size * 4
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c, r, w = s / 2, s * 0.32, s * 0.10
    d.arc([c - r, c - r, c + r, c + r], start=-30, end=250, fill=GOLD, width=int(w))
    a = math.radians(-30)                       # where the arc ends
    px, py = c + r * math.cos(a), c + r * math.sin(a)
    tx, ty = -math.sin(a), math.cos(a)          # along the arc
    nx, ny = math.cos(a), math.sin(a)           # out from the centre
    L, W = s * 0.15, s * 0.11
    d.polygon([(px + tx * L, py + ty * L),
               (px - nx * W, py - ny * W),
               (px + nx * W, py + ny * W)], fill=GOLD)
    return im.resize((size, size), Image.LANCZOS)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    for name, im in (("settings", gear(512)), ("update", refresh(512))):
        im.save(OUT / f"{name}.png")
        im.save(OUT / f"{name}.ico", sizes=sizes)
        print("wrote", (OUT / f"{name}.png").name, "and", f"{name}.ico")


if __name__ == "__main__":
    main()

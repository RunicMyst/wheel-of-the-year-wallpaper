"""Draw today's wheel from the prepared layers in assets/wheel (Pillow only, no Inkscape).

Spotlight rules: today's Sabbat, zodiac sign, month (both month rings) and - on the day itself -
solstice/equinox wedge are lit; everything else is gently darkened. Today's moon is brightened
and enlarged, the other moons darkened. Wedge art and centre art are cropped into their shapes.
"""
import json

from PIL import Image, ImageChops, ImageDraw, ImageOps

from .compose import open_photo

# Lit versions of the original fills
LIGHT = {"#1a1a1a": "#4a4a4a", "#4d4d4d": "#8c8c8c", "#5a2ca0": "#8f5fe0",
         "#ff7f2a": "#ffb070", "#0000d4": "#4d6bff", "#00aa44": "#33e07a", "#ffcc00": "#ffe666"}


def _rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def darker(h, f):
    return tuple(int(v * f) for v in _rgb(h))


def lighter(h, f):
    return tuple(int(v + (255 - v) * f) for v in _rgb(h))


def brightness(im, f):
    """Scale an RGBA image's colour (not its transparency) by f."""
    r, g, b, a = im.split()
    r, g, b = (c.point(lambda v: min(255, int(v * f))) for c in (r, g, b))
    return Image.merge("RGBA", (r, g, b, a))


def fade(im, opacity):
    r, g, b, a = im.split()
    return Image.merge("RGBA", (r, g, b, a.point(lambda v: int(v * opacity))))


def slot_symbol(canvas_size, mask, x, y, angle, pic, dim):
    """A symbol fitted inside one of the unnamed Sabbat-ring slots, turned to follow the ring
    (flipped on the bottom half so it isn't upside down), clipped to the slot."""
    full = Image.new("L", canvas_size, 0)
    full.paste(mask, (x, y))
    upright = full.rotate(angle, Image.BICUBIC)  # slot now at 12 o'clock
    box = upright.getbbox()
    bw, bh = box[2] - box[0], box[3] - box[1]
    sym = ImageOps.contain(open_photo(pic, (int(bw), int(bh))).convert("RGBA"), (int(bw * 0.8), int(bh * 0.8)), Image.LANCZOS)
    if 90 < angle < 270:
        sym = sym.rotate(180)
    layer = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    layer.alpha_composite(sym, (box[0] + (bw - sym.width) // 2, box[1] + (bh - sym.height) // 2))
    layer = layer.rotate(-angle, Image.BICUBIC)
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), full))
    return brightness(layer, dim)


def render(assets, st, cfg, wedge_art, centre_art, slot_art=None):
    """Return the wheel as a transparent RGBA image (about 2300 px across)."""
    slot_art = slot_art or {}
    man = json.loads((assets / "manifest.json").read_text(encoding="utf-8"))
    canvas = Image.new("RGBA", tuple(man["size"]), (0, 0, 0, 0))
    look = cfg["look"]
    rings = {"norse": look["norse_ring"], "almanac": look["almanac_ring"]}
    for ring, key in (("zodiac", "zodiac_ring"), ("sabbat", "sabbat_ring")):
        if look.get(key):  # blank = leave that ring the colour it was drawn
            rings[ring] = look[key]
    active = {"sabbat": st.sabbat, "zodiac": st.zodiac, "norse": st.month, "almanac": st.month,
              "wedge": st.season_event, "art": st.month, "sabbat-slot": None}
    layers = man["layers"]
    # South of the equator each Sabbat sits opposite where it is drawn, and the wedges change
    # season, so the prepared southern labels are used and the highlight moves to the other side.
    south = st.hemisphere == "south"
    swapped = man.get("south_labels", {}) if south else {}
    if south:
        from .calendar import OPPOSITE
        active = {k: (OPPOSITE.get(v, v) if k in ("sabbat", "wedge") else v) for k, v in active.items()}

    def load(layer):
        return Image.open(assets / layer["file"])

    # 1. the backing disc, then the coloured segments (and wedge art), in drawing order
    canvas.alpha_composite(Image.open(assets / "under.png"))
    for L in (l for l in layers if l["kind"] == "fill"):
        mask = load(L)
        lit = L["key"] is not None and L["key"] == active[L["ring"]]
        if L["ring"] == "art" and (pic := wedge_art.get(L["key"])):
            piece = ImageOps.fit(open_photo(pic, mask.size).convert("RGBA"), mask.size, Image.LANCZOS)
            if not lit:
                piece = brightness(piece, look["dim"])
            piece.putalpha(ImageChops.multiply(piece.getchannel("A"), mask))
            canvas.alpha_composite(piece, (L["x"], L["y"]))
            continue
        if L["ring"] == "art":
            colour = _rgb(L["fill"])  # plain wedges stay as drawn
        elif L["ring"] in rings:
            colour = lighter(rings[L["ring"]], look["highlight_strength"]) if lit else darker(rings[L["ring"]], 0.75)
        elif lit:
            colour = _rgb(LIGHT.get(L["fill"], L["fill"]))
        else:
            colour = darker(L["fill"], look["wedge_dim"] if L["ring"] == "wedge" else look["dim"])
        solid = Image.new("RGBA", mask.size, colour + (255,))
        solid.putalpha(mask)
        canvas.alpha_composite(solid, (L["x"], L["y"]))
        if L["ring"] == "sabbat-slot" and (pic := slot_art.get(L["key"])):
            canvas.alpha_composite(slot_symbol(canvas.size, mask, L["x"], L["y"], L["angle"], pic, look["dim"]))

    # 2. outlines, dividers and everything else that never changes
    canvas.alpha_composite(Image.open(assets / "over.png"))

    # 3. labels - inactive ones faded. The Old Norse month ring follows [panel] month_names:
    #    "norse" / "modern" swap in a prepared label centred where the drawn one sits; "both" = as drawn.
    style = cfg["panel"]["month_names"]
    swaps = man.get("month_labels", {})
    for L in (l for l in layers if l["kind"] == "label"):
        im, x, y = load(L).convert("RGBA"), L["x"], L["y"]
        if L["id"] in swapped:
            cx, cy = x + L["w"] / 2, y + L["h"] / 2
            im = Image.open(assets / swapped[L["id"]]).convert("RGBA")
            x, y = round(cx - im.width / 2), round(cy - im.height / 2)
        if L["ring"] == "norse" and style in ("norse", "modern") and style in swaps.get(L["key"], {}):
            cx, cy = x + L["w"] / 2, y + L["h"] / 2
            im = Image.open(assets / swaps[L["key"]][style]).convert("RGBA")
            x, y = round(cx - im.width / 2), round(cy - im.height / 2)
        if L["key"] != active[L["ring"]]:
            im = fade(im, look["text_dim"])
        canvas.alpha_composite(im, (x, y))

    # 4. centre: the Vegvísir, or the user's picture cropped to the circle
    for L in (l for l in layers if l["kind"] == "centre"):
        im = load(L).convert("RGBA")
        if centre_art:
            pic = ImageOps.fit(open_photo(centre_art, im.size).convert("RGBA"), im.size, Image.LANCZOS)
            circle = Image.new("L", im.size, 0)
            ImageDraw.Draw(circle).ellipse([0, 0, im.width - 1, im.height - 1], fill=255)
            pic.putalpha(ImageChops.multiply(pic.getchannel("A"), circle))
            im = pic
        canvas.alpha_composite(im, (L["x"], L["y"]))

    # 5. moons: today's one brighter and bigger (drawn last so it sits on top)
    today = f"{st.month}:{st.moon_icon}"
    moons = [l for l in layers if l["kind"] == "moon"]
    for L in sorted(moons, key=lambda l: l["key"] == today):
        im = load(L).convert("RGBA")
        if L["key"] == today:
            s = look["moon_scale"]
            big = brightness(im, look["moon_lift"]).resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
            canvas.alpha_composite(big, (L["x"] - (big.width - im.width) // 2, L["y"] - (big.height - im.height) // 2))
        else:
            canvas.alpha_composite(brightness(im, look["moon_dim"]), (L["x"], L["y"]))
    return canvas

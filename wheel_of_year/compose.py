"""Lay out the final wallpaper: background photo, wheel on one side, info panel in the corner."""
import math
from pathlib import Path

from datetime import datetime

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps, ImageStat

from . import astro, config, folders

FONTS = Path(__file__).resolve().parent.parent / "assets" / "fonts"
Image.MAX_IMAGE_PIXELS = 400_000_000  # someone's 100-megapixel photo isn't an attack


def open_photo(path, want=None):
    """Open a picture, letting JPEGs decode at a reduced size when they're far bigger than
    we need - a 169-megapixel photo would otherwise take ~500 MB of memory to load."""
    im = Image.open(path)
    if want:
        im.draft("RGB", want)
    return ImageOps.exif_transpose(im)


def _font(name, size):
    p = FONTS / name
    return ImageFont.truetype(str(p), size) if p.exists() else ImageFont.load_default(size)


ACCENTS = {   # named colours for [panel] accent - any "#rrggbb" works too
    "oxblood": "#964646", "gold": "#c8a05a", "iron": "#828894",
    "bone": "#bebab0", "forest": "#4a7a55", "night": "#26407f",
}


# A colour for each Sabbat, used when accent = "season". Any of these can be overridden in
# config.toml under [accents].
SEASON_ACCENTS = {
    "Samhain": "oxblood", "Yule": "night", "Imbolc": "bone", "Ostara": "forest",
    "Beltane": "#b5503c", "Litha": "gold", "Lughnasadh": "#c08a3e", "Mabon": "#8c4a2f",
}


def resolve_accent(cfg, st):
    """Turn the accent setting into an actual colour.

    "season" follows the Sabbat, "rotate" changes daily through the named colours, and anything
    else is used as given.
    """
    setting = str(cfg["panel"]["accent"]).strip().lower()
    chosen = dict(cfg.get("accents", {}))
    if setting == "season":
        table = {k.lower(): v for k, v in chosen.items()}
        return table.get(st.sabbat.lower(), SEASON_ACCENTS[st.sabbat])
    if setting == "rotate":
        names = list(ACCENTS)
        return names[st.day.toordinal() % len(names)]
    return setting


def accent_colours(setting):
    """Every colour the panel uses, worked out from one accent colour.

    Text is lightened towards white but pulled back towards the accent, so the colour survives
    at brighter levels instead of fading to cream. A floor keeps every line readable even when
    someone picks a very dark accent.
    """
    name = str(setting).strip().lower()
    value = ACCENTS.get(name, name)
    try:
        base = tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))
    except (ValueError, IndexError):
        base = tuple(int(ACCENTS["oxblood"][i:i + 2], 16) for i in (1, 3, 5))

    def tone(f):
        pale = (c + (255 - c) * f for c in base)
        mixed = [p * 0.55 + b * 0.45 + 30 * f for p, b in zip(pale, base)]
        lum = 0.2126 * mixed[0] + 0.7152 * mixed[1] + 0.0722 * mixed[2]
        floor = 95 + 125 * f
        if lum < floor:
            mixed = [c + (255 - c) * (floor - lum) / (255 - lum) for c in mixed]
        return tuple(min(255, int(c)) for c in mixed)

    return {"border": base + (170,), "rule": base + (100,),
            "date": tone(0.52), "phase": tone(0.74), "pct": tone(0.40), "times": tone(0.34),
            "main": tone(0.66), "sub": tone(0.46), "event": tone(0.30)}


def _clock(t, style="12h"):
    if style == "24h":
        return f"{t.hour:02d}:{t.minute:02d}"
    return f"{t.hour % 12 or 12}:{t.minute:02d} {'AM' if t.hour < 12 else 'PM'}"  # (no %-I on Windows)


def _date_short(d, style):
    """Just the day and month, for the countdown line: "21 December" / "December 21"."""
    return f"{d.day} {d:%B}" if style == "day-first" else f"{d:%B} {d.day}"


def _date(d, style):
    return f"{d:%A} · {d.day} {d:%B} {d.year}" if style == "day-first" else f"{d:%A} · {d:%B} {d.day}, {d.year}"


def sabbat_name(cfg, name):
    """The user's own name for a Sabbat, if they set one (e.g. Lughnasadh = "Lammas")."""
    table = {k.lower(): v for k, v in cfg["sabbat_names"].items()}
    return table.get(name.lower(), name)


def _busyness(im):
    """How much is going on in an image: brightness + detail. Lower = better place for the wheel."""
    g = ImageOps.grayscale(im).resize((160, 90))
    edges = g.filter(ImageFilter.FIND_EDGES)
    return ImageStat.Stat(g).mean[0] + 2 * ImageStat.Stat(edges).mean[0]


def choose_side(photo_path, photo, setting="auto"):
    if setting in ("left", "right"):
        return setting
    forced = folders.side_override(photo_path) if photo_path else None
    if forced:
        return forced
    if photo is None:
        return "right"
    w, h = photo.size
    if w / h < 1.2:  # portrait/square photos sit on the left, the wheel on the right
        return "right"
    left, right = photo.crop((0, 0, w // 2, h)), photo.crop((w // 2, 0, w, h))
    return "left" if _busyness(left) < _busyness(right) else "right"


def _fade_mask(size, fade):
    w, h = size
    mask = Image.new("L", size, 255); d = ImageDraw.Draw(mask)
    for i in range(fade):
        a = int(255 * (i / fade) ** 1.5)
        d.line([(i, 0), (i, h)], fill=a); d.line([(w - 1 - i, 0), (w - 1 - i, h)], fill=a)
    return mask


def background(photo, W, H, side, cfg):
    """Dark base with the photo on it, shaded towards the wheel's side so the wheel stays readable."""
    bg = Image.new("RGB", (W, H), (8, 7, 10))
    if photo is not None:
        photo = ImageEnhance.Brightness(photo.convert("RGB")).enhance(cfg["look"]["photo_brightness"])
        if photo.width / photo.height >= 1.2:  # landscape: fill the screen
            bg = ImageOps.fit(photo, (W, H), Image.LANCZOS)
        else:  # portrait: fit to height on the side away from the wheel, edges faded into the dark
            ph = photo.resize((max(1, int(photo.width * H / photo.height)), H), Image.LANCZOS)
            cx = int(W * (0.27 if side == "right" else 0.73))
            bg.paste(ph, (cx - ph.width // 2, 0), _fade_mask(ph.size, max(40, ph.width // 5)))
    # shade behind the wheel
    shade = Image.linear_gradient("L").rotate(90 if side == "right" else -90).resize((W, H))
    shade = shade.point(lambda v: int(min(255, max(0, (v - 90) * 1.6)) * cfg["look"]["wheel_side_shade"]))
    return Image.composite(Image.new("RGB", (W, H), (6, 5, 8)), bg, shade)


def month_line(st, style):
    """style: "norse", "modern" or "both" (config: [panel] month_names)."""
    month = {"modern": st.month, "both": f"{st.norse_month} ({st.month})"}.get(style, st.norse_month)
    return f"{month}  ·  {st.almanac_moon}"


def panel_lines(st, cfg, place):
    """The panel's contents: (text, style key) in order."""
    p = cfg["panel"]
    lines = [(_date(st.day, p["date_format"]), "date"), (st.moon_phase, "phase")]
    if p["show_illumination"]:
        lines.append((f"{round(st.moon_fraction * 100)}% illuminated", "pct"))
    if p["show_moon_times"] and place:
        lines.append((_times("Moonrise", "Moonset", "moon", st, place, p), "times"))
    if p["show_sun_times"] and place:
        lines.append((_times("Sunrise", "Sunset", "sun", st, place, p), "times"))
    main = sabbat_name(cfg, st.sabbat) + (f"  ·  {st.zodiac}" if p["show_zodiac"] else "")
    lines.append((main, "main"))
    lines.append((month_line(st, p["month_names"]), "sub"))
    if p["show_countdown"]:
        days = st.days_to_next
        when = "tomorrow" if days == 1 else f"in {days} days"
        nxt, on = sabbat_name(cfg, st.next_sabbat), _date_short(st.next_sabbat_start, p["date_format"])
        lines.append(({"date": f"{nxt}  ·  {on}", "both": f"{nxt} {when}  ·  {on}"}
                      .get(p["countdown_style"], f"{nxt} {when}"), "sub"))
    # The day itself, which the countdown above has already moved past.
    if st.festival:
        lines.append((f"{sabbat_name(cfg, st.festival)} today", "event"))
    if st.season_event:
        lines.append((f"{st.season_event}  ·  {_clock(st.season_event_time, p['clock'])}", "event"))
    for text in config.observances(cfg, st.day):
        lines.append((f"◆ {text}", "event"))
    return lines


def _times(rise_word, set_word, body, st, place, p):
    lat, lon, _ = place
    rise, setting = astro.rise_set(body, st.day, lat, lon)   # local time zone, daylight saving and all
    parts = [f"{rise_word} {_clock(rise, p['clock'])}" if rise else f"No {rise_word.lower()}",
             f"{set_word} {_clock(setting, p['clock'])}" if setting else f"No {set_word.lower()}"]
    return "  ·  ".join(parts)


def info_panel(st, scale, cfg, place):
    s = lambda v: int(round(v * scale))
    sizes = {"date": 17, "phase": 21, "pct": 17, "times": 15, "main": 17, "sub": 17, "event": 17}
    bold = {"phase"}
    colours = accent_colours(resolve_accent(cfg, st))
    fonts = {k: _font("DejaVuSerif-Bold.ttf" if k in bold else "DejaVuSerif.ttf", s(v)) for k, v in sizes.items()}
    lines = panel_lines(st, cfg, place)
    pad, icon, gap_after_icon = s(16), s(44), s(10)
    # Lay out: date, then the moon block beside the icon, a rule, then the rest.
    rows, y, rule_y = [], s(14), None
    icon_rows = [i for i, (_, k) in enumerate(lines) if k in ("phase", "pct", "times")]
    for i, (text, k) in enumerate(lines):
        x = pad + (icon + gap_after_icon if k in ("phase", "pct", "times") else 0)
        if i and lines[i - 1][1] in ("phase", "pct", "times") and k not in ("phase", "pct", "times"):
            rule_y = y + s(6)
            y = rule_y + s(8)
        rows.append((x, y, text, k))
        y += s(sizes[k] + 7)
    icon_top = rows[icon_rows[0]][1] if icon_rows else s(46)
    height = y + s(8)
    measure = ImageDraw.Draw(Image.new("L", (1, 1)))
    width = int(max(s(330), max(x + measure.textlength(t, font=fonts[k]) for x, _, t, k in rows) + pad))
    p = Image.new("RGBA", (width, height), (0, 0, 0, 0)); d = ImageDraw.Draw(p)
    d.rounded_rectangle([0, 0, width - 1, height - 1], s(12), fill=(10, 8, 14, 185),
                        outline=colours["border"], width=max(1, s(1)))
    icon_file = {"NM": "NewMoon.png", "WX": "WaxingMoon.png", "FM": "FullMoon.png", "WN": "WanningMoon.png"}[st.moon_icon]
    p.alpha_composite(Image.open(FONTS.parent / "moons" / icon_file).convert("RGBA").resize((icon, icon), Image.LANCZOS),
                      (pad, icon_top))
    if rule_y:
        d.line([(pad, rule_y), (width - pad, rule_y)], fill=colours["rule"], width=max(1, s(1)))
    for x, yy, text, k in rows:
        d.text((x, yy), text, font=fonts[k], fill=colours[k])
    return p


def compose(photo_path, wheel_png, st, cfg, edges=None, place=None):
    edges = edges or {}  # screen space taken by taskbars, in pixels
    W, H = cfg["screen"]["width"], cfg["screen"]["height"]
    scale = H / 1080
    photo = open_photo(photo_path, (W * 2, H * 2)) if photo_path else None
    side = choose_side(photo_path, photo, cfg["look"]["wheel_side"])
    out = background(photo, W, H, side, cfg).convert("RGBA")

    wh = int(H * cfg["look"]["wheel_height"])
    wheel = wheel_png.resize((int(wheel_png.width * wh / wheel_png.height), wh), Image.LANCZOS)
    R = wh / 2
    panel = info_panel(st, scale, cfg, place)
    margin, gap = int(28 * scale), int(70 * scale)
    top, bottom = edges.get("top", 0), edges.get("bottom", 0)
    corner = cfg["panel"]["corner"]
    if corner == "auto":
        corner = ("bottom-right" if side == "right" else "bottom-left")
    vert, horiz = corner.split("-")
    px = (W - edges.get("right", 0) - panel.width - margin) if horiz == "right" else edges.get("left", 0) + margin
    py = (H - bottom - panel.height - margin) if vert == "bottom" else top + margin
    cx = int(W * (0.672 if side == "right" else 0.328)); cy = (top + H - bottom) // 2 - int(20 * scale)

    def too_close(cx):
        # nearest point of the panel rectangle to the wheel centre
        nx = min(max(cx, px), px + panel.width); ny = min(max(cy, py), py + panel.height)
        return math.hypot(nx - cx, ny - cy) < R + gap
    step = -4 if side == "right" else 4
    while too_close(cx) and R < cx < W - R:
        cx += step  # slide the wheel away from the panel; never shrink it

    shadow_a = Image.new("L", (wheel.width + 2 * gap, wheel.height + 2 * gap), 0)
    shadow_a.paste(wheel.getchannel("A"), (gap, gap))
    shadow = Image.new("RGBA", shadow_a.size, (0, 0, 0, 0))
    shadow.putalpha(shadow_a.filter(ImageFilter.GaussianBlur(int(30 * scale))).point(lambda v: int(v * 0.8)))
    out.alpha_composite(shadow, (cx - wheel.width // 2 - gap, cy - wheel.height // 2 - gap))
    out.alpha_composite(wheel, (cx - wheel.width // 2, cy - wheel.height // 2))
    out.alpha_composite(panel, (px, py))
    return out.convert("RGB"), side

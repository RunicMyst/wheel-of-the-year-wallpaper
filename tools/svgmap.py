"""Find the wheel's parts in the Inkscape SVG by their geometry.

The SVG has no meaningful ids, so every shape is located by its fill colour and its distance and
angle from the wheel's centre (angles in degrees, clockwise from 12 o'clock). Distances are
measured relative to the moon-icon ring, so this keeps working if the drawing is rescaled.
Results are cached in build/cache and refreshed whenever the SVG changes.
"""
import difflib
import json
import math
import re
from dataclasses import dataclass, field
from xml.etree import ElementTree as ET

import inkscape

LABEL = "{http://www.inkscape.org/namespaces/inkscape}label"
MONTH_AT = ["November", "December", "January", "February", "March", "April",
            "May", "June", "July", "August", "September", "October"]  # month slot at 0°, 30°, ... clockwise
SABBATS = ["Samhain", "Yule", "Imbolc", "Ostara", "Beltane", "Litha", "Lughnasadh", "Mabon"]
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius",
         "Capricorn", "Aquarius", "Pisces"]
WEDGE_ANGLE = {"Winter Solstice": 45, "Spring Equinox": 135, "Summer Solstice": 225, "Autumn Equinox": 315}
WEDGE_FILLS = {"#ff7f2a", "#0000d4", "#00aa44", "#ffcc00"}


@dataclass
class WheelMap:
    sabbat: dict = field(default_factory=dict)     # name -> {"path": id, "text": id}
    zodiac: dict = field(default_factory=dict)     # sign -> {"path", "text"}
    norse: dict = field(default_factory=dict)      # English month -> {"path", "text"}
    almanac: dict = field(default_factory=dict)    # English month -> {"path", "text"}
    wedges: dict = field(default_factory=dict)     # "Autumn Equinox" -> {"path", "texts": [...]}
    art: dict = field(default_factory=dict)        # English month -> big inner wedge path id
    moons: dict = field(default_factory=dict)      # English month -> {"NM": id, "WX": id, "FM": id, "WN": id}
    other_moons: list = field(default_factory=list)  # moon icons that couldn't be assigned (kept dimmed)
    center: str = ""                                  # the centre (Vegvísir) image id
    fills: dict = field(default_factory=dict)      # path id -> original fill colour


def _fill(el):
    m = re.search(r"fill:(#[0-9a-fA-F]{6})", el.attrib.get("style", ""))
    return m.group(1).lower() if m else None


def _closest(name, options):
    m = difflib.get_close_matches(name.lower(), [o.lower() for o in options], n=1, cutoff=0.6)
    return next(o for o in options if o.lower() == m[0]) if m else None


def _angdist(a, b):
    return abs((a - b + 180) % 360 - 180)


def build_map(svg):
    boxes = inkscape.query_all(svg)
    root = ET.parse(svg).getroot()
    items = []  # (kind, element, id, text/label)
    for el in root.iter():
        tag = el.tag.split("}")[-1]; i = el.attrib.get("id")
        if i in boxes and tag in ("path", "text", "image"):
            text = "".join(el.itertext()).strip() if tag == "text" else el.attrib.get(LABEL, "")
            items.append((tag, el, i, text))

    def center_of(i):
        x, y, w, h = boxes[i]
        return x + w / 2, y + h / 2

    images = [(el, i, t) for k, el, i, t in items if k == "image"]
    sizes = sorted(boxes[i][2] for _, i, _ in images)
    icon = sizes[len(sizes) // 2]  # the 48 moon icons are the common size
    icons = [(el, i, t) for el, i, t in images if abs(boxes[i][2] - icon) < icon * 0.2]
    xs = [center_of(i)[0] for _, i, _ in icons]; ys = [center_of(i)[1] for _, i, _ in icons]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    ring = sum(math.hypot(center_of(i)[0] - cx, center_of(i)[1] - cy) for _, i, _ in icons) / len(icons)

    def polar(i):
        x, y = center_of(i)
        return math.hypot(x - cx, y - cy) / ring, math.degrees(math.atan2(x - cx, -(y - cy))) % 360

    m = WheelMap()
    center = min((i for _, i, _ in images), key=lambda i: polar(i)[0])
    m.center = center
    paths = {"sabbat": [], "zodiac": [], "almanac": [], "norse": [], "wedge": [], "art": []}
    texts = []
    for kind, el, i, t in items:
        r, a = polar(i)
        if kind == "path":
            f = _fill(el)
            if not f: continue
            m.fills[i] = f
            if f in WEDGE_FILLS: paths["wedge"].append((i, a))
            elif f == "#5a2ca0": paths["zodiac"].append((i, a))
            elif f == "#4d4d4d": paths["almanac" if r < 0.86 else "norse"].append((i, a))
            elif f == "#1a1a1a" and 0.68 < r < 0.8: paths["sabbat"].append((i, a))
            elif f == "#1a1a1a" and r < 0.6: paths["art"].append((i, a))
        elif kind == "text":
            texts.append((i, t, r, a))

    def nearest(group, a):
        return min(paths[group], key=lambda p: _angdist(p[1], a))[0] if paths[group] else None

    for i, t, r, a in texts:
        flat = t.replace(" ", "")
        if (s := _closest(flat, [x.upper() for x in SABBATS])) and flat.isupper() and len(flat) <= 10:
            m.sabbat[s.title()] = {"path": nearest("sabbat", a), "text": i}
        elif 0.6 < r < 0.68 and (s := _closest(re.match(r"[A-Z]+", t).group(0) if re.match(r"[A-Z]+", t) else t, [x.upper() for x in SIGNS])):
            m.zodiac[s.title()] = {"path": nearest("zodiac", a), "text": i}
        elif 0.8 < r < 0.86 and "-" not in t:
            month = MONTH_AT[round(a / 30) % 12]
            m.almanac[month] = {"path": nearest("almanac", a), "text": i}
        elif r >= 0.86 and "-" in t:
            month = _closest(t.split("-", 1)[1], MONTH_AT) or MONTH_AT[round(a / 30) % 12]
            m.norse[month] = {"path": nearest("norse", a), "text": i}
    for name, ang in WEDGE_ANGLE.items():
        p = min(paths["wedge"], key=lambda p: _angdist(p[1], ang))[0]
        wt = [i for i, t, r, a in texts if _angdist(a, ang) < 6 and r < 0.8 and not t.isupper()]
        m.wedges[name] = {"path": p, "texts": wt}
    for i, a in paths["art"]:
        m.art[MONTH_AT[round(a / 30) % 12]] = i
    for el, i, t in icons:
        kind = t[:2].upper()
        if kind in ("NM", "WX", "FM", "WN"):
            _, a = polar(i)
            m.moons.setdefault(MONTH_AT[int((a + 15) // 30) % 12], {})[kind] = i
        else:
            m.other_moons.append(i)
    return m


def load(svg, cache_dir):
    """Build (or reuse the cached) map for this SVG."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache = cache_dir / "wheelmap.json"
    stamp = f"{svg.stat().st_mtime_ns}:{svg.stat().st_size}"
    if cache.exists():
        data = json.loads(cache.read_text())
        if data.get("stamp") == stamp:
            return WheelMap(**data["map"])
    m = build_map(svg)
    cache.write_text(json.dumps({"stamp": stamp, "map": m.__dict__}, ensure_ascii=False, indent=1))
    return m

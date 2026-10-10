#!/usr/bin/env python3
"""Maintainer tool: cut the Inkscape SVG into the layers the wallpaper is drawn from.

Run this (from the project folder) only after changing WheelOfTheYear_Page__.svg. It needs
Inkscape; the wallpaper itself then only needs Python + Pillow.

Output: assets/wheel/  - one transparent PNG per recolourable segment, label and moon icon,
        plus under.png / over.png (the fixed parts below and above them), centre.png, and manifest.json describing them.
"""
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import inkscape, svgmap  # noqa: E402  (maintainer-only modules, next to this file)

SVG = ROOT / "WheelOfTheYear_Page__.svg"
RAW = ROOT / "build" / "assets_raw"
OUT = ROOT / "assets" / "wheel"
DPI = 300  # wheel comes out ~2330 px across

# Alternative text for the Old Norse month ring, chosen with [panel] month_names in config.toml.
# ("both" uses the labels exactly as drawn in the SVG.)
MONTH_LABELS = {
    "norse": {"January": "Þorri", "February": "Góa", "March": "Einmánuður", "April": "Harpa", "May": "Skerpla",
              "June": "Sólmánuður", "July": "Heyannir", "August": "Tvímánuður", "September": "Haustmánuður",
              "October": "Gormánuður", "November": "Ýlir", "December": "Mörsugur"},
    "modern": {m: m for m in ["January", "February", "March", "April", "May", "June", "July", "August",
                              "September", "October", "November", "December"]},
}


# Southern hemisphere: the seasons are six months apart, so the Sabbat names swap to the
# opposite side of the wheel and the solstice/equinox wedges change season.
OPPOSITE = {"SAMHAIN": "BELTANE", "BELTANE": "SAMHAIN", "YULE": "LITHA", "LITHA": "YULE",
            "IMBOLC": "LUGHNASADH", "LUGHNASADH": "IMBOLC", "OSTARA": "MABON", "MABON": "OSTARA",
            "Winter": "Summer", "Summer": "Winter", "Spring": "Autumn", "Autumn": "Spring", "Autum": "Spring"}


def export_many(svg, jobs):
    """jobs: [(element id or None for the whole page, output png)] - one Inkscape process."""
    actions = [f"export-dpi:{DPI}", "export-area-page", "export-background-opacity:0", "export-type:png"]
    for eid, png in jobs:
        rel = png.relative_to(ROOT)
        if eid:
            actions += [f"export-id:{eid}", "export-id-only"]
        actions += [f"export-filename:{rel}", "export-do"]
    subprocess.run(inkscape.command() + [str(svg.relative_to(ROOT)), "--actions=" + ";".join(actions)],
                   cwd=ROOT, check=True, capture_output=True)


def main():
    RAW.mkdir(parents=True, exist_ok=True); OUT.mkdir(parents=True, exist_ok=True)
    m = svgmap.build_map(SVG)

    layers = []  # (kind, element id, key, ring)
    for name, e in m.sabbat.items():
        layers += [("fill", e["path"], name, "sabbat"), ("label", e["text"], name, "sabbat")]
    for name, e in m.zodiac.items():
        layers += [("fill", e["path"], name, "zodiac"), ("label", e["text"], name, "zodiac")]
    for month, e in m.norse.items():
        layers += [("fill", e["path"], month, "norse"), ("label", e["text"], month, "norse")]
    for month, e in m.almanac.items():
        layers += [("fill", e["path"], month, "almanac"), ("label", e["text"], month, "almanac")]
    for name, e in m.wedges.items():
        layers += [("fill", e["path"], name, "wedge")] + [("label", t, name, "wedge") for t in e["texts"]]
    for month, pid in m.art.items():
        layers.append(("fill", pid, month, "art"))
    # Sabbat ring slots without a Sabbat name still need their fill (they dim like the rest)
    named = {e["path"] for e in m.sabbat.values()}
    root = ET.parse(SVG).getroot()
    doc_order = {el.attrib.get("id"): n for n, el in enumerate(root.iter())}
    for pid, f in m.fills.items():
        if f == "#1a1a1a" and pid not in named and pid not in m.art.values():
            layers.append(("fill", pid, None, "sabbat"))
    for month, g in m.moons.items():
        for phase, iid in g.items():
            layers.append(("moon", iid, f"{month}:{phase}", "moon"))
    layers += [("moon", i, None, "moon") for i in m.other_moons]
    layers.append(("centre", m.center, None, "centre"))
    layers.sort(key=lambda l: doc_order.get(l[1], 0))

    # The fixed parts, split where the coloured segments sit in the drawing order:
    # "under" (the backing disc drawn before them) and "over" (outlines etc. drawn after them).
    hide = {l[1] for l in layers}
    first_fill = min(doc_order[l[1]] for l in layers if l[0] == "fill")
    leaves = ("path", "text", "image", "use", "circle", "ellipse", "rect", "line", "polyline", "polygon")
    for part, keep in (("under", lambda n: n < first_fill), ("over", lambda n: n > first_fill)):
        tree = ET.parse(SVG)
        for n, el in enumerate(tree.getroot().iter()):
            if el.tag.split("}")[-1] in leaves and (el.attrib.get("id") in hide or not keep(n)):
                el.attrib["style"] = el.attrib.get("style", "") + ";display:none"
        tree.write(RAW / f"{part}.svg", xml_declaration=True, encoding="utf-8")

    jobs = [(l[1], RAW / f"{l[1]}.png") for l in layers]
    print(f"exporting {len(jobs) + 2} layers with Inkscape ...")
    export_many(SVG, jobs)
    for part in ("under", "over"):
        export_many(RAW / f"{part}.svg", [(None, RAW / f"{part}.png")])

    # Crop everything to the wheel and each layer to its own content.
    fixed = {part: Image.open(RAW / f"{part}.png") for part in ("under", "over")}
    box = fixed["over"].getchannel("A").getbbox()
    for l in layers:
        b = Image.open(RAW / f"{l[1]}.png").getchannel("A").getbbox()
        box = (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
    manifest = {"size": [box[2] - box[0], box[3] - box[1]], "layers": []}
    cx, cy = manifest["size"][0] / 2, manifest["size"][1] / 2  # the moon ring is the outer edge, so this is the centre
    spacers = {0: "Samhain-Yule", 60: "Yule-Imbolc", 150: "Ostara-Beltane", 240: "Litha-Lughnasadh"}
    for part, im in fixed.items():
        im.crop(box).save(OUT / f"{part}.png", optimize=True)
    for kind, eid, key, ring in layers:
        im = Image.open(RAW / f"{eid}.png").crop(box)
        b = im.getchannel("A").getbbox()
        im = im.crop(b)
        if kind == "fill":  # only the shape matters; colour is applied at run time
            im = im.getchannel("A")
        name = f"{kind}-{eid}.png"
        im.save(OUT / name, optimize=True)
        angle = math.degrees(math.atan2(b[0] + im.width / 2 - cx, -(b[1] + im.height / 2 - cy))) % 360
        if ring == "sabbat" and key is None:  # the four unnamed Sabbat-ring slots: named by their neighbours
            key = spacers[min(spacers, key=lambda a: abs((angle - a + 180) % 360 - 180))]
            ring = "sabbat-slot"
        manifest["layers"].append({"kind": kind, "id": eid, "key": key, "ring": ring, "file": name,
                                   "x": b[0], "y": b[1], "w": im.width, "h": im.height,
                                   "angle": round(angle, 2), "fill": m.fills.get(eid)})

    # Norse-only / modern-only versions of the month-ring labels: same font, size, angle and outline,
    # just different words. At run time each is centred where the original label sits.
    manifest["month_labels"] = {}
    for style, words in MONTH_LABELS.items():
        tree = ET.parse(SVG)
        byid = {el.attrib.get("id"): el for el in tree.getroot().iter()}
        for month, e in m.norse.items():
            spans = [c for c in byid[e["text"]].iter() if c.tag.endswith("tspan")]
            spans[0].text = words[month]
            for extra in spans[1:]:
                extra.text = ""
        tree.write(RAW / f"months-{style}.svg", xml_declaration=True, encoding="utf-8")
        export_many(RAW / f"months-{style}.svg", [(e["text"], RAW / f"{style}-{e['text']}.png") for e in m.norse.values()])
        for month, e in m.norse.items():
            im = Image.open(RAW / f"{style}-{e['text']}.png").crop(box)
            im = im.crop(im.getchannel("A").getbbox())
            name = f"month-{style}-{e['text']}.png"
            im.save(OUT / name, optimize=True)
            manifest["month_labels"].setdefault(month, {})[style] = name
    # Southern-hemisphere versions of the Sabbat-ring names and the wedge season words.
    tree = ET.parse(SVG)
    byid = {el.attrib.get("id"): el for el in tree.getroot().iter()}
    swap_ids = [e["text"] for e in m.sabbat.values()] + [t for w in m.wedges.values() for t in w["texts"]]
    changed = []
    for tid in swap_ids:
        spans = [c for c in byid[tid].iter() if c.tag.endswith("tspan")]
        if any((c.text or "").strip() in OPPOSITE for c in spans):
            for c in spans:
                c.text = OPPOSITE.get((c.text or "").strip(), c.text)
            changed.append(tid)
    tree.write(RAW / "south.svg", xml_declaration=True, encoding="utf-8")
    export_many(RAW / "south.svg", [(tid, RAW / f"south-{tid}.png") for tid in changed])
    manifest["south_labels"] = {}
    for tid in changed:
        im = Image.open(RAW / f"south-{tid}.png").crop(box)
        im = im.crop(im.getchannel("A").getbbox())
        name = f"south-{tid}.png"
        im.save(OUT / name, optimize=True)
        manifest["south_labels"][tid] = name

    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False))

    # Moon icons for the info panel, and the panel font (DejaVu, free licence) so every system looks the same.
    moons = ROOT / "assets" / "moons"; moons.mkdir(exist_ok=True)
    for f in ("NewMoon.png", "WaxingMoon.png", "FullMoon.png", "WanningMoon.png"):
        shutil.copy2(ROOT / f, moons / f)
    fonts = ROOT / "assets" / "fonts"; fonts.mkdir(exist_ok=True)
    for f in ("DejaVuSerif.ttf", "DejaVuSerif-Bold.ttf"):
        shutil.copy2(Path("/usr/share/fonts/truetype/dejavu") / f, fonts / f)
    shutil.copy2("/usr/share/doc/fonts-dejavu-core/copyright", fonts / "LICENSE-DejaVu.txt")
    print(f"wrote {len(manifest['layers'])} layers to {OUT.relative_to(ROOT)}  size {manifest['size']}")


if __name__ == "__main__":
    main()

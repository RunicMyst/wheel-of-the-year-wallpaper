"""Render today's Wheel of the Year wallpaper and set it on the desktop.

    wheel-of-the-year.py                                   today, and set it as the wallpaper
    wheel-of-the-year.py --date 2026-10-31 --no-set --out samhain.jpg   preview another day
"""
import argparse
import json
import sys
import traceback
from datetime import date, datetime
from pathlib import Path

from . import __version__, calendar, compose, config, desktop, folders, location, wheel

APP = Path(__file__).resolve().parent.parent       # code + assets
# User folders (backgrounds/, wedges/, center/, config.toml) live next to the code in the
# workshop, or one level up in a release (where the code sits in app/).
HOME = APP if (APP / "backgrounds").is_dir() else APP.parent

def load_config():
    cfg, notes = config.load(HOME / "config.toml")
    return cfg


def log(msg):
    (HOME / "build").mkdir(exist_ok=True)
    with open(HOME / "build" / "log.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S}  {msg}\n")
    print(msg)


def run(args):
    cfg, notes = config.load(HOME / "config.toml")
    for note in notes:
        log(f"settings: {note}")
    build = HOME / "build"
    if not args.no_set and not args.out and not desktop.display_ready():
        desktop.wait_for_display()   # at boot we can start before the desktop does
    detected = desktop.screen()
    screen_cache = build / "cache" / "screen.json"
    if detected:
        screen_cache.parent.mkdir(parents=True, exist_ok=True)
        screen_cache.write_text(json.dumps(detected))
    elif screen_cache.exists():  # e.g. running before the desktop is fully up: use the last known screen
        detected = tuple(json.loads(screen_cache.read_text()))
    scale = detected[2] if detected else 1.0
    if args.size:
        w, h = map(int, args.size.lower().split("x"))
    else:
        w = cfg["screen"]["width"] if cfg["screen"]["width"] != "auto" else (detected[0] if detected else 3840)
        h = cfg["screen"]["height"] if cfg["screen"]["height"] != "auto" else (detected[1] if detected else 2160)
    cfg["screen"].update(width=int(w), height=int(h))
    edges = desktop.reserved_edges(scale)
    if detected and (w, h) != tuple(detected[:2]):  # previewing at another size: scale taskbar space too
        edges = {k: int(v * h / detected[1]) for k, v in edges.items()}

    place = location.find(cfg)
    where = location.hemisphere(cfg, place)
    st = calendar.state_for(args.date, hemisphere=where)
    picture_notes = []
    photo = folders.pick(HOME / "backgrounds" / st.sabbat, st.day, HOME / "backgrounds" / "Any", picture_notes)
    art = folders.wedge_art(HOME / "wedges", st.day, picture_notes)
    centre = folders.pick(HOME / "center", st.day, notes=picture_notes)
    slots = folders.slot_art(HOME / "sabbat-ring", st.day, picture_notes)
    for note in picture_notes:
        log(f"pictures: {note}")

    wheel_img = wheel.render(APP / "assets" / "wheel", st, cfg, art, centre, slots)
    image, side = compose.compose(photo, wheel_img, st, cfg, edges, place)

    if args.out:
        out = args.out
    else:
        outdir = build / "wallpaper"; outdir.mkdir(parents=True, exist_ok=True)
        # A new file name every time: desktops (Plasma especially) ignore a picture whose path
        # hasn't changed, so redrawing into the same name would look like nothing happened.
        out = outdir / f"wheel-of-the-year-{st.day.isoformat()}-{datetime.now():%H%M%S}.jpg"
    image.save(out, quality=95)
    log(f"v{__version__}  {st.day}: {st.sabbat} · {st.zodiac} · {st.norse_month}/{st.almanac_moon} · {st.moon_phase} "
        f"{round(st.moon_fraction * 100)}%" + (f" · {st.season_event}" if st.season_event else "")
        + f" | background: {photo.name if photo else 'none (black)'}, wheel {side}, wedge art {len(art)}/12, ring symbols {len(slots)}/4, "
        f"centre {centre.name if centre else 'Vegvísir'} | {w}x{h} | {where}"
        + (f", {location.pretty(place)} ({place[2]})" if place else ", location unknown")
        + f" -> {out}")

    if not args.no_set and not args.out:
        if desktop.set_wallpaper(out):
            log("wallpaper set")
        else:
            log(f"couldn't set the wallpaper automatically on this desktop ({desktop.desktop_name()}); "
                f"the picture is saved at {out}")
        keep = sorted(outdir.glob("wheel-of-the-year-*.jpg"), key=lambda f: f.stat().st_mtime)[:-cfg["output"]["keep"]]
        for f in keep:
            if f != out:
                f.unlink()


def main(argv=None):
    ap = argparse.ArgumentParser(prog="wheel-of-the-year", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", type=date.fromisoformat, default=date.today(), help="render for this day (YYYY-MM-DD)")
    ap.add_argument("--no-set", action="store_true", help="don't change the desktop wallpaper")
    ap.add_argument("--out", type=Path, help="write the image here instead of build/wallpaper/")
    ap.add_argument("--size", help="output size, e.g. 1920x1080 (default: your screen)")
    ap.add_argument("--version", action="version", version=f"Wheel of the Year {__version__}")
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):  # Windows consoles may not handle ·, ð, á: don't crash over it
        if stream is not None and hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")
    try:
        run(args)
    except Exception:
        log("ERROR\n" + traceback.format_exc())
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

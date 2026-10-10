# Wheel of the Year Wallpaper

A KDE Plasma desktop wallpaper built around a Norse-themed Wheel of the Year. It redraws itself
every day to spotlight what is current: the Sabbat, zodiac sign, Old Norse month and almanac
moon, today's moon phase, and — on the day itself — the solstice or equinox. A small panel in
the corner shows the date, moon phase and illumination.

![Example](docs/examples/example-plain-wedges.jpg)

## This folder is the workshop

The ready-to-use copies live in `releases/` — each has its own README:

| Folder | For |
|---|---|
| `releases/Wheel of the Year - Linux/` | Linux (KDE Plasma, GNOME). Install with `./install.sh`. |
| `releases/Wheel of the Year - Windows 10-11/` (+ `.zip` to send) | Windows 10/11 — includes its own Python. |
| _(macOS)_ | Not built yet — waiting for someone with a Mac to test it. |

Everything else here is for making changes:

```bash
./wheel-of-the-year.py --date 2026-10-31 --no-set --out samhain.jpg   # preview any day
python3 tools/make_release.py all        # rebuild the releases after a fix
python3 tools/build_assets.py            # only after editing the SVG (needs Inkscape)
```

`make_release.py` updates the program in an existing release but never touches its pictures
or its `config.toml`, so fixes can be rolled out to a copy that's already in use.

## Make it yours

Everything is driven by folders — add or delete pictures, nothing else to change:

| Folder | What it does |
|---|---|
| `backgrounds/<Sabbat>/` | Background photos for each Sabbat (a different one each day) |
| `wedges/01-January` … `12-December` | Art for the 12 large inner wedges |
| `sabbat-ring/<A-B>/` | Symbols for the four unnamed Sabbat-ring slots |
| `center/` | Replaces the Vegvísir in the centre |

Each folder has its own README. Colours, sizes and dimming live in `config.toml`.

## How it works

- `wheel_of_year/astro.py` — solstices/equinoxes and moon phase (Meeus, *Astronomical Algorithms*)
- `wheel_of_year/calendar.py` — what is active on a given day
- `wheel_of_year/wheel.py` — draws the wheel with spotlight highlighting and art (Pillow only)
- `wheel_of_year/compose.py` — background, wheel placement, info panel
- `wheel_of_year/desktop.py` — screen size, taskbar space, wallpaper + lock screen (Windows, KDE, GNOME)
- `tools/build_assets.py` (+ `svgmap.py`, `inkscape.py`) — cuts the SVG into the layers in `assets/wheel/`
- `tools/make_release.py` — assembles `releases/`

Moon phase icons are clipped from a CC BY-SA 4.0 lunar calendar on Wikimedia Commons
(`Calendario_Lunar_2026.png`).

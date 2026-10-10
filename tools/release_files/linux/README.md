# Wheel of the Year Wallpaper — Linux

**Version @VERSION@**

A desktop wallpaper built around a Norse-themed Wheel of the Year. Every day it redraws itself
to spotlight what is current:

- the **Sabbat** (the most recent one that has begun),
- the **zodiac sign**,
- the **month** — both the Old Norse name and the almanac moon name,
- today's **moon phase** (that moon icon is brighter and larger),
- and, on the day itself, the **solstice or equinox** (its coloured wedge lights up).

A small panel in the corner shows the date, moon phase, how much of the moon is lit, and the
current Sabbat, sign and month.

This sets your **desktop wallpaper** only. The lock screen and login screen are left alone.

![Example](example.jpg)

*The example uses the author's own Samhain altar photo. Your copy starts with empty folders, so
the background is plain black until you add pictures of your own — see "Make it yours" below.*

---

## What you need

- Linux with **KDE Plasma** (fully supported) or **GNOME** (and GNOME-based desktops such as
  Cinnamon or Budgie — should work; the corner panel may need nudging).
- **Python 3.11 or newer** — already installed on nearly every current Linux.
- **Pillow** (Python's picture library):
  - Kubuntu / Ubuntu / Debian / Mint: `sudo apt install python3-pil`
  - Fedora: `sudo dnf install python3-pillow`
  - Arch / Manjaro: `sudo pacman -S python-pillow`

Nothing else — no other programs to install.

**macOS isn't supported yet.** Most of the program would work as it is; what's missing are the
Mac-specific parts (setting the wallpaper, screen size, the daily schedule). If you use a Mac
and would be willing to test it, please open an issue — that's all that's holding it up.

## Install

1. Put this folder wherever you like to keep it (for example in your home folder).
2. Open a terminal **in this folder** (in Dolphin: right-click the folder background →
   *Open Terminal Here*) and run:

   ```bash
   ./install.sh
   ```

That's it. Today's wallpaper appears straight away, and a **"Wheel of the Year" folder** appears
on your desktop holding three shortcuts: **Settings**, **Update Wallpaper Now**, and
**Pictures** (which opens the folders the wallpaper reads). From then on it refreshes every night at
00:01 and shortly after you log in (so it catches up if the computer was off or asleep).

The program runs from this folder — nothing is copied anywhere else. **If you move or rename
this folder, run `./install.sh` again.**

## Make it yours

Everything is controlled by folders — add or delete pictures, nothing else to change:

| Folder | What it does |
|---|---|
| `backgrounds/<Sabbat>/` | The photo behind the wheel. One folder per Sabbat; every photo in it is used, a different one each day. Empty = black background. |
| `backgrounds/Any/` | Photos used whenever a Sabbat's own folder is empty — handy if you just have a few favourites. |
| `wedges/01-January` … `12-December` | A picture for each of the 12 large inner wedges. Empty = plain wedge. |
| `sabbat-ring/` | Symbols for the four unnamed slots in the Sabbat ring (e.g. runes). Empty = plain slot. |
| `center/` | A picture to replace the Vegvísir in the centre. Empty = Vegvísir. |

Each folder has its own short README with details.

Use the **Pictures** shortcut to open the right folders — there is a second copy of them in the
workshop that the wallpaper does not read. After adding pictures, double-click **Update
Wallpaper Now** rather than waiting until tomorrow.

## Settings

Double-click **Settings** in the "Wheel of the Year" folder on your desktop. It opens
`config.toml` in your text editor. Change a value, save, then run `./update-now.sh`.

Nothing you type can break it: if a setting isn't understood, the default is used and a note
appears in `build/log.txt`.

| Setting | What it does |
|---|---|
| `month_names` | Month names on the wheel's outer ring and in the panel: `"norse"` (Haustmánuður), `"modern"` (September) or `"both"` |
| `corner`, `date_format`, `clock` | Where the panel sits, day-first or month-first dates, 12- or 24-hour times |
| `show_countdown` | Adds "Mabon in 3 days" |
| `show_moon_times`, `show_sun_times` | Adds moonrise/moonset and sunrise/sunset times |
| `show_zodiac`, `show_illumination` | Hide those lines if you don't want them |
| `[sabbat_names]` | Your own names in the panel, e.g. `Lughnasadh = "Lammas"` |
| `[dates]` | Your own dates, e.g. `"10-31" = "Ancestor night"` — shown on the day with a ◆ |
| `[location]` | Latitude and longitude for rise/set times. Blank = estimated from your time zone |
| `hemisphere` | `"auto"`, `"north"` or `"south"` (see below) |
| `wheel_side` | `"auto"`, `"left"` or `"right"` |
| `norse_ring`, `almanac_ring`, `zodiac_ring`, `sabbat_ring`, `highlight_strength` | Ring colours and how strongly today's segments light up |
| `dim`, `text_dim`, `moon_dim`, `wheel_height` | Sizes and how strongly the rest is dimmed |

### South of the equator

Set `hemisphere = "south"` (or leave it on `"auto"`, which works it out from your latitude) and
the Sabbats move to where they belong: Samhain at the start of May, Yule at the June solstice,
and so on. The names on the wheel swap to the opposite side to match, and the solstice and
equinox wedges change season. The zodiac, months and moons are the same everywhere, so they
don't move. The almanac moon names (Harvest Moon, Snow Moon) still follow northern seasons,
since they're painted on the wheel.

### Your location

Only moonrise/moonset and sunrise/sunset need it, plus telling north from south. Leave it blank
and it's estimated from your computer's time zone, which is usually within a few minutes.
Nothing is sent anywhere — it's all worked out on your own computer, with no internet needed.

## Preview another day

```bash
./update-now.sh --date 2026-10-31 --no-set --out samhain.jpg
```

This makes a picture for 31 October 2026 without touching your desktop.

## Updating to a newer version

Unpack the new folder over the old one and run `./install.sh` again. Your photos, your settings
(`config.toml`) and your log are kept — only the program inside `app/` is replaced.
`config.default.toml` always shows the current defaults, in case a new setting appears.

## Remove

```bash
./install.sh --remove
```

This stops the daily refresh. Your current wallpaper stays until you pick a different one in
your desktop settings. Then delete this folder if you like.

## Troubleshooting

- **What happened on each run** is written to `build/log.txt` (newest at the bottom). Errors
  are recorded there too — please include it when reporting a problem.
- **The wallpaper didn't change at midnight:** check `systemctl --user status wheel-of-the-year.timer`.
  Run `./install.sh` again if it isn't listed as active.
- **The corner panel is hidden behind a taskbar:** on KDE this is detected automatically. On
  other desktops, set a smaller `wheel_height` or tell us which desktop you use.
- **Blurry background:** the photo is smaller than your screen. Use a bigger photo.

## If something goes wrong

Send `build/log.txt` (it records every run, newest at the bottom) along with what you expected
and what happened instead. The version is at the top of this file and on every line of the log.

## Credits

- Wheel design, Vegvísir and rune ring: the author.
- Moon phase icons: clipped from *Calendario Lunar 2026* on Wikimedia Commons, CC BY-SA 4.0.
- Panel font: DejaVu Serif (free licence, see `app/assets/fonts/LICENSE-DejaVu.txt`).
- Solstice/equinox and moon calculations: Jean Meeus, *Astronomical Algorithms*.

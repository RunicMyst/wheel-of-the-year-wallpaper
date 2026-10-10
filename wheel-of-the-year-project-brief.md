# Wheel of the Year Wallpaper — Project Brief

Handoff document for continuing this project in Claude Code. Written after an extensive
design/build session in claude.ai chat — this captures everything decided so Claude Code
doesn't need to re-derive it.

## The Goal

A desktop wallpaper for Linux (Kubuntu/KDE Plasma) showing a Norse-themed "Wheel of the
Year" — Sabbats, zodiac, seasons, Old Norse + modern months, moon phases — that **regenerates
automatically on a schedule** (via cron) to visually highlight whichever Sabbat, zodiac sign,
month, and moon phase are currently active. Not a live widget — a static image that gets
regenerated periodically and reset as the wallpaper.

Eventually this project will also be published to GitHub, same as an earlier sibling project
(a custom Elder Futhark XKB Linux keyboard layout, published at `github.com/RunicMyst/elder-futhark-xkb`).

## Current Source of Truth

**The user's current working file is an Inkscape `.svg`** (evolved from an original FreeCAD
`.FCStd` → DXF export → SVG export → now hand-edited directly in Inkscape). This SVG is the
real, authoritative source — NOT the original FreeCAD file, which is now an earlier/outdated
stage. Bring the latest `.svg` into Claude Code as the starting point.

The user finds FreeCAD/DXF/QCAD workflows clunky for this kind of 2D graphic design work and
has settled on Inkscape as the tool they're actually building in. FreeCAD may still be used
later for an unrelated *3D physical model* build of this design — that's a separate future
project, not part of the wallpaper automation.

## Design Structure (confirmed, built, and correct)

Working from center outward:

1. **Center circle** — a hand-traced Vegvísir (Icelandic "Viking compass," from the 1860 Huld
   Manuscript — note: NOT actually Viking-Age, it's 19th-century Icelandic folk magic, but
   authentic to modern Norse/heathen practice) surrounded by a ring of the 24 Elder Futhark
   runes. The rune ring was traced by the user using their own verified rune-to-Unicode data
   from the keyboard layout project (see Elder Futhark reference below). Some blank/sparse
   areas remain in this ring that the user still wants to fill in (decorative flourishes or
   small symbols) — not urgent, cosmetic only.

2. **4 colored solstice/equinox wedges** — long, narrow, radially-oriented (text runs outward
   along the spoke, NOT curved around the circumference). Each has a distinct color, purely
   decorative ("wanted some color to help break things up"):
   - Autumn Equinox — orange — "September 22/23"
   - Winter Solstice — blue — "December 21/22"
   - Summer Solstice — yellow — "June 20/21/22"
   - Spring Equinox — green — "March 20/21"

3. **Purple zodiac ring** — 12 wedges, each with the zodiac name + real date range:
   - Aries 21 Mar–19 Apr, Taurus 20 Apr–20 May, Gemini 21 May–20 June, Cancer 21 June–22 July,
     Leo 23 July–22 Aug, Virgo 23 Aug–22 Sept, Libra 23 Sept–22 Oct, Scorpio 23 Oct–21 Nov,
     Sagittarius 22 Nov–21 Dec, Capricorn 22 Dec–19 Jan, Aquarius 20 Jan–18 Feb, Pisces 19 Feb–20 Mar
   - This ring has 12 slots total; 8 are zodiac wedges, 4 are "used" by the colored
     solstice/equinox wedges described above (i.e. the solstice/equinox wedges sit *within*
     this same ring's slot structure, not a separate ring).

4. **Sabbat ring** — 8 Sabbat names, gray, curved around the circumference (NOT radial like
   the solstice/equinox ones): Samhain, Yule, Imbolc, Ostara, Beltane, Litha, Lughnasadh, Mabon.
   Each Sabbat is angularly anchored to align with its corresponding season wedge (Yule aligns
   with Winter Solstice, Ostara with Spring Equinox, Litha with Summer Solstice, Mabon with
   Autumn Equinox; the 4 cross-quarter Sabbats — Imbolc, Beltane, Lughnasadh, Samhain — fall
   exactly halfway between their neighboring anchor points).

5. **Two outer thin rings**, both curved text:
   - Old Norse month names (correct Unicode spelling, confirmed working in Inkscape — no
     placeholder/substitution needed there, unlike the earlier DXF era of this project):
     Gormánuður (Oct), Ýlir (Nov), Mörsugur (Dec), Þorri (Jan), Góa (Feb), Einmánuður (Mar),
     Harpa (Apr), Skerpla (May), Sólmánuður (Jun), Heyannir (Jul), Tvímánuður (Aug),
     Haustmánuður (Sep)
   - Popular English almanac moon names (deliberately kept, NOT swapped to anything else —
     user wants both traditions represented, "to remember ancestors and stay in modern
     times"): Cold Moon (Dec), Wolf Moon (Jan), Snow Moon (Feb), Worm Moon (Mar), Pink Moon
     (Apr), Flower Moon (May), Strawberry Moon (Jun), Buck Moon (Jul), Sturgeon Moon (Aug),
     Harvest Moon (Sep), Beaver Moon (Oct), Hunter's Moon (Nov)

6. **Outermost ring — 48 moon phase icons**, one every 7.5°, cycling New → Waxing → Full →
   Waning, repeated 12 times (one full cycle per month, not tied to real specific calendar
   dates — decorative/symbolic, representing the general lunar cycle). Icons were clipped by
   the user in Inkscape from a real CC BY-SA 4.0 licensed Wikimedia lunar calendar image
   (`Calendario_Lunar_2026.png`), sized ~11.72mm diameter (matching original placeholder dot
   size), RGBA PNGs with real transparency.

## What Does NOT Need Highlighting

The 4 colored solstice/equinox wedges are purely decorative color accents — they do NOT need
date-based highlighting logic. Neither do the still-blank/sparse areas in the center rune
ring. Only these 5 things need "what's currently active" highlighting:
**moon phase, zodiac sign, Sabbat, month (Norse+modern), solstice/equinox.**

## Automation Script Requirements

Build a Python script that:
1. Determines today's date
2. Looks up the current: zodiac sign, Sabbat, month (both Norse+modern), nearest
   solstice/equinox, and moon phase (real astronomical calculation or a reasonable
   approximation)
3. Regenerates the wallpaper with the currently-active item(s) visually highlighted in each
   of those 5 rings (brighter color, glow/outline, or similar — user hasn't specified exact
   highlight style yet, worth asking)
4. Sets the result as the KDE Plasma desktop wallpaper
5. Runs on a schedule via cron (daily is probably sufficient; moon phase changes slowly
   enough that daily regeneration is fine)

Since the current file is SVG (vector, not flattened), the highlight logic can likely target
named/identified shapes directly (e.g. select "the Taurus wedge" as an actual SVG element and
change its fill/stroke) rather than doing raster pixel-region math — cleaner than the
approach fought through earlier in the DXF/PNG era of this project (see "Lessons Learned"
below).

## Reference Data: Elder Futhark Rune Mapping

From the sibling keyboard-layout project — used to build the center rune ring by hand in
Inkscape, and may be useful again for the automation script or for any further rune-related
elements:

| Key | Rune | Name | Unicode |
|---|---|---|---|
| a | ᚨ | Ansuz | U+16A8 |
| b | ᛒ | Berkano | U+16D2 |
| c | ᚦ | Thurisaz | U+16A6 |
| d | ᛞ | Dagaz | U+16DE |
| e | ᛖ | Ehwaz | U+16D6 |
| f | ᚠ | Fehu | U+16A0 |
| g | ᚷ | Gebo | U+16B7 |
| h | ᚺ | Hagalaz | U+16BA |
| i | ᛁ | Isa | U+16C1 |
| j / y | ᛃ | Jera | U+16C3 |
| k | ᚲ | Kenaz | U+16B2 |
| l | ᛚ | Laguz | U+16DA |
| m | ᛗ | Mannaz | U+16D7 |
| n | ᚾ | Nauthiz | U+16BE |
| o | ᛟ | Othala | U+16DF |
| p | ᛈ | Perthro | U+16C8 |
| q | ᛇ | Eihwaz | U+16C7 |
| r | ᚱ | Raidho | U+16B1 |
| s | ᛊ | Sowilo | U+16CA |
| t | ᛏ | Tiwaz | U+16CF |
| u / v | ᚢ | Uruz | U+16A2 |
| w | ᚹ | Wunjo | U+16B9 |
| x | ᛜ | Ingwaz | U+16DC |
| z | ᛉ | Algiz | U+16C9 |

## Art Licensing — What's Still Needed, and Where to Look

**Still needed:** seasonal/nature illustrations for the purple zodiac wedges (matching the
spirit of a commercial Etsy reference image the user liked but can't legally use — nature
imagery like eggs/hares for spring, bees/honey for summer, pumpkins/mushrooms for autumn,
holly/candles for winter), plus possibly some zodiac glyph icons, plus whatever eventually
fills the blank spots in the center rune ring.

**Key lesson learned:** searching by the *modern Sabbat name* (e.g. "Beltane art") mostly
surfaces copyrighted Etsy/Pinterest/stock-photo content, because the 8 Sabbat names are a
20th-century Wiccan framework with no antique art created "for" them historically. **Searching
by each Sabbat's traditional symbol instead works dramatically better** — e.g. search "hare"
for Ostara, "memento mori skull" for Samhain, "holly" for Yule, "hawthorn"/"maypole" for
Beltane, "oak"/"solstice sun" for Litha, "wheat sheaf" for Lughnasadh, "apple"/"harvest" for
Mabon, "snowdrop"/"candle" for Imbolc.

**Trusted sources (all verified working during this session, genuinely free, no paywall
encountered):**
- **Wikimedia Commons** (commons.wikimedia.org) — best source overall; check the
  "Licensing" section on each file page for "public domain" or "CC0"
- **Rawpixel** (rawpixel.com) — filter specifically for their "Free Image from public domain
  license" tag; their site also mixes in modern AI-generated content labeled "generated
  image" — skip those, only use items with a real named artist + date
- **Picture Box Blue** (pictureboxblue.com) — dedicated vintage botanical illustration
  collection, genuinely free

**Explicitly ruled out: Picryl.com.** Despite marketing itself as a "public domain search
engine," real user reviews confirm it gates downloads behind reCaptcha/donation prompts even
for paying subscribers, has a paid tier despite the free-sounding branding, and one review
documents them selling a user's actual copyrighted artwork without permission. Do not use.

**License terms to look for:** "Public Domain" or "CC0" = fully free, no conditions. "CC BY" =
free but needs artist credit. "CC BY-SA" = free with credit, and anything built from it must
be shared under the same license (this covers the moon phase source image, so the eventual
GitHub repo's README should credit it). Avoid anything requiring payment/subscription, and
anything with no license stated at all (assume fully copyrighted).

## Lessons Learned (worth knowing before touching the geometry/rendering pipeline again)

The path to the current working SVG went through a lot of trial and error worth knowing about:

- **FreeCAD's DXF export drops text unless "Use legacy exporter" is checked** in
  Edit → Preferences → Import-Export → DXF. The newer default C++ exporter doesn't
  reliably export TEXT entities.
- **DXF doesn't handle special Unicode characters well** (þ, ð, á, ö, etc. in the Old Norse
  words) — this required an ASCII-placeholder-then-substitute workaround during the DXF era.
  This is a non-issue now that the user works directly in Inkscape (real Unicode support,
  typed/pasted directly).
- **Multiple independent attempts at reconstructing the text layout/rotation programmatically
  (via raw DXF rotation values, via a custom curved-text algorithm, via `ezdxf`'s matplotlib
  rendering backend) all produced incorrect results** — text overlapping, upside-down, or
  scrambled — due to coordinate-system/rotation-convention mismatches between DXF, SVG, and
  the various rendering libraries. **What actually worked:** rendering the FreeCAD SVG export
  directly with `cairosvg` (a proper, transform-aware SVG rasterizer), rather than trying to
  reinterpret the geometry from scratch.
- **For extracting precise coordinates from an SVG with nested group transforms, `svgelements`
  (not `svgpathtools`) correctly composes all nested transforms** — `svgpathtools` was tried
  first and gave wrong (un-transformed) coordinates.
- **The most reliable way to find the 48 moon-dot positions turned out to be direct image
  analysis** (OpenCV `HoughCircles` on the rendered PNG, filtering detected circles by
  consistent distance-from-center) rather than continuing to fight SVG coordinate extraction —
  this gave a clean, verified result (exactly 48 circles, consistent radius, even 7.5° spacing)
  after several SVG-coordinate approaches produced subtly wrong scale/offset values.
- **Net takeaway:** now that the user works directly in Inkscape, most of this pain is
  avoidable — Inkscape's own SVG is clean and can likely be manipulated directly (e.g. with
  a library that understands Inkscape's SVG dialect, or even by having Inkscape itself run
  headless export commands) rather than needing another round of coordinate reverse-engineering.

## File Inventory (as of end of this session)

- Latest Inkscape `.svg` — the current real source of truth (user to provide fresh copy)
- Original FreeCAD `.FCStd` — outdated, kept only for possible future 3D-print project
- 4 clipped moon phase PNGs (New/Waxing/Full/Waning), RGBA, ~350×350px, CC BY-SA 4.0 sourced
- `linux-command-reference.md` — the user's running personal Linux notes doc (separate project,
  may not be relevant to Claude Code but exists in their broader Linux-learning project)

## Immediate Next Steps

1. Get the latest Inkscape SVG into the Claude Code project directory
2. Decide on and implement the highlight visual style (glow, brighter color, outline — ask
   the user)
3. Build the date → current-item lookup logic for the 5 rings that need it
4. Build the SVG regeneration + KDE wallpaper-setting + cron scheduling
5. Continue the art search for the zodiac-wedge seasonal imagery and center-ring blank spots,
   using the symbol-based search strategy and trusted sources above
6. Eventually: publish to GitHub, following the same pattern as the Elder Futhark keyboard
   project (public repo, README with setup instructions, LICENSE file, proper attribution for
   any CC BY-SA sourced assets)

## Background Photos (decided 2026-09-21)

The wallpaper is laid out as a background photo with the wheel made smaller and placed to one
side (not centered), so the photo's subject stays visible.

**User-editable folders are the configuration.** `backgrounds/<Sabbat>/` holds the photos for
each Sabbat. The script reads the current Sabbat's folder at every render, so anyone using the
project can add/delete photos to match their taste — no code or config changes.

- Any number of photos per Sabbat (counts do not need to match); **all** photos are used,
  rotating to a new one each day and cycling through the whole folder.
- Empty folder → plain black background (decided 2026-09-19: no generated fallback).
- Any orientation/format (jpg/jpeg/png/webp). The wheel goes on the darker/emptier side
  automatically; a `_wheel-left` / `_wheel-right` filename suffix overrides it.
- `backgrounds/Sorting file/` is an unsorted inbox (Claude drops found photos there for the
  user to review); never used by the renderer.
- Preferred look: dark, moody, candlelit altar still-lifes with each Sabbat's symbols (the
  user's own Samhain ancestor-altar photo is the reference), plus fog, fire in darkness, aurora.
- Photos are personal and mostly not redistributable: `.gitignore` keeps the folders
  (`.gitkeep`) but excludes the images; `backgrounds/README.md` explains usage.

## Info Panel (decided 2026-09-19)

Moon illumination % is NOT drawn as curved text around the moon ring (would be too small).
Instead a small info panel sits in the corner nearest the wheel, showing exactly what the
wheel currently highlights: date; moon phase name + icon + % illuminated; current Sabbat and
zodiac sign; Norse month and almanac moon name. Mockup: `build/work/panel_mock.py`.

## Highlight Rules (decided 2026-09-19)

- Style: gold glow + brighter fill on each active segment; labels stay on top.
- Sabbat: the most recent Sabbat that has passed (not the nearest).
- Zodiac, Norse month, almanac moon: the ones containing today's date.
- Moon phase: the matching icon (New / Waxing / Full / Waning) within the current month's group.
- Solstice/equinox wedge: lit **only on the actual day** of that year's solstice/equinox
  (computed astronomically each year, local date — it shifts a day or so between years).
  The info panel shows a solstice/equinox line only on that day.

## Wedge & Centre Art (decided 2026-09-19)

User-customisable art, same "folders are the config" rule as backgrounds:
- `wedges/01-January` … `wedges/12-December`: picture fills the big inner wedge under that
  month (0° = November, clockwise, 30° per month), cropped to the wedge via an SVG pattern.
  Multiple pictures rotate daily; empty = plain. Current month's wedge full brightness,
  others dimmed like the rest of the spotlight.
- `center/`: replaces the Vegvísir centre image (`image1-76`), cropped to the circle; empty =
  Vegvísir. Multiple rotate daily.
- Images git-ignored; READMEs in each folder.

## Sabbat-Ring Symbols (decided 2026-09-19)

The Sabbat ring has 12 slots but 8 Sabbats; the four unnamed slots (between Samhain-Yule at the
top, Yule-Imbolc, Ostara-Beltane, Litha-Lughnasadh) get folders `sabbat-ring/<A-B>/`. A picture
is fitted (not cropped) inside the slot, rotated to follow the ring and flipped on the bottom
half so it reads upright; transparency kept. Never highlighted - dimmed with the ring.
Multiple pictures rotate daily; empty = plain.

## Month-Name Option (decided 2026-09-19)

`[panel] month_names` = "norse" | "modern" | "both" controls BOTH the corner panel and the Old
Norse month ring on the wheel. "norse"/"modern" swap in labels pre-rendered by
tools/build_assets.py from the SVG (same Arial Black style/angle, centred on the original);
"both" shows the ring exactly as drawn (e.g. "Haustmánuður-September"). All other wheel text
is unchanged.

## Customisation Round (built 2026-09-20)

All settings live in `config.toml`, opened by a **Settings launcher with a gear icon**
(`Settings.desktop` on Linux / `Settings.lnk` on Windows, both created by the installer;
icon drawn by `tools/make_icon.py` -> `assets/icons/settings.{png,ico}`).
`wheel_of_year/config.py` validates every value: a bad setting falls back to the default and
writes a plain-English note to `build/log.txt` instead of failing.

Added: personal dates (`[dates]`, "MM-DD" or "YYYY-MM-DD", shown with a ◆); countdown to the
next Sabbat; own Sabbat names in the panel (`[sabbat_names]`); `backgrounds/Any/` fallback
folder; zodiac/Sabbat ring colours + `highlight_strength`; panel corner, date format, 12/24h
clock and per-line toggles; `wheel_side` for every photo at once; moonrise/moonset and
sunrise/sunset (Meeus, computed offline) with `[location]` or a position estimated from the
computer's time zone (`assets/timezones.json`, built by `tools/build_timezones.py` from
tz zone.tab + CLDR windowsZones); and `hemisphere = auto|north|south` - southern swaps the
Sabbat dates and shows prepared southern labels (Sabbat names to the opposite side, wedge
seasons swapped). Almanac moon names stay northern (painted on the wheel).

## Future: towards an app release

Not now, but the agreed direction once the folder-based version has been tested:
- **Tray icon** (by the clock, both Windows and KDE) with Settings / Update now / Pause. The
  info panel drawn into the wallpaper can never be clickable - a wallpaper is a flat image -
  so a tray icon is the way to make the settings reachable in place. Today's stand-in is a
  gear shortcut on the desktop, added by the installer.
- With a program already running in the tray, a **screensaver** and a **login-screen**
  version become straightforward follow-ons (the user doesn't need these personally; they are
  for others who might).
- A small **settings window** (dropdowns, colour swatches) instead of editing config.toml -
  only if testers find the text file fiddly. On Windows this adds ~10 MB to the bundle.

## macOS (parked 2026-09-20)

Not built: no tester available (none of the user's Mac contacts would want this wallpaper), and
it can't be tested here the way the Windows build was with Wine. Roughly a day's work when a
tester appears: `desktop.py` backend (wallpaper via AppleScript/`osascript` - fragile on recent
macOS and needs the Automation permission; screen size from `system_profiler`; menu bar + Dock
insets from the Dock's plist), a launchd agent for the daily run, a bundled Python (macOS's own
is too old for `tomllib`), and a small .app wrapper so the gear shortcut can carry an icon.
Lock screen: not possible without admin rights. Both release READMEs now ask for a macOS tester.

## Lock screen removed from this app (2026-09-20)

The lock screen and login screen moved to their own project/session
(`~/Desktop/Witchcraft/Linux Sign-In and Lock Screen/HANDOFF.md`), so `desktop.py` no longer
touches `kscreenlockerrc` and the `[desktop] lock_screen` setting is gone. This app sets the
desktop wallpaper only. Version bumped to 0.9.1.

## Candidates for the next round (not built)

Batched while the user runs v0.9.4 for a month; nothing goes out until it's worth an update.

- **Two-tier Sabbat highlight:** brighter on the Sabbat's own day, a step softer for the rest of
  its stretch, so 31 October stands out from the days either side while the wheel still shows
  which season you are in.
- **`[sabbat_dates]` overrides in config.toml**, e.g. `Samhain = "10-01"`, for traditions that
  begin a Sabbat earlier or keep it over several days.
- **True-shape moon for the highlighted icon.** The ring's 48 icons are a decorative cycle of
  four phases, so the "Full" icon lights about 3 days either side of full (user noticed: icon
  went Full on 23 Sept at 91%, panel only said Full Moon on the 25th-26th). Eight icons per
  month would be 96 round the rim - too small, per the user. Instead: keep the 48, but draw
  *today's* highlighted icon as the moon's actual lit shape (Pillow can draw the terminator),
  leaving the other 47 as they are. No new artwork, no size change.

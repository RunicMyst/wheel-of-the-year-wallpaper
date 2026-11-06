# What's changed

Newest first. Version numbers appear in the zip name, at the top of the README, and on every
line of `build/log.txt`, so you can always tell which copy someone is running.

## 1.0.0 — 5 November 2026

First public release.

- **A Sabbat can now light only on the days it is actually kept.** Set `festival_only = true`
  and Samhain lights on 31 October alone, Yule for the twelve nights, and so on. In between,
  the symbol slot drawn in that gap lights instead — which finally gives the four Sabbat-ring
  symbols something to do, about 170 days of the year. In the four gaps where the wheel has no
  slot drawn, the Sabbat ring simply rests until the next Sabbat arrives. The month ring, moon
  ring, zodiac and inner wedge carry on lighting every day as before.
  Off by default: the wheel keeps working exactly as it did unless you turn this on.
- **How long each Sabbat is kept** is yours to set, under `[festival_days]`. The defaults follow
  how each is actually kept rather than treating them all alike: **Samhain 3 nights** (the
  Gaulish "three nights of Samonios", and the three-day assembly at Tara), **Yule 3 nights**
  (jól as a three-night midwinter feast — the familiar twelve nights are a modern
  reconstruction, so set `Yule = 12` if that is how you keep it), **Litha 3 days** (Midsummer in
  Scandinavia runs about three days around the Eve), and one day each for the rest.
- **Fixed: the panel never said "Samhain today".** On a Sabbat it skipped straight to counting
  down the next one, because the moment a Sabbat arrives it becomes the current one. The day
  itself now gets its own line.
- **The countdown can show the date**, not just the number of days: `countdown_style` takes
  `"days"`, `"date"` (Mabon · 22 September) or `"both"`.
- **Your background photos and the seasonal accent colour are unaffected** by any of this. They
  still follow the Sabbat's whole season, so your Samhain pictures stay up until Yule.

## 0.9.8 — 10 October 2026

- **The panel's colour can now follow the year.** `accent = "season"` gives each Sabbat its own
  colour — oxblood at Samhain, deep blue at Yule, bone at Imbolc, green at Ostara, fire red at
  Beltane, gold at Litha, wheat at Lughnasadh, russet at Mabon. Change any of them under
  `[accents]`. `accent = "rotate"` picks a different named colour each day instead.

## 0.9.7 — 10 October 2026

- **The whole panel now takes its colour from the accent**, not just the border and two lines.
  The text keeps the colour as it brightens instead of fading to cream.
- **"night" is a deeper blue** — the old one was so pale it looked like grey.
- **Very dark accents stay readable**: the dimmer lines are lifted to a minimum brightness.

## 0.9.6 — 10 October 2026

- **The panel's colour is now a setting.** `accent` takes a name — oxblood, gold, iron, bone,
  forest, night — or any colour code you like. It colours the panel's border and the words it
  highlights, and the Settings and Update icons match.
- **The default is now oxblood**, matching the wheel's Norse month ring, instead of gold.

## 0.9.5 — 10 October 2026

- **All the shortcuts now live in one "Wheel of the Year" folder on your desktop** instead of
  three loose icons: Settings, Update Wallpaper Now, and Pictures (which opens the folders the
  wallpaper reads). Older loose icons are tidied away when you install.
- **Added a Pictures shortcut**, so there's no hunting for the right folder.

## 0.9.4 — 26 September 2026

- **Fixed: a crash report after starting the computer.** If the PC was switched on and the
  wallpaper ran before the desktop had finished loading, it asked the system for the screen
  size too early and left a crash report behind. The wallpaper itself was always fine. It now
  waits for the desktop before asking, so nothing crashes.
- **Fixed:** the program could report success when setting the wallpaper had in fact failed.

## 0.9.3 — 23 September 2026

- **Fixed: one bad file could stop the wallpaper updating.** A file that isn't really a picture
  (a phone photo renamed to `.jpg`, or a half-copied download) used to stop the whole thing,
  and the wallpaper would quietly stay on yesterday's. Now it's skipped, the next picture is
  used, and the log says which file was ignored.
- **Fixed: sunrise, sunset, moonrise and moonset were an hour out** around daylight-saving
  changes. (Arizona never sees this; everywhere with clock changes does.)
- **Fixed:** a very large photo (50+ megapixels) used far more memory than it needed to.
- **Added:** a note in the log when a wedge folder is misnamed — `October` instead of
  `10-October` was being ignored silently.

## 0.9.2 — 21 September 2026

- **Fixed: "Update now" appeared to do nothing.** The new picture was drawn correctly, but the
  desktop kept showing the old one because the file name hadn't changed. Each redraw now gets
  its own name.
- **Fixed:** the "Update now" launcher didn't work when the folder path contained spaces.
- **Added: an "Update now" icon** (the arrow) on the desktop and in the folder, so you don't
  need a terminal after adding pictures or changing settings. It shows a brief notification
  when it's done.

## 0.9.1 — 20 September 2026

- **Removed the lock screen feature.** The lock screen and login screen became their own
  project, so this one now only sets the desktop wallpaper.

## 0.9.0 — 20 September 2026

First version given to other people.

- The wheel redraws itself every day and highlights what's current: the Sabbat, zodiac sign,
  Old Norse month, almanac moon name, today's moon phase, and — on the day itself — the
  solstice or equinox.
- A panel in the corner shows the date, moon phase and how much of the moon is lit, plus
  optional moonrise/moonset, sunrise/sunset, a countdown to the next Sabbat, and your own
  dates such as birthdays or anniversaries.
- **Your pictures, your wheel:** folders for background photos (one per Sabbat), art for the
  12 inner wedges, symbols for the 4 unnamed Sabbat-ring slots, and the centre.
- **Settings** in a plain text file with a gear icon to open it. A mistake in it never stops
  the wallpaper: the default is used and the log explains what wasn't understood.
- **North or south of the equator**, worked out from your time zone or set by hand.
- **Windows 10/11 and Linux** (KDE Plasma, GNOME). The Windows copy brings its own Python, so
  there's nothing else to install.

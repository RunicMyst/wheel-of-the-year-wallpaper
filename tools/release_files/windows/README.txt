WHEEL OF THE YEAR WALLPAPER  -  for Windows 10 and 11
=====================================================
Version @VERSION@

A desktop wallpaper built around a Norse-themed Wheel of the Year. Every day it redraws
itself to spotlight what is current:

  - the Sabbat (the most recent one that has begun)
  - the zodiac sign
  - the month - both its Old Norse name and its almanac moon name
  - today's moon phase (that moon is shown brighter and larger)
  - and, on the day itself, the solstice or equinox (its coloured wedge lights up)

A small panel in the corner shows the date, the moon phase, how much of the moon is lit,
and the current Sabbat, sign and month. See "example.jpg" for what it looks like - that one
uses the author's own Samhain altar photo. Your copy starts with empty folders, so your
background is plain black until you add pictures of your own (see MAKE IT YOURS below).

Everything it needs is inside this folder. You don't need to install Python or anything
else, and it never needs administrator rights.


macOS is not supported yet. Most of the program would work as it is; the Mac-specific parts
(setting the wallpaper, screen size, the daily schedule) still need writing and, more to the
point, testing. If you use a Mac and would be willing to test it, please get in touch.


INSTALL
-------
1. Unzip the whole folder somewhere you'll keep it.
   (Right-click the .zip > "Extract All...". Don't run it from inside the zip.)

   A tip: pick a spot that is NOT inside OneDrive. A new picture is made every day, and
   inside OneDrive those would be uploaded over and over. C:\Users\<you>\Pictures or a
   folder on your desktop is ideal.

2. Open the folder and double-click  Install.cmd

   A black window opens for a few seconds, draws today's wallpaper and sets it.
   Press any key to close it. A folder called "Wheel of the Year" appears on your desktop
   with three shortcuts inside: Settings, Update Wallpaper Now, and Pictures (which opens
   the folders the wallpaper reads).

   If Windows shows "Windows protected your PC", click "More info" then "Run anyway".
   This appears for any file downloaded from the internet that isn't from a big company.

That's it. From now on the wallpaper redraws itself every night at 00:01 and whenever you
log in, so it catches up if the computer was off or asleep at midnight.

IMPORTANT: the program runs from this folder. If you move or rename the folder later,
double-click Install.cmd again.


MAKE IT YOURS
-------------
Everything is controlled by folders. Add or delete pictures - there's nothing else to change.

  backgrounds\<Sabbat name>\
      The photo behind the wheel. One folder for each Sabbat. Every photo in it gets used,
      a different one each day. Folders can hold any number of photos.
      Empty folder = black background.

  wedges\01-January ... wedges\12-December
      A picture for each of the 12 large wedges inside the wheel (each sits under that
      month). Empty = plain wedge.

  sabbat-ring\
      Symbols for the four slots in the Sabbat ring that have no Sabbat name - for example
      a rune or a triple moon. Transparent .png pictures look best. Empty = plain slot.

  backgrounds\Any\
      Photos used whenever a Sabbat's own folder is empty - handy if you only have a few
      favourites and don't want to sort them.

  center\
      A picture to replace the Norse compass (Vegvísir) in the middle of the wheel.
      Empty = the compass.

Each folder has its own short README.txt with the details. Pictures can be .jpg, .jpeg,
.png or .webp. For backgrounds, bigger is better - ideally at least as wide as your screen.

After adding pictures you don't have to wait until tomorrow: double-click
"Update Wallpaper Now.cmd".


SETTINGS
--------
Double-click Settings in the "Wheel of the Year" folder on your desktop. It opens the
settings file in Notepad. Change a value, save the file, then double-click "Update Wallpaper Now.cmd".

Nothing you type can break it: if a setting isn't understood, the program uses the default,
carries on, and writes a note in build\log.txt saying what it didn't understand.

  month_names      Month names on the wheel's outer ring and in the panel:
                     "norse"  ->  Haustmánuður
                     "modern" ->  September
                     "both"   ->  Haustmánuður (September)
  corner           Which corner the panel sits in
  date_format      "day-first" (20 September 2026) or "month-first" (September 20, 2026)
  clock            "12h" (3:42 PM) or "24h" (15:42)
  show_countdown   Adds "Mabon in 3 days"
  show_moon_times  Adds "Moonrise 3:42 PM · Moonset 12:11 AM"
  show_sun_times   Adds sunrise and sunset
  show_zodiac, show_illumination
                   Turn those lines off if you don't want them
  [sabbat_names]   Your own names in the panel, e.g.   Lughnasadh = "Lammas"
  [dates]          Your own dates, e.g.   "10-31" = "Ancestor night"
                   They appear on the day with a ◆ in front.
  [location]       Latitude and longitude, only needed for rise and set times. Leave blank
                   and it is estimated from your time zone. Nothing is ever sent anywhere.
  hemisphere       "auto", "north" or "south" - see below
  wheel_side       "auto", "left" or "right"
  norse_ring, almanac_ring, zodiac_ring, sabbat_ring, highlight_strength
                   Ring colours and how strongly today's segments light up
  dim, text_dim, moon_dim, wheel_height
                   Sizes, and how strongly everything that isn't current is dimmed


SOUTH OF THE EQUATOR
--------------------
If you live in Australia, New Zealand, South Africa or South America, set
hemisphere = "south" (or leave it on "auto", which works it out for you). The Sabbats then
fall where they belong - Samhain at the start of May, Yule at the June solstice - and the
names on the wheel swap to the opposite side to match. The zodiac, months and moon phases are
the same everywhere, so they stay put. The moon names (Harvest Moon, Snow Moon) still follow
northern seasons, because they are painted on the wheel.


UPDATING TO A NEWER VERSION
---------------------------
Unzip the new version over the old folder (choose "Replace the files in the destination")
and double-click Install.cmd again. Your photos and your settings are kept - only the program
inside the "app" folder is replaced. The file config.default.toml always shows the current
defaults, in case a new setting has appeared.


REMOVE
------
Double-click  Uninstall.cmd.  The daily refresh stops. Your current wallpaper stays until you
pick another one in Settings > Personalization > Background. Then you can delete this folder.


TROUBLESHOOTING
---------------
* What happened each time it ran is written to  build\log.txt  (newest at the bottom).
  Please send that file along if you report a problem.
* The wallpaper didn't change at midnight: open "Task Scheduler" from the Start menu,
  click "Task Scheduler Library" and look for "Wheel of the Year Wallpaper". If it's
  missing, run Install.cmd again.
* The corner panel is behind the taskbar: this is detected automatically; if it still
  happens, please report it (with build\log.txt).
* Blurry background: that photo is smaller than your screen - use a bigger one.
* Several monitors: the wallpaper is made for your main monitor.
* The lock screen is never changed - this sets the desktop wallpaper only.
* Moonrise/moonset times look wrong: put your exact latitude and longitude in the settings.
  Without them they are estimated from your time zone.


IF SOMETHING GOES WRONG
-----------------------
Send these two things and it can usually be fixed quickly:

  1. build\log.txt   (inside this folder - it records every run, newest at the bottom)
  2. What you expected to happen, and what happened instead.

The version number is at the top of this file and on every line of the log, so it's clear
which copy you have.


CREDITS
-------
Wheel design, Vegvísir and rune ring: the author.
Moon phase icons: clipped from "Calendario Lunar 2026" on Wikimedia Commons, CC BY-SA 4.0.
Panel font: DejaVu Serif (free licence - see app\assets\fonts\LICENSE-DejaVu.txt).
Solstice/equinox and moon calculations: Jean Meeus, "Astronomical Algorithms".
Includes Python (python.org, PSF licence) and Pillow (MIT-CMU licence).

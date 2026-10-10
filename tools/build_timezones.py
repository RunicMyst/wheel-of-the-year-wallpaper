#!/usr/bin/env python3
"""Maintainer tool: build assets/timezones.json - a rough position for each time zone.

Used only when nobody has typed their own latitude/longitude: the wallpaper then estimates the
position from the computer's time zone, which is close enough for moonrise/moonset to the
nearest few minutes, and tells north from south for the Sabbats.

Sources: the tz database's zone.tab (public domain) and CLDR's windowsZones.xml (Unicode
licence) for Windows' own time zone names.
"""
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZONE_TAB = Path("/usr/share/zoneinfo/zone.tab")
CLDR = "https://raw.githubusercontent.com/unicode-org/cldr/main/common/supplemental/windowsZones.xml"


def dms(text):
    """'+3326-11204' -> (33.43, -112.07)"""
    m = re.fullmatch(r"([+-])(\d{2})(\d{2})(\d{2})?([+-])(\d{3})(\d{2})(\d{2})?", text)
    s1, la_d, la_m, la_s, s2, lo_d, lo_m, lo_s = m.groups()
    lat = int(la_d) + int(la_m) / 60 + int(la_s or 0) / 3600
    lon = int(lo_d) + int(lo_m) / 60 + int(lo_s or 0) / 3600
    return round(lat * (-1 if s1 == "-" else 1), 3), round(lon * (-1 if s2 == "-" else 1), 3)


def main():
    zones = {}
    for line in ZONE_TAB.read_text().splitlines():
        if line.startswith("#") or not line.strip():
            continue
        _, coords, name = line.split("\t")[:3]
        zones[name] = dms(coords)

    xml = urllib.request.urlopen(CLDR, timeout=60).read().decode()
    windows = {}
    for m in re.finditer(r'<mapZone other="([^"]+)" territory="([^"]+)" type="([^"]+)"', xml):
        other, territory, types = m.groups()
        if territory == "001":  # the default zone for that Windows name
            first = types.split()[0]
            if first in zones:
                windows[other] = first

    out = ROOT / "assets" / "timezones.json"
    out.write_text(json.dumps({"zones": zones, "windows": windows}, indent=0, sort_keys=True))
    print(f"{len(zones)} time zones, {len(windows)} Windows names -> {out.relative_to(ROOT)} "
          f"({out.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()

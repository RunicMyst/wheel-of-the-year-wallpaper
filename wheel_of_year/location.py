"""Where the computer is: used for moonrise/moonset and for north/south of the equator.

Nothing is ever sent anywhere. Either the person types their latitude and longitude in
config.toml, or we estimate it from the computer's own time zone.
"""
import json
import os
import re
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"


def timezone_name():
    """The computer's time zone, e.g. 'America/Phoenix' - or None."""
    if sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r"SYSTEM\CurrentControlSet\Control\TimeZoneInformation") as k:
                name = winreg.QueryValueEx(k, "TimeZoneKeyName")[0].rstrip("\0")
            table = json.loads((ASSETS / "timezones.json").read_text())
            return table["windows"].get(name)
        except Exception:
            return None
    if (tz := os.environ.get("TZ")) and "/" in tz:
        return tz
    link = Path("/etc/localtime")
    if link.is_symlink() and "zoneinfo/" in (target := os.readlink(link)):
        return target.split("zoneinfo/", 1)[1]
    f = Path("/etc/timezone")
    if f.exists():
        return f.read_text().strip() or None
    return None


def find(cfg):
    """(latitude, longitude, description) or None if we can't work it out."""
    lat, lon = cfg["location"].get("latitude"), cfg["location"].get("longitude")
    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
        return float(lat), float(lon), "from config.toml"
    name = timezone_name()
    if name:
        try:
            zones = json.loads((ASSETS / "timezones.json").read_text())["zones"]
        except OSError:
            return None
        if name in zones:
            lat, lon = zones[name]
            return lat, lon, f"estimated from time zone {name}"
    return None


def hemisphere(cfg, place):
    """"north" or "south" - from the setting, or from the latitude when it is "auto"."""
    setting = str(cfg["look"].get("hemisphere", "auto")).lower()
    if setting in ("north", "south"):
        return setting
    return "south" if place and place[0] < 0 else "north"


def pretty(place):
    lat, lon, _ = place
    return f"{abs(lat):.2f}°{'N' if lat >= 0 else 'S'} {abs(lon):.2f}°{'E' if lon >= 0 else 'W'}"

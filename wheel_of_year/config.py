"""Settings: defaults, reading config.toml, and checking values.

A bad setting never stops the wallpaper: the default is used instead and a plain-English note
goes in the log, e.g.  clock: expected one of 12h, 24h, got "yes" - using "12h".
"""
import re
import tomllib

DEFAULTS = {
    "panel": {
        "month_names": "norse",        # norse | modern | both  (outer ring + panel)
        "accent": "gold",              # a name, "#rrggbb", "season" (follows the Sabbat) or "rotate"
        "corner": "auto",              # auto | top-left | top-right | bottom-left | bottom-right
        "date_format": "day-first",    # day-first | month-first
        "clock": "12h",                # 12h | 24h
        "show_zodiac": True,
        "show_illumination": True,
        "show_countdown": False,       # "Mabon in 3 days"
        "countdown_style": "days",     # days | date | both
        "show_moon_times": False,      # "Moonrise 3:42 PM · Moonset 1:18 AM"
        "show_sun_times": False,
    },
    "sabbat_names": {},                # e.g. Lughnasadh = "Lammas"
    "festival_days": {},               # how long each Sabbat is kept, e.g. Samhain = 3
    "accents": {},                     # per-Sabbat colours when accent = "season"
    "dates": {},                       # e.g. "10-31" = "Ancestor night"
    "location": {"latitude": "", "longitude": ""},
    "look": {
        "festival_only": False,        # light a Sabbat only on the days it is actually kept
        "hemisphere": "auto",          # auto | north | south
        "wheel_side": "auto",          # auto | left | right
        "wheel_height": 0.78,
        "norse_ring": "#6a2c2c", "almanac_ring": "#34466a",
        "zodiac_ring": "", "sabbat_ring": "",   # blank = as drawn
        "highlight_strength": 0.4,
        "dim": 0.55, "text_dim": 0.55, "wedge_dim": 0.6,
        "moon_dim": 0.4, "moon_lift": 1.35, "moon_scale": 1.3,
        "photo_brightness": 0.9, "wheel_side_shade": 0.8,
    },
    "screen": {"width": "auto", "height": "auto"},
    "output": {"keep": 3},
}

CHOICES = {
    ("panel", "month_names"): ["norse", "modern", "both"],
    ("panel", "corner"): ["auto", "top-left", "top-right", "bottom-left", "bottom-right"],
    ("panel", "date_format"): ["day-first", "month-first"],
    ("panel", "clock"): ["12h", "24h"],
    ("panel", "countdown_style"): ["days", "date", "both"],
    ("look", "hemisphere"): ["auto", "north", "south"],
    ("look", "wheel_side"): ["auto", "left", "right"],
}
RANGES = {  # numbers that must stay sensible
    ("look", "wheel_height"): (0.3, 1.0), ("look", "dim"): (0, 2), ("look", "text_dim"): (0, 1),
    ("look", "wedge_dim"): (0, 2), ("look", "moon_dim"): (0, 2), ("look", "moon_lift"): (0.2, 4),
    ("look", "moon_scale"): (0.5, 3), ("look", "photo_brightness"): (0.1, 2),
    ("look", "wheel_side_shade"): (0, 1), ("look", "highlight_strength"): (0, 1),
    ("location", "latitude"): (-90, 90), ("location", "longitude"): (-180, 180),
    ("output", "keep"): (1, 100),
}
COLOURS = [("look", k) for k in ("norse_ring", "almanac_ring", "zodiac_ring", "sabbat_ring")]


def _accent_ok(value):
    from .compose import ACCENTS
    v = str(value).strip().lower()
    return v in ACCENTS or v in ("season", "rotate") or re.fullmatch(r"#[0-9a-f]{6}", v) is not None


def _check(section, key, value, default, notes):
    def bad(why):
        notes.append(f'{key}: {why}, got {value!r} - using {default!r}')
        return default
    if (section, key) == ("panel", "accent"):
        return str(value).strip().lower() if _accent_ok(value) else bad(
            'expected a colour name (oxblood, gold, iron, bone, forest, night), "season", '
            '"rotate" or "#rrggbb"')
    if (section, key) in CHOICES:
        if not isinstance(value, str) or value.lower() not in CHOICES[(section, key)]:
            return bad("expected one of " + ", ".join(CHOICES[(section, key)]))
        return value.lower()
    if (section, key) in COLOURS:
        if value in ("", None):
            return ""
        if not (isinstance(value, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", value)):
            return bad('expected a colour like "#6a2c2c"')
        return value.lower()
    if isinstance(default, bool):
        return value if isinstance(value, bool) else bad("expected true or false")
    if (section, key) in RANGES:
        lo, hi = RANGES[(section, key)]
        if value in ("", None) and default == "":
            return ""
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return bad("expected a number")
        if not lo <= value <= hi:
            return bad(f"expected a number between {lo} and {hi}")
        return value
    if key in ("width", "height"):
        if value == "auto" or (isinstance(value, int) and 320 <= value <= 20000):
            return value
        return bad('expected "auto" or a screen size like 1920')
    return value


def load(path):
    """(settings, notes) - notes are plain-English problems worth showing the user."""
    cfg = {k: dict(v) for k, v in DEFAULTS.items()}
    notes = []
    if not path.exists():
        return cfg, notes
    try:
        # utf-8-sig: Notepad on Windows may save the file with a byte-order mark
        raw = tomllib.loads(path.read_text(encoding="utf-8-sig"))
    except (tomllib.TOMLDecodeError, OSError) as e:
        return cfg, [f"couldn't read config.toml ({e}) - using all the default settings"]
    for section, values in raw.items():
        if section not in cfg:
            notes.append(f"[{section}]: not a known section - ignored")
            continue
        if section == "festival_days":
            from .calendar import FESTIVAL_DAYS
            for key, value in values.items():
                name = str(key).strip().capitalize()
                if name not in FESTIVAL_DAYS:
                    notes.append(f"[festival_days] {key}: not a Sabbat name - ignored")
                elif isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 120:
                    notes.append(f"[festival_days] {key}: expected a whole number of days between "
                                 f"1 and 120, got {value!r} - ignored")
                else:
                    cfg[section][name] = value
            continue
        if section in ("dates", "sabbat_names", "accents"):  # free-form tables
            cfg[section].update({str(k): str(v) for k, v in values.items()})
            continue
        for key, value in values.items():
            if key not in cfg[section]:
                notes.append(f"{key}: not a known setting - ignored")
                continue
            cfg[section][key] = _check(section, key, value, DEFAULTS[section][key], notes)
    return cfg, notes


def observances(cfg, day):
    """Personal dates falling on `day`: ["Grandma Ruth's birthday", ...].

    Keys are "MM-DD" (every year) or "YYYY-MM-DD" (once).
    """
    out = []
    for key, text in cfg["dates"].items():
        k = key.strip()
        if re.fullmatch(r"\d{2}-\d{2}", k) and k == day.strftime("%m-%d"):
            out.append(text)
        elif re.fullmatch(r"\d{4}-\d{2}-\d{2}", k) and k == day.isoformat():
            out.append(text)
    return out

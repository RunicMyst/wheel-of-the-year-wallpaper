"""What is active on a given day: Sabbat, zodiac sign, month, moon phase, solstice/equinox."""
from dataclasses import dataclass
from datetime import date, datetime, time

from . import astro

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]
NORSE = ["Þorri", "Góa", "Einmánuður", "Harpa", "Skerpla", "Sólmánuður", "Heyannir", "Tvímánuður",
         "Haustmánuður", "Gormánuður", "Ýlir", "Mörsugur"]
ALMANAC = ["Wolf Moon", "Snow Moon", "Worm Moon", "Pink Moon", "Flower Moon", "Strawberry Moon", "Buck Moon",
           "Sturgeon Moon", "Harvest Moon", "Hunter's Moon", "Beaver Moon", "Cold Moon"]

# (sign, start month, start day) - each sign runs until the next one starts
ZODIAC = [("Capricorn", 1, 1), ("Aquarius", 1, 20), ("Pisces", 2, 19), ("Aries", 3, 21), ("Taurus", 4, 20),
          ("Gemini", 5, 21), ("Cancer", 6, 21), ("Leo", 7, 23), ("Virgo", 8, 23), ("Libra", 9, 23),
          ("Scorpio", 10, 23), ("Sagittarius", 11, 22), ("Capricorn", 12, 22)]

# Solar Sabbats start on that year's actual solstice/equinox; the cross-quarter days are fixed.
# South of the equator the seasons are six months apart, so both tables flip.
SOLAR = {"north": {"Ostara": "march", "Litha": "june", "Mabon": "september", "Yule": "december"},
         "south": {"Mabon": "march", "Yule": "june", "Ostara": "september", "Litha": "december"}}
FIXED = {"north": {"Imbolc": (2, 1), "Beltane": (5, 1), "Lughnasadh": (8, 1), "Samhain": (10, 31)},
         "south": {"Lughnasadh": (2, 1), "Samhain": (5, 1), "Imbolc": (8, 1), "Beltane": (11, 1)}}
SEASON_WEDGE = {"north": {"march": "Spring Equinox", "june": "Summer Solstice",
                          "september": "Autumn Equinox", "december": "Winter Solstice"},
                "south": {"march": "Autumn Equinox", "june": "Winter Solstice",
                          "september": "Spring Equinox", "december": "Summer Solstice"}}
# How many days each Sabbat is actually kept, counting from its own date. Settings override any.
#   Samhain 3 - the Gaulish calendar's "three nights of Samonios", and the three-day assembly
#               at Tara in the medieval Irish sources. Sunset 31 Oct to sunset 2 Nov.
#   Yule 3    - jol as a three-night midwinter feast (Jackson Crawford). The familiar twelve
#               nights are a modern reconstruction: set Yule = 12 if you keep it that way.
#   Litha 3   - Midsummer in Scandinavia is kept over about three days around the Eve.
#   The rest are single days: Imbolc and Beltane begin at sunset on the eve and run one day,
#   Lughnasadh is 1 August, and Ostara and Mabon are the equinoxes themselves.
FESTIVAL_DAYS = {"Samhain": 3, "Yule": 3, "Imbolc": 1, "Ostara": 1,
                 "Beltane": 1, "Litha": 3, "Lughnasadh": 1, "Mabon": 1}

# The four unnamed Sabbat-ring slots, each drawn in the gap between two Sabbats. The other four
# pairs sit side by side with nothing between them, so in those stretches the ring simply rests.
BETWEEN = {("Samhain", "Yule"): "Samhain-Yule", ("Yule", "Imbolc"): "Yule-Imbolc",
           ("Ostara", "Beltane"): "Ostara-Beltane", ("Litha", "Lughnasadh"): "Litha-Lughnasadh"}

OPPOSITE = {"Samhain": "Beltane", "Beltane": "Samhain", "Yule": "Litha", "Litha": "Yule",
            "Imbolc": "Lughnasadh", "Lughnasadh": "Imbolc", "Ostara": "Mabon", "Mabon": "Ostara",
            "Spring Equinox": "Autumn Equinox", "Autumn Equinox": "Spring Equinox",
            "Summer Solstice": "Winter Solstice", "Winter Solstice": "Summer Solstice"}


@dataclass
class DayState:
    day: date
    hemisphere: str
    sabbat: str
    sabbat_start: date
    next_sabbat: str
    next_sabbat_start: date
    zodiac: str
    month: str
    norse_month: str
    almanac_moon: str
    moon_fraction: float    # 0..1 illuminated
    moon_elongation: float  # degrees, 0 = new
    moon_phase: str         # e.g. "Waxing Gibbous"
    moon_icon: str          # NM / WX / FM / WN
    season_event: str | None  # e.g. "Autumn Equinox" only on the actual day
    season_event_time: datetime | None
    festival: str | None = None    # the Sabbat actually being kept today, else None
    gap: tuple | None = None       # (Sabbat just gone, Sabbat coming) while none is being kept

    @property
    def days_to_next(self):
        return (self.next_sabbat_start - self.day).days


def local_date(dt_utc):
    return dt_utc.astimezone().date()


def sabbat_dates(year, hemisphere="north"):
    out = {name: date(year, m, d) for name, (m, d) in FIXED[hemisphere].items()}
    out.update({name: local_date(astro.season_start(year, which)) for name, which in SOLAR[hemisphere].items()})
    return out


def state_for(day, moon_at=None, hemisphere="north", festival_days=None):
    """Everything the wallpaper shows for local date `day`.

    The moon phase is taken at `moon_at` (a local datetime; defaults to noon of `day`).
    `festival_days` overrides how long individual Sabbats are kept (see FESTIVAL_DAYS).
    """
    events = sorted((d, n) for y in (day.year - 1, day.year, day.year + 1)
                    for n, d in sabbat_dates(y, hemisphere).items())
    past = [e for e in events if e[0] <= day]
    future = [e for e in events if e[0] > day]
    sabbat_start, sabbat = past[-1]
    next_start, next_sabbat = future[0]

    zodiac = [s for s, m, d in ZODIAC if (day.month, day.day) >= (m, d)][-1]

    moon_at = moon_at or datetime.combine(day, time(12)).astimezone()
    frac, elong, _ = astro.moon_phase(moon_at)

    season_event = season_time = None
    for which, label in SEASON_WEDGE[hemisphere].items():
        t = astro.season_start(day.year, which)
        if local_date(t) == day:
            season_event, season_time = label, t.astimezone()

    # Which Sabbat is actually being kept today, as against whose season we are in. The season
    # still decides the background folder and the panel's accent; only the ring uses these two.
    kept = (festival_days or {}).get(sabbat) or FESTIVAL_DAYS.get(sabbat, 1)
    festival = sabbat if (day - sabbat_start).days < kept else None
    gap = None if festival else (sabbat, next_sabbat)

    i = day.month - 1
    return DayState(day, hemisphere, sabbat, sabbat_start, next_sabbat, next_start, zodiac, MONTHS[i], NORSE[i], ALMANAC[i],
                    frac, elong, astro.phase_name(elong), astro.phase_icon(elong), season_event, season_time,
                    festival, gap)

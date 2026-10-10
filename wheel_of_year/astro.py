"""Astronomy: solstices/equinoxes and moon phase.

Formulas from Jean Meeus, *Astronomical Algorithms* (2nd ed.):
  - ch. 27 (equinoxes & solstices, accurate to about a minute for years 1000-3000)
  - ch. 47/48 (moon position and illuminated fraction, accurate to well under 1%)
No third-party packages needed.
"""
import math
from datetime import datetime, timedelta, timezone

J2000 = 2451545.0
DELTA_T = timedelta(seconds=69)  # TT - UTC, close enough for this century


def jd_to_datetime(jd):
    """Julian Day -> aware UTC datetime."""
    return datetime(2000, 1, 1, 12, tzinfo=timezone.utc) + timedelta(days=jd - J2000)


def datetime_to_jd(dt):
    return J2000 + (dt.astimezone(timezone.utc) - datetime(2000, 1, 1, 12, tzinfo=timezone.utc)).total_seconds() / 86400


# ---------------------------------------------------------------- equinoxes & solstices (Meeus ch. 27)

_MEAN = {  # Table 27.B, years 2000-3000: JDE0 = a + b*Y + c*Y^2 + d*Y^3 + e*Y^4, Y = (year-2000)/1000
    "march":     (2451623.80984, 365242.37404, 0.05169, -0.00411, -0.00057),
    "june":      (2451716.56767, 365241.62603, 0.00325, 0.00888, -0.00030),
    "september": (2451810.21715, 365242.01767, -0.11575, 0.00337, 0.00078),
    "december":  (2451900.05952, 365242.74049, -0.06223, -0.00823, 0.00032),
}
_PERIODIC = [  # Table 27.C: A, B (deg), C (deg/century)
    (485, 324.96, 1934.136), (203, 337.23, 32964.467), (199, 342.08, 20.186), (182, 27.85, 445267.112),
    (156, 73.14, 45036.886), (136, 171.52, 22518.443), (77, 222.54, 65928.934), (74, 296.72, 3034.906),
    (70, 243.58, 9037.513), (58, 119.81, 33718.147), (52, 297.17, 150.678), (50, 21.02, 2281.226),
    (45, 247.54, 29929.562), (44, 325.15, 31555.956), (29, 60.93, 4443.417), (18, 155.12, 67555.328),
    (17, 288.79, 4562.452), (16, 198.04, 62894.029), (14, 199.76, 31436.921), (12, 95.39, 14577.848),
    (12, 287.11, 31931.756), (12, 320.81, 34777.259), (9, 227.73, 1222.114), (8, 15.45, 16859.074),
]


def season_start(year, which):
    """UTC datetime of the March/June equinox-solstice etc. `which` in _MEAN."""
    y = (year - 2000) / 1000
    a, b, c, d, e = _MEAN[which]
    jde0 = a + b * y + c * y ** 2 + d * y ** 3 + e * y ** 4
    t = (jde0 - J2000) / 36525
    w = math.radians(35999.373 * t - 2.47)
    dl = 1 + 0.0334 * math.cos(w) + 0.0007 * math.cos(2 * w)
    s = sum(A * math.cos(math.radians(B + C * t)) for A, B, C in _PERIODIC)
    return jd_to_datetime(jde0 + 0.00001 * s / dl) - DELTA_T


# ---------------------------------------------------------------- moon (Meeus ch. 47/48)

def _moon_angles(dt):
    t = (datetime_to_jd(dt) + DELTA_T.total_seconds() / 86400 - J2000) / 36525
    D = 297.8501921 + 445267.1114034 * t - 0.0018819 * t ** 2 + t ** 3 / 545868 - t ** 4 / 113065000
    M = 357.5291092 + 35999.0502909 * t - 0.0001536 * t ** 2 + t ** 3 / 24490000
    Mp = 134.9633964 + 477198.8675055 * t + 0.0087414 * t ** 2 + t ** 3 / 69699 - t ** 4 / 14712000
    return D % 360, M % 360, Mp % 360


def moon_phase(dt):
    """Return (illuminated_fraction 0..1, elongation_deg 0..360, waxing: bool).

    Elongation 0 = new moon, 90 = first quarter, 180 = full, 270 = last quarter.
    """
    D, M, Mp = _moon_angles(dt)
    r = math.radians
    i = (180 - D - 6.289 * math.sin(r(Mp)) + 2.100 * math.sin(r(M)) - 1.274 * math.sin(r(2 * D - Mp))
         - 0.658 * math.sin(r(2 * D)) - 0.214 * math.sin(r(2 * Mp)) - 0.110 * math.sin(r(D)))
    k = (1 + math.cos(r(i))) / 2
    elong = (180 - i) % 360
    return k, elong, elong < 180


PHASE_NAMES = [  # (upper elongation bound, name) - the 4 principal phases get a ~±1 day window
    (12, "New Moon"), (78, "Waxing Crescent"), (102, "First Quarter"), (168, "Waxing Gibbous"),
    (192, "Full Moon"), (258, "Waning Gibbous"), (282, "Last Quarter"), (348, "Waning Crescent"), (360, "New Moon"),
]


def phase_name(elong):
    return next(n for lim, n in PHASE_NAMES if elong < lim)


def phase_icon(elong):
    """Which of the wheel's 4 moon icons matches: NM, WX, FM or WN."""
    return "NM" if elong < 45 or elong >= 315 else "WX" if elong < 135 else "FM" if elong < 225 else "WN"


# ---------------------------------------------------------------- moon & sun position, rise and set

# Meeus table 47.A (largest terms): D, M, M', F, coefficient for longitude (1e-6 deg)
_LON = [
    (0, 0, 1, 0, 6288774), (2, 0, -1, 0, 1274027), (2, 0, 0, 0, 658314), (0, 0, 2, 0, 213618),
    (0, 1, 0, 0, -185116), (0, 0, 0, 2, -114332), (2, 0, -2, 0, 58793), (2, -1, -1, 0, 57066),
    (2, 0, 1, 0, 53322), (2, -1, 0, 0, 45758), (0, 1, -1, 0, -40923), (1, 0, 0, 0, -34720),
    (0, 1, 1, 0, -30383), (2, 0, 0, -2, 15327), (0, 0, 1, 2, -12528), (0, 0, 1, -2, 10980),
    (4, 0, -1, 0, 10675), (0, 0, 3, 0, 10034), (4, 0, -2, 0, 8548), (2, 1, -1, 0, -7888),
    (2, 1, 0, 0, -6766), (1, 0, -1, 0, -5163), (1, 1, 0, 0, 4987), (2, -1, 1, 0, 4036),
    (2, 0, 2, 0, 3994), (4, 0, 0, 0, 3861), (2, 0, -3, 0, 3665),
]
# Meeus table 47.B: coefficient for latitude (1e-6 deg)
_LAT = [
    (0, 0, 0, 1, 5128122), (0, 0, 1, 1, 280602), (0, 0, 1, -1, 277693), (2, 0, 0, -1, 173237),
    (2, 0, -1, 1, 55413), (2, 0, -1, -1, 46271), (2, 0, 0, 1, 32573), (0, 0, 2, 1, 17198),
    (2, 0, 1, -1, 9266), (0, 0, 2, -1, 8822), (2, -1, 0, -1, 8216), (2, 0, -2, -1, 4324),
    (2, 0, 1, 1, 4200), (2, 1, 0, -1, -3359), (2, -1, -1, 1, 2463), (2, -1, 0, 1, 2211),
    (2, -1, -1, -1, 2065), (0, 1, -1, -1, -1870), (4, 0, -1, -1, 1828), (0, 1, 0, 1, -1794),
]


def _centuries(dt):
    return (datetime_to_jd(dt) + DELTA_T.total_seconds() / 86400 - J2000) / 36525


def moon_equatorial(dt):
    """(right ascension, declination) of the moon in degrees."""
    t = _centuries(dt)
    r = math.radians
    Lp = 218.3164477 + 481267.88123421 * t - 0.0015786 * t ** 2 + t ** 3 / 538841 - t ** 4 / 65194000
    D = 297.8501921 + 445267.1114034 * t - 0.0018819 * t ** 2 + t ** 3 / 545868
    M = 357.5291092 + 35999.0502909 * t - 0.0001536 * t ** 2
    Mp = 134.9633964 + 477198.8675055 * t + 0.0087414 * t ** 2 + t ** 3 / 69699
    F = 93.2720950 + 483202.0175233 * t - 0.0036539 * t ** 2 - t ** 3 / 3526000
    E = 1 - 0.002516 * t - 0.0000074 * t ** 2  # correction for terms involving the sun
    def total(table):
        s = 0.0
        for d, m, mp, f, c in table:
            s += c * (E ** abs(m)) * math.sin(r(d * D + m * M + mp * Mp + f * F))
        return s / 1e6
    lon, lat = Lp + total(_LON), total(_LAT)
    eps = 23.439291 - 0.0130042 * t
    sl, cl, sb, cb, se, ce = math.sin(r(lon)), math.cos(r(lon)), math.sin(r(lat)), math.cos(r(lat)), math.sin(r(eps)), math.cos(r(eps))
    ra = math.degrees(math.atan2(sl * ce - (sb / cb) * se, cl)) % 360
    dec = math.degrees(math.asin(sb * ce + cb * se * sl))
    return ra, dec


def sun_equatorial(dt):
    """(right ascension, declination) of the sun in degrees (Meeus ch. 25, low precision)."""
    t = _centuries(dt)
    r = math.radians
    L0 = 280.46646 + 36000.76983 * t
    M = 357.52911 + 35999.05029 * t
    c = ((1.914602 - 0.004817 * t) * math.sin(r(M)) + (0.019993 - 0.000101 * t) * math.sin(r(2 * M))
         + 0.000289 * math.sin(r(3 * M)))
    lon = L0 + c
    eps = 23.439291 - 0.0130042 * t
    ra = math.degrees(math.atan2(math.cos(r(eps)) * math.sin(r(lon)), math.cos(r(lon)))) % 360
    dec = math.degrees(math.asin(math.sin(r(eps)) * math.sin(r(lon))))
    return ra, dec


def _gmst(dt):
    """Greenwich mean sidereal time in degrees."""
    jd = datetime_to_jd(dt)
    t = (jd - J2000) / 36525
    return (280.46061837 + 360.98564736629 * (jd - J2000) + 0.000387933 * t ** 2 - t ** 3 / 38710000) % 360


def altitude(ra, dec, lat, lon, dt):
    """Altitude of an object above the horizon, in degrees (lon: east positive)."""
    h = math.radians((_gmst(dt) + lon - ra) % 360)
    la, de = math.radians(lat), math.radians(dec)
    return math.degrees(math.asin(math.sin(la) * math.sin(de) + math.cos(la) * math.cos(de) * math.cos(h)))


def rise_set(body, day, lat, lon, tz=None):
    """(rise, set) as local datetimes on local date `day`, or None where it doesn't happen.

    body: "moon" or "sun". Steps through the day and refines each horizon crossing; accurate to
    about a minute, which is all the panel shows. Times are stepped in UTC and converted back
    afterwards, so a daylight-saving change during the day is handled by the system's own rules.
    """
    horizon = 0.125 if body == "moon" else -0.833  # moon: semidiameter + parallax; sun: refraction
    equatorial = moon_equatorial if body == "moon" else sun_equatorial
    midnight = datetime(day.year, day.month, day.day)          # naive: local midnight that date
    start = (midnight.replace(tzinfo=tz) if tz else midnight.astimezone()).astimezone(timezone.utc)
    step = timedelta(minutes=10)

    def alt(t):
        ra, dec = equatorial(t)
        return altitude(ra, dec, lat, lon, t) - horizon

    rise = setting = None
    t0, a0 = start, alt(start)
    for i in range(1, 145):
        t1 = start + i * step
        a1 = alt(t1)
        if a0 <= 0 < a1 or a1 <= 0 < a0:
            lo, hi = t0, t1  # bisect to the minute
            for _ in range(12):
                mid = lo + (hi - lo) / 2
                if (alt(lo) <= 0) == (alt(mid) <= 0):
                    lo = mid
                else:
                    hi = mid
            when = (lo + (hi - lo) / 2).astimezone(tz).replace(second=0, microsecond=0)
            if a1 > a0:
                rise = rise or when
            else:
                setting = setting or when
        t0, a0 = t1, a1
    return rise, setting

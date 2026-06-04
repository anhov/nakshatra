"""
Birth chart D-1 (Rashi) and D-9 (Navamsha).

Computes for a birth moment (date + time + timezone + place):
  • Lagna (Ascendant) — sidereal, Lahiri, Whole Sign
  • 9 Grahas: Sun Moon Mars Mercury Jupiter Venus Saturn Rahu Ketu
      – sidereal longitude, sign, house (Whole Sign), nakshatra, pada
      – retrograde status
      – D-9 Navamsha sign
      – simplified strength label
  • D-9 Navamsha Lagna
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

import swisseph as swe

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_LAHIRI = swe.SIDM_LAHIRI
_FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
_FLAGS_SPEED = _FLAGS | swe.FLG_SPEED
_SEG = 360.0 / 27  # degrees per nakshatra

SIGN_NAMES: list[str] = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

NAKSHATRA_NAMES: list[str] = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

# (planet_name, swe_id) — Ketu uses None; computed from Rahu + 180°
_GRAHA_IDS: list[tuple[str, int | None]] = [
    ("Sun",     swe.SUN),
    ("Moon",    swe.MOON),
    ("Mars",    swe.MARS),
    ("Mercury", swe.MERCURY),
    ("Jupiter", swe.JUPITER),
    ("Venus",   swe.VENUS),
    ("Saturn",  swe.SATURN),
    ("Rahu",    swe.MEAN_NODE),
    ("Ketu",    None),
]

# Exaltation sign index for each graha (traditional Parashari values)
_EXALTATION: dict[str, int] = {
    "Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5,
    "Jupiter": 3, "Venus": 11, "Saturn": 6, "Rahu": 2, "Ketu": 8,
}
# Debilitation = exaltation + 6 (mod 12)
_DEBILITATION: dict[str, int] = {k: (v + 6) % 12 for k, v in _EXALTATION.items()}

# Own signs (moolatrikona + own)
_OWN_SIGNS: dict[str, list[int]] = {
    "Sun": [4], "Moon": [3],
    "Mars": [0, 7], "Mercury": [2, 5],
    "Jupiter": [8, 11], "Venus": [1, 6],
    "Saturn": [9, 10],
    "Rahu": [], "Ketu": [],
}

# D-9 Navamsha: starting sign for each rashi (fire→Aries, earth→Cap, air→Lib, water→Can)
_NAV_STARTS: list[int] = [0, 9, 6, 3, 0, 9, 6, 3, 0, 9, 6, 3]

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class GrahaPosition:
    name: str
    longitude: float        # sidereal, 0–360°
    sign_index: int         # 0=Aries … 11=Pisces
    sign: str
    sign_degree: float      # degrees within sign (0–30)
    house: int              # 1–12, Whole Sign
    nakshatra_index: int    # 0–26
    nakshatra: str
    pada: int               # 1–4
    is_retrograde: bool
    navamsha_index: int     # D-9 sign index 0–11
    navamsha: str           # D-9 sign name
    is_vargottama: bool     # D-1 sign == D-9 sign
    strength: str           # "Exalted" | "Own Sign" | "Neutral" | "Debilitated"


@dataclass
class LagnaInfo:
    longitude: float        # sidereal Ascendant degree
    sign_index: int
    sign: str
    sign_degree: float
    nakshatra_index: int
    nakshatra: str
    pada: int
    navamsha_index: int
    navamsha: str           # D-9 Ascendant sign


@dataclass
class BirthChart:
    birth_date: str         # ISO-8601 date
    birth_time: str         # "HH:MM" local
    timezone: str           # IANA tz
    latitude: float
    geo_longitude: float
    julian_day: float
    lagna: LagnaInfo
    grahas: list[GrahaPosition]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _norm(deg: float) -> float:
    return deg % 360.0


def _jd(dt: datetime) -> float:
    utc = dt.astimezone(timezone.utc)
    return swe.julday(
        utc.year, utc.month, utc.day,
        utc.hour + utc.minute / 60.0 + utc.second / 3600.0,
    )


def _nakshatra_pada(lon: float) -> tuple[int, int]:
    """Returns (nakshatra_index 0–26, pada 1–4)."""
    raw = lon / _SEG
    idx = int(raw) % 27
    deg_in = (raw - int(raw)) * _SEG
    pada = min(int(deg_in / (_SEG / 4)) + 1, 4)
    return idx, pada


def _navamsha_idx(lon: float) -> int:
    sign = int(lon / 30) % 12
    deg_in_sign = lon % 30
    nav = int(deg_in_sign / (30.0 / 9))  # 0–8
    return (_NAV_STARTS[sign] + nav) % 12


def _strength(name: str, sign_idx: int) -> str:
    if sign_idx == _EXALTATION.get(name, -1):
        return "Exalted"
    if sign_idx == _DEBILITATION.get(name, -1):
        return "Debilitated"
    if sign_idx in _OWN_SIGNS.get(name, []):
        return "Own Sign"
    return "Neutral"


def _build_graha(
    name: str,
    lon: float,
    speed: float,
    asc_sign: int,
    force_retro: bool = False,
) -> GrahaPosition:
    sign_idx = int(lon / 30) % 12
    nav_idx = _navamsha_idx(lon)
    nak_idx, pada = _nakshatra_pada(lon)
    house = (sign_idx - asc_sign) % 12 + 1
    return GrahaPosition(
        name=name,
        longitude=round(lon, 6),
        sign_index=sign_idx,
        sign=SIGN_NAMES[sign_idx],
        sign_degree=round(lon % 30, 4),
        house=house,
        nakshatra_index=nak_idx,
        nakshatra=NAKSHATRA_NAMES[nak_idx],
        pada=pada,
        is_retrograde=force_retro or speed < 0,
        navamsha_index=nav_idx,
        navamsha=SIGN_NAMES[nav_idx],
        is_vargottama=(sign_idx == nav_idx),
        strength=_strength(name, sign_idx),
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_birth_chart(
    birth_date: date,
    birth_time: str,
    tz_name: str,
    latitude: float,
    longitude: float,
) -> BirthChart:
    """
    Calculate D-1 birth chart (and D-9 Navamsha signs) for a person.

    Args:
        birth_date:  Date of birth.
        birth_time:  Local time of birth as "HH:MM".
        tz_name:     IANA timezone, e.g. "Asia/Kolkata".
        latitude:    Birth place latitude (positive = North).
        longitude:   Birth place longitude (positive = East).

    Returns:
        BirthChart with Lagna and all 9 Graha positions.
    """
    hh, mm = (int(x) for x in birth_time.split(":"))
    tz = ZoneInfo(tz_name)
    birth_dt = datetime(
        birth_date.year, birth_date.month, birth_date.day,
        hh, mm, 0, tzinfo=tz,
    )

    swe.set_sid_mode(_LAHIRI)
    jd = _jd(birth_dt)

    # Ascendant (sidereal, Whole Sign)
    cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b"W", swe.FLG_SIDEREAL)
    asc_lon = _norm(ascmc[0])
    asc_sign = int(asc_lon / 30) % 12
    asc_nav_idx = _navamsha_idx(asc_lon)
    asc_nak_idx, asc_pada = _nakshatra_pada(asc_lon)

    lagna = LagnaInfo(
        longitude=round(asc_lon, 6),
        sign_index=asc_sign,
        sign=SIGN_NAMES[asc_sign],
        sign_degree=round(asc_lon % 30, 4),
        nakshatra_index=asc_nak_idx,
        nakshatra=NAKSHATRA_NAMES[asc_nak_idx],
        pada=asc_pada,
        navamsha_index=asc_nav_idx,
        navamsha=SIGN_NAMES[asc_nav_idx],
    )

    # Nine Grahas
    grahas: list[GrahaPosition] = []
    rahu_lon: float = 0.0

    for name, planet_id in _GRAHA_IDS:
        if name == "Ketu":
            lon = _norm(rahu_lon + 180.0)
            graha = _build_graha(name, lon, -1.0, asc_sign, force_retro=True)
        else:
            result, _ = swe.calc_ut(jd, planet_id, _FLAGS_SPEED)  # type: ignore[arg-type]
            lon = _norm(result[0])
            speed = result[3]
            if name == "Rahu":
                rahu_lon = lon
                force_retro = True  # mean node always retrograde
            else:
                force_retro = False
            graha = _build_graha(name, lon, speed, asc_sign, force_retro=force_retro)

        grahas.append(graha)

    return BirthChart(
        birth_date=birth_date.isoformat(),
        birth_time=birth_time,
        timezone=tz_name,
        latitude=latitude,
        geo_longitude=longitude,
        julian_day=round(jd, 6),
        lagna=lagna,
        grahas=grahas,
    )

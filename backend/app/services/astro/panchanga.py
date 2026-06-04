"""
Panchanga — the five Hindu almanac elements for a given date and timezone.

Elements calculated:
  Tithi    — lunar day (1–30), based on Moon–Sun elongation
  Vara     — weekday with planetary ruler
  Nakshatra — Moon's lunar mansion (1–27)
  Yoga     — combined Sun+Moon nakshatra (1–27)
  Karana   — half-tithi (one of 11 named types)

All calculations use Swiss Ephemeris with Lahiri (Chitrapaksha) ayanamsha,
targeting ±1 arc-minute accuracy against Jagannatha Hora.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

import swisseph as swe

# ---------------------------------------------------------------------------
# Swiss Ephemeris setup
# ---------------------------------------------------------------------------

_LAHIRI = swe.SIDM_LAHIRI
_FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

# ---------------------------------------------------------------------------
# Name tables
# ---------------------------------------------------------------------------

_TITHI_BASE = [
    "Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dvadashi", "Trayodashi", "Chaturdashi",
]

TITHI_NAMES: list[str] = (
    [f"Shukla {n}" for n in _TITHI_BASE]
    + ["Purnima"]
    + [f"Krishna {n}" for n in _TITHI_BASE]
    + ["Amavasya"]
)  # indices 0–29 → tithis 1–30

NAKSHATRA_NAMES: list[str] = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

YOGA_NAMES: list[str] = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
    "Atiganda", "Sukarma", "Dhriti", "Shula", "Ganda",
    "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
    "Indra", "Vaidhriti",
]

# 7 movable karanas cycle 8× per lunar month (positions 2–57 out of 60)
_MOVABLE_KARANAS: list[str] = [
    "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
]

# Planetary rulers of each weekday (Vedic order: 0=Sun/Sunday … 6=Saturn/Saturday)
_VARA_TABLE: list[tuple[str, str, str]] = [
    ("Sunday",    "Sun",     "Ravivar"),
    ("Monday",    "Moon",    "Somvar"),
    ("Tuesday",   "Mars",    "Mangalvar"),
    ("Wednesday", "Mercury", "Budhvar"),
    ("Thursday",  "Jupiter", "Guruvar"),
    ("Friday",    "Venus",   "Shukravar"),
    ("Saturday",  "Saturn",  "Shanivar"),
]

_SEG = 360.0 / 27  # 13°20' — span of one nakshatra / yoga segment

# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------


@dataclass
class TithiInfo:
    number: int        # 1–30
    name: str          # e.g. "Shukla Navami"
    paksha: str        # "Shukla" (waxing) or "Krishna" (waning)
    elapsed_pct: float # 0–100: how far through the current tithi


@dataclass
class VaraInfo:
    number: int    # 0 = Sunday … 6 = Saturday (Vedic convention)
    english: str   # "Sunday"
    ruler: str     # "Sun"
    sanskrit: str  # "Ravivar"


@dataclass
class NakshatraInfo:
    number: int        # 1–27
    name: str          # e.g. "Uttara Phalguni"
    pada: int          # 1–4 (quarter within the nakshatra)
    elapsed_pct: float # 0–100: how far through the current nakshatra


@dataclass
class YogaInfo:
    number: int        # 1–27
    name: str          # e.g. "Vriddhi"
    elapsed_pct: float # 0–100


@dataclass
class KaranaInfo:
    number: int        # 1–60: positional index within the lunar month
    name: str          # e.g. "Bava", "Vishti", "Kintughna"
    is_fixed: bool     # True for the 4 fixed karanas
    elapsed_pct: float # 0–100: how far through the current karana


@dataclass
class Panchanga:
    date: str               # ISO-8601 date, e.g. "2025-06-04"
    local_time: str         # ISO-8601 datetime in local tz
    julian_day: float
    tithi: TithiInfo
    vara: VaraInfo
    nakshatra: NakshatraInfo
    yoga: YogaInfo
    karana: KaranaInfo
    sun_longitude: float    # sidereal degrees (Lahiri)
    moon_longitude: float   # sidereal degrees (Lahiri)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _norm(deg: float) -> float:
    """Normalise degrees to [0, 360)."""
    return deg % 360.0


def _jd(dt: datetime) -> float:
    """Timezone-aware datetime → Julian Day Number (UT)."""
    utc = dt.astimezone(timezone.utc)
    return swe.julday(
        utc.year, utc.month, utc.day,
        utc.hour + utc.minute / 60.0 + utc.second / 3600.0,
    )


def _sidereal_lon(jd: float, planet: int) -> float:
    """Sidereal longitude of a planet at Julian Day jd (Lahiri ayanamsha)."""
    result, _ = swe.calc_ut(jd, planet, _FLAGS)
    return _norm(result[0])


# ---------------------------------------------------------------------------
# Five-element calculators
# ---------------------------------------------------------------------------


def _tithi(moon_lon: float, sun_lon: float) -> TithiInfo:
    diff = _norm(moon_lon - sun_lon)
    num = int(diff / 12.0) + 1          # 1–30
    elapsed = (diff % 12.0) / 12.0 * 100.0
    paksha = "Shukla" if num <= 15 else "Krishna"
    return TithiInfo(
        number=num,
        name=TITHI_NAMES[num - 1],
        paksha=paksha,
        elapsed_pct=round(elapsed, 2),
    )


def _vara(dt: datetime) -> VaraInfo:
    # dt is already in local timezone; weekday() gives Mon=0…Sun=6
    vedic = (dt.weekday() + 1) % 7     # Sun=0 … Sat=6
    eng, ruler, skt = _VARA_TABLE[vedic]
    return VaraInfo(number=vedic, english=eng, ruler=ruler, sanskrit=skt)


def _nakshatra(moon_lon: float) -> NakshatraInfo:
    raw = moon_lon / _SEG               # 0.0–27.0
    idx = int(raw) % 27                 # 0–26
    elapsed_in_seg = (raw - int(raw)) * _SEG
    elapsed = elapsed_in_seg / _SEG * 100.0
    pada = min(int(elapsed_in_seg / (_SEG / 4)) + 1, 4)  # 1–4
    return NakshatraInfo(
        number=idx + 1,
        name=NAKSHATRA_NAMES[idx],
        pada=pada,
        elapsed_pct=round(elapsed, 2),
    )


def _yoga(sun_lon: float, moon_lon: float) -> YogaInfo:
    combined = _norm(sun_lon + moon_lon)
    raw = combined / _SEG
    idx = int(raw) % 27
    elapsed = (raw - int(raw)) * 100.0
    return YogaInfo(
        number=idx + 1,
        name=YOGA_NAMES[idx],
        elapsed_pct=round(elapsed, 2),
    )


def _karana(moon_lon: float, sun_lon: float) -> KaranaInfo:
    diff = _norm(moon_lon - sun_lon)
    k_idx = int(diff / 6.0) % 60       # 0–59 positional index in lunar month
    elapsed = (diff % 6.0) / 6.0 * 100.0

    if k_idx == 0:
        name, is_fixed = "Kintughna", True
    elif 1 <= k_idx <= 56:
        name, is_fixed = _MOVABLE_KARANAS[(k_idx - 1) % 7], False
    elif k_idx == 57:
        name, is_fixed = "Shakuni", True
    elif k_idx == 58:
        name, is_fixed = "Chatushpada", True
    else:  # 59
        name, is_fixed = "Naga", True

    return KaranaInfo(
        number=k_idx + 1,
        name=name,
        is_fixed=is_fixed,
        elapsed_pct=round(elapsed, 2),
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_panchanga(
    target_date: date,
    tz_name: str,
    hour: int = 6,
    minute: int = 0,
) -> Panchanga:
    """
    Calculate Panchanga for a given date and timezone.

    Args:
        target_date: The calendar date.
        tz_name:     IANA timezone string, e.g. "Asia/Kolkata".
        hour:        Local hour for the calculation (default 6 — early morning,
                     approximates sunrise in India). Pass the actual sunrise hour
                     for precise muhurta work.
        minute:      Local minute (default 0).

    Returns:
        Panchanga dataclass with all five elements plus raw planet longitudes.
    """
    tz = ZoneInfo(tz_name)
    local_dt = datetime(
        target_date.year, target_date.month, target_date.day,
        hour, minute, 0, tzinfo=tz,
    )

    swe.set_sid_mode(_LAHIRI)
    jd = _jd(local_dt)

    sun_lon = _sidereal_lon(jd, swe.SUN)
    moon_lon = _sidereal_lon(jd, swe.MOON)

    return Panchanga(
        date=target_date.isoformat(),
        local_time=local_dt.isoformat(),
        julian_day=round(jd, 6),
        tithi=_tithi(moon_lon, sun_lon),
        vara=_vara(local_dt),
        nakshatra=_nakshatra(moon_lon),
        yoga=_yoga(sun_lon, moon_lon),
        karana=_karana(moon_lon, sun_lon),
        sun_longitude=round(sun_lon, 6),
        moon_longitude=round(moon_lon, 6),
    )

"""
Daily personal transits (Gochara).

Calculates where the 9 grahas are on a given date and interprets them
relative to the natal Moon sign and Lagna (Whole Sign, Lahiri ayanamsha).

Includes:
  • House position from natal Moon  — primary Gochara (Vedic standard)
  • House position from natal Lagna — secondary reference
  • Favorable / unfavorable flag per planet (classical Parashari rules)
  • Sade Sati detection (Saturn in 12th / 1st / 2nd from natal Moon)
  • Shani Dhaiya detection (Saturn in 4th or 8th from natal Moon)
  • Weighted transit score 0–10 for use by day_score.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

import swisseph as swe

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_LAHIRI = swe.SIDM_LAHIRI
_FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

SIGN_NAMES: list[str] = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

_NAK_NAMES: list[str] = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

_SEG: float = 360.0 / 27

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

# Classical Parashari Gochara — favorable house positions from natal Moon sign
_GOCHARA_FAVORABLE: dict[str, frozenset[int]] = {
    "Sun":     frozenset({3, 6, 10, 11}),
    "Moon":    frozenset({1, 3, 6, 7, 10, 11}),
    "Mars":    frozenset({3, 6, 11}),
    "Mercury": frozenset({2, 4, 6, 8, 10, 11}),
    "Jupiter": frozenset({2, 5, 7, 9, 11}),
    "Venus":   frozenset({1, 2, 3, 4, 5, 8, 9, 11, 12}),
    "Saturn":  frozenset({3, 6, 11}),
    "Rahu":    frozenset({3, 6, 10, 11}),
    "Ketu":    frozenset({3, 6, 11}),
}

# Significance weight for scoring (slow-moving planets have more lasting impact)
_WEIGHT: dict[str, int] = {
    "Jupiter": 3, "Saturn": 3,
    "Rahu": 2, "Ketu": 2, "Mars": 2,
    "Sun": 1, "Moon": 1, "Mercury": 1, "Venus": 1,
}
_MAX_SCORE: int = sum(_WEIGHT.values())  # 16

# Plain-English effect descriptions (zero jargon; challenging ones include guidance)
_EFFECTS: dict[str, dict[bool, str]] = {
    "Sun": {
        True:  "A great day for visibility, leadership, and getting recognition.",
        False: "Keep a low profile; authority figures or your ego may create friction.",
    },
    "Moon": {
        True:  "Emotions flow smoothly — good for home, family, and nurturing others.",
        False: "Emotions run high. Prioritise rest and gentle self-care today.",
    },
    "Mars": {
        True:  "High energy — excellent for exercise, bold decisions, and new initiatives.",
        False: "Avoid confrontations and unnecessary risks. Channel energy into focused work.",
    },
    "Mercury": {
        True:  "Sharp thinking and clear communication. Good for writing, travel, and negotiations.",
        False: "Double-check everything — misunderstandings happen easily right now.",
    },
    "Jupiter": {
        True:  "Expansive, optimistic energy. Great for growth, learning, and big decisions.",
        False: "Look before you leap. Avoid overcommitting or overspending.",
    },
    "Venus": {
        True:  "Wonderful for relationships, creative work, beauty, and enjoyment.",
        False: "Handle relationship and financial matters gently today.",
    },
    "Saturn": {
        True:  "Steady, disciplined energy. Good for hard work, long-term plans, and structure.",
        False: "Expect delays and extra responsibility. Patience and persistence pay off.",
    },
    "Rahu": {
        True:  "Good for bold ambitions, technology, and stepping outside your comfort zone.",
        False: "Watch for confusion or unrealistic plans. Ground yourself before deciding.",
    },
    "Ketu": {
        True:  "Spiritual clarity and letting go of what no longer serves you.",
        False: "You may feel scattered or ungrounded. Anchor yourself in simple routines.",
    },
}

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class TransitPlanet:
    name: str
    longitude: float
    sign_index: int
    sign: str
    sign_degree: float
    nakshatra: str
    pada: int
    is_retrograde: bool
    house_from_moon: int    # 1-12 (primary Gochara)
    house_from_lagna: int   # 1-12
    is_favorable: bool      # Gochara from Moon
    weight: int             # 1-3 transit significance
    effect: str             # plain English


@dataclass
class SaturnWatch:
    has_sade_sati: bool
    sade_sati_phase: str | None   # "Rising" | "Peak" | "Setting"
    has_shani_dhaiya: bool
    shani_dhaiya_house: int | None  # 4 or 8


@dataclass
class TransitResult:
    date: str
    local_time: str
    planets: list[TransitPlanet]
    saturn_watch: SaturnWatch
    transit_score: float            # 0-10; input for day_score.py
    quality: str                    # "Excellent" | "Good" | "Mixed" | "Challenging"
    favorable_planets: list[str]
    challenging_planets: list[str]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _norm(d: float) -> float:
    return d % 360.0


def _jd(dt: datetime) -> float:
    utc = dt.astimezone(timezone.utc)
    return swe.julday(
        utc.year, utc.month, utc.day,
        utc.hour + utc.minute / 60.0 + utc.second / 3600.0,
    )


def _nak_pada(lon: float) -> tuple[str, int]:
    raw = lon / _SEG
    idx = int(raw) % 27
    deg_in = (raw - int(raw)) * _SEG
    pada = min(int(deg_in / (_SEG / 4)) + 1, 4)
    return _NAK_NAMES[idx], pada


def _house(transit_sign: int, natal_sign: int) -> int:
    return (transit_sign - natal_sign) % 12 + 1


def _quality(score: float) -> str:
    if score >= 7.0:
        return "Excellent"
    if score >= 5.5:
        return "Good"
    if score >= 4.0:
        return "Mixed"
    return "Challenging"


def _sade_sati_phase(saturn_house_from_moon: int) -> str | None:
    return {12: "Rising", 1: "Peak", 2: "Setting"}.get(saturn_house_from_moon)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_transits(
    natal_moon_lon: float,
    natal_lagna_lon: float,
    transit_date: date,
    tz_name: str,
    hour: int = 6,
    minute: int = 0,
) -> TransitResult:
    """
    Calculate personal transits for a given date.

    Args:
        natal_moon_lon:  Sidereal Moon longitude at birth (from get_birth_chart).
        natal_lagna_lon: Sidereal Lagna longitude at birth.
        transit_date:    Date to calculate transits for.
        tz_name:         IANA timezone, e.g. "Asia/Kolkata".
        hour:            Local hour for the snapshot (default 6 — approx sunrise).
        minute:          Local minute (default 0).

    Returns:
        TransitResult with all 9 graha transits, Saturn conditions, and a
        0–10 transit_score for use by day_score.py.
    """
    tz = ZoneInfo(tz_name)
    local_dt = datetime(transit_date.year, transit_date.month, transit_date.day,
                        hour, minute, 0, tzinfo=tz)

    swe.set_sid_mode(_LAHIRI)
    jd = _jd(local_dt)

    natal_moon_sign = int(natal_moon_lon / 30) % 12
    natal_lagna_sign = int(natal_lagna_lon / 30) % 12

    planets: list[TransitPlanet] = []
    raw_score: int = 0
    rahu_lon: float = 0.0

    for name, pid in _GRAHA_IDS:
        if name == "Ketu":
            lon = _norm(rahu_lon + 180.0)
            speed = -1.0   # always retrograde
            is_retro = True
        else:
            result, _ = swe.calc_ut(jd, pid, _FLAGS)  # type: ignore[arg-type]
            lon = _norm(result[0])
            speed = result[3]
            is_retro = speed < 0
            if name == "Rahu":
                rahu_lon = lon
                is_retro = True

        sign_idx = int(lon / 30) % 12
        nak, pada = _nak_pada(lon)
        h_moon = _house(sign_idx, natal_moon_sign)
        h_lagna = _house(sign_idx, natal_lagna_sign)
        favorable = h_moon in _GOCHARA_FAVORABLE[name]
        weight = _WEIGHT[name]
        raw_score += weight * (1 if favorable else -1)

        planets.append(TransitPlanet(
            name=name,
            longitude=round(lon, 6),
            sign_index=sign_idx,
            sign=SIGN_NAMES[sign_idx],
            sign_degree=round(lon % 30, 4),
            nakshatra=nak,
            pada=pada,
            is_retrograde=is_retro,
            house_from_moon=h_moon,
            house_from_lagna=h_lagna,
            is_favorable=favorable,
            weight=weight,
            effect=_EFFECTS[name][favorable],
        ))

    # Normalise score to 0–10
    transit_score = round((raw_score + _MAX_SCORE) / (2 * _MAX_SCORE) * 10, 2)

    # Saturn conditions
    saturn = next(p for p in planets if p.name == "Saturn")
    sati_phase = _sade_sati_phase(saturn.house_from_moon)
    shani_dhaiya = saturn.house_from_moon in {4, 8}

    saturn_watch = SaturnWatch(
        has_sade_sati=sati_phase is not None,
        sade_sati_phase=sati_phase,
        has_shani_dhaiya=shani_dhaiya and sati_phase is None,
        shani_dhaiya_house=saturn.house_from_moon if shani_dhaiya and sati_phase is None else None,
    )

    favorable_planets = [p.name for p in planets if p.is_favorable]
    challenging_planets = [p.name for p in planets if not p.is_favorable]

    return TransitResult(
        date=transit_date.isoformat(),
        local_time=local_dt.isoformat(),
        planets=planets,
        saturn_watch=saturn_watch,
        transit_score=transit_score,
        quality=_quality(transit_score),
        favorable_planets=favorable_planets,
        challenging_planets=challenging_planets,
    )

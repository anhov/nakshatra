"""
Muhurta — daily auspicious and inauspicious timing windows.

Computes for a given date and geographic location:
  • Sunrise, sunset, solar noon  (via Swiss Ephemeris rise_trans)
  • Brahma Muhurta  (96 min before sunrise, 48-min window for spiritual practice)
  • Rahu Kala       (1/8 of day — inauspicious)
  • Gulika Kala     (1/8 of day — inauspicious, Saturn's period)
  • Yama Ganda      (1/8 of day — inauspicious)
  • Abhijit Muhurta (±24 min around solar noon — auspicious)
  • Choghadiya      (8 day + 8 night variable-length windows)
  • Hora            (12 day + 12 night planetary hours)

All start/end times are ISO-8601 strings in the supplied timezone.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import swisseph as swe

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_GEOFLAGS = swe.FLG_SWIEPH

# Inauspicious period slot (1-indexed, out of 8 equal daytime parts)
# keyed by Vedic weekday: 0=Sun, 1=Mon, ..., 6=Sat
_RAHU_SLOT:  list[int] = [8, 2, 7, 5, 6, 4, 3]
_GULIKA_SLOT: list[int] = [6, 5, 4, 3, 2, 1, 7]
_YAMA_SLOT:   list[int] = [4, 3, 2, 7, 5, 6, 1]

# Choghadiya: 7 names cycling; 8 periods per half-day
CHOGHADIYA_NAMES: list[str] = ["Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog"]
_CHOG_QUALITY: dict[str, str] = {
    "Amrit": "Excellent", "Shubh": "Good", "Labh": "Good",
    "Char": "Neutral", "Udveg": "Avoid", "Rog": "Avoid", "Kaal": "Avoid",
}
_CHOG_DESC: dict[str, str] = {
    "Amrit": "Excellent for all new beginnings, important decisions, and travel.",
    "Shubh": "Auspicious for ceremonies, new ventures, and important meetings.",
    "Labh": "Good for business dealings, financial activity, and work that brings gain.",
    "Char": "Favorable for travel, movement, communication, and social activities.",
    "Udveg": "An unsettled period. Stick to routine work; avoid major decisions.",
    "Rog": "Associated with conflict and friction. Keep a low profile today.",
    "Kaal": "The most inauspicious Choghadiya. Rest or handle only routine tasks.",
}
# Day start index (Vedic weekday 0=Sun…6=Sat)
_CHOG_DAY_START:   list[int] = [0, 3, 6, 2, 5, 1, 4]
# Night start index
_CHOG_NIGHT_START: list[int] = [5, 1, 4, 3, 6, 0, 2]

# Hora: 12 day + 12 night planetary hours
# Sequence starting from each day lord (Chaldean order: Sun→Venus→Mercury→Moon→Saturn→Jupiter→Mars)
HORA_SEQ: list[str] = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]
_HORA_FIRST_IDX: list[int] = [0, 3, 6, 2, 5, 1, 4]  # keyed by Vedic weekday
_HORA_QUALITY: dict[str, str] = {
    "Jupiter": "Excellent", "Venus": "Good", "Moon": "Good",
    "Mercury": "Good", "Sun": "Neutral", "Mars": "Avoid", "Saturn": "Avoid",
}
_HORA_DESC: dict[str, str] = {
    "Sun":     "Good for authority, leadership, government matters, and health.",
    "Moon":    "Supportive for creativity, intuition, family, and emotional matters.",
    "Mars":    "High-energy but prone to conflict. Best for physical tasks, not negotiations.",
    "Mercury": "Excellent for writing, communication, learning, and business.",
    "Jupiter": "The most auspicious Hora. Great for new beginnings, study, and ceremonies.",
    "Venus":   "Wonderful for relationships, arts, beauty, luxury, and creative work.",
    "Saturn":  "Slow-moving energy. Suitable for discipline and routine, not new starts.",
}

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class TimeWindow:
    name: str
    planet: str | None
    start: str          # ISO-8601 local datetime
    end: str
    quality: str        # "Excellent" | "Good" | "Neutral" | "Avoid"
    description: str


@dataclass
class MuhurtaResult:
    date: str
    timezone: str
    sunrise: str
    sunset: str
    solar_noon: str
    day_duration_minutes: float
    brahma_muhurta: TimeWindow
    abhijit: TimeWindow
    rahu_kala: TimeWindow
    gulika_kala: TimeWindow
    yama_ganda: TimeWindow
    choghadiyas_day: list[TimeWindow]    # 8 windows (sunrise → sunset)
    choghadiyas_night: list[TimeWindow]  # 8 windows (sunset → next sunrise)
    horas: list[TimeWindow]              # 24 windows (12 day + 12 night)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _jd_to_dt(jd: float, tz: ZoneInfo) -> datetime:
    """Convert Julian Day (UT) to aware datetime in the given timezone."""
    y, m, d, h = swe.revjul(jd)
    hh = int(h)
    mm = int((h - hh) * 60)
    ss = int(((h - hh) * 60 - mm) * 60)
    utc_dt = datetime(y, m, d, hh, mm, ss, tzinfo=timezone.utc)
    return utc_dt.astimezone(tz)


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


def _rise_set(target_date, lat: float, lon: float) -> tuple[datetime, datetime, datetime, datetime]:
    """
    Returns (sunrise, sunset, solar_noon, next_sunrise) in UTC as aware datetimes.
    Starts search 24 hours before midnight UTC to handle all timezones safely.
    """
    jd_start = swe.julday(target_date.year, target_date.month, target_date.day, 0.0) - 1.0
    geopos = [lon, lat, 0.0]

    def _find(rsmi: int, after_jd: float) -> float:
        _, times = swe.rise_trans(after_jd, swe.SUN, rsmi, geopos, 1013.25, 15.0, _GEOFLAGS)
        return times[0]

    sr_jd   = _find(swe.CALC_RISE,      jd_start)  # sunrise on target date
    ss_jd   = _find(swe.CALC_SET,       sr_jd)     # sunset AFTER that sunrise
    noon_jd = _find(swe.CALC_MTRANSIT,  sr_jd)     # solar noon between sunrise and sunset
    nsr_jd  = _find(swe.CALC_RISE,      ss_jd)     # next sunrise (following night)

    utc = timezone.utc
    to_utc = lambda jd: _jd_to_dt(jd, ZoneInfo("UTC"))  # noqa: E731
    return to_utc(sr_jd), to_utc(ss_jd), to_utc(noon_jd), to_utc(nsr_jd)


def _slot_window(sunrise: datetime, slot: int, slot_dur: timedelta) -> tuple[datetime, datetime]:
    """Return (start, end) for a 1-indexed slot in the daytime."""
    start = sunrise + (slot - 1) * slot_dur
    return start, start + slot_dur


def _inauspicious(name: str, start: datetime, end: datetime, tz: ZoneInfo) -> TimeWindow:
    return TimeWindow(
        name=name, planet=None,
        start=_iso(start.astimezone(tz)),
        end=_iso(end.astimezone(tz)),
        quality="Avoid",
        description=(
            "An inauspicious period. Avoid starting new ventures, travel, "
            "important meetings, or major decisions during this window."
        ),
    )


def _choghadiya_windows(
    period_start: datetime,
    period_end: datetime,
    start_idx: int,
    tz: ZoneInfo,
) -> list[TimeWindow]:
    total = period_end - period_start
    slot = total / 8
    windows: list[TimeWindow] = []
    for i in range(8):
        name = CHOGHADIYA_NAMES[(start_idx + i) % 7]
        s = period_start + i * slot
        e = s + slot
        windows.append(TimeWindow(
            name=name, planet=None,
            start=_iso(s.astimezone(tz)),
            end=_iso(e.astimezone(tz)),
            quality=_CHOG_QUALITY[name],
            description=_CHOG_DESC[name],
        ))
    return windows


def _hora_windows(
    period_start: datetime,
    period_end: datetime,
    first_planet_idx: int,
    hora_offset: int,       # 0 for day (first 12), 12 for night (last 12)
    tz: ZoneInfo,
) -> list[TimeWindow]:
    total = period_end - period_start
    slot = total / 12
    windows: list[TimeWindow] = []
    for i in range(12):
        planet = HORA_SEQ[(first_planet_idx + hora_offset + i) % 7]
        s = period_start + i * slot
        e = s + slot
        windows.append(TimeWindow(
            name=f"{planet} Hora",
            planet=planet,
            start=_iso(s.astimezone(tz)),
            end=_iso(e.astimezone(tz)),
            quality=_HORA_QUALITY[planet],
            description=_HORA_DESC[planet],
        ))
    return windows


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_muhurta(
    target_date,
    tz_name: str,
    latitude: float,
    longitude: float,
) -> MuhurtaResult:
    """
    Calculate all daily timing windows (Muhurta) for a given date and location.

    Args:
        target_date: Calendar date (datetime.date).
        tz_name:     IANA timezone, e.g. "Asia/Kolkata".
        latitude:    Geographic latitude (positive = North).
        longitude:   Geographic longitude (positive = East).

    Returns:
        MuhurtaResult with all timing windows as local-time ISO strings.
    """
    tz = ZoneInfo(tz_name)
    sunrise_utc, sunset_utc, noon_utc, next_sunrise_utc = _rise_set(target_date, latitude, longitude)

    # Vedic weekday from the local date at sunrise
    local_sunrise = sunrise_utc.astimezone(tz)
    vedic_day = (local_sunrise.weekday() + 1) % 7  # 0=Sun … 6=Sat

    day_dur = sunset_utc - sunrise_utc
    slot_dur = day_dur / 8
    day_minutes = round(day_dur.total_seconds() / 60, 1)

    # ── Brahma Muhurta ───────────────────────────────────────────────────────
    brahma_end = sunrise_utc - timedelta(minutes=48)
    brahma_start = sunrise_utc - timedelta(minutes=96)
    brahma = TimeWindow(
        name="Brahma Muhurta", planet=None,
        start=_iso(brahma_start.astimezone(tz)),
        end=_iso(brahma_end.astimezone(tz)),
        quality="Excellent",
        description=(
            "The most auspicious window for meditation, yoga, and spiritual practice. "
            "Rising early in this period sets a powerful intention for the whole day."
        ),
    )

    # ── Inauspicious periods ─────────────────────────────────────────────────
    def _inausp(label: str, slot: int) -> TimeWindow:
        s, e = _slot_window(sunrise_utc, slot, slot_dur)
        return _inauspicious(label, s, e, tz)

    rahu_kala  = _inausp("Rahu Kala",  _RAHU_SLOT[vedic_day])
    gulika_kala = _inausp("Gulika Kala", _GULIKA_SLOT[vedic_day])
    yama_ganda  = _inausp("Yama Ganda", _YAMA_SLOT[vedic_day])

    # ── Abhijit Muhurta ───────────────────────────────────────────────────────
    abhijit = TimeWindow(
        name="Abhijit Muhurta", planet="Sun",
        start=_iso((noon_utc - timedelta(minutes=24)).astimezone(tz)),
        end=_iso((noon_utc + timedelta(minutes=24)).astimezone(tz)),
        quality="Excellent",
        description=(
            "One of the best windows of the day for new beginnings, important meetings, "
            "and decisions. The sun is at its peak power."
        ),
    )

    # ── Choghadiya ────────────────────────────────────────────────────────────
    chog_day   = _choghadiya_windows(sunrise_utc, sunset_utc,      _CHOG_DAY_START[vedic_day],   tz)
    chog_night = _choghadiya_windows(sunset_utc,  next_sunrise_utc, _CHOG_NIGHT_START[vedic_day], tz)

    # ── Hora ──────────────────────────────────────────────────────────────────
    first_idx = _HORA_FIRST_IDX[vedic_day]
    # Night hora offset: how many Horas have elapsed in the day sequence (12)
    horas_day   = _hora_windows(sunrise_utc, sunset_utc,       first_idx,  0,  tz)
    horas_night = _hora_windows(sunset_utc,  next_sunrise_utc, first_idx, 12,  tz)

    return MuhurtaResult(
        date=target_date.isoformat(),
        timezone=tz_name,
        sunrise=_iso(local_sunrise),
        sunset=_iso(sunset_utc.astimezone(tz)),
        solar_noon=_iso(noon_utc.astimezone(tz)),
        day_duration_minutes=day_minutes,
        brahma_muhurta=brahma,
        abhijit=abhijit,
        rahu_kala=rahu_kala,
        gulika_kala=gulika_kala,
        yama_ganda=yama_ganda,
        choghadiyas_day=chog_day,
        choghadiyas_night=chog_night,
        horas=horas_day + horas_night,
    )

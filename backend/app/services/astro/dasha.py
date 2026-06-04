"""
Vimshottari Dasha — 120-year planetary period system.

Calculates all Maha Dashas and their Antardashas from the Moon's birth nakshatra.
Returns the currently active Maha Dasha and Antardasha for any query date.

Reference: Brihat Parashara Hora Shastra, chapter on Vimshottari.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SEQUENCE: list[str] = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
]

YEARS: dict[str, int] = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10,
    "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17,
}

TOTAL_YEARS: int = 120        # sum of all YEARS values
DAYS_PER_YEAR: float = 365.25  # Julian year

# Nakshatra → Dasha lord: the 9-planet sequence repeats 3× across 27 nakshatras.
# Nakshatra 0 (Ashwini) = Ketu, 1 (Bharani) = Venus, ... cycles every 9.
_NAK_LORD: list[str] = SEQUENCE * 3  # length 27, index matches nakshatra index 0–26

_NAK_NAMES: list[str] = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

_SEG: float = 360.0 / 27  # degrees per nakshatra

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class AntardashaInfo:
    lord: str
    start: date
    end: date
    duration_days: int


@dataclass
class MahaDashaInfo:
    lord: str
    start: date
    end: date
    duration_days: int
    antardashas: list[AntardashaInfo] = field(default_factory=list)


@dataclass
class ActivePeriod:
    mahadasha: str
    md_start: date
    md_end: date
    md_elapsed_pct: float    # 0–100
    antardasha: str
    ad_start: date
    ad_end: date
    ad_elapsed_pct: float    # 0–100


@dataclass
class DashaResult:
    birth_date: str
    moon_nakshatra: str
    dasha_lord_at_birth: str
    remaining_years_at_birth: float   # years left in first Maha Dasha at birth
    mahadashas: list[MahaDashaInfo]   # 9 periods covering one 120-year cycle
    active: ActivePeriod | None       # active period at query_date; None if out of range


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _to_days(years: float) -> int:
    return round(years * DAYS_PER_YEAR)


def _antardasha_years(md_years: int, ad_years: int) -> float:
    """Antardasha duration = (MD_years × AD_years) / 120."""
    return (md_years * ad_years) / TOTAL_YEARS


def _build_antardashas(
    md_lord: str, md_years: int, md_start: date
) -> list[AntardashaInfo]:
    """9 Antardashas within a Maha Dasha, starting from the MD lord."""
    start_idx = SEQUENCE.index(md_lord)
    ads: list[AntardashaInfo] = []
    current = md_start
    for i in range(9):
        ad_lord = SEQUENCE[(start_idx + i) % 9]
        ad_days = _to_days(_antardasha_years(md_years, YEARS[ad_lord]))
        end = current + timedelta(days=ad_days)
        ads.append(AntardashaInfo(lord=ad_lord, start=current, end=end, duration_days=ad_days))
        current = end
    return ads


def _elapsed_pct(period_start: date, period_end: date, query: date) -> float:
    total = (period_end - period_start).days
    if total == 0:
        return 0.0
    elapsed = (query - period_start).days
    return round(max(0.0, min(100.0, elapsed / total * 100.0)), 2)


def _find_active(mahadashas: list[MahaDashaInfo], query: date) -> ActivePeriod | None:
    for md in mahadashas:
        if md.start <= query < md.end:
            for ad in md.antardashas:
                if ad.start <= query < ad.end:
                    return ActivePeriod(
                        mahadasha=md.lord,
                        md_start=md.start,
                        md_end=md.end,
                        md_elapsed_pct=_elapsed_pct(md.start, md.end, query),
                        antardasha=ad.lord,
                        ad_start=ad.start,
                        ad_end=ad.end,
                        ad_elapsed_pct=_elapsed_pct(ad.start, ad.end, query),
                    )
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_dasha(
    moon_longitude: float,
    birth_date: date,
    query_date: date | None = None,
) -> DashaResult:
    """
    Calculate Vimshottari Dasha sequence from the Moon's sidereal birth longitude.

    Args:
        moon_longitude: Sidereal Moon longitude at birth (from get_birth_chart).
        birth_date:     Date of birth.
        query_date:     Date to identify the active period (default: today).

    Returns:
        DashaResult with all 9 Maha Dashas, their Antardashas, and the active period.
    """
    if query_date is None:
        query_date = date.today()

    # Moon nakshatra and its dasha lord
    nak_idx = int(moon_longitude / _SEG) % 27
    elapsed_frac = (moon_longitude % _SEG) / _SEG
    nak_name = _NAK_NAMES[nak_idx]
    lord = _NAK_LORD[nak_idx]

    # Days already elapsed in the birth dasha at the moment of birth
    first_years = YEARS[lord]
    elapsed_days_at_birth = _to_days(elapsed_frac * first_years)
    remaining_days = _to_days(first_years) - elapsed_days_at_birth
    remaining_years = round(remaining_days / DAYS_PER_YEAR, 4)

    # Theoretical start of the first Maha Dasha (may be before birth_date)
    first_start = birth_date - timedelta(days=elapsed_days_at_birth)

    # Build all 9 Maha Dashas
    lord_idx = SEQUENCE.index(lord)
    mahadashas: list[MahaDashaInfo] = []
    current_start = first_start

    for i in range(9):
        md_lord = SEQUENCE[(lord_idx + i) % 9]
        md_years = YEARS[md_lord]
        md_days = _to_days(md_years)
        md_end = current_start + timedelta(days=md_days)
        antardashas = _build_antardashas(md_lord, md_years, current_start)
        mahadashas.append(MahaDashaInfo(
            lord=md_lord,
            start=current_start,
            end=md_end,
            duration_days=md_days,
            antardashas=antardashas,
        ))
        current_start = md_end

    active = _find_active(mahadashas, query_date)

    return DashaResult(
        birth_date=birth_date.isoformat(),
        moon_nakshatra=nak_name,
        dasha_lord_at_birth=lord,
        remaining_years_at_birth=remaining_years,
        mahadashas=mahadashas,
        active=active,
    )

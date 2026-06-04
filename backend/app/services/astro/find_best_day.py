"""
Find Best Day — search the next N days for the top 3 dates for a given life category.

Categories: Travel, Contracts, Medical, Relationships, Moving, New Project,
            Interview, Surgery, Investment, Wedding, Meeting, Creative Work,
            Learning, Spiritual Practice, Other
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from app.services.astro.day_score import _panchanga_score, _dasha_score, _combine, _quality_label, quick_score
from app.services.astro.dasha import get_dasha
from app.services.astro.ephemeris import get_birth_chart
from app.services.astro.panchanga import get_panchanga
from app.services.astro.transits import get_transits

# ---------------------------------------------------------------------------
# Category configuration
# ---------------------------------------------------------------------------

_CFG: dict[str, dict] = {
    "Travel": {
        "key": ["Mercury", "Moon"], "boost": {"Mercury": 2.0, "Moon": 1.5},
        "avoid_t": {4, 9, 14, 19, 24, 29},
        "reason": "Mercury and Moon favor smooth, safe journeys",
    },
    "Contracts": {
        "key": ["Mercury", "Jupiter"], "boost": {"Mercury": 2.0, "Jupiter": 2.0},
        "avoid_t": {4, 9, 14, 29, 30},
        "reason": "Strong Mercury and Jupiter support clear, beneficial agreements",
    },
    "Medical": {
        "key": ["Sun", "Moon"], "boost": {"Sun": 1.5, "Moon": 1.5},
        "avoid_t": {4, 8, 9, 14, 22, 29},
        "avoid_nak": {"Mula", "Ardra", "Ashlesha", "Jyeshtha"},
        "reason": "Supportive planetary conditions for healing and health",
    },
    "Relationships": {
        "key": ["Venus", "Moon", "Jupiter"], "boost": {"Venus": 2.0, "Moon": 1.5},
        "avoid_t": {4, 9, 14, 30},
        "reason": "Venus and Moon create warmth, connection, and emotional openness",
    },
    "Moving": {
        "key": ["Moon", "Mercury"], "boost": {"Moon": 1.5, "Mercury": 1.5},
        "avoid_t": {4, 9, 14},
        "reason": "Good energy for establishing a new home and fresh beginnings",
    },
    "New Project": {
        "key": ["Jupiter", "Sun", "Mars"], "boost": {"Jupiter": 2.0, "Sun": 1.5},
        "avoid_t": {4, 9, 14, 30},
        "reason": "Expansive, initiating energy for bold new ventures",
    },
    "Interview": {
        "key": ["Mercury", "Jupiter", "Sun"], "boost": {"Mercury": 2.0, "Jupiter": 1.5},
        "avoid_t": {4, 9, 14},
        "reason": "Clear thinking, confident presentation, and favourable impressions",
    },
    "Surgery": {
        "key": ["Mars", "Sun"], "boost": {"Mars": 1.5, "Sun": 1.5},
        "avoid_t": {4, 8, 9, 14, 15, 22, 29, 30},
        "avoid_nak": {"Ardra", "Ashlesha", "Jyeshtha", "Mula", "Bharani"},
        "reason": "Mars and Sun in good position; avoiding inauspicious timing",
    },
    "Investment": {
        "key": ["Jupiter", "Venus", "Mercury"], "boost": {"Jupiter": 2.0, "Venus": 1.5},
        "avoid_t": {4, 9, 14, 30},
        "reason": "Jupiter and Venus support financial growth and wise decisions",
    },
    "Wedding": {
        "key": ["Venus", "Jupiter", "Moon"],
        "boost": {"Venus": 2.5, "Jupiter": 2.0, "Moon": 1.5},
        "avoid_t": {4, 9, 14, 30},
        "reason": "Exceptional planetary harmony for a lasting and joyful union",
    },
    "Meeting": {
        "key": ["Mercury", "Jupiter"], "boost": {"Mercury": 1.5, "Jupiter": 1.5},
        "avoid_t": {4, 9, 14},
        "reason": "Productive communication and mutual understanding",
    },
    "Creative Work": {
        "key": ["Venus", "Moon", "Mercury"], "boost": {"Venus": 2.0, "Moon": 1.5},
        "avoid_t": {4, 9, 14},
        "reason": "Inspiration flows freely; creative expression is effortless",
    },
    "Learning": {
        "key": ["Mercury", "Jupiter"], "boost": {"Mercury": 2.0, "Jupiter": 2.0},
        "avoid_t": {},
        "reason": "Sharp intellect, excellent retention, and love of ideas",
    },
    "Spiritual Practice": {
        "key": ["Moon", "Ketu", "Jupiter"],
        "boost": {"Moon": 1.5, "Ketu": 2.0, "Jupiter": 1.5},
        "avoid_t": set(),
        "bonus_t": {11, 15, 26, 30},
        "reason": "Deep inner connection, clarity, and spiritual receptivity",
    },
    "Other": {
        "key": [], "boost": {}, "avoid_t": set(),
        "reason": "Overall auspicious conditions",
    },
}

CATEGORIES: list[str] = list(_CFG.keys())


@dataclass
class BestDay:
    date: str
    rank: int
    score: float
    quality: str
    reason: str
    tags: list[str]


@dataclass
class FindBestDayResult:
    category: str
    days_searched: int
    results: list[BestDay]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _cat_score(base: float, p, tr, category: str) -> float:
    cfg = _CFG.get(category, _CFG["Other"])
    score = base

    if p.tithi.number in cfg.get("avoid_t", set()):
        score -= 3.0
    if p.tithi.number in cfg.get("bonus_t", set()):
        score += 1.5
    if p.nakshatra.name in cfg.get("avoid_nak", set()):
        score -= 2.0

    key = set(cfg.get("key", []))
    for pl in tr.planets:
        if pl.name in key and pl.is_favorable:
            score += 0.5 * cfg["boost"].get(pl.name, 1.0)

    return round(max(1.0, min(10.0, score)), 2)


def _reason(p, tr, d, category: str, score: float) -> str:
    cfg = _CFG.get(category, _CFG["Other"])
    base = cfg["reason"]
    fav_key = [pl.name for pl in tr.planets
               if pl.name in set(cfg.get("key", [])) and pl.is_favorable]

    if p.tithi.number in (11, 26):
        return f"Ekadashi adds auspicious depth. {base}."
    if p.tithi.number == 15:
        return f"Full Moon amplifies the energy. {base}."
    if fav_key:
        return f"{' and '.join(fav_key)} in supportive position. {base}. Moon in {p.nakshatra.name}."
    return f"{base}. Moon in {p.nakshatra.name}."


def _tags(p, tr, d) -> list[str]:
    tags: list[str] = []
    if p.tithi.number == 15:
        tags.append("Full Moon")
    elif p.tithi.number in (11, 26):
        tags.append("Ekadashi")
    if tr.saturn_watch.has_sade_sati:
        tags.append("Sade Sati")
    fav = [pl.name for pl in tr.planets if pl.is_favorable and pl.weight >= 2]
    tags.extend(f"{n} ✓" for n in fav[:2])
    return tags


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def find_best_days(
    birth_date: date,
    birth_time: str,
    tz_name: str,
    latitude: float,
    longitude: float,
    category: str = "Other",
    from_date: date | None = None,
    days_ahead: int = 90,
) -> FindBestDayResult:
    """
    Find the top 3 best upcoming dates for a given life category.

    Args:
        birth_date … longitude: Birth data for personal chart.
        category:   One of CATEGORIES.
        from_date:  Start of search window (default: today).
        days_ahead: How many days forward to scan (default 90).

    Returns:
        FindBestDayResult with ranked top-3 dates and plain-English reasons.
    """
    if from_date is None:
        from_date = date.today()

    chart = get_birth_chart(birth_date, birth_time, tz_name, latitude, longitude)
    moon  = next(g for g in chart.grahas if g.name == "Moon")
    cat   = category if category in _CFG else "Other"

    candidates: list[tuple[float, date, object, object, object]] = []

    for offset in range(days_ahead):
        d = from_date + timedelta(days=offset)
        p  = get_panchanga(d, tz_name)
        dasha = get_dasha(moon.longitude, birth_date, d)
        tr = get_transits(moon.longitude, chart.lagna.longitude, d, tz_name)

        base, _ = quick_score(moon.longitude, chart.lagna.longitude, birth_date, d, tz_name)
        cs = _cat_score(base, p, tr, cat)
        candidates.append((cs, d, p, tr, dasha))

    # Sort descending; pick top 3 non-consecutive to spread results
    candidates.sort(key=lambda x: x[0], reverse=True)

    results: list[BestDay] = []
    used: set[date] = set()

    for cs, d, p, tr, dasha in candidates:
        if len(results) == 3:
            break
        # Avoid bunching: skip if a date within 2 days already chosen
        if any(abs((d - u).days) < 2 for u in used):
            continue
        results.append(BestDay(
            date=d.isoformat(),
            rank=len(results) + 1,
            score=cs,
            quality=_quality_label(cs),
            reason=_reason(p, tr, dasha, cat, cs),
            tags=_tags(p, tr, dasha),
        ))
        used.add(d)

    return FindBestDayResult(category=cat, days_searched=days_ahead, results=results)

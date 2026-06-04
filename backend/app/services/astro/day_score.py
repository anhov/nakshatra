"""
Day Score — aggregates all five Vedic signals into a single daily summary.

Inputs:
  • Panchanga (Tithi, Vara, Nakshatra, Yoga, Karana)
  • Dasha    (current Maha Dasha + Antardasha)
  • Transits (personal Gochara from Moon, weighted 0-10)
  • Muhurta  (timing windows — Rahu Kala, Choghadiya, Hora, Abhijit)

Outputs:
  • day_score    1–10 float
  • quality      plain-English label ("Excellent" … "Rest Day")
  • tagline      one sentence for the Today screen header
  • activities   4 ActivityCard objects (emoji + title + description + timing)
  • avoid_text   single cautionary note
  • avoid_suggestion  constructive alternative
  • best_times   up to 3 time windows (strings)
  • avoid_times  up to 2 time windows (strings)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from app.services.astro.dasha import DashaResult, get_dasha
from app.services.astro.ephemeris import BirthChart, get_birth_chart
from app.services.astro.muhurta import MuhurtaResult, get_muhurta
from app.services.astro.panchanga import Panchanga, get_panchanga
from app.services.astro.transits import TransitResult, get_transits

# ---------------------------------------------------------------------------
# Scoring tables
# ---------------------------------------------------------------------------

# Tithi quality (1-indexed, 1–30)
_TITHI_SCORE: dict[int, float] = {
    1: 7, 2: 8, 3: 7, 4: 4, 5: 9,
    6: 7, 7: 8, 8: 7, 9: 6, 10: 8,
    11: 9, 12: 8, 13: 7, 14: 4, 15: 9,
    16: 7, 17: 8, 18: 7, 19: 4, 20: 9,
    21: 7, 22: 8, 23: 7, 24: 6, 25: 8,
    26: 9, 27: 8, 28: 7, 29: 4, 30: 5,
}

# Vara quality (English weekday name)
_VARA_SCORE: dict[str, float] = {
    "Sunday": 7, "Monday": 8, "Tuesday": 6,
    "Wednesday": 9, "Thursday": 9, "Friday": 8, "Saturday": 5,
}

# Nakshatra quality (traditional classification)
# Dhruva=9, Mridu=9, Laghu=8, Chara=7, Sadharan=6, Tikshna=5, Ugra=4
_NAK_SCORE: dict[str, float] = {
    "Ashwini": 8, "Bharani": 4, "Krittika": 6,
    "Rohini": 9, "Mrigashira": 8, "Ardra": 5,
    "Punarvasu": 7, "Pushya": 9, "Ashlesha": 5,
    "Magha": 4, "Purva Phalguni": 4, "Uttara Phalguni": 9,
    "Hasta": 8, "Chitra": 8, "Swati": 7,
    "Vishakha": 6, "Anuradha": 8, "Jyeshtha": 5,
    "Mula": 5, "Purva Ashadha": 4, "Uttara Ashadha": 9,
    "Shravana": 7, "Dhanishtha": 7, "Shatabhisha": 7,
    "Purva Bhadrapada": 4, "Uttara Bhadrapada": 9, "Revati": 9,
}

# Yoga quality
_YOGA_SCORE: dict[str, float] = {
    "Vishkambha": 4, "Priti": 9, "Ayushman": 9, "Saubhagya": 9, "Shobhana": 9,
    "Atiganda": 4, "Sukarma": 9, "Dhriti": 9, "Shula": 4, "Ganda": 4,
    "Vriddhi": 8, "Dhruva": 9, "Vyaghata": 4, "Harshana": 9, "Vajra": 5,
    "Siddhi": 9, "Vyatipata": 3, "Variyan": 8, "Parigha": 4, "Shiva": 9,
    "Siddha": 9, "Sadhya": 9, "Shubha": 9, "Shukla": 8, "Brahma": 9,
    "Indra": 9, "Vaidhriti": 3,
}

# Karana quality
_KARANA_SCORE: dict[str, float] = {
    "Bava": 8, "Balava": 8, "Kaulava": 8, "Taitila": 8,
    "Gara": 7, "Vanija": 8, "Vishti": 3,
    "Shakuni": 5, "Chatushpada": 5, "Naga": 5, "Kintughna": 6,
}

# Dasha planet quality (natural benefic/malefic, simplified)
_DASHA_QUALITY: dict[str, float] = {
    "Jupiter": 9.0, "Venus": 8.0, "Moon": 8.0, "Mercury": 7.0,
    "Sun": 6.0, "Mars": 5.5, "Saturn": 5.0, "Rahu": 5.0, "Ketu": 5.0,
}

# Activity blueprints keyed by planet name
_PLANET_ACTIVITY: dict[str, tuple[str, str, str]] = {
    # planet: (emoji, title, description)
    "Jupiter": (
        "📚", "Learning & Growth",
        "Expand your knowledge — study, read, teach, or plan something big. Jupiter's influence makes new ideas stick.",
    ),
    "Venus": (
        "💕", "Relationships & Creativity",
        "Connect with people you love, express yourself creatively, or simply enjoy something beautiful.",
    ),
    "Mercury": (
        "💬", "Communication & Deals",
        "Write that email, have the important conversation, negotiate, or handle paperwork. Your words land well.",
    ),
    "Moon": (
        "🏠", "Home & Intuition",
        "Tend to your home, nurture your relationships, and trust your gut feelings in any decisions today.",
    ),
    "Mars": (
        "⚡", "Energy & Bold Action",
        "Channel Mars's drive — exercise, start that project you've been putting off, or tackle something physical.",
    ),
    "Sun": (
        "🌟", "Career & Visibility",
        "Step forward in your career, make your work visible, or take a leadership role. Today favours confidence.",
    ),
    "Saturn": (
        "🎯", "Discipline & Long-Term Plans",
        "Slow, steady progress wins today. Work on systems, plans, or anything that requires sustained focus.",
    ),
    "Rahu": (
        "🔭", "Innovation & New Horizons",
        "Explore unconventional ideas, technology, or connections outside your usual circle.",
    ),
    "Ketu": (
        "🧘", "Spiritual Practice & Letting Go",
        "Meditate, journal, or release something that no longer serves you. Inner work is the focus.",
    ),
}

# Fallback activities when fewer than 4 favorable planets
_FALLBACK_ACTIVITIES: list[tuple[str, str, str]] = [
    ("🌿", "Rest & Recovery",
     "Give your body and mind a chance to restore. Light walks, healthy meals, and early sleep pay off."),
    ("📓", "Reflection & Planning",
     "Review your goals, write in a journal, or plan next steps. Inner clarity leads to outer results."),
    ("🤝", "Routine & Maintenance",
     "Handle routine responsibilities and maintain what you've already built. Solid, steady effort."),
    ("🙏", "Gratitude & Appreciation",
     "Count your blessings, reconnect with what matters most, and approach the day with a calm heart."),
]

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class ActivityCard:
    emoji: str
    title: str
    description: str
    timing: str | None   # e.g. "Best: 11:10–11:58"


@dataclass
class DayScore:
    date: str
    score: float                 # 1.0–10.0, one decimal
    quality: str                 # "Excellent" … "Rest Day"
    tagline: str                 # one plain-English sentence
    moon_nakshatra: str          # for Today screen medallion
    moon_nakshatra_number: int   # 1–27
    paksha: str                  # "Waxing" | "Waning" | "Full Moon" | "New Moon"
    tithi_label: str             # plain English lunar day
    current_mahadasha: str       # e.g. "Sun period"
    current_antardasha: str      # e.g. "Saturn sub-period"
    activities: list[ActivityCard]
    avoid_text: str              # single "better to avoid" sentence
    avoid_suggestion: str        # constructive what-to-do-instead
    best_times: list[str]        # up to 3 auspicious windows
    avoid_times: list[str]       # up to 2 inauspicious windows
    panchanga_score: float       # component subscores (for debugging / transparency)
    transit_score: float
    dasha_score: float


# ---------------------------------------------------------------------------
# Internal scoring helpers
# ---------------------------------------------------------------------------


def _panchanga_score(p: Panchanga) -> float:
    t = _TITHI_SCORE.get(p.tithi.number, 6.0)
    v = _VARA_SCORE.get(p.vara.english, 6.0)
    n = _NAK_SCORE.get(p.nakshatra.name, 6.0)
    y = _YOGA_SCORE.get(p.yoga.name, 6.0)
    k = _KARANA_SCORE.get(p.karana.name, 6.0)
    # Weights: Tithi 3, Vara 2, Nakshatra 3, Yoga 1, Karana 1  (sum=10)
    return (t * 3 + v * 2 + n * 3 + y + k) / 10


def _dasha_score(d: DashaResult) -> float:
    if not d.active:
        return 6.0
    md = _DASHA_QUALITY.get(d.active.mahadasha, 6.0)
    ad = _DASHA_QUALITY.get(d.active.antardasha, 6.0)
    return round(md * 0.6 + ad * 0.4, 2)


def _combine(p_score: float, t_score: float, d_score: float, tr: TransitResult) -> float:
    raw = p_score * 0.35 + t_score * 0.40 + d_score * 0.25
    # Saturn condition modifiers
    if tr.saturn_watch.has_sade_sati:
        raw -= 1.5
    elif tr.saturn_watch.has_shani_dhaiya:
        raw -= 0.75
    return round(max(1.0, min(10.0, raw)), 1)


def _quality_label(score: float) -> str:
    if score >= 8.5:
        return "Excellent"
    if score >= 7.0:
        return "Very Good"
    if score >= 5.5:
        return "Good"
    if score >= 4.0:
        return "Mixed"
    if score >= 2.5:
        return "Challenging"
    return "Rest Day"


# ---------------------------------------------------------------------------
# Content generation
# ---------------------------------------------------------------------------


def _tithi_label(p: Panchanga) -> str:
    n = p.tithi.number
    if n == 15:
        return "Full Moon"
    if n == 30:
        return "New Moon"
    phase = "waxing" if p.tithi.paksha == "Shukla" else "waning"
    day = n if n <= 15 else n - 15
    return f"Lunar day {day} ({phase})"


def _paksha(p: Panchanga) -> str:
    if p.tithi.number == 15:
        return "Full Moon"
    if p.tithi.number == 30:
        return "New Moon"
    return "Waxing" if p.tithi.paksha == "Shukla" else "Waning"


def _tagline(score: float, quality: str, tr: TransitResult, p: Panchanga, d: DashaResult) -> str:
    fav = tr.favorable_planets
    nak = p.nakshatra.name

    # Special conditions first
    if tr.saturn_watch.has_sade_sati:
        return (
            "Saturn's passage through your Moon sign asks for patience and inner strength — "
            "focus on what you can control and let go of the rest."
        )
    if p.yoga.name in ("Vyatipata", "Vaidhriti"):
        return (
            "Today carries an unusual cosmic intensity — use it for deep inner work "
            "or spiritual practice rather than launching new plans."
        )
    if p.tithi.number in (15,):
        return (
            f"Full Moon energy illuminates {nak}'s themes — emotions and insights run high. "
            "A powerful night for reflection, celebration, or releasing what you've outgrown."
        )
    if p.tithi.number == 30:
        return (
            "New Moon — a quiet, introspective day ideal for rest, ancestors, and setting "
            "intentions for the cycle ahead."
        )

    # Score-based taglines
    md_label = d.active.mahadasha if d.active else "current"
    ad_label = d.active.antardasha if d.active else "present"
    top2 = ", ".join(fav[:2]).lower() if len(fav) >= 2 else "positive"

    if score >= 8.5:
        return (
            f"An exceptionally auspicious day — {nak}'s energy supports {top2} matters, "
            f"and your {md_label} period is working in your favour."
        )
    if score >= 7.0:
        return (
            f"A very good day overall, with {top2} energy flowing freely. "
            f"Your {md_label}–{ad_label} period adds a steady background tone."
        )
    if score >= 5.5:
        avd = tr.challenging_planets[0].lower() if tr.challenging_planets else "a few"
        return (
            f"{nak} brings grounded, capable energy. Lean into {top2 or 'your strengths'} "
            f"and take {avd}'s friction in stride."
        )
    if score >= 4.0:
        return (
            f"A more measured day — pace yourself and focus on what matters most. "
            f"Small, thoughtful steps work better than big pushes right now."
        )
    return (
        "A quiet, introspective day — rest, reflect, and restore. "
        "The tide turns; tomorrow is likely brighter."
    )


def _select_activities(tr: TransitResult, p: Panchanga, best_time: str | None) -> list[ActivityCard]:
    """Pick 4 ActivityCards from favorable planets, falling back to nakshatra/generic."""
    # Prioritise by weight (heaviest planets first)
    ordered_fav = sorted(
        [pl for pl in tr.planets if pl.is_favorable],
        key=lambda x: x.weight,
        reverse=True,
    )
    cards: list[ActivityCard] = []
    seen_titles: set[str] = set()

    for pl in ordered_fav:
        if pl.name in _PLANET_ACTIVITY:
            emoji, title, desc = _PLANET_ACTIVITY[pl.name]
            if title not in seen_titles:
                cards.append(ActivityCard(emoji=emoji, title=title, description=desc, timing=best_time))
                seen_titles.add(title)
        if len(cards) == 4:
            break

    # Fill remaining slots with fallback activities
    for emoji, title, desc in _FALLBACK_ACTIVITIES:
        if len(cards) >= 4:
            break
        if title not in seen_titles:
            cards.append(ActivityCard(emoji=emoji, title=title, description=desc, timing=None))
            seen_titles.add(title)

    return cards[:4]


def _avoid_content(tr: TransitResult, p: Panchanga) -> tuple[str, str]:
    """Return (avoid_text, avoid_suggestion)."""
    parts: list[str] = []

    # Vishti (Bhadra) Karana
    if p.karana.name == "Vishti":
        parts.append("starting anything new during Vishti Karana (Bhadra)")

    # Inauspicious Yoga
    if p.yoga.name in ("Vyatipata", "Vaidhriti"):
        parts.append(f"launching important plans while {p.yoga.name} yoga is active")

    # Rikta tithi
    if p.tithi.number in (4, 9, 14, 19, 24, 29):
        parts.append("signing contracts or major financial commitments")

    # Heavy challenging transits
    heavy = [pl.name for pl in tr.planets if not pl.is_favorable and pl.weight >= 2]
    if "Jupiter" in heavy:
        parts.append("overextending yourself or chasing unrealistic opportunities")
    if "Saturn" in heavy:
        parts.append("rushing important decisions — Saturn's friction rewards patience")

    if not parts:
        parts.append("overcommitting or starting too many things at once")

    avoid_text = "Better to avoid " + parts[0] + "."
    suggestion_map = {
        "starting anything new during Vishti Karana (Bhadra)":
            "Wait for Bhadra to pass (check end time above), then proceed with your plans.",
        f"launching important plans while {p.yoga.name} yoga is active":
            "Channel this intense energy into deep focus or spiritual practice instead.",
        "signing contracts or major financial commitments":
            "Use today to review terms carefully; sign when the tithi improves.",
        "overextending yourself or chasing unrealistic opportunities":
            "Focus on consolidating existing gains rather than expanding right now.",
        "rushing important decisions — Saturn's friction rewards patience":
            "Give important matters more time — a decision made in 3 days will be stronger.",
        "overcommitting or starting too many things at once":
            "Pick one priority and move it forward with full attention.",
    }
    suggestion = suggestion_map.get(parts[0], "Take it one step at a time — steady wins the day.")
    return avoid_text, suggestion


def _timing_windows(m: MuhurtaResult, tr: TransitResult) -> tuple[list[str], list[str]]:
    """Return (best_times, avoid_times)."""
    # Build Rahu Kala span for overlap check
    rk_start = m.rahu_kala.start[11:16]
    rk_end   = m.rahu_kala.end[11:16]

    best: list[str] = []
    # Abhijit is almost always safe
    best.append(f"Abhijit Muhurta: {m.abhijit.start[11:16]}–{m.abhijit.end[11:16]}")

    # Best daytime Choghadiya (Amrit/Shubh that don't overlap with Rahu Kala)
    for c in m.choghadiyas_day:
        if c.quality in ("Excellent", "Good") and c.start[11:16] != rk_start:
            best.append(f"{c.name}: {c.start[11:16]}–{c.end[11:16]}")
        if len(best) == 3:
            break

    avoid: list[str] = [
        f"Rahu Kala: {rk_start}–{rk_end}",
        f"Gulika Kala: {m.gulika_kala.start[11:16]}–{m.gulika_kala.end[11:16]}",
    ]
    return best[:3], avoid[:2]


# ---------------------------------------------------------------------------
# Public API — lightweight batch scorer (no muhurta; used by month view / find-best-day)
# ---------------------------------------------------------------------------


def quick_score(
    moon_lon: float,
    lagna_lon: float,
    birth_date: date,
    query_date: date,
    tz_name: str,
) -> tuple[float, str]:
    """
    Compute day score without muhurta, for batch operations.
    Returns (score 1-10, quality label).
    """
    p  = get_panchanga(query_date, tz_name)
    d  = get_dasha(moon_lon, birth_date, query_date)
    tr = get_transits(moon_lon, lagna_lon, query_date, tz_name)

    p_s = _panchanga_score(p)
    d_s = _dasha_score(d)
    t_s = tr.transit_score
    score = _combine(p_s, t_s, d_s, tr)
    return score, _quality_label(score)


# ---------------------------------------------------------------------------
# Public API — full score with content
# ---------------------------------------------------------------------------


def get_day_score(
    birth_date: date,
    birth_time: str,
    tz_name: str,
    latitude: float,
    longitude: float,
    query_date: date | None = None,
) -> DayScore:
    """
    Calculate the complete daily summary for the Today screen.

    Args:
        birth_date:  Date of birth.
        birth_time:  Local time of birth as "HH:MM".
        tz_name:     IANA timezone, e.g. "Asia/Kolkata".
        latitude:    Birth / current location latitude.
        longitude:   Birth / current location longitude.
        query_date:  Date to score (default: today).

    Returns:
        DayScore with score, tagline, 4 activity cards, and timing windows.
    """
    if query_date is None:
        query_date = date.today()

    # ── Gather all signals ────────────────────────────────────────────────
    chart: BirthChart = get_birth_chart(birth_date, birth_time, tz_name, latitude, longitude)
    moon_graha = next(g for g in chart.grahas if g.name == "Moon")

    p:  Panchanga     = get_panchanga(query_date, tz_name)
    d:  DashaResult   = get_dasha(moon_graha.longitude, birth_date, query_date)
    tr: TransitResult = get_transits(
        moon_graha.longitude, chart.lagna.longitude, query_date, tz_name
    )
    m:  MuhurtaResult = get_muhurta(query_date, tz_name, latitude, longitude)

    # ── Score ─────────────────────────────────────────────────────────────
    p_score = round(_panchanga_score(p), 2)
    d_score = _dasha_score(d)
    t_score = tr.transit_score
    score   = _combine(p_score, t_score, d_score, tr)
    quality = _quality_label(score)

    # ── Content ───────────────────────────────────────────────────────────
    best_times, avoid_times = _timing_windows(m, tr)
    best_time_str = best_times[0] if best_times else None

    tagline  = _tagline(score, quality, tr, p, d)
    cards    = _select_activities(tr, p, best_time_str)
    avoid_text, avoid_suggestion = _avoid_content(tr, p)

    md_label = f"{d.active.mahadasha} period" if d.active else "—"
    ad_label = f"{d.active.antardasha} sub-period" if d.active else "—"

    return DayScore(
        date=query_date.isoformat(),
        score=score,
        quality=quality,
        tagline=tagline,
        moon_nakshatra=p.nakshatra.name,
        moon_nakshatra_number=p.nakshatra.number,
        paksha=_paksha(p),
        tithi_label=_tithi_label(p),
        current_mahadasha=md_label,
        current_antardasha=ad_label,
        activities=cards,
        avoid_text=avoid_text,
        avoid_suggestion=avoid_suggestion,
        best_times=best_times,
        avoid_times=avoid_times,
        panchanga_score=p_score,
        transit_score=t_score,
        dasha_score=d_score,
    )

"""
Month view — lightweight day scores for every day in a calendar month.

Returns a color-coded summary used by the Calendar screen.
Birth chart is computed once; each day needs only panchanga + dasha + transits.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date

from app.services.astro.day_score import quick_score
from app.services.astro.ephemeris import get_birth_chart

_COLOR: dict[str, str] = {
    "Excellent":  "#2D6A4F",
    "Very Good":  "#52B788",
    "Good":       "#74C69D",
    "Mixed":      "#F4A261",
    "Challenging":"#E76F51",
    "Rest Day":   "#AE2012",
}


@dataclass
class DaySummary:
    date: str
    score: float
    quality: str
    color: str


@dataclass
class MonthSummary:
    year: int
    month: int
    days: list[DaySummary]


def get_month_summary(
    birth_date: date,
    birth_time: str,
    tz_name: str,
    latitude: float,
    longitude: float,
    year: int,
    month: int,
) -> MonthSummary:
    """Compute day scores for every day in a month."""
    chart = get_birth_chart(birth_date, birth_time, tz_name, latitude, longitude)
    moon  = next(g for g in chart.grahas if g.name == "Moon")

    _, days_in_month = calendar.monthrange(year, month)
    summaries: list[DaySummary] = []

    for day in range(1, days_in_month + 1):
        d = date(year, month, day)
        score, quality = quick_score(
            moon.longitude, chart.lagna.longitude, birth_date, d, tz_name
        )
        summaries.append(DaySummary(
            date=d.isoformat(),
            score=score,
            quality=quality,
            color=_COLOR.get(quality, "#F4A261"),
        ))

    return MonthSummary(year=year, month=month, days=summaries)

"""
Calendar event labelling.

Receives a list of calendar events (title + datetime range) and returns
each event labelled as Good / Okay / Reschedule based on:
  1. Day score for that date
  2. Whether the event time overlaps Rahu Kala or Gulika Kala
  3. Choghadiya quality at the event start time

Calendar data is NEVER stored — it is processed and discarded per request.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from app.services.astro.day_score import quick_score
from app.services.astro.ephemeris import get_birth_chart
from app.services.astro.muhurta import MuhurtaResult, get_muhurta, TimeWindow

# ── Dataclasses ───────────────────────────────────────────────────────────────


@dataclass
class CalendarEvent:
    id: str
    title: str
    start: str   # ISO-8601 in local timezone
    end: str


@dataclass
class LabelledEvent:
    id: str
    title: str
    start: str
    end: str
    label: str    # "Good" | "Okay" | "Reschedule"
    emoji: str    # ✓  ~  ↓
    reason: str


# ── Internal helpers ──────────────────────────────────────────────────────────


def _overlaps(event_start: datetime, event_end: datetime, window: TimeWindow) -> bool:
    """Return True if event overlaps the given TimeWindow."""
    try:
        tz = event_start.tzinfo
        ws = datetime.fromisoformat(window.start).astimezone(tz)
        we = datetime.fromisoformat(window.end).astimezone(tz)
        return event_start < we and event_end > ws
    except Exception:
        return False


def _choghadiya_quality(event_start: datetime, m: MuhurtaResult) -> str:
    """Return the Choghadiya quality ('Excellent', 'Good', 'Neutral', 'Avoid') at event start."""
    for c in m.choghadiyas_day + m.choghadiyas_night:
        try:
            tz = event_start.tzinfo
            cs = datetime.fromisoformat(c.start).astimezone(tz)
            ce = datetime.fromisoformat(c.end).astimezone(tz)
            if cs <= event_start < ce:
                return c.quality
        except Exception:
            continue
    return "Neutral"


def _label_event(
    event: CalendarEvent,
    day_score: float,
    quality: str,
    m: MuhurtaResult,
) -> LabelledEvent:
    start = datetime.fromisoformat(event.start)
    end   = datetime.fromisoformat(event.end)

    # Check inauspicious overlaps
    rahu_overlap   = _overlaps(start, end, m.rahu_kala)
    gulika_overlap = _overlaps(start, end, m.gulika_kala)
    yama_overlap   = _overlaps(start, end, m.yama_ganda)
    chog           = _choghadiya_quality(start, m)

    if rahu_overlap:
        return LabelledEvent(
            **event.__dict__,
            label="Reschedule", emoji="↓",
            reason="Falls during Rahu Kala — try to move this to a different time if possible.",
        )
    if gulika_overlap or yama_overlap:
        return LabelledEvent(
            **event.__dict__,
            label="Okay", emoji="~",
            reason="Overlaps a minor inauspicious period. Proceed with care.",
        )
    if chog == "Avoid":
        return LabelledEvent(
            **event.__dict__,
            label="Okay", emoji="~",
            reason=f"Choghadiya at this time is less favourable. Still workable.",
        )

    # Day-score based label
    if day_score >= 7.0 and chog in ("Excellent", "Good"):
        return LabelledEvent(
            **event.__dict__,
            label="Good", emoji="✓",
            reason=f"Great timing — {quality.lower()} day energy and a favourable window.",
        )
    if day_score >= 5.5:
        return LabelledEvent(
            **event.__dict__,
            label="Good", emoji="✓",
            reason=f"Good day overall — this time works well.",
        )
    if day_score >= 4.0:
        return LabelledEvent(
            **event.__dict__,
            label="Okay", emoji="~",
            reason=f"Mixed energy day. This event can go ahead; keep expectations flexible.",
        )
    return LabelledEvent(
        **event.__dict__,
        label="Reschedule", emoji="↓",
        reason="Challenging day energy. Consider moving this to a higher-scoring date if you can.",
    )


# ── Public API ────────────────────────────────────────────────────────────────


def label_events(
    events: list[CalendarEvent],
    birth_date,
    birth_time: str,
    tz_name: str,
    latitude: float,
    longitude: float,
) -> list[LabelledEvent]:
    """
    Label calendar events as Good / Okay / Reschedule.

    Events are read, processed, and never stored.
    """
    if not events:
        return []

    chart = get_birth_chart(birth_date, birth_time, tz_name, latitude, longitude)
    moon  = next(g for g in chart.grahas if g.name == "Moon")

    # Compute day scores and muhurta once per unique date
    dates = {e.start.split("T")[0] for e in events}
    from datetime import date as _date
    scores:   dict[str, tuple[float, str]] = {}
    muhurtas: dict[str, MuhurtaResult]     = {}

    for ds in dates:
        d = _date.fromisoformat(ds)
        scores[ds]   = quick_score(moon.longitude, chart.lagna.longitude, birth_date, d, tz_name)
        muhurtas[ds] = get_muhurta(d, tz_name, latitude, longitude)

    return [
        _label_event(ev, *scores[ev.start.split("T")[0]], muhurtas[ev.start.split("T")[0]])
        for ev in events
    ]

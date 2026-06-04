"""
Ekadashi service — detect Ekadashi dates and return names + meanings.

Ekadashi = 11th tithi (Shukla) or 26th tithi (Krishna), occurring twice monthly.
The name is determined by the solar month (Sun's sidereal sign) and paksha.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

import swisseph as swe

from app.services.astro.panchanga import get_panchanga

# ---------------------------------------------------------------------------
# Ekadashi name table: (solar_month 1-12, paksha) → name + meaning
# solar_month: 1=Chaitra(Aries) … 12=Phalguna(Pisces)
# ---------------------------------------------------------------------------

_NAMES: dict[tuple[int, str], tuple[str, str]] = {
    (1,  "Shukla"):  ("Kamada Ekadashi",       "The wish-fulfilling fast that removes sins and grants blessings."),
    (1,  "Krishna"): ("Papamochani Ekadashi",   "Liberates from all sins accumulated in this and past lives."),
    (2,  "Shukla"):  ("Mohini Ekadashi",        "Destroys illusion and grants liberation; favoured by Vishnu."),
    (2,  "Krishna"): ("Varuthini Ekadashi",     "Grants spiritual protection and removes fear of death."),
    (3,  "Shukla"):  ("Nirjala Ekadashi",       "The most potent fast — no water for 24 hours earns the merit of all Ekadashis."),
    (3,  "Krishna"): ("Apara Ekadashi",         "Removes infamy and grants fame, wealth, and liberation."),
    (4,  "Shukla"):  ("Devshayani Ekadashi",    "Vishnu enters cosmic sleep; a day for deep devotion and inner retreat."),
    (4,  "Krishna"): ("Yogini Ekadashi",        "Frees from disease and bestows health, wealth, and happiness."),
    (5,  "Shukla"):  ("Putrada Ekadashi",       "Blesses families with children, love, and continuity."),
    (5,  "Krishna"): ("Aja Ekadashi",           "Removes sins from multiple past lives and grants liberation."),
    (6,  "Shukla"):  ("Parsva Ekadashi",        "Vishnu turns in his cosmic sleep; sacred for devotion and charity."),
    (6,  "Krishna"): ("Indira Ekadashi",        "Liberates ancestors from the lower planes; perform ancestral rites."),
    (7,  "Shukla"):  ("Papankusha Ekadashi",    "Removes the greatest sins and grants entry into higher realms."),
    (7,  "Krishna"): ("Rama Ekadashi",          "Beloved of Rama; brings joy, prosperity, and liberation."),
    (8,  "Shukla"):  ("Devutthana Ekadashi",    "Vishnu awakens from cosmic sleep; the most auspicious day of the year."),
    (8,  "Krishna"): ("Utpanna Ekadashi",       "The birth of Ekadashi as a sacred vow; honours its divine origin."),
    (9,  "Shukla"):  ("Mokshada Ekadashi",      "Grants liberation to devotees and their ancestors; day of the Bhagavad Gita."),
    (9,  "Krishna"): ("Saphala Ekadashi",       "Makes all endeavours fruitful and removes obstacles."),
    (10, "Shukla"):  ("Putrada Ekadashi",       "The second Putrada — brings joy, children, and family harmony."),
    (10, "Krishna"): ("Sat-tila Ekadashi",      "Sesame seed rituals remove sins; generous charity brings merit."),
    (11, "Shukla"):  ("Jaya Ekadashi",          "Grants victory over enemies, inner demons, and all obstacles."),
    (11, "Krishna"): ("Vijaya Ekadashi",        "The victory fast — ensures success in all righteous pursuits."),
    (12, "Shukla"):  ("Amalaki Ekadashi",       "Sacred to the Amla tree (Vishnu's favourite); grants long life and prosperity."),
    (12, "Krishna"): ("Papamochani Ekadashi",   "Removes sins and purifies the soul at the close of the lunar year."),
}


@dataclass
class EkadashiInfo:
    date: str
    name: str
    paksha: str          # "Shukla" or "Krishna"
    meaning: str
    guidance: str        # plain-English practical guidance


def _guidance(name: str, paksha: str) -> str:
    base = (
        "A sacred day for fasting, prayer, and inner reflection. "
        "Avoid meat, alcohol, and unnecessary conflict. "
    )
    if "Nirjala" in name:
        return base + "Observe a waterless fast if possible — it carries the merit of all Ekadashis."
    if "Devshayani" in name or "Parsva" in name or "Devutthana" in name:
        return base + "Vishnu's cosmic sleep makes this especially powerful for chanting and meditation."
    if "Indira" in name:
        return base + "Perform ancestral prayers (Tarpan) to bring peace to departed souls."
    if "Mokshada" in name:
        return base + "Read from the Bhagavad Gita — this is the day it was spoken."
    return base + "Chanting, charity, and keeping the mind calm bring the greatest benefit."


def _solar_month(target_date: date, tz_name: str) -> int:
    """Return the solar month index 1-12 (Aries=1 … Pisces=12)."""
    from zoneinfo import ZoneInfo
    from datetime import datetime, timezone
    tz_obj = ZoneInfo(tz_name)
    dt = datetime(target_date.year, target_date.month, target_date.day, 6, 0, 0, tzinfo=tz_obj)
    utc = dt.astimezone(timezone.utc)
    jd = swe.julday(utc.year, utc.month, utc.day,
                    utc.hour + utc.minute / 60 + utc.second / 3600)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    sun, _ = swe.calc_ut(jd, swe.SUN, flags)
    return int(sun[0] / 30) % 12 + 1  # 1=Aries … 12=Pisces


def get_ekadashi(target_date: date, tz_name: str) -> EkadashiInfo | None:
    """
    If target_date is an Ekadashi, return its name and meaning. Otherwise None.
    """
    p = get_panchanga(target_date, tz_name)
    if p.tithi.number not in (11, 26):
        return None

    paksha = "Shukla" if p.tithi.number == 11 else "Krishna"
    solar_m = _solar_month(target_date, tz_name)
    name, meaning = _NAMES.get((solar_m, paksha), ("Ekadashi", "A sacred lunar fast day."))

    return EkadashiInfo(
        date=target_date.isoformat(),
        name=name,
        paksha=paksha,
        meaning=meaning,
        guidance=_guidance(name, paksha),
    )


def get_upcoming_ekadashis(
    tz_name: str,
    from_date: date | None = None,
    count: int = 6,
) -> list[EkadashiInfo]:
    """Return the next `count` Ekadashi dates from from_date."""
    if from_date is None:
        from_date = date.today()

    results: list[EkadashiInfo] = []
    d = from_date
    while len(results) < count:
        ek = get_ekadashi(d, tz_name)
        if ek:
            results.append(ek)
            d += timedelta(days=5)   # skip ahead to avoid double-counting same tithi
        else:
            d += timedelta(days=1)
        if (d - from_date).days > 400:   # safety guard
            break
    return results

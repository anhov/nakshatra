# Nakshatra — Claude Code Instructions

## Project
Vedic astrology mobile app. React Native frontend + Python FastAPI backend.

## Rules
1. All astrological calculations via pyswisseph only — never approximate or hardcode
2. Zero jargon in user-facing strings — plain English always
3. Design tokens: cream `#F6F0E6` bg, ink `#221A10` text, gold `#C4963A` accent
4. Calendar data never persisted to database — read, process, discard
5. Birth data always encrypted (AES-256 at rest, TLS in transit)
6. Every API endpoint must validate birth data completeness before calculating
7. Ayanamsha: Lahiri (SIDM_LAHIRI). House system: Whole Sign. Accuracy target: ±1 arc-minute vs Jagannatha Hora

## Stack
- Backend: Python 3.11+ · FastAPI · pyswisseph 2.10+ · PostgreSQL · Redis
- Mobile: React Native (iOS + Android)
- Auth: Apple Sign-In + Google Sign-In + email/password
- Push: Firebase Cloud Messaging

## File Structure
```
/backend
  /app
    /routers          # FastAPI route handlers
    /services
      /astro          # All pyswisseph calculation modules
      /calendar       # Calendar integration logic
      /content        # Affirmations, mantras, content delivery
    /models           # SQLAlchemy models
    /schemas          # Pydantic schemas
  /tests

/mobile
  /src
    /screens          # Today, Calendar, FindDay, MyChart, Onboarding
    /components       # Shared UI components
    /services         # API calls
    /assets           # SVG illustrations (27 nakshatra medallions)
```

## Key Services — MVP Build Order
1. `astro/ephemeris.py`  — birth chart D-1 via Swiss Ephemeris
2. `astro/panchanga.py`  — Tithi, Vara, Nakshatra, Yoga, Karana  ✅ done
3. `astro/dasha.py`      — Vimshottari Dasha (major + sub-period)
4. `astro/transits.py`   — personal daily transits for all 9 grahas
5. `astro/muhurta.py`    — Rahu Kala, Choghadiya, Abhijit, Hora
6. `astro/day_score.py`  — aggregate daily score 1–10 + plain English output
7. `calendar/sync.py`    — read and label user calendar events
8. `content/affirmations.py` — select daily affirmation by Dasha + day quality
9. `content/mantras.py`  — select mantra by Dasha lord + Moon nakshatra
10. `content/ekadashi.py` — detect Ekadashi dates + guidance card

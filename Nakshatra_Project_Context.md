# Nakshatra — Project Context & Agent Configuration
> Full conversation summary · June 2025 · v1.0

---

## 1. Product Overview

**Nakshatra** is a personal Vedic astrology planner — a mobile app (iOS + Android) that:
- Syncs with the user's Google / Apple Calendar
- Calculates auspicious and inauspicious days **personally** for each user based on their birth chart
- Speaks **plain language only** — zero astrological jargon visible to the user
- Covers all areas of life: work, health, finances, relationships, travel, spirituality

**Core promise:** "Every day is favourable for something. Find out what — for you personally."

---

## 2. Product Decisions Made

| Decision | Choice |
|---|---|
| App name | **Nakshatra** |
| Platform | Mobile (iOS + Android) — React Native or Flutter |
| Target audience | Women 25–45, wellness/spirituality, any time of day usage |
| Language | **English** (primary) |
| Design style | Editorial / Vintage Minimal (cream background, thin serif fonts, gold accents, vintage celestial illustrations) |
| Colour palette | Cream `#F6F0E6` + Dark Ink `#221A10` + Gold `#C4963A` — light theme |
| Typography | Cormorant Garamond (headings, italic) + Jost (body) |
| Astro engine | Swiss Ephemeris via pyswisseph (Python backend) |
| Monetisation | Free / Premium $7.99/mo / Jyotishi Pro $19.99/mo |

---

## 3. Design Reference

User uploaded a reference image (book tracker app "Margin") with this aesthetic:
- Warm cream/ivory background `#F5F0E8`
- Dark ink typography (no pure black)
- Vintage engravings / line illustrations
- Cormorant Garamond serif for headlines
- Thin clean sans-serif for body
- Gold/amber highlight accent
- Lots of white space ("breathing room")
- Minimal — very few elements per screen

**DO NOT use:** pure white `#FFFFFF`, pure black `#000000`, harsh contrast, bullet-heavy UI, neon colours, dark purple/navy backgrounds (user rejected that palette).

---

## 4. App Screens (all designed and prototyped)

### Screen 1 — Today (Home)
- Greeting: "Good morning, [Name]"
- Date display
- Vintage celestial medallion SVG (changes with Moon nakshatra)
- Day tagline: plain English sentence
- Day score strip: X/10 + quality label + Moon nakshatra
- Favourable activities grid (4 cards): emoji + title + description + timing badge
- "Better to avoid" warning strip (amber/red tone, supportive language)
- Calendar events from user's calendar: each labelled ✓ Good / ~ Okay / ↓ Consider rescheduling

### Screen 2 — Calendar
- Month view with colour-coded days:
  - Dark green: Excellent
  - Light green: Good
  - Amber: Caution
  - Muted red: Rest day
  - Dark circle: Today
- Tap any day → detail card: date, quality, favourable activities tags, one avoid note
- Legend below calendar

### Screen 3 — Find Best Day
- Headline: "Find Your Best Day"
- Category grid (6 visible, 15 total): Travel, Contracts, Medical, Relationships, Moving, New Project, Interview, Surgery, Investment, Wedding, Meeting, Creative Work, Learning, Spiritual Practice, Other
- Select category → Top 3 best upcoming dates with rank number, date, plain-English reason, tags

### Screen 4 — My Chart
- Year band (dark background): current year theme + Dasha description
- Current Life Period card: Major Dasha, Sub-period, Theme + progress bar
- Birth Chart card: Rising Sign, Moon Sign, Sun Sign, Birth Star (Nakshatra)
- Planetary Positions card: all 9 grahas with house, sign, strength label (strong/mixed/weak)

### Screen 5 — Onboarding (3 steps)
- Step 1: Birth details — date, time, place (with "I don't know exact time" option)
- Step 2: Connect calendar (Google / Apple)
- Step 3: Notification preferences
- Progress dots at bottom

---

## 5. Full Feature List (from PRD)

### MVP (0–3 months)
- Birth chart D-1 via Swiss Ephemeris
- Navamsha D-9
- Panchanga (Tithi, Vara, Nakshatra, Yoga, Karana)
- Vimshottari Dasha (major + sub-period)
- Personal transits for all 9 grahas
- Muhurta windows: Rahu Kala, Gulika, Yama Ganda, Abhijit, Hora, Choghadiya
- Day score (1–10) + plain English headline
- Favourable activities grid
- Calendar read sync (Google + Apple)
- Event labelling: Good / Caution / Reschedule
- Month view colour map
- Find Best Day (15 categories, top 3 results)
- **Ekadashi highlights** — name, meaning, push notification eve before
- **Daily affirmation** tied to Dasha theme and day quality
- **Moon nakshatra daily card** — plain English energy theme
- **Planetary mantra** for Dasha lord + Moon nakshatra with YouTube/Spotify link
- Morning push notification (customisable time)
- Onboarding (3-step) with birth time unknown flow
- Vintage celestial illustration (27 variants for each nakshatra)

### v1.0 (3–6 months)
- Ashtakavarga transit scoring
- Tajaka Varshaphala (annual chart) with all Tajaka yogas:
  - Itthashala, Isarafa, Muthasila, Nakta, Kambula, Duhphali Kuttha, Rutha/Mutha, Varshesha, Muntha, Pancha
- Sade Sati tracker (7.5-year Saturn transit)
- Yogini Dasha (secondary system)
- Pratyantara Dasha (level 3)
- Audio mantra pronunciation
- Weekly remedy plan (colour + food + charity + mantra)
- Deity of the day (by Vara)
- New moon intention prompts / Full moon ritual guidance
- Journal prompts (365 unique, tied to astro themes)
- Weekly Sunday digest notification
- Dasha change notification
- App Store public launch

### v2.0 (6–12 months)
- AI affirmation personalisation (LLM-generated, personal to user)
- Mood tracker + compare with transits over time
- Gemstone / crystal guidance by transits
- D-9 Navamsha + D-10 Dashamsha charts with summaries
- Multiple profiles (family members)
- Synastry / compatibility between two charts
- PDF export — full natal report
- iOS/Android home screen widget
- B2B API for Jyotish practitioners

### v3.0 (12–24 months)
- Full D-60 chart set (D-1 to D-60)
- Jaimini Chara Dasha
- Prasna (horary astrology)
- Community features
- White-label licensing
- Hindi language support

---

## 6. Astrological Systems to Implement

All calculations via **Swiss Ephemeris** (C library) + **pyswisseph** (Python wrapper).

### Core Engine
- Ayanamsha: **Lahiri / Chitrapaksha** (default)
- House system: **Whole Sign** (default)
- 9 Grahas: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu

### Panchanga (daily 5 elements)
- Tithi (1–30 lunar days)
- Vara (weekday, planetary ruler)
- Nakshatra (Moon's nakshatra, 1–27)
- Yoga (27 yogas: Sun + Moon longitude sum)
- Karana (half-tithi, 11 types, changes 2× per day)

### Dasha Systems
- **Vimshottari Dasha** — primary, 120-year cycle
- Antardasha (sub-period)
- Pratyantara Dasha (sub-sub-period)
- Sukshma Dasha (level 4)
- Yogini Dasha — secondary, 36-year cycle
- Jaimini Chara Dasha — v3.0

### Muhurta (timing)
- Rahu Kala (1.5 hrs/day, varies by weekday)
- Yama Ganda
- Gulika Kala
- Abhijit Muhurta (midday window)
- Hora (planetary hours)
- Choghadiya: Amrit, Shubh, Labh, Char (good) / Rog, Kal, Udveg (avoid)
- Brahma Muhurta (48 min before sunrise)

### Tajaka System (annual chart)
- Varshaphala (Solar Return chart)
- Varshesha (year lord)
- Muntha (sensitive point = 1° × age from Lagna)
- Pancha (5 key planets of the year)
- All 10 Tajaka yogas

### Transits
- Personal transits of all 9 grahas
- Ashtakavarga (point-based transit strength)
- Gochara-phala (planet-in-sign relative to Moon)
- Sade Sati (Saturn over Moon — 3 phases)
- Shani Dhaiya (Saturn over 4th and 8th from Moon)
- Retrograde planet effects

### Divisional Charts (Vargas)
- D-1 Rashi (main) — MVP
- D-9 Navamsha (marriage/dharma) — MVP
- D-10 Dashamsha (career) — v2.0
- D-2 through D-60 — v3.0

### Shad Bala (planetary strength)
- Sthana Bala, Dig Bala, Kala Bala, Cheshta Bala, Naisargika Bala, Drik Bala — v2.0

### Special Lagnas
- Chandra Lagna, Surya Lagna
- Arudha Lagna, Upapada Lagna
- Hora Lagna, Ghati Lagna, Bhava Lagna

### Sacred Calendar
- Ekadashi (twice monthly — 11th tithi waxing + waning)
- Purnima (Full Moon) + Amavasya (New Moon)
- Pradosh Vrat (13th tithi)
- Solar/Lunar eclipses
- Major Vedic festivals (Navratri, Diwali, Shivaratri, Holi, etc.)

---

## 7. Content Library Requirements

| Content Type | Volume | Phase |
|---|---|---|
| Affirmations by Dasha planet | 50+ × 9 = 450+ | MVP |
| Nakshatra daily cards | 27 | MVP |
| Planetary mantras | 9 (with phonetics + YouTube link) | MVP |
| Nakshatra mantras | 27 | MVP |
| Ekadashi names + meanings | 24/year | MVP |
| Vedic festival descriptions | 20+ | v1.0 |
| Journal prompts | 365 (mapped to astro themes) | v1.0 |
| Remedy library | 9 planets × 5 items = 45 | v1.0 |
| Deity descriptions (Vara) | 7 | v1.0 |

**Tone rules for all content:**
- Zero Sanskrit terminology visible to user
- Warm, supportive, non-alarming — even for difficult days
- Every "challenging" indicator MUST include a constructive suggestion
- Max reading level: Grade 8

---

## 8. Rectification Feature (Birth Time Unknown)

Users who don't know their exact birth time can use the **Rectification Flow**:

### Method A — Life Events (primary)
User answers 10–15 questions about key life events with dates:
- First serious relationship
- First major career success / loss
- Health challenges
- Major move or relocation
- Loss of a parent
- Marriage / divorce
- Children born

System tests all possible birth times within stated interval → finds time where most events align with Dasha activations and house transits.

### Method B — Lagna by Appearance/Personality
- Each Lagna changes every ~2 hours
- Show user 2–3 possible Lagna descriptions
- Ask: leadership vs. peacemaker? Slim vs. sturdy build? Practical vs. dreamy?
- Narrow down most likely Lagna → infer birth time range

**Important UX note:** Always show "approximate time" disclaimer. Most features (Dasha, transits, Ekadashi) work even without exact birth time.

---

## 9. Market Research — User Complaints to Avoid

Researched real user reviews from AstroTalk, Align27, Co-Star, Cosmic Insights, Auraly.

| Competitor Problem | Nakshatra Solution |
|---|---|
| Generic predictions not tied to birth chart | 100% personal Swiss Ephemeris calculation |
| Fear-based upselling, manipulation | Fixed subscription, supportive tone only |
| Impossible to cancel, hidden charges | Standard App Store / Play Store subscription |
| Too complex — requires existing Jyotish knowledge | Zero terminology, plain English throughout |
| Confusing: Vedic vs Western zodiac signs | Clear onboarding explanation |
| Pay separately for every small feature | All features included in one tier |
| Scary predictions with no guidance | Every warning includes what TO do instead |
| No audio for mantras — can't pronounce | Audio + YouTube link from MVP |
| Wrong planetary positions / inaccurate calculations | Swiss Ephemeris — gold standard accuracy |
| No customer support | Standard App Store channels + in-app FAQ |

---

## 10. Technical Stack

### Backend
- Language: **Python 3.11+**
- Framework: **FastAPI**
- Astro library: **pyswisseph** (Swiss Ephemeris Python wrapper)
- Database: **PostgreSQL**
- Cache: **Redis** (cache daily calculations per user)
- Auth: Apple Sign-In + Google Sign-In + email/password

### Mobile
- Framework: **React Native** or **Flutter** (TBD)
- Calendar: EventKit (iOS) + CalendarContract (Android) + Google Calendar API (OAuth 2.0)
- Push: **Firebase Cloud Messaging (FCM)**
- Offline: SQLite local cache for today's data

### Infrastructure
- All astrological calculations run **server-side** (never on device)
- Accuracy requirement: match Jagannatha Hora output within ±1 arc-minute
- Ayanamsha: Lahiri (default)

### Privacy
- Birth data encrypted at rest (AES-256) + in transit (TLS 1.3)
- Calendar data NEVER stored on server — read locally, processed, discarded
- GDPR + CCPA compliant

---

## 11. Claude Code Agent Configuration

### What the agent needs to know

```
You are the lead developer for Nakshatra — a Vedic astrology mobile app.

PRODUCT CONTEXT:
- App name: Nakshatra
- Platform: React Native (iOS + Android)
- Backend: Python FastAPI + pyswisseph (Swiss Ephemeris)
- Database: PostgreSQL + Redis cache
- Calendar: EventKit (iOS), CalendarContract (Android), Google Calendar API

DESIGN RULES (strictly enforced):
- Background: #F6F0E6 (warm cream) — NEVER pure white #FFFFFF
- Text: #221A10 (dark ink) — NEVER pure black #000000
- Accent: #C4963A (gold)
- Fonts: Cormorant Garamond (headings) + Jost (body)
- Style: Editorial Vintage Minimal — lots of whitespace, thin lines, no heavy shadows
- NO dark backgrounds, NO purple/navy themes

TONE RULES (all user-facing text):
- ZERO astrological jargon visible to user
- Plain English only: "Great day for negotiations" NOT "Jupiter in the 11th activates Rohini"
- Warm and supportive — even for challenging days
- Every warning MUST include a constructive suggestion

ASTROLOGY ENGINE RULES:
- Swiss Ephemeris via pyswisseph — gold standard, use this exclusively
- Ayanamsha: Lahiri (sidereal)
- House system: Whole Sign
- Accuracy target: match Jagannatha Hora within ±1 arc-minute
- All calculations server-side only

CURRENT PHASE: MVP
MVP features only unless explicitly told otherwise. See feature list in this document.
```

### Recommended CLAUDE.md for the project root

```markdown
# Nakshatra — Claude Code Instructions

## Project
Vedic astrology mobile app. React Native frontend + Python FastAPI backend.

## Rules
1. All astrological calculations via pyswisseph only — never approximate or hardcode
2. Zero jargon in user-facing strings — plain English always
3. Design tokens: cream #F6F0E6 bg, ink #221A10 text, gold #C4963A accent
4. Calendar data never persisted to database — read, process, discard
5. Birth data always encrypted (AES-256 at rest, TLS in transit)
6. Every API endpoint must validate birth data completeness before calculating

## File Structure
/backend
  /app
    /routers       # FastAPI route handlers
    /services
      /astro        # All pyswisseph calculation modules
      /calendar     # Calendar integration logic
      /content      # Affirmations, mantras, content delivery
    /models         # SQLAlchemy models
    /schemas        # Pydantic schemas
  /tests

/mobile
  /src
    /screens        # Today, Calendar, FindDay, MyChart, Onboarding
    /components     # Shared UI components
    /services       # API calls
    /assets         # SVG illustrations (27 nakshatra medallions)

## Key Services to Build First (MVP order)
1. astro/ephemeris.py — birth chart calculation
2. astro/panchanga.py — daily Tithi, Vara, Nakshatra, Yoga, Karana
3. astro/dasha.py — Vimshottari Dasha calculation
4. astro/transits.py — personal daily transits
5. astro/muhurta.py — Rahu Kala, Choghadiya, Abhijit
6. astro/day_score.py — aggregate daily score (1–10) + plain English output
7. calendar/sync.py — read and label user calendar events
8. content/affirmations.py — select daily affirmation by Dasha + day quality
9. content/mantras.py — select mantra by Dasha lord + Moon nakshatra
10. content/ekadashi.py — detect Ekadashi dates + generate guidance card
```

---

## 12. Files Produced This Session

| File | Description |
|---|---|
| `Nakshatra_App_Proposal.docx` | Full business proposal (9 sections) |
| `Nakshatra_PRD_v1.docx` | Product Requirements Document (~120 requirements) |
| `nakshatra_color_guide.html` | Interactive colour palette analysis (dark themes) |
| `nakshatra_light_palette.html` | Light palette guide (pink/lavender/ivory options) |
| `nakshatra_prototype.html` | First interactive UI prototype |
| `nakshatra_full_ui.html` | **Final full UI** — 5 screens, cream/gold/ink, editorial style |
| `Nakshatra_Project_Context.md` | **This file** — full context for Claude Code agent |

---

## 13. Next Steps

- [ ] Set up Python backend project with FastAPI
- [ ] Install pyswisseph and validate calculations against Jagannatha Hora
- [ ] Build `panchanga.py` — first calculation module
- [ ] Build `day_score.py` — aggregates all signals into 1–10 score
- [ ] Set up React Native project with navigation
- [ ] Implement Onboarding screen (birth data input)
- [ ] Implement Today screen with mock data
- [ ] Connect backend to Today screen
- [ ] Implement Calendar sync (start with Google Calendar)
- [ ] Write content: 27 nakshatra cards + 9 Dasha affirmation sets
- [ ] Design 27 nakshatra SVG medallions
- [ ] Implement Ekadashi detection + guidance cards
- [ ] Implement mantra module with YouTube links
- [ ] Beta test with 20–30 Jyotish community members

---

*Last updated: June 2025 · Conversation with Claude Sonnet*

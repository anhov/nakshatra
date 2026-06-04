from pydantic import BaseModel


class EkadashiResponse(BaseModel):
    date: str
    name: str
    paksha: str
    meaning: str
    guidance: str


class UpcomingEkadashisResponse(BaseModel):
    ekadashis: list[EkadashiResponse]


class AffirmationResponse(BaseModel):
    affirmation: str
    dasha_lord: str
    quality: str


class PlanetaryMantraResponse(BaseModel):
    planet: str
    beej_mantra: str
    vedic_mantra: str
    phonetics: str
    meaning: str
    repetitions: int
    best_day: str
    youtube_search: str


class NakshatraMantraResponse(BaseModel):
    nakshatra: str
    number: int
    deity: str
    mantra: str
    phonetics: str
    energy_theme: str
    youtube_search: str

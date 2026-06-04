from pydantic import BaseModel


class TransitPlanetResponse(BaseModel):
    name: str
    longitude: float
    sign_index: int
    sign: str
    sign_degree: float
    nakshatra: str
    pada: int
    is_retrograde: bool
    house_from_moon: int
    house_from_lagna: int
    is_favorable: bool
    weight: int
    effect: str


class SaturnWatchResponse(BaseModel):
    has_sade_sati: bool
    sade_sati_phase: str | None
    has_shani_dhaiya: bool
    shani_dhaiya_house: int | None


class TransitResponse(BaseModel):
    date: str
    local_time: str
    planets: list[TransitPlanetResponse]
    saturn_watch: SaturnWatchResponse
    transit_score: float
    quality: str
    favorable_planets: list[str]
    challenging_planets: list[str]

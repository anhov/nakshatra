from pydantic import BaseModel


class TithiResponse(BaseModel):
    number: int
    name: str
    paksha: str
    elapsed_pct: float


class VaraResponse(BaseModel):
    number: int
    english: str
    ruler: str
    sanskrit: str


class NakshatraResponse(BaseModel):
    number: int
    name: str
    pada: int
    elapsed_pct: float


class YogaResponse(BaseModel):
    number: int
    name: str
    elapsed_pct: float


class KaranaResponse(BaseModel):
    number: int
    name: str
    is_fixed: bool
    elapsed_pct: float


class PanchangaResponse(BaseModel):
    date: str
    local_time: str
    julian_day: float
    sun_longitude: float
    moon_longitude: float
    tithi: TithiResponse
    vara: VaraResponse
    nakshatra: NakshatraResponse
    yoga: YogaResponse
    karana: KaranaResponse

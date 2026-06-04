from pydantic import BaseModel


class TimeWindowResponse(BaseModel):
    name: str
    planet: str | None
    start: str
    end: str
    quality: str
    description: str


class MuhurtaResponse(BaseModel):
    date: str
    timezone: str
    sunrise: str
    sunset: str
    solar_noon: str
    day_duration_minutes: float
    brahma_muhurta: TimeWindowResponse
    abhijit: TimeWindowResponse
    rahu_kala: TimeWindowResponse
    gulika_kala: TimeWindowResponse
    yama_ganda: TimeWindowResponse
    choghadiyas_day: list[TimeWindowResponse]
    choghadiyas_night: list[TimeWindowResponse]
    horas: list[TimeWindowResponse]

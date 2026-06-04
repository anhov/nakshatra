from pydantic import BaseModel


class ActivityCardResponse(BaseModel):
    emoji: str
    title: str
    description: str
    timing: str | None


class DayScoreResponse(BaseModel):
    date: str
    score: float
    quality: str
    tagline: str
    moon_nakshatra: str
    moon_nakshatra_number: int
    paksha: str
    tithi_label: str
    current_mahadasha: str
    current_antardasha: str
    activities: list[ActivityCardResponse]
    avoid_text: str
    avoid_suggestion: str
    best_times: list[str]
    avoid_times: list[str]
    panchanga_score: float
    transit_score: float
    dasha_score: float

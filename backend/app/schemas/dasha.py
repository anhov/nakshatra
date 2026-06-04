from pydantic import BaseModel


class AntardashaResponse(BaseModel):
    lord: str
    start: str
    end: str
    duration_days: int


class MahaDashaResponse(BaseModel):
    lord: str
    start: str
    end: str
    duration_days: int
    antardashas: list[AntardashaResponse]


class ActivePeriodResponse(BaseModel):
    mahadasha: str
    md_start: str
    md_end: str
    md_elapsed_pct: float
    antardasha: str
    ad_start: str
    ad_end: str
    ad_elapsed_pct: float


class DashaResponse(BaseModel):
    birth_date: str
    moon_nakshatra: str
    dasha_lord_at_birth: str
    remaining_years_at_birth: float
    mahadashas: list[MahaDashaResponse]
    active: ActivePeriodResponse | None

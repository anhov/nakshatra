from pydantic import BaseModel


class GrahaResponse(BaseModel):
    name: str
    longitude: float
    sign_index: int
    sign: str
    sign_degree: float
    house: int
    nakshatra_index: int
    nakshatra: str
    pada: int
    is_retrograde: bool
    navamsha_index: int
    navamsha: str
    is_vargottama: bool
    strength: str


class LagnaResponse(BaseModel):
    longitude: float
    sign_index: int
    sign: str
    sign_degree: float
    nakshatra_index: int
    nakshatra: str
    pada: int
    navamsha_index: int
    navamsha: str


class BirthChartResponse(BaseModel):
    birth_date: str
    birth_time: str
    timezone: str
    latitude: float
    geo_longitude: float
    julian_day: float
    lagna: LagnaResponse
    grahas: list[GrahaResponse]

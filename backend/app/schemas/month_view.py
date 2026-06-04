from pydantic import BaseModel


class DaySummaryResponse(BaseModel):
    date: str
    score: float
    quality: str
    color: str


class MonthSummaryResponse(BaseModel):
    year: int
    month: int
    days: list[DaySummaryResponse]

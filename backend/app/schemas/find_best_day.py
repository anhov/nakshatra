from pydantic import BaseModel


class BestDayResponse(BaseModel):
    date: str
    rank: int
    score: float
    quality: str
    reason: str
    tags: list[str]


class FindBestDayResponse(BaseModel):
    category: str
    days_searched: int
    results: list[BestDayResponse]

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from app.middleware.subscription import Tier, check_feature, get_tier
from app.schemas.month_view import DaySummaryResponse, MonthSummaryResponse
from app.services.astro.month_view import get_month_summary

router = APIRouter(prefix="/month", tags=["calendar"])


@router.get("", response_model=MonthSummaryResponse)
def month(
    birth_date: date  = Query(...),
    birth_time: str   = Query(...),
    tz: str           = Query("Asia/Kolkata"),
    lat: float        = Query(...),
    lon: float        = Query(...),
    year: int         = Query(...),
    month: int        = Query(..., ge=1, le=12),
    tier: Tier        = Depends(get_tier),
) -> MonthSummaryResponse:
    try:
        result = get_month_summary(birth_date, birth_time, tz, lat, lon, year, month)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    show_scores = check_feature(tier, "month:scores")
    return MonthSummaryResponse(
        year=result.year,
        month=result.month,
        days=[
            DaySummaryResponse(
                date=d.date,
                score=d.score if show_scores else 0.0,
                quality=d.quality if show_scores else "",
                color=d.color,   # color always shown (free users see colour dots)
            )
            for d in result.days
        ],
    )

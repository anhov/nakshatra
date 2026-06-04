from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app.schemas.panchanga import PanchangaResponse
from app.services.astro.panchanga import get_panchanga

router = APIRouter(prefix="/panchanga", tags=["panchanga"])


@router.get("", response_model=PanchangaResponse)
def panchanga(
    date: date = Query(..., description="Calendar date, e.g. 2025-06-04"),
    tz: str = Query("Asia/Kolkata", description="IANA timezone, e.g. Asia/Kolkata"),
    hour: int = Query(6, ge=0, le=23, description="Local hour for calculation"),
    minute: int = Query(0, ge=0, le=59, description="Local minute for calculation"),
) -> PanchangaResponse:
    try:
        result = get_panchanga(date, tz, hour=hour, minute=minute)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return PanchangaResponse(
        date=result.date,
        local_time=result.local_time,
        julian_day=result.julian_day,
        sun_longitude=result.sun_longitude,
        moon_longitude=result.moon_longitude,
        tithi=result.tithi.__dict__,
        vara=result.vara.__dict__,
        nakshatra=result.nakshatra.__dict__,
        yoga=result.yoga.__dict__,
        karana=result.karana.__dict__,
    )

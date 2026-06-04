from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app.schemas.muhurta import MuhurtaResponse, TimeWindowResponse
from app.services.astro.muhurta import get_muhurta

router = APIRouter(prefix="/muhurta", tags=["muhurta"])


def _w(win) -> TimeWindowResponse:
    return TimeWindowResponse(**win.__dict__)


def _to_response(r) -> MuhurtaResponse:
    return MuhurtaResponse(
        date=r.date,
        timezone=r.timezone,
        sunrise=r.sunrise,
        sunset=r.sunset,
        solar_noon=r.solar_noon,
        day_duration_minutes=r.day_duration_minutes,
        brahma_muhurta=_w(r.brahma_muhurta),
        abhijit=_w(r.abhijit),
        rahu_kala=_w(r.rahu_kala),
        gulika_kala=_w(r.gulika_kala),
        yama_ganda=_w(r.yama_ganda),
        choghadiyas_day=[_w(c) for c in r.choghadiyas_day],
        choghadiyas_night=[_w(c) for c in r.choghadiyas_night],
        horas=[_w(h) for h in r.horas],
    )


@router.get("", response_model=MuhurtaResponse)
def muhurta(
    date: date = Query(..., description="Date, e.g. 2026-06-04"),
    tz: str = Query("Asia/Kolkata", description="IANA timezone"),
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
) -> MuhurtaResponse:
    try:
        result = get_muhurta(date, tz, lat, lon)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _to_response(result)

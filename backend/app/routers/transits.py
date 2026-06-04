from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app.schemas.transits import SaturnWatchResponse, TransitPlanetResponse, TransitResponse
from app.services.astro.ephemeris import get_birth_chart
from app.services.astro.transits import get_transits

router = APIRouter(prefix="/transits", tags=["transits"])


def _to_response(result) -> TransitResponse:
    return TransitResponse(
        date=result.date,
        local_time=result.local_time,
        planets=[TransitPlanetResponse(**p.__dict__) for p in result.planets],
        saturn_watch=SaturnWatchResponse(**result.saturn_watch.__dict__),
        transit_score=result.transit_score,
        quality=result.quality,
        favorable_planets=result.favorable_planets,
        challenging_planets=result.challenging_planets,
    )


@router.get("", response_model=TransitResponse)
def transits(
    birth_date: date = Query(..., description="Date of birth, e.g. 1990-04-15"),
    birth_time: str = Query(..., description='Time of birth, e.g. "08:30"'),
    tz: str = Query("Asia/Kolkata", description="IANA timezone"),
    lat: float = Query(..., description="Birth latitude"),
    lon: float = Query(..., description="Birth longitude"),
    transit_date: date | None = Query(None, description="Date to calculate transits for (default: today)"),
    transit_hour: int = Query(6, ge=0, le=23),
    transit_minute: int = Query(0, ge=0, le=59),
) -> TransitResponse:
    if transit_date is None:
        from datetime import date as _date
        transit_date = _date.today()
    try:
        chart = get_birth_chart(birth_date, birth_time, tz, lat, lon)
        moon = next(g for g in chart.grahas if g.name == "Moon")
        result = get_transits(
            moon.longitude,
            chart.lagna.longitude,
            transit_date,
            tz,
            transit_hour,
            transit_minute,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _to_response(result)

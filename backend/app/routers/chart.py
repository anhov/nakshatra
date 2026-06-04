from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app.schemas.chart import BirthChartResponse, GrahaResponse, LagnaResponse
from app.services.astro.ephemeris import get_birth_chart

router = APIRouter(prefix="/chart", tags=["chart"])


def _to_response(chart) -> BirthChartResponse:
    return BirthChartResponse(
        birth_date=chart.birth_date,
        birth_time=chart.birth_time,
        timezone=chart.timezone,
        latitude=chart.latitude,
        geo_longitude=chart.geo_longitude,
        julian_day=chart.julian_day,
        lagna=LagnaResponse(**chart.lagna.__dict__),
        grahas=[GrahaResponse(**g.__dict__) for g in chart.grahas],
    )


@router.get("/birth", response_model=BirthChartResponse)
def birth_chart(
    date: date = Query(..., description="Date of birth, e.g. 1990-04-15"),
    time: str = Query(..., description='Time of birth, e.g. "08:30"'),
    tz: str = Query("Asia/Kolkata", description="IANA timezone"),
    lat: float = Query(..., description="Birth latitude, e.g. 22.57"),
    lon: float = Query(..., description="Birth longitude, e.g. 88.36"),
) -> BirthChartResponse:
    try:
        chart = get_birth_chart(date, time, tz, lat, lon)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _to_response(chart)

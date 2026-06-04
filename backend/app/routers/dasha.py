from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app.schemas.dasha import (
    ActivePeriodResponse,
    AntardashaResponse,
    DashaResponse,
    MahaDashaResponse,
)
from app.services.astro.dasha import get_dasha
from app.services.astro.ephemeris import get_birth_chart

router = APIRouter(prefix="/dasha", tags=["dasha"])


def _d(d: date) -> str:
    return d.isoformat()


def _to_response(result) -> DashaResponse:
    mds = [
        MahaDashaResponse(
            lord=md.lord,
            start=_d(md.start),
            end=_d(md.end),
            duration_days=md.duration_days,
            antardashas=[
                AntardashaResponse(
                    lord=ad.lord,
                    start=_d(ad.start),
                    end=_d(ad.end),
                    duration_days=ad.duration_days,
                )
                for ad in md.antardashas
            ],
        )
        for md in result.mahadashas
    ]

    active = None
    if result.active:
        a = result.active
        active = ActivePeriodResponse(
            mahadasha=a.mahadasha,
            md_start=_d(a.md_start),
            md_end=_d(a.md_end),
            md_elapsed_pct=a.md_elapsed_pct,
            antardasha=a.antardasha,
            ad_start=_d(a.ad_start),
            ad_end=_d(a.ad_end),
            ad_elapsed_pct=a.ad_elapsed_pct,
        )

    return DashaResponse(
        birth_date=result.birth_date,
        moon_nakshatra=result.moon_nakshatra,
        dasha_lord_at_birth=result.dasha_lord_at_birth,
        remaining_years_at_birth=result.remaining_years_at_birth,
        mahadashas=mds,
        active=active,
    )


@router.get("", response_model=DashaResponse)
def dasha(
    birth_date: date = Query(..., description="Date of birth, e.g. 1990-04-15"),
    birth_time: str = Query(..., description='Time of birth, e.g. "08:30"'),
    tz: str = Query("Asia/Kolkata", description="IANA timezone"),
    lat: float = Query(..., description="Birth latitude"),
    lon: float = Query(..., description="Birth longitude"),
    query_date: date | None = Query(None, description="Date to identify active period (default: today)"),
) -> DashaResponse:
    try:
        chart = get_birth_chart(birth_date, birth_time, tz, lat, lon)
        moon = next(g for g in chart.grahas if g.name == "Moon")
        result = get_dasha(moon.longitude, birth_date, query_date)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _to_response(result)

from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app.schemas.content import (
    AffirmationResponse,
    EkadashiResponse,
    NakshatraMantraResponse,
    PlanetaryMantraResponse,
    UpcomingEkadashisResponse,
)
from app.services.content.affirmations import get_affirmation
from app.services.content.ekadashi import get_ekadashi, get_upcoming_ekadashis
from app.services.content.mantras import get_nakshatra_mantra, get_planetary_mantra

router = APIRouter(prefix="/content", tags=["content"])


@router.get("/ekadashi", response_model=EkadashiResponse | None)
def ekadashi(
    date: date = Query(...),
    tz: str    = Query("Asia/Kolkata"),
):
    try:
        result = get_ekadashi(date, tz)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if result is None:
        return None
    return EkadashiResponse(**result.__dict__)


@router.get("/ekadashis/upcoming", response_model=UpcomingEkadashisResponse)
def upcoming_ekadashis(
    tz: str     = Query("Asia/Kolkata"),
    from_date: date | None = Query(None),
    count: int  = Query(6, ge=1, le=24),
):
    try:
        results = get_upcoming_ekadashis(tz, from_date, count)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return UpcomingEkadashisResponse(
        ekadashis=[EkadashiResponse(**r.__dict__) for r in results]
    )


@router.get("/affirmation", response_model=AffirmationResponse)
def affirmation(
    dasha_lord: str = Query(..., description="Current Maha Dasha planet"),
    quality: str    = Query(..., description="Day quality label"),
    date: date | None = Query(None),
):
    try:
        text = get_affirmation(dasha_lord, quality, date)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return AffirmationResponse(affirmation=text, dasha_lord=dasha_lord, quality=quality)


@router.get("/mantra/planet/{planet}", response_model=PlanetaryMantraResponse)
def planetary_mantra(planet: str):
    m = get_planetary_mantra(planet)
    return PlanetaryMantraResponse(**m.__dict__)


@router.get("/mantra/nakshatra/{nakshatra}", response_model=NakshatraMantraResponse)
def nakshatra_mantra(nakshatra: str):
    m = get_nakshatra_mantra(nakshatra)
    return NakshatraMantraResponse(**m.__dict__)

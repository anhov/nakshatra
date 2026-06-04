from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from app.middleware.subscription import Tier, check_feature, get_tier
from app.schemas.day_score import ActivityCardResponse, DayScoreResponse
from app.services.astro.day_score import get_day_score

router = APIRouter(prefix="/today", tags=["today"])


def _to_response(r, tier: Tier) -> DayScoreResponse:
    full = check_feature(tier, "today:full_activities")
    timing = check_feature(tier, "today:timing_windows")

    return DayScoreResponse(
        date=r.date,
        score=r.score,
        quality=r.quality,
        tagline=r.tagline,
        moon_nakshatra=r.moon_nakshatra,
        moon_nakshatra_number=r.moon_nakshatra_number,
        paksha=r.paksha,
        tithi_label=r.tithi_label,
        # Free tier: only major period shown; AD shown as "Upgrade for sub-period"
        current_mahadasha=r.current_mahadasha,
        current_antardasha=(
            r.current_antardasha
            if check_feature(tier, "dasha:antardasha")
            else "Upgrade for sub-period detail"
        ),
        # Free tier: limit to 2 activities
        activities=[ActivityCardResponse(**a.__dict__) for a in (r.activities if full else r.activities[:2])],
        avoid_text=r.avoid_text,
        avoid_suggestion=r.avoid_suggestion,
        best_times=r.best_times if timing else [],
        avoid_times=r.avoid_times if timing else r.avoid_times[:1],  # free: Rahu Kala only
        panchanga_score=r.panchanga_score,
        transit_score=r.transit_score,
        dasha_score=r.dasha_score,
    )


@router.get("", response_model=DayScoreResponse)
def today(
    birth_date: date = Query(...),
    birth_time: str  = Query(...),
    tz: str          = Query("Asia/Kolkata"),
    lat: float       = Query(...),
    lon: float       = Query(...),
    query_date: date | None = Query(None),
    tier: Tier       = Depends(get_tier),
) -> DayScoreResponse:
    try:
        result = get_day_score(birth_date, birth_time, tz, lat, lon, query_date)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _to_response(result, tier)

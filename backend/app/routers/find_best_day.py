from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from app.middleware.subscription import Tier, check_feature, get_tier
from app.schemas.find_best_day import BestDayResponse, FindBestDayResponse
from app.services.astro.find_best_day import CATEGORIES, find_best_days

router = APIRouter(prefix="/find-best-day", tags=["find-best-day"])

_FREE_CATEGORIES = ["Travel", "New Project", "Other"]


@router.get("/categories")
def categories(tier: Tier = Depends(get_tier)) -> dict:
    if check_feature(tier, "find_best_day:all_cats"):
        return {"categories": CATEGORIES}
    return {"categories": _FREE_CATEGORIES, "upgrade_for_more": True}


@router.get("", response_model=FindBestDayResponse)
def find_best(
    birth_date: date  = Query(...),
    birth_time: str   = Query(...),
    tz: str           = Query("Asia/Kolkata"),
    lat: float        = Query(...),
    lon: float        = Query(...),
    category: str     = Query("Other"),
    from_date: date | None = Query(None),
    days_ahead: int   = Query(90, ge=7, le=180),
    tier: Tier        = Depends(get_tier),
) -> FindBestDayResponse:
    full = check_feature(tier, "find_best_day:full")

    # Free tier: only allowed 3 categories
    if not full and category not in _FREE_CATEGORIES:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "premium_required",
                "message": f"The '{category}' category requires Premium. Free plan includes: {_FREE_CATEGORIES}",
                "upgrade_url": "https://nakshatra.app/upgrade",
            },
        )

    try:
        result = find_best_days(birth_date, birth_time, tz, lat, lon, category, from_date, days_ahead)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Free tier: only first result
    results = result.results if full else result.results[:1]
    return FindBestDayResponse(
        category=result.category,
        days_searched=result.days_searched,
        results=[BestDayResponse(**d.__dict__) for d in results],
    )

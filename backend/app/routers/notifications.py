"""
Notification registration and preferences.
Stores Expo push tokens and user notification settings.
"""

import uuid
from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.middleware.subscription import Tier, get_tier, require_premium

router = APIRouter(prefix="/notifications", tags=["notifications"])

# In-memory store for MVP (replace with DB queries when PostgreSQL is set up)
_tokens: dict[str, dict] = {}


class RegisterTokenRequest(BaseModel):
    user_id: str
    expo_push_token: str
    platform: str = "unknown"   # "ios" | "android"


class NotificationPrefsRequest(BaseModel):
    user_id: str
    morning_enabled: bool = True
    morning_hour: int = 7
    morning_minute: int = 0
    ekadashi_enabled: bool = True
    dasha_change_enabled: bool = True


class RegisterTokenResponse(BaseModel):
    success: bool
    registration_id: str


class PrefsResponse(BaseModel):
    user_id: str
    morning_enabled: bool
    morning_hour: int
    morning_minute: int
    ekadashi_enabled: bool
    dasha_change_enabled: bool


@router.post("/register", response_model=RegisterTokenResponse)
def register_token(
    body: RegisterTokenRequest,
    tier: Tier = Depends(get_tier),
) -> RegisterTokenResponse:
    require_premium(tier)
    reg_id = str(uuid.uuid4())
    _tokens[body.user_id] = {
        "token": body.expo_push_token,
        "platform": body.platform,
        "registered_at": datetime.utcnow().isoformat(),
        "prefs": {
            "morning_enabled": True,
            "morning_hour": 7,
            "morning_minute": 0,
            "ekadashi_enabled": True,
            "dasha_change_enabled": True,
        },
    }
    return RegisterTokenResponse(success=True, registration_id=reg_id)


@router.put("/preferences", response_model=PrefsResponse)
def update_preferences(
    body: NotificationPrefsRequest,
    tier: Tier = Depends(get_tier),
) -> PrefsResponse:
    require_premium(tier)
    if body.user_id in _tokens:
        _tokens[body.user_id]["prefs"] = {
            "morning_enabled":      body.morning_enabled,
            "morning_hour":         body.morning_hour,
            "morning_minute":       body.morning_minute,
            "ekadashi_enabled":     body.ekadashi_enabled,
            "dasha_change_enabled": body.dasha_change_enabled,
        }
    return PrefsResponse(user_id=body.user_id, **body.model_dump(exclude={"user_id"}))


@router.post("/send-daily/{user_id}")
async def send_daily(
    user_id: str,
    birth_date: str,
    birth_time: str,
    tz: str = "Asia/Kolkata",
    lat: float = 0.0,
    lon: float = 0.0,
    tier: Tier = Depends(get_tier),
):
    """
    Trigger the morning daily notification for one user.
    Called by an external cron job — not from the mobile app.
    """
    require_premium(tier)
    entry = _tokens.get(user_id)
    if not entry:
        raise HTTPException(404, "No push token registered for this user")
    if not entry["prefs"].get("morning_enabled"):
        return {"sent": False, "reason": "morning notifications disabled"}

    from app.services.astro.day_score import get_day_score
    from datetime import date as _date
    score_data = get_day_score(
        _date.fromisoformat(birth_date), birth_time, tz, lat, lon
    )
    from app.services.notifications.push import send_morning_reading
    ok = await send_morning_reading(
        entry["token"], score_data.score, score_data.quality, score_data.moon_nakshatra
    )
    return {"sent": ok}

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.middleware.subscription import Tier, get_tier, require_premium
from app.services.calendar.sync import CalendarEvent, label_events

router = APIRouter(prefix="/calendar", tags=["calendar"])


class EventIn(BaseModel):
    id: str
    title: str
    start: str   # ISO-8601
    end: str


class EventOut(BaseModel):
    id: str
    title: str
    start: str
    end: str
    label: str
    emoji: str
    reason: str


class LabelRequest(BaseModel):
    events: list[EventIn]
    birth_date: str
    birth_time: str
    timezone: str
    latitude: float
    longitude: float


class LabelResponse(BaseModel):
    labelled_events: list[EventOut]


@router.post("/label", response_model=LabelResponse)
def label_calendar_events(
    body: LabelRequest,
    tier: Tier = Depends(get_tier),
) -> LabelResponse:
    require_premium(tier)
    try:
        result = label_events(
            events=[CalendarEvent(**e.model_dump()) for e in body.events],
            birth_date=date.fromisoformat(body.birth_date),
            birth_time=body.birth_time,
            tz_name=body.timezone,
            latitude=body.latitude,
            longitude=body.longitude,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return LabelResponse(labelled_events=[EventOut(**e.__dict__) for e in result])

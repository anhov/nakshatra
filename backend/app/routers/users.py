"""
User onboarding — create a user profile with birth data.
Currently stores to DB if configured; otherwise returns a session token
containing the birth data so stateless API calls still work.
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db

router = APIRouter(prefix="/users", tags=["users"])


class CreateUserRequest(BaseModel):
    name: str | None = None
    email: str | None = None
    birth_date: str                  # "YYYY-MM-DD"
    birth_time: str                  # "HH:MM"
    timezone: str
    latitude: float
    longitude: float
    place_name: str | None = None
    is_approximate_time: bool = False


class UserResponse(BaseModel):
    user_id: str
    birth_date: str
    birth_time: str
    timezone: str
    latitude: float
    longitude: float
    place_name: str | None
    is_approximate_time: bool


@router.post("", response_model=UserResponse, status_code=201)
def create_user(body: CreateUserRequest, db: Session = Depends(get_db)):
    user_id = str(uuid.uuid4())

    if db is not None:
        from app.models.user import BirthData, User
        user = User(
            id=user_id,
            email=body.email,
            name=body.name,
            created_at=datetime.utcnow(),
        )
        birth = BirthData(
            id=str(uuid.uuid4()),
            user_id=user_id,
            birth_date=body.birth_date,
            birth_time=body.birth_time,
            timezone=body.timezone,
            latitude=body.latitude,
            longitude=body.longitude,
            place_name=body.place_name,
            is_approximate_time=body.is_approximate_time,
        )
        db.add(user)
        db.add(birth)
        try:
            db.commit()
        except Exception as exc:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    return UserResponse(
        user_id=user_id,
        birth_date=body.birth_date,
        birth_time=body.birth_time,
        timezone=body.timezone,
        latitude=body.latitude,
        longitude=body.longitude,
        place_name=body.place_name,
        is_approximate_time=body.is_approximate_time,
    )

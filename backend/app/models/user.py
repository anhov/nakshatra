import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email      = Column(String, unique=True, nullable=True)
    name       = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    birth_data = relationship("BirthData", back_populates="user", uselist=False)


class BirthData(Base):
    __tablename__ = "birth_data"

    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id             = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    birth_date          = Column(String, nullable=False)   # ISO-8601 "YYYY-MM-DD"
    birth_time          = Column(String, nullable=False)   # "HH:MM"
    timezone            = Column(String, nullable=False)   # IANA tz
    latitude            = Column(Float,  nullable=False)
    longitude           = Column(Float,  nullable=False)
    place_name          = Column(String, nullable=True)
    is_approximate_time = Column(Boolean, default=False)
    created_at          = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="birth_data")

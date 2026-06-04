from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl

from app.schemas.common import ORMModel, TimestampedModel


class UptimeCheckCreate(BaseModel):
    response_time_ms: float = Field(ge=0)
    is_available: bool
    checked_at: datetime


class DowntimeEventCreate(BaseModel):
    started_at: datetime
    ended_at: datetime | None = None
    reason: str = Field(min_length=2, max_length=500)


class UptimeTargetCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    url: HttpUrl
    environment: str = Field(min_length=2, max_length=50)
    is_active: bool = True
    checks: list[UptimeCheckCreate] = Field(default_factory=list)
    downtime_events: list[DowntimeEventCreate] = Field(default_factory=list)


class UptimeTargetUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    url: HttpUrl | None = None
    environment: str | None = Field(default=None, min_length=2, max_length=50)
    is_active: bool | None = None


class UptimeCheckResponse(ORMModel):
    id: int
    response_time_ms: float
    is_available: bool
    checked_at: datetime


class DowntimeEventResponse(ORMModel):
    id: int
    started_at: datetime
    ended_at: datetime | None
    reason: str


class UptimeTargetResponse(TimestampedModel):
    name: str
    url: str
    environment: str
    is_active: bool
    checks: list[UptimeCheckResponse]
    downtime_events: list[DowntimeEventResponse]

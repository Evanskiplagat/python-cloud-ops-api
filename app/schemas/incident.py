from datetime import datetime

from pydantic import BaseModel, Field

from app.models.incident import IncidentSeverity, IncidentStatus
from app.schemas.common import ORMModel, TimestampedModel


class IncidentEventCreate(BaseModel):
    message: str = Field(min_length=2)
    occurred_at: datetime


class IncidentEventResponse(ORMModel):
    id: int
    message: str
    occurred_at: datetime


class IncidentCreate(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    description: str = Field(min_length=5)
    severity: IncidentSeverity
    status: IncidentStatus = IncidentStatus.OPEN
    timeline: list[IncidentEventCreate] = Field(default_factory=list)


class IncidentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = Field(default=None, min_length=5)
    severity: IncidentSeverity | None = None
    status: IncidentStatus | None = None
    resolved_at: datetime | None = None


class IncidentResponse(TimestampedModel):
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    resolved_at: datetime | None
    timeline: list[IncidentEventResponse]

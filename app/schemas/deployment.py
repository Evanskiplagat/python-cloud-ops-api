from datetime import datetime

from pydantic import BaseModel, Field

from app.models.deployment import DeploymentStatus
from app.schemas.common import TimestampedModel


class DeploymentCreate(BaseModel):
    service: str = Field(min_length=2, max_length=255)
    version: str = Field(min_length=1, max_length=100)
    environment: str = Field(min_length=2, max_length=50)
    status: DeploymentStatus = DeploymentStatus.PENDING
    deployed_at: datetime


class DeploymentUpdate(BaseModel):
    service: str | None = Field(default=None, min_length=2, max_length=255)
    version: str | None = Field(default=None, min_length=1, max_length=100)
    environment: str | None = Field(default=None, min_length=2, max_length=50)
    status: DeploymentStatus | None = None
    deployed_at: datetime | None = None


class DeploymentResponse(TimestampedModel):
    service: str
    version: str
    environment: str
    status: DeploymentStatus
    deployed_at: datetime

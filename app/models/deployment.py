from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.mixins import TimestampMixin


class DeploymentStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class Deployment(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    service: Mapped[str] = mapped_column(String(255), index=True)
    version: Mapped[str] = mapped_column(String(100), index=True)
    environment: Mapped[str] = mapped_column(String(50), index=True)
    status: Mapped[DeploymentStatus] = mapped_column(Enum(DeploymentStatus), default=DeploymentStatus.PENDING)
    deployed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

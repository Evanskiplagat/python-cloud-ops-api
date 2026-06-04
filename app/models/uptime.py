from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin


class UptimeTarget(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    url: Mapped[str] = mapped_column(String(1024), unique=True)
    environment: Mapped[str] = mapped_column(String(50), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    checks: Mapped[list["UptimeCheck"]] = relationship(
        back_populates="target", cascade="all, delete-orphan", order_by="UptimeCheck.checked_at"
    )
    downtime_events: Mapped[list["DowntimeEvent"]] = relationship(
        back_populates="target", cascade="all, delete-orphan", order_by="DowntimeEvent.started_at"
    )


class UptimeCheck(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    target_id: Mapped[int] = mapped_column(ForeignKey("uptimetarget.id", ondelete="CASCADE"), index=True)
    response_time_ms: Mapped[float] = mapped_column(Float)
    is_available: Mapped[bool] = mapped_column(Boolean)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    target: Mapped[UptimeTarget] = relationship(back_populates="checks")


class DowntimeEvent(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    target_id: Mapped[int] = mapped_column(ForeignKey("uptimetarget.id", ondelete="CASCADE"), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reason: Mapped[str] = mapped_column(String(500))

    target: Mapped[UptimeTarget] = relationship(back_populates="downtime_events")

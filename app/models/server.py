from enum import StrEnum

from sqlalchemy import Enum, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.mixins import TimestampMixin


class ServerStatus(StrEnum):
    RUNNING = "running"
    DEGRADED = "degraded"
    STOPPED = "stopped"
    UNKNOWN = "unknown"


class Server(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    environment: Mapped[str] = mapped_column(String(50), index=True)
    ip_address: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    cpu_usage: Mapped[float] = mapped_column(Float, default=0.0)
    memory_usage: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[ServerStatus] = mapped_column(Enum(ServerStatus), default=ServerStatus.UNKNOWN)

from pydantic import BaseModel, Field, IPvAnyAddress

from app.models.server import ServerStatus
from app.schemas.common import TimestampedModel


class ServerBase(BaseModel):
    name: str
    environment: str
    ip_address: str
    cpu_usage: float
    memory_usage: float
    status: ServerStatus


class ServerCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    environment: str = Field(min_length=2, max_length=50)
    ip_address: IPvAnyAddress
    cpu_usage: float = Field(ge=0, le=100)
    memory_usage: float = Field(ge=0, le=100)
    status: ServerStatus = ServerStatus.UNKNOWN


class ServerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    environment: str | None = Field(default=None, min_length=2, max_length=50)
    ip_address: IPvAnyAddress | None = None
    cpu_usage: float | None = Field(default=None, ge=0, le=100)
    memory_usage: float | None = Field(default=None, ge=0, le=100)
    status: ServerStatus | None = None


class ServerResponse(TimestampedModel):
    name: str
    environment: str
    ip_address: str
    cpu_usage: float
    memory_usage: float
    status: ServerStatus

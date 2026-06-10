from typing import Any

from app.schemas.common import TimestampedModel


class AuditLogResponse(TimestampedModel):
    actor_user_id: int | None
    action: str
    entity_type: str
    entity_id: int | None
    before_state: dict[str, Any] | None
    after_state: dict[str, Any] | None

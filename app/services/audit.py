from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy.inspection import inspect as sa_inspect
from sqlalchemy.orm import Session

from app.core.pagination import PaginatedResponse, PaginationParams
from app.models.audit import AuditLog
from app.models.user import User
from app.repositories.audit import AuditLogRepository
from app.schemas.audit import AuditLogResponse


def _normalize_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def snapshot_model(entity: Any) -> dict[str, Any]:
    mapper = sa_inspect(entity.__class__)
    return {column.key: _normalize_value(getattr(entity, column.key)) for column in mapper.column_attrs}


class AuditService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = AuditLogRepository(db)

    def record(
        self,
        action: str,
        entity_type: str,
        actor: User | None,
        entity_id: int | None = None,
        before_state: dict[str, Any] | None = None,
        after_state: dict[str, Any] | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            actor_user_id=actor.id if actor else None,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            before_state=before_state,
            after_state=after_state,
        )
        self.repository.add(entry)
        return entry

    def list(
        self,
        pagination: PaginationParams,
        actor_user_id: int | None,
        action: str | None,
        entity_type: str | None,
    ) -> PaginatedResponse[AuditLogResponse]:
        statement = self.repository.list(actor_user_id=actor_user_id, action=action, entity_type=entity_type)
        items, total = self.repository.paginate(statement, pagination.offset, pagination.page_size)
        return PaginatedResponse[AuditLogResponse](
            items=[AuditLogResponse.model_validate(item) for item in items],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        )

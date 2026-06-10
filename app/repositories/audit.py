from sqlalchemy import Select, desc, select
from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.repositories.base import Repository


class AuditLogRepository(Repository[AuditLog]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, AuditLog)

    def list(
        self,
        actor_user_id: int | None = None,
        action: str | None = None,
        entity_type: str | None = None,
    ) -> Select:
        statement = select(AuditLog).order_by(desc(AuditLog.created_at), desc(AuditLog.id))
        if actor_user_id is not None:
            statement = statement.where(AuditLog.actor_user_id == actor_user_id)
        if action:
            statement = statement.where(AuditLog.action == action)
        if entity_type:
            statement = statement.where(AuditLog.entity_type == entity_type)
        return statement

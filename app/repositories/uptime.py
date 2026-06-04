from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.uptime import UptimeTarget
from app.repositories.base import Repository


class UptimeTargetRepository(Repository[UptimeTarget]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, UptimeTarget)

    def list(self, environment: str | None = None, is_active: bool | None = None):
        statement = (
            select(UptimeTarget)
            .options(selectinload(UptimeTarget.checks), selectinload(UptimeTarget.downtime_events))
            .order_by(UptimeTarget.created_at.desc())
        )
        if environment:
            statement = statement.where(UptimeTarget.environment == environment)
        if is_active is not None:
            statement = statement.where(UptimeTarget.is_active == is_active)
        return statement

from sqlalchemy.orm import Session

from app.core.errors import AppException
from app.core.pagination import PaginatedResponse, PaginationParams
from app.models.uptime import DowntimeEvent, UptimeCheck, UptimeTarget
from app.repositories.uptime import UptimeTargetRepository
from app.schemas.uptime import UptimeTargetCreate, UptimeTargetResponse, UptimeTargetUpdate


class UptimeService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = UptimeTargetRepository(db)

    def create(self, payload: UptimeTargetCreate) -> UptimeTarget:
        entity = UptimeTarget(
            name=payload.name,
            url=str(payload.url),
            environment=payload.environment,
            is_active=payload.is_active,
            checks=[UptimeCheck(**check.model_dump()) for check in payload.checks],
            downtime_events=[DowntimeEvent(**event.model_dump()) for event in payload.downtime_events],
        )
        self.repository.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def list(self, pagination: PaginationParams, environment: str | None, is_active: bool | None):
        statement = self.repository.list(environment=environment, is_active=is_active)
        items, total = self.repository.paginate(statement, pagination.offset, pagination.page_size)
        return PaginatedResponse[UptimeTargetResponse](
            items=[UptimeTargetResponse.model_validate(item) for item in items],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        )

    def get(self, target_id: int) -> UptimeTarget:
        entity = self.repository.get(target_id)
        if not entity:
            raise AppException("Uptime target not found", 404)
        return entity

    def update(self, target_id: int, payload: UptimeTargetUpdate) -> UptimeTarget:
        entity = self.get(target_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(entity, field, str(value) if field == "url" and value is not None else value)
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, target_id: int) -> None:
        entity = self.get(target_id)
        self.repository.delete(entity)
        self.db.commit()

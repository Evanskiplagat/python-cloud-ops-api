from datetime import UTC, datetime

from fastapi import status
from sqlalchemy.orm import Session

from app.core.errors import AppException
from app.core.pagination import PaginatedResponse, PaginationParams
from app.models.incident import Incident, IncidentEvent, IncidentStatus
from app.repositories.incident import IncidentRepository
from app.schemas.incident import IncidentCreate, IncidentResponse, IncidentUpdate


class IncidentService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = IncidentRepository(db)

    def create(self, payload: IncidentCreate) -> Incident:
        entity = Incident(
            title=payload.title,
            description=payload.description,
            severity=payload.severity,
            status=payload.status,
            timeline=[IncidentEvent(message=event.message, occurred_at=event.occurred_at) for event in payload.timeline],
        )
        if payload.status == IncidentStatus.RESOLVED:
            entity.resolved_at = datetime.now(UTC)
        self.repository.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def list(self, pagination: PaginationParams, status_filter: str | None, severity: str | None):
        statement = self.repository.list(status=status_filter, severity=severity)
        items, total = self.repository.paginate(statement, pagination.offset, pagination.page_size)
        return PaginatedResponse[IncidentResponse](
            items=[IncidentResponse.model_validate(item) for item in items],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        )

    def get(self, incident_id: int) -> Incident:
        entity = self.repository.get(incident_id)
        if not entity:
            raise AppException("Incident not found", status.HTTP_404_NOT_FOUND)
        return entity

    def update(self, incident_id: int, payload: IncidentUpdate) -> Incident:
        entity = self.get(incident_id)
        updates = payload.model_dump(exclude_unset=True)
        if updates.get("status") == IncidentStatus.RESOLVED and entity.resolved_at is None:
            updates["resolved_at"] = updates.get("resolved_at") or datetime.now(UTC)
        for field, value in updates.items():
            setattr(entity, field, value)
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def add_event(self, incident_id: int, message: str, occurred_at: datetime) -> Incident:
        entity = self.get(incident_id)
        entity.timeline.append(IncidentEvent(message=message, occurred_at=occurred_at))
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, incident_id: int) -> None:
        entity = self.get(incident_id)
        self.repository.delete(entity)
        self.db.commit()

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.incident import Incident, IncidentSeverity, IncidentStatus
from app.repositories.base import Repository


class IncidentRepository(Repository[Incident]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, Incident)

    def list(self, status: str | None = None, severity: str | None = None):
        statement = select(Incident).options(selectinload(Incident.timeline)).order_by(Incident.created_at.desc())
        if status:
            statement = statement.where(Incident.status == IncidentStatus(status))
        if severity:
            statement = statement.where(Incident.severity == IncidentSeverity(severity))
        return statement

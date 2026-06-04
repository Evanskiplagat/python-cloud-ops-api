from datetime import datetime

from fastapi import APIRouter, Depends, Query, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.auth.authorization import require_roles
from app.core.enums import Role
from app.core.pagination import PaginatedResponse, PaginationParams
from app.models.user import User
from app.schemas.incident import IncidentCreate, IncidentResponse, IncidentUpdate
from app.services.incident import IncidentService

router = APIRouter()


class IncidentEventPayload(BaseModel):
    message: str = Field(min_length=2)
    occurred_at: datetime


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
def create_incident(
    payload: IncidentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(Role.ADMIN, Role.DEVOPS_ENGINEER, Role.DEVELOPER)),
) -> IncidentResponse:
    return IncidentResponse.model_validate(IncidentService(db).create(payload))


@router.get("", response_model=PaginatedResponse[IncidentResponse])
def list_incidents(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status_filter: str | None = Query(default=None, alias="status"),
    severity: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(Role.ADMIN, Role.DEVOPS_ENGINEER, Role.DEVELOPER, Role.VIEWER)),
):
    return IncidentService(db).list(PaginationParams(page=page, page_size=page_size), status_filter, severity)


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(Role.ADMIN, Role.DEVOPS_ENGINEER, Role.DEVELOPER, Role.VIEWER)),
) -> IncidentResponse:
    return IncidentResponse.model_validate(IncidentService(db).get(incident_id))


@router.put("/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: int,
    payload: IncidentUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(Role.ADMIN, Role.DEVOPS_ENGINEER)),
) -> IncidentResponse:
    return IncidentResponse.model_validate(IncidentService(db).update(incident_id, payload))


@router.post("/{incident_id}/timeline", response_model=IncidentResponse)
def add_timeline_event(
    incident_id: int,
    payload: IncidentEventPayload,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(Role.ADMIN, Role.DEVOPS_ENGINEER, Role.DEVELOPER)),
) -> IncidentResponse:
    return IncidentResponse.model_validate(IncidentService(db).add_event(incident_id, payload.message, payload.occurred_at))


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(Role.ADMIN)),
) -> Response:
    IncidentService(db).delete(incident_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.auth.authorization import require_roles
from app.core.enums import Role
from app.core.pagination import PaginatedResponse, PaginationParams
from app.models.user import User
from app.schemas.uptime import UptimeTargetCreate, UptimeTargetResponse, UptimeTargetUpdate
from app.services.uptime import UptimeService

router = APIRouter()


@router.post("", response_model=UptimeTargetResponse, status_code=status.HTTP_201_CREATED)
def create_target(
    payload: UptimeTargetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.ADMIN, Role.DEVOPS_ENGINEER)),
) -> UptimeTargetResponse:
    return UptimeTargetResponse.model_validate(UptimeService(db).create(payload, current_user))


@router.get("", response_model=PaginatedResponse[UptimeTargetResponse])
def list_targets(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    environment: str | None = None,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(Role.ADMIN, Role.DEVOPS_ENGINEER, Role.DEVELOPER, Role.VIEWER)),
):
    return UptimeService(db).list(PaginationParams(page=page, page_size=page_size), environment, is_active)


@router.get("/{target_id}", response_model=UptimeTargetResponse)
def get_target(
    target_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(Role.ADMIN, Role.DEVOPS_ENGINEER, Role.DEVELOPER, Role.VIEWER)),
) -> UptimeTargetResponse:
    return UptimeTargetResponse.model_validate(UptimeService(db).get(target_id))


@router.put("/{target_id}", response_model=UptimeTargetResponse)
def update_target(
    target_id: int,
    payload: UptimeTargetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.ADMIN, Role.DEVOPS_ENGINEER)),
) -> UptimeTargetResponse:
    return UptimeTargetResponse.model_validate(UptimeService(db).update(target_id, payload, current_user))


@router.delete("/{target_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_target(
    target_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.ADMIN)),
) -> Response:
    UptimeService(db).delete(target_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

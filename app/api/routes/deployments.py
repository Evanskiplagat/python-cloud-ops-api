from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.auth.authorization import require_roles
from app.core.enums import Role
from app.core.pagination import PaginatedResponse, PaginationParams
from app.models.user import User
from app.schemas.deployment import DeploymentCreate, DeploymentResponse, DeploymentUpdate
from app.services.deployment import DeploymentService

router = APIRouter()


@router.post("", response_model=DeploymentResponse, status_code=status.HTTP_201_CREATED)
def create_deployment(
    payload: DeploymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.ADMIN, Role.DEVOPS_ENGINEER, Role.DEVELOPER)),
) -> DeploymentResponse:
    return DeploymentResponse.model_validate(DeploymentService(db).create(payload, current_user))


@router.get("", response_model=PaginatedResponse[DeploymentResponse])
def list_deployments(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    environment: str | None = None,
    service: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(Role.ADMIN, Role.DEVOPS_ENGINEER, Role.DEVELOPER, Role.VIEWER)),
):
    return DeploymentService(db).list(
        PaginationParams(page=page, page_size=page_size), environment, service, status_filter
    )


@router.get("/{deployment_id}", response_model=DeploymentResponse)
def get_deployment(
    deployment_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(Role.ADMIN, Role.DEVOPS_ENGINEER, Role.DEVELOPER, Role.VIEWER)),
) -> DeploymentResponse:
    return DeploymentResponse.model_validate(DeploymentService(db).get(deployment_id))


@router.put("/{deployment_id}", response_model=DeploymentResponse)
def update_deployment(
    deployment_id: int,
    payload: DeploymentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.ADMIN, Role.DEVOPS_ENGINEER)),
) -> DeploymentResponse:
    return DeploymentResponse.model_validate(DeploymentService(db).update(deployment_id, payload, current_user))


@router.delete("/{deployment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deployment(
    deployment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.ADMIN)),
) -> Response:
    DeploymentService(db).delete(deployment_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

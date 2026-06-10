from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.auth.authorization import require_roles
from app.core.enums import Role
from app.core.pagination import PaginatedResponse, PaginationParams
from app.models.user import User
from app.schemas.server import ServerCreate, ServerResponse, ServerUpdate
from app.services.server import ServerService

router = APIRouter()


@router.post("", response_model=ServerResponse, status_code=status.HTTP_201_CREATED)
def create_server(
    payload: ServerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.ADMIN, Role.DEVOPS_ENGINEER)),
) -> ServerResponse:
    return ServerResponse.model_validate(ServerService(db).create(payload, current_user))


@router.get("", response_model=PaginatedResponse[ServerResponse])
def list_servers(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    environment: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(Role.ADMIN, Role.DEVOPS_ENGINEER, Role.DEVELOPER, Role.VIEWER)),
):
    pagination = PaginationParams(page=page, page_size=page_size)
    return ServerService(db).list(pagination, environment, status_filter)


@router.get("/{server_id}", response_model=ServerResponse)
def get_server(
    server_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(Role.ADMIN, Role.DEVOPS_ENGINEER, Role.DEVELOPER, Role.VIEWER)),
) -> ServerResponse:
    return ServerResponse.model_validate(ServerService(db).get(server_id))


@router.put("/{server_id}", response_model=ServerResponse)
def update_server(
    server_id: int,
    payload: ServerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.ADMIN, Role.DEVOPS_ENGINEER)),
) -> ServerResponse:
    return ServerResponse.model_validate(ServerService(db).update(server_id, payload, current_user))


@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_server(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.ADMIN)),
) -> Response:
    ServerService(db).delete(server_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

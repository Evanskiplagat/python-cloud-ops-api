from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.auth.authorization import require_roles
from app.core.enums import Role
from app.core.pagination import PaginatedResponse, PaginationParams
from app.models.user import User
from app.schemas.audit import AuditLogResponse
from app.services.audit import AuditService

router = APIRouter()


@router.get("", response_model=PaginatedResponse[AuditLogResponse])
def list_audit_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    actor_user_id: int | None = None,
    action: str | None = None,
    entity_type: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(Role.ADMIN)),
):
    return AuditService(db).list(
        PaginationParams(page=page, page_size=page_size),
        actor_user_id=actor_user_id,
        action=action,
        entity_type=entity_type,
    )

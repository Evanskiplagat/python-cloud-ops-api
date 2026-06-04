from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.auth.authorization import require_roles
from app.core.enums import Role
from app.models.user import User
from app.schemas.dashboard import DashboardSummary
from app.services.dashboard import DashboardService

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
def get_summary(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(Role.ADMIN, Role.DEVOPS_ENGINEER, Role.DEVELOPER, Role.VIEWER)),
) -> DashboardSummary:
    return DashboardService(db).summary()

from sqlalchemy.orm import Session

from app.repositories.dashboard import DashboardRepository
from app.schemas.dashboard import DashboardSummary


class DashboardService:
    def __init__(self, db: Session) -> None:
        self.repository = DashboardRepository(db)

    def summary(self) -> DashboardSummary:
        return DashboardSummary.model_validate(self.repository.summary())

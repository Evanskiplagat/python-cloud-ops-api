from sqlalchemy import Float, cast, func, select
from sqlalchemy.orm import Session

from app.models.deployment import Deployment, DeploymentStatus
from app.models.incident import Incident, IncidentStatus
from app.models.server import Server
from app.models.uptime import UptimeCheck


class DashboardRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def summary(self) -> dict:
        total_servers = self.db.scalar(select(func.count()).select_from(Server)) or 0
        active_deployments = (
            self.db.scalar(
                select(func.count()).select_from(Deployment).where(Deployment.status == DeploymentStatus.RUNNING)
            )
            or 0
        )
        open_incidents = (
            self.db.scalar(
                select(func.count()).select_from(Incident).where(Incident.status != IncidentStatus.RESOLVED)
            )
            or 0
        )
        availability = self.db.scalar(select(func.avg(cast(UptimeCheck.is_available, Float))))
        environment_rows = self.db.execute(
            select(Server.environment, func.count()).group_by(Server.environment).order_by(Server.environment)
        ).all()
        return {
            "total_servers": total_servers,
            "active_deployments": active_deployments,
            "open_incidents": open_incidents,
            "uptime_percentage": round(float(availability or 0) * 100, 2),
            "environment_overview": {environment: count for environment, count in environment_rows},
        }

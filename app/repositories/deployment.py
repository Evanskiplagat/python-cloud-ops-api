from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.deployment import Deployment
from app.repositories.base import Repository


class DeploymentRepository(Repository[Deployment]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, Deployment)

    def list(self, environment: str | None = None, service: str | None = None):
        statement = select(Deployment).order_by(Deployment.deployed_at.desc())
        if environment:
            statement = statement.where(Deployment.environment == environment)
        if service:
            statement = statement.where(Deployment.service == service)
        return statement

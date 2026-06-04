from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.server import Server, ServerStatus
from app.repositories.base import Repository


class ServerRepository(Repository[Server]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, Server)

    def list(self, environment: str | None = None, status: str | None = None):
        statement = select(Server).order_by(Server.created_at.desc())
        if environment:
            statement = statement.where(Server.environment == environment)
        if status:
            statement = statement.where(Server.status == ServerStatus(status))
        return statement

from fastapi import status
from sqlalchemy.orm import Session

from app.core.errors import AppException
from app.core.pagination import PaginatedResponse, PaginationParams
from app.models.server import Server
from app.models.user import User
from app.repositories.server import ServerRepository
from app.schemas.server import ServerCreate, ServerResponse, ServerUpdate
from app.services.audit import AuditService, snapshot_model


class ServerService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = ServerRepository(db)
        self.audit = AuditService(db)

    def create(self, payload: ServerCreate, actor: User) -> Server:
        entity = Server(**payload.model_dump(mode="json"))
        self.repository.add(entity)
        self.audit.record("server.create", "server", actor, entity_id=entity.id, after_state=snapshot_model(entity))
        self.db.commit()
        return entity

    def list(self, pagination: PaginationParams, environment: str | None, status_filter: str | None):
        statement = self.repository.list(environment=environment, status=status_filter)
        items, total = self.repository.paginate(statement, pagination.offset, pagination.page_size)
        return PaginatedResponse[ServerResponse](
            items=[ServerResponse.model_validate(item) for item in items],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        )

    def get(self, server_id: int) -> Server:
        entity = self.repository.get(server_id)
        if not entity:
            raise AppException("Server not found", status.HTTP_404_NOT_FOUND)
        return entity

    def update(self, server_id: int, payload: ServerUpdate, actor: User) -> Server:
        entity = self.get(server_id)
        before_state = snapshot_model(entity)
        for field, value in payload.model_dump(exclude_unset=True, mode="json").items():
            setattr(entity, field, value)
        self.db.add(entity)
        self.db.flush()
        self.audit.record(
            "server.update",
            "server",
            actor,
            entity_id=entity.id,
            before_state=before_state,
            after_state=snapshot_model(entity),
        )
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, server_id: int, actor: User) -> None:
        entity = self.get(server_id)
        before_state = snapshot_model(entity)
        self.repository.delete(entity)
        self.audit.record("server.delete", "server", actor, entity_id=server_id, before_state=before_state)
        self.db.commit()

from fastapi import status
from sqlalchemy.orm import Session

from app.core.errors import AppException
from app.core.pagination import PaginatedResponse, PaginationParams
from app.models.deployment import Deployment
from app.models.user import User
from app.repositories.deployment import DeploymentRepository
from app.schemas.deployment import DeploymentCreate, DeploymentResponse, DeploymentUpdate
from app.services.audit import AuditService, snapshot_model


class DeploymentService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = DeploymentRepository(db)
        self.audit = AuditService(db)

    def create(self, payload: DeploymentCreate, actor: User) -> Deployment:
        entity = Deployment(**payload.model_dump())
        self.repository.add(entity)
        self.audit.record(
            "deployment.create",
            "deployment",
            actor,
            entity_id=entity.id,
            after_state=snapshot_model(entity),
        )
        self.db.commit()
        return entity

    def list(
        self,
        pagination: PaginationParams,
        environment: str | None,
        service: str | None,
        status_filter: str | None,
    ):
        statement = self.repository.list(environment=environment, service=service, status=status_filter)
        items, total = self.repository.paginate(statement, pagination.offset, pagination.page_size)
        return PaginatedResponse[DeploymentResponse](
            items=[DeploymentResponse.model_validate(item) for item in items],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        )

    def get(self, deployment_id: int) -> Deployment:
        entity = self.repository.get(deployment_id)
        if not entity:
            raise AppException("Deployment not found", status.HTTP_404_NOT_FOUND)
        return entity

    def update(self, deployment_id: int, payload: DeploymentUpdate, actor: User) -> Deployment:
        entity = self.get(deployment_id)
        before_state = snapshot_model(entity)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(entity, field, value)
        self.db.add(entity)
        self.db.flush()
        self.audit.record(
            "deployment.update",
            "deployment",
            actor,
            entity_id=entity.id,
            before_state=before_state,
            after_state=snapshot_model(entity),
        )
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, deployment_id: int, actor: User) -> None:
        entity = self.get(deployment_id)
        before_state = snapshot_model(entity)
        self.repository.delete(entity)
        self.audit.record("deployment.delete", "deployment", actor, entity_id=deployment_id, before_state=before_state)
        self.db.commit()

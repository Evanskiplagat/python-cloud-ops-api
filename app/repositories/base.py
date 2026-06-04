from typing import Generic, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


class Repository(Generic[ModelT]):
    def __init__(self, db: Session, model: type[ModelT]) -> None:
        self.db = db
        self.model = model

    def get(self, entity_id: int) -> ModelT | None:
        return self.db.get(self.model, entity_id)

    def add(self, entity: ModelT) -> ModelT:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def delete(self, entity: ModelT) -> None:
        self.db.delete(entity)

    def paginate(self, statement: Select, offset: int, limit: int) -> tuple[list[ModelT], int]:
        total = self.db.scalar(select(func.count()).select_from(statement.order_by(None).subquery())) or 0
        items = list(self.db.scalars(statement.offset(offset).limit(limit)).all())
        return items, total

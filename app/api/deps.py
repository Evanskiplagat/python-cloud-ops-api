from collections.abc import Generator

from fastapi import Request
from sqlalchemy.orm import Session

from app.database.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_token_store(request: Request):
    return request.app.state.redis


__all__ = ["get_db", "get_token_store"]

from app.database.base import Base
from app.database.session import engine
from app.models import *  # noqa: F403


def init_db() -> None:
    Base.metadata.create_all(bind=engine)

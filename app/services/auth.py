from datetime import timedelta

from fastapi import status
from sqlalchemy.orm import Session

from app.core.errors import AppException
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import TokenResponse, UserLogin, UserRegister


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)

    def register(self, payload: UserRegister) -> User:
        if self.users.get_by_email(payload.email):
            raise AppException("Email is already registered", status.HTTP_409_CONFLICT)
        user = User(
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=get_password_hash(payload.password),
            role=payload.role,
        )
        self.users.add(user)
        self.db.commit()
        return user

    def login(self, payload: UserLogin) -> TokenResponse:
        user = self.users.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.hashed_password):
            raise AppException("Invalid email or password", status.HTTP_401_UNAUTHORIZED)
        token = create_access_token(user.email, expires_delta=timedelta(minutes=60))
        return TokenResponse(access_token=token)

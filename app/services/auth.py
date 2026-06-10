from datetime import UTC, datetime, timedelta

from fastapi import status
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.errors import AppException
from app.core.security import create_access_token, create_refresh_token, decode_access_token, get_password_hash, verify_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import LogoutRequest, RefreshTokenRequest, TokenResponse, UserLogin, UserRegister
from app.services.audit import AuditService, snapshot_model


class AuthService:
    def __init__(self, db: Session, token_store) -> None:
        self.db = db
        self.token_store = token_store
        self.users = UserRepository(db)
        self.audit = AuditService(db)

    def _issue_token_pair(self, email: str) -> TokenResponse:
        return TokenResponse(
            access_token=create_access_token(email, expires_delta=timedelta(minutes=60)),
            refresh_token=create_refresh_token(email),
        )

    def _revoke_token(self, token: str) -> None:
        try:
            payload = decode_access_token(token)
        except JWTError as exc:
            raise AppException("Invalid token", status.HTTP_401_UNAUTHORIZED) from exc

        token_id = payload.get("jti")
        expiration = payload.get("exp")
        if not token_id or not expiration:
            raise AppException("Invalid token", status.HTTP_401_UNAUTHORIZED)

        ttl = max(int(datetime.fromtimestamp(expiration, tz=UTC).timestamp() - datetime.now(UTC).timestamp()), 1)
        self.token_store.set(f"revoked_token:{token_id}", "1", ex=ttl)

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
        self.audit.record("auth.register", "user", None, entity_id=user.id, after_state=snapshot_model(user))
        self.db.commit()
        return user

    def login(self, payload: UserLogin) -> TokenResponse:
        user = self.users.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.hashed_password):
            raise AppException("Invalid email or password", status.HTTP_401_UNAUTHORIZED)
        tokens = self._issue_token_pair(user.email)
        self.audit.record("auth.login", "user", user, entity_id=user.id, after_state={"email": user.email})
        self.db.commit()
        return tokens

    def refresh(self, payload: RefreshTokenRequest) -> TokenResponse:
        try:
            token_payload = decode_access_token(payload.refresh_token)
        except JWTError as exc:
            raise AppException("Invalid refresh token", status.HTTP_401_UNAUTHORIZED) from exc

        email = token_payload.get("sub")
        token_type = token_payload.get("type")
        token_id = token_payload.get("jti")
        if not email or token_type != "refresh" or not token_id:
            raise AppException("Invalid refresh token", status.HTTP_401_UNAUTHORIZED)
        if self.token_store.get(f"revoked_token:{token_id}"):
            raise AppException("Refresh token has been revoked", status.HTTP_401_UNAUTHORIZED)

        user = self.users.get_by_email(email)
        if not user or not user.is_active:
            raise AppException("User is inactive", status.HTTP_401_UNAUTHORIZED)

        self._revoke_token(payload.refresh_token)
        tokens = self._issue_token_pair(user.email)
        self.audit.record("auth.refresh", "user", user, entity_id=user.id, after_state={"email": user.email})
        self.db.commit()
        return tokens

    def logout(self, current_access_token: str, payload: LogoutRequest, current_user: User) -> None:
        self._revoke_token(current_access_token)
        self._revoke_token(payload.refresh_token)
        self.audit.record("auth.logout", "user", current_user, entity_id=current_user.id, after_state={"email": current_user.email})
        self.db.commit()

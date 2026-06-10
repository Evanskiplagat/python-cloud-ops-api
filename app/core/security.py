from datetime import UTC, datetime, timedelta
from uuid import uuid4

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def _create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    expire = datetime.now(UTC) + expires_delta
    return jwt.encode(
        {"sub": subject, "exp": expire, "type": token_type, "jti": str(uuid4())},
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    return _create_token(
        subject,
        "access",
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(subject: str, expires_delta: timedelta | None = None) -> str:
    return _create_token(
        subject,
        "refresh",
        expires_delta or timedelta(minutes=settings.refresh_token_expire_minutes),
    )


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

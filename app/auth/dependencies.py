from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_token_store
from app.core.config import settings
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.user import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")


def get_current_active_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    token_store=Depends(get_token_store),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        email = payload.get("sub")
        token_type = payload.get("type")
        token_id = payload.get("jti")
        if not email or token_type != "access" or not token_id:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc

    if token_store.get(f"revoked_token:{token_id}"):
        raise credentials_exception

    user = UserRepository(db).get_by_email(email=email)
    if not user or not user.is_active:
        raise credentials_exception
    return user

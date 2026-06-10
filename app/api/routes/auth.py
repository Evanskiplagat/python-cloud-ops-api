from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_token_store
from app.auth.dependencies import get_current_active_user, oauth2_scheme
from app.models.user import User
from app.schemas.auth import LogoutRequest, RefreshTokenRequest, TokenResponse, UserLogin, UserRegister, UserResponse
from app.services.auth import AuthService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db), token_store=Depends(get_token_store)) -> User:
    return AuthService(db, token_store).register(payload)


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db), token_store=Depends(get_token_store)) -> TokenResponse:
    return AuthService(db, token_store).login(payload)


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db),
    token_store=Depends(get_token_store),
) -> TokenResponse:
    return AuthService(db, token_store).refresh(payload)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    payload: LogoutRequest,
    db: Session = Depends(get_db),
    token_store=Depends(get_token_store),
    current_user: User = Depends(get_current_active_user),
    access_token: str = Depends(oauth2_scheme),
) -> Response:
    AuthService(db, token_store).logout(access_token, payload, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_active_user)) -> User:
    return current_user

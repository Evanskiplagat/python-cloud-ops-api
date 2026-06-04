from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.auth.dependencies import get_current_active_user
from app.core.enums import Role
from app.models.user import User


def require_roles(*allowed_roles: Role) -> Callable[[User], User]:
    def dependency(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user

    return dependency

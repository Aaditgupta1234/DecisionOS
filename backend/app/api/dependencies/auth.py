"""Authentication dependencies for route protection and RBAC authorization."""

from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.constants import UserRole
from app.database.session import get_db
from app.models.user import User
from app.schemas.token import TokenPayload
from app.services.auth_service import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    """Decodes JWT access token and retrieves the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        sub: str = payload.get("sub")
        if sub is None:
            raise credentials_exception
        token_data = TokenPayload(
            sub=sub,
            email=payload.get("email"),
            role=payload.get("role"),
            exp=payload.get("exp"),
        )
    except JWTError:
        raise credentials_exception

    try:
        user_uuid = UUID(token_data.sub)
    except ValueError:
        raise credentials_exception

    user = get_user_by_id(db, user_id=user_uuid)
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensures the authenticated user has an active account."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account.",
        )
    return current_user


def require_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """RBAC Dependency: Restricts endpoint access strictly to ADMIN role users."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted. Admin privileges required.",
        )
    return current_user

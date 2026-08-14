"""Authentication and RBAC authorization endpoint handlers."""

from typing import Any
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_active_user, require_admin
from app.core.security import create_access_token
from app.database.session import get_db
from app.models.user import User
from app.schemas.base import SuccessResponse
from app.schemas.token import TokenResponse
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.auth_service import authenticate_user, register_user

router = APIRouter()


@router.post(
    "/register",
    response_model=SuccessResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="User Registration",
)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
) -> Any:
    """Registers a new user account (defaults to ANALYST role)."""
    user = register_user(db=db, user_in=user_in)
    return SuccessResponse(
        message="User registered successfully.",
        data=UserResponse.model_validate(user),
    )


@router.post(
    "/login",
    response_model=SuccessResponse[TokenResponse],
    summary="User Login & OAuth2 Token Issue",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Any:
    """Authenticates user credentials and issues a signed JWT access token."""
    user = authenticate_user(
        db=db,
        email=form_data.username,
        password=form_data.password,
    )
    access_token = create_access_token(
        subject=user.id,
        extra_claims={
            "email": user.email,
            "role": user.role,
        },
    )
    return SuccessResponse(
        message="Login successful.",
        data=TokenResponse(
            access_token=access_token,
            token_type="bearer",
        ),
    )


@router.post(
    "/login/json",
    response_model=SuccessResponse[TokenResponse],
    summary="User Login (JSON Body alternative)",
)
def login_json(
    credentials: UserLogin,
    db: Session = Depends(get_db),
) -> Any:
    """Authenticates user credentials passed in JSON format and issues a JWT token."""
    user = authenticate_user(
        db=db,
        email=credentials.email,
        password=credentials.password,
    )
    access_token = create_access_token(
        subject=user.id,
        extra_claims={
            "email": user.email,
            "role": user.role,
        },
    )
    return SuccessResponse(
        message="Login successful.",
        data=TokenResponse(
            access_token=access_token,
            token_type="bearer",
        ),
    )


@router.get(
    "/me",
    response_model=SuccessResponse[UserResponse],
    summary="Current User Profile",
)
def get_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Returns profile information of the currently authenticated user."""
    return SuccessResponse(
        message="User profile retrieved.",
        data=UserResponse.model_validate(current_user),
    )


@router.get(
    "/health",
    summary="Protected Auth Health Verification",
)
def auth_health(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Returns JWT token authentication status and user payload metadata."""
    return {
        "authenticated": True,
        "user_id": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role,
    }


@router.get(
    "/admin-only",
    summary="Admin RBAC Protected Route",
)
def admin_only(
    current_user: User = Depends(require_admin),
) -> Any:
    """Protected endpoint accessible exclusively by ADMIN users."""
    return SuccessResponse(
        message="Admin access granted.",
        data={
            "admin": True,
            "user_id": str(current_user.id),
            "email": current_user.email,
        },
    )

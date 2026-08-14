"""Authentication Service Layer handling user registration, authentication, and user lookup."""

from typing import Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import UserRole
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Retrieves a user by email address."""
    return db.query(User).filter(User.email == email.lower().strip()).first()


def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
    """Retrieves a user by UUID primary key."""
    return db.query(User).filter(User.id == user_id).first()


def register_user(
    db: Session,
    user_in: UserCreate,
    role: UserRole = UserRole.ANALYST,
) -> User:
    """Registers a new user into the system with hashed password.
    
    Default role is ANALYST for security (prevents first-user admin escalation).
    """
    existing_user = get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists.",
        )

    db_user = User(
        email=user_in.email.lower().strip(),
        full_name=user_in.full_name.strip(),
        hashed_password=hash_password(user_in.password),
        role=role,
        is_active=True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User:
    """Authenticates user credentials and checks active account status.
    
    Raises HTTPException 401 if credentials invalid or 400 if user inactive.
    """
    user = get_user_by_email(db, email=email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive.",
        )

    return user

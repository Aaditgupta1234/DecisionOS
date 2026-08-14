"""JWT Token Schemas."""

from typing import Optional
from pydantic import BaseModel


class TokenResponse(BaseModel):
    """Token response returned upon successful login."""
    access_token: str
    token_type: str = "bearer"
    # TODO: Refresh token support (Future Phase enhancement)


class TokenPayload(BaseModel):
    """Payload decoded from signed JWT access tokens."""
    sub: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None

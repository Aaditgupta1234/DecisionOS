"""Base Pydantic response schemas for consistent API output across DecisionOS."""

from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success API response schema."""
    success: bool = True
    message: str = "Operation successful"
    data: Optional[T] = None


class ErrorResponse(BaseModel):
    """Standard error API response schema."""
    success: bool = False
    message: str = "An error occurred"
    details: Optional[Any] = None

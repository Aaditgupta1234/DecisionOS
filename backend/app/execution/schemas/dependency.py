"""Pydantic v2 schemas for Initiative Dependencies (Phase 12)."""

import uuid
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from app.execution.constants import DependencyType


class DependencyCreate(BaseModel):
    """Payload for creating a dependency between two initiatives."""
    source_initiative_id: UUID
    target_initiative_id: UUID
    dependency_type: DependencyType = DependencyType.BLOCKS
    notes: Optional[str] = Field(None, max_length=255)


class DependencyResponse(BaseModel):
    """Serialized initiative dependency response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    source_initiative_id: UUID
    source_initiative_title: Optional[str] = None
    target_initiative_id: UUID
    target_initiative_title: Optional[str] = None
    dependency_type: DependencyType
    notes: Optional[str] = None
    created_at: datetime


class DependencyListResponse(BaseModel):
    """Container response for dependencies of an initiative or organization."""
    organization_id: UUID
    initiative_id: Optional[UUID] = None
    total_dependencies: int = 0
    dependencies: List[DependencyResponse] = Field(default_factory=list)

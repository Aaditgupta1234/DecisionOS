"""Pydantic Schemas for Multi-Tenant Organizations and Memberships."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import OrgRole


class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="Organization display name")
    slug: Optional[str] = Field(None, min_length=2, max_length=255, description="Unique URL slug (auto-generated if omitted)")
    logo_url: Optional[str] = Field(None, max_length=1024, description="Optional logo image URL")


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    slug: Optional[str] = Field(None, min_length=2, max_length=255)
    logo_url: Optional[str] = Field(None, max_length=1024)
    is_active: Optional[bool] = None


class OrganizationMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    user_id: UUID
    role: OrgRole
    email: Optional[str] = None
    full_name: Optional[str] = None
    created_at: datetime


class OrganizationMemberCreate(BaseModel):
    email: str = Field(..., description="Email of user to add or invite to organization")
    role: OrgRole = Field(default=OrgRole.ANALYST, description="Assigned tenant role")


class OrganizationMemberUpdate(BaseModel):
    role: OrgRole = Field(..., description="Updated tenant role")


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    created_by: Optional[UUID] = None
    logo_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    current_user_role: Optional[OrgRole] = None
    member_count: Optional[int] = 1


class OrganizationDetailResponse(OrganizationResponse):
    members: List[OrganizationMemberResponse] = []

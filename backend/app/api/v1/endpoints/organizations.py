"""Organization and Multi-Tenant SaaS Endpoints."""

from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.base import SuccessResponse
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationDetailResponse,
    OrganizationMemberCreate,
    OrganizationMemberResponse,
    OrganizationMemberUpdate,
    OrganizationResponse,
    OrganizationUpdate,
)
from app.services.organization_service import OrganizationService

router = APIRouter()


@router.post(
    "",
    response_model=SuccessResponse[OrganizationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Organization",
)
async def create_organization(
    data: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Creates a new Organization with the caller as OWNER."""
    service = OrganizationService(db)
    result = await service.create_organization(current_user, data)
    return SuccessResponse(
        message="Organization created successfully.",
        data=result,
    )


@router.get(
    "",
    response_model=SuccessResponse[List[OrganizationResponse]],
    summary="List User Organizations",
)
async def list_organizations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Lists all organizations the caller belongs to."""
    service = OrganizationService(db)
    result = await service.get_user_organizations(current_user)
    return SuccessResponse(
        message="Organizations retrieved successfully.",
        data=result,
    )


@router.get(
    "/current",
    response_model=SuccessResponse[OrganizationResponse],
    summary="Get Current Active Organization",
)
async def get_current_organization(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Retrieves the caller's active/primary organization."""
    service = OrganizationService(db)
    result = await service.get_current_organization(current_user)
    return SuccessResponse(
        message="Current organization retrieved successfully.",
        data=result,
    )


@router.get(
    "/{org_id}",
    response_model=SuccessResponse[OrganizationDetailResponse],
    summary="Get Organization Details & Members",
)
async def get_organization(
    org_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Retrieves organization details including membership list."""
    service = OrganizationService(db)
    result = await service.get_organization_details(org_id, current_user)
    return SuccessResponse(
        message="Organization details retrieved successfully.",
        data=result,
    )


@router.patch(
    "/{org_id}",
    response_model=SuccessResponse[OrganizationResponse],
    summary="Update Organization Settings",
)
async def update_organization(
    org_id: UUID,
    data: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Updates organization profile settings (Requires OWNER or ADMIN)."""
    service = OrganizationService(db)
    result = await service.update_organization(org_id, current_user, data)
    return SuccessResponse(
        message="Organization updated successfully.",
        data=result,
    )


@router.get(
    "/{org_id}/members",
    response_model=SuccessResponse[List[OrganizationMemberResponse]],
    summary="List Organization Members",
)
async def list_members(
    org_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Lists all members of the organization."""
    service = OrganizationService(db)
    details = await service.get_organization_details(org_id, current_user)
    return SuccessResponse(
        message="Members retrieved successfully.",
        data=details.members,
    )


@router.post(
    "/{org_id}/members",
    response_model=SuccessResponse[OrganizationMemberResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add Member to Organization",
)
async def add_member(
    org_id: UUID,
    data: OrganizationMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Adds an existing user to the organization (Requires OWNER or ADMIN)."""
    service = OrganizationService(db)
    result = await service.add_or_invite_member(org_id, current_user, data.email, data.role)
    return SuccessResponse(
        message="Member added successfully.",
        data=result,
    )


@router.patch(
    "/{org_id}/members/{member_id}",
    response_model=SuccessResponse[OrganizationMemberResponse],
    summary="Update Member Role",
)
async def update_member_role(
    org_id: UUID,
    member_id: UUID,
    data: OrganizationMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Updates a member's role (Requires OWNER or ADMIN, protects last owner)."""
    service = OrganizationService(db)
    result = await service.update_member_role(org_id, current_user, member_id, data.role)
    return SuccessResponse(
        message="Member role updated successfully.",
        data=result,
    )


@router.delete(
    "/{org_id}/members/{member_id}",
    response_model=SuccessResponse[dict],
    summary="Remove Member from Organization",
)
async def remove_member(
    org_id: UUID,
    member_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Removes a member from the organization (Requires OWNER or ADMIN, protects last owner)."""
    service = OrganizationService(db)
    await service.remove_member(org_id, current_user, member_id)
    return SuccessResponse(
        message="Member removed successfully.",
        data={"removed_member_id": str(member_id)},
    )

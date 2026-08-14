"""Tenant authorization dependencies and multi-tenant security guards."""

from typing import Callable, Tuple
from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_active_user
from app.core.constants import OrgRole
from app.database.session import get_db
from app.models.dataset import Dataset
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.models.user import User
from app.repositories.organization_repository import OrganizationRepository

ROLE_HIERARCHY = {
    OrgRole.OWNER: 4,
    OrgRole.ADMIN: 3,
    OrgRole.ANALYST: 2,
    OrgRole.VIEWER: 1,
}


def require_org_membership(
    org_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Tuple[Organization, OrganizationMember]:
    """
    Ensures the current user is an active member of the specified organization.
    Returns (Organization, OrganizationMember).
    """
    repo = OrganizationRepository(db)
    # Synchronous helper check
    stmt_org = db.query(Organization).filter(Organization.id == org_id, Organization.is_active.is_(True)).first()
    if not stmt_org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found or inactive.",
        )

    membership = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org_id,
        OrganizationMember.user_id == current_user.id,
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You are not a member of this organization.",
        )

    return stmt_org, membership


def require_org_role(min_role: OrgRole) -> Callable:
    """
    Dependency factory verifying the caller holds at least `min_role` in the organization.
    """
    def _role_guard(
        org_and_member: Tuple[Organization, OrganizationMember] = Depends(require_org_membership),
    ) -> Tuple[Organization, OrganizationMember]:
        _, membership = org_and_member
        user_level = ROLE_HIERARCHY.get(membership.role, 0)
        required_level = ROLE_HIERARCHY.get(min_role, 99)

        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires minimum role '{min_role.value}'. Your role is '{membership.role.value}'.",
            )
        return org_and_member

    return _role_guard


def require_dataset_access(
    dataset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dataset:
    """
    Verifies that the current user has access to the specified dataset through
    organization membership or legacy ownership.
    """
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.is_deleted.is_(False)).first()
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found.",
        )

    # 1. If dataset is assigned to an organization, check membership
    if dataset.organization_id:
        membership = db.query(OrganizationMember).filter(
            OrganizationMember.organization_id == dataset.organization_id,
            OrganizationMember.user_id == current_user.id,
        ).first()

        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Dataset belongs to an organization you do not have access to.",
            )
    else:
        # 2. Fallback for legacy datasets before migration
        if dataset.uploaded_by != current_user.id and current_user.role.value != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to legacy unassigned dataset.",
            )

    return dataset

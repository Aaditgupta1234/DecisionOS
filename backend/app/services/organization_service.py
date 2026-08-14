"""Service Layer for Multi-Tenant Organization and Team Membership Management."""

import re
import uuid
from typing import List, Optional, Tuple, Union
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.constants import OrgRole
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.models.user import User
from app.repositories.organization_repository import OrganizationRepository
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationDetailResponse,
    OrganizationMemberResponse,
    OrganizationResponse,
    OrganizationUpdate,
)


class OrganizationService:
    """Business logic for Organizations, Tenancy, and RBAC Member management."""

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db
        self.repo = OrganizationRepository(db)

    def _slugify(self, text: str) -> str:
        s = re.sub(r"[^\w\s-]", "", text.lower()).strip()
        return re.sub(r"[-\s]+", "-", s)

    async def create_organization(
        self,
        caller: User,
        data: OrganizationCreate,
    ) -> OrganizationResponse:
        """Creates a new Organization and assigns the creator as OWNER."""
        base_slug = self._slugify(data.slug or data.name)
        if not base_slug:
            base_slug = f"org-{str(uuid.uuid4())[:8]}"

        existing = await self.repo.get_by_slug(base_slug)
        slug = base_slug if not existing else f"{base_slug}-{str(uuid.uuid4())[:6]}"

        org = await self.repo.create(
            name=data.name,
            slug=slug,
            created_by=caller.id,
            logo_url=data.logo_url,
        )

        # Creator is always assigned OWNER role
        await self.repo.add_member(org.id, caller.id, OrgRole.OWNER)

        return OrganizationResponse(
            id=org.id,
            name=org.name,
            slug=org.slug,
            created_by=org.created_by,
            logo_url=org.logo_url,
            is_active=org.is_active,
            created_at=org.created_at,
            updated_at=org.updated_at,
            current_user_role=OrgRole.OWNER,
            member_count=1,
        )

    async def get_user_organizations(self, caller: User) -> List[OrganizationResponse]:
        """Lists all organizations the user belongs to with their scoped role."""
        org_pairs = await self.repo.get_user_organizations(caller.id)
        if not org_pairs:
            # Auto-provision Personal Organization for backward compatibility
            default_org = await self.create_organization(
                caller,
                OrganizationCreate(name=f"{caller.full_name or 'Personal'} Workspace"),
            )
            return [default_org]

        result: List[OrganizationResponse] = []
        for org, member in org_pairs:
            members = await self.repo.get_members(org.id)
            result.append(
                OrganizationResponse(
                    id=org.id,
                    name=org.name,
                    slug=org.slug,
                    created_by=org.created_by,
                    logo_url=org.logo_url,
                    is_active=org.is_active,
                    created_at=org.created_at,
                    updated_at=org.updated_at,
                    current_user_role=member.role,
                    member_count=len(members),
                )
            )
        return result

    async def get_current_organization(self, caller: User) -> OrganizationResponse:
        """Retrieves user's primary/active organization."""
        orgs = await self.get_user_organizations(caller)
        return orgs[0]

    async def get_organization_details(
        self,
        org_id: UUID,
        caller: User,
    ) -> OrganizationDetailResponse:
        """Retrieves organization details and membership list for authorized members."""
        membership = await self.repo.get_membership(org_id, caller.id)
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You are not a member of this organization.",
            )

        org = await self.repo.get_by_id(org_id)
        if not org or not org.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found or inactive.",
            )

        members = await self.repo.get_members(org_id)
        member_responses = [
            OrganizationMemberResponse(
                id=m.id,
                organization_id=m.organization_id,
                user_id=m.user_id,
                role=m.role,
                email=m.user.email if m.user else None,
                full_name=m.user.full_name if m.user else None,
                created_at=m.created_at,
            )
            for m in members
        ]

        return OrganizationDetailResponse(
            id=org.id,
            name=org.name,
            slug=org.slug,
            created_by=org.created_by,
            logo_url=org.logo_url,
            is_active=org.is_active,
            created_at=org.created_at,
            updated_at=org.updated_at,
            current_user_role=membership.role,
            member_count=len(members),
            members=member_responses,
        )

    async def update_organization(
        self,
        org_id: UUID,
        caller: User,
        data: OrganizationUpdate,
    ) -> OrganizationResponse:
        """Updates organization details (Requires OWNER or ADMIN)."""
        membership = await self.repo.get_membership(org_id, caller.id)
        if not membership or membership.role not in [OrgRole.OWNER, OrgRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Organization Owners and Admins can update settings.",
            )

        org = await self.repo.get_by_id(org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found.",
            )

        update_kwargs = {}
        if data.name:
            update_kwargs["name"] = data.name
        if data.slug:
            existing = await self.repo.get_by_slug(data.slug)
            if existing and existing.id != org.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Slug '{data.slug}' is already in use by another organization.",
                )
            update_kwargs["slug"] = self._slugify(data.slug)
        if data.logo_url is not None:
            update_kwargs["logo_url"] = data.logo_url
        if data.is_active is not None:
            update_kwargs["is_active"] = data.is_active

        updated_org = await self.repo.update(org, **update_kwargs)
        members = await self.repo.get_members(org_id)

        return OrganizationResponse(
            id=updated_org.id,
            name=updated_org.name,
            slug=updated_org.slug,
            created_by=updated_org.created_by,
            logo_url=updated_org.logo_url,
            is_active=updated_org.is_active,
            created_at=updated_org.created_at,
            updated_at=updated_org.updated_at,
            current_user_role=membership.role,
            member_count=len(members),
        )

    async def add_or_invite_member(
        self,
        org_id: UUID,
        caller: User,
        email: str,
        role: OrgRole,
    ) -> OrganizationMemberResponse:
        """Adds an existing user to the organization (Requires OWNER or ADMIN)."""
        membership = await self.repo.get_membership(org_id, caller.id)
        if not membership or membership.role not in [OrgRole.OWNER, OrgRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Organization Owners and Admins can add members.",
            )

        # Find target user by email
        stmt = select(User).where(User.email == email.strip().lower())
        if hasattr(self.db, "execute") and self.repo._is_async():
            res = await self.db.execute(stmt)
        else:
            res = self.db.execute(stmt)
        target_user = res.scalar_one_or_none()

        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email '{email}' not found.",
            )

        existing_member = await self.repo.get_membership(org_id, target_user.id)
        if existing_member:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User '{email}' is already a member of this organization.",
            )

        new_member = await self.repo.add_member(org_id, target_user.id, role)
        return OrganizationMemberResponse(
            id=new_member.id,
            organization_id=new_member.organization_id,
            user_id=new_member.user_id,
            role=new_member.role,
            email=target_user.email,
            full_name=target_user.full_name,
            created_at=new_member.created_at,
        )

    async def update_member_role(
        self,
        org_id: UUID,
        caller: User,
        member_id: UUID,
        new_role: OrgRole,
    ) -> OrganizationMemberResponse:
        """Updates a member's role (Requires OWNER or ADMIN, protects last owner)."""
        caller_membership = await self.repo.get_membership(org_id, caller.id)
        if not caller_membership or caller_membership.role not in [OrgRole.OWNER, OrgRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Organization Owners and Admins can update roles.",
            )

        members = await self.repo.get_members(org_id)
        target_member = next((m for m in members if m.id == member_id), None)
        if not target_member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization member not found.",
            )

        # Protect last OWNER from being demoted
        if target_member.role == OrgRole.OWNER and new_role != OrgRole.OWNER:
            owner_count = await self.repo.count_owners(org_id)
            if owner_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot demote the last remaining Organization Owner.",
                )

        updated = await self.repo.update_member_role(target_member, new_role)
        return OrganizationMemberResponse(
            id=updated.id,
            organization_id=updated.organization_id,
            user_id=updated.user_id,
            role=updated.role,
            email=updated.user.email if updated.user else None,
            full_name=updated.user.full_name if updated.user else None,
            created_at=updated.created_at,
        )

    async def remove_member(
        self,
        org_id: UUID,
        caller: User,
        member_id: UUID,
    ) -> None:
        """Removes a member from the organization (Requires OWNER or ADMIN, protects last owner)."""
        caller_membership = await self.repo.get_membership(org_id, caller.id)
        if not caller_membership or caller_membership.role not in [OrgRole.OWNER, OrgRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Organization Owners and Admins can remove members.",
            )

        members = await self.repo.get_members(org_id)
        target_member = next((m for m in members if m.id == member_id), None)
        if not target_member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization member not found.",
            )

        # Protect last OWNER from being removed
        if target_member.role == OrgRole.OWNER:
            owner_count = await self.repo.count_owners(org_id)
            if owner_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot remove the last remaining Organization Owner.",
                )

        await self.repo.remove_member(target_member)

"""Repository for Multi-Tenant Organization and Membership Data Access."""

import uuid
from typing import List, Optional, Tuple, Union
from uuid import UUID
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload

from app.core.constants import OrgRole
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.models.user import User


class OrganizationRepository:
    """Data access repository for Organizations and Member roles."""

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db

    def _is_async(self) -> bool:
        return isinstance(self.db, AsyncSession)

    async def _execute(self, stmt):
        if self._is_async():
            return await self.db.execute(stmt)
        return self.db.execute(stmt)

    async def _commit(self):
        if self._is_async():
            await self.db.commit()
        else:
            self.db.commit()

    async def _refresh(self, obj):
        if self._is_async():
            await self.db.refresh(obj)
        else:
            self.db.refresh(obj)

    async def get_by_id(self, org_id: UUID) -> Optional[Organization]:
        stmt = select(Organization).where(Organization.id == org_id)
        result = await self._execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Organization]:
        stmt = select(Organization).where(Organization.slug == slug)
        result = await self._execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        name: str,
        slug: str,
        created_by: Optional[UUID] = None,
        logo_url: Optional[str] = None,
    ) -> Organization:
        org = Organization(
            name=name,
            slug=slug,
            created_by=created_by,
            logo_url=logo_url,
            is_active=True,
        )
        self.db.add(org)
        await self._commit()
        await self._refresh(org)
        return org

    async def update(self, org: Organization, **kwargs) -> Organization:
        for k, v in kwargs.items():
            if v is not None:
                setattr(org, k, v)
        await self._commit()
        await self._refresh(org)
        return org

    async def get_user_organizations(self, user_id: UUID) -> List[Tuple[Organization, OrganizationMember]]:
        stmt = (
            select(Organization, OrganizationMember)
            .join(OrganizationMember, Organization.id == OrganizationMember.organization_id)
            .where(OrganizationMember.user_id == user_id, Organization.is_active.is_(True))
            .order_by(Organization.created_at.asc())
        )
        result = await self._execute(stmt)
        return result.all()

    async def get_membership(self, org_id: UUID, user_id: UUID) -> Optional[OrganizationMember]:
        stmt = (
            select(OrganizationMember)
            .where(
                OrganizationMember.organization_id == org_id,
                OrganizationMember.user_id == user_id,
            )
        )
        result = await self._execute(stmt)
        return result.scalar_one_or_none()

    async def get_members(self, org_id: UUID) -> List[OrganizationMember]:
        stmt = (
            select(OrganizationMember)
            .options(selectinload(OrganizationMember.user))
            .where(OrganizationMember.organization_id == org_id)
            .order_by(OrganizationMember.created_at.asc())
        )
        result = await self._execute(stmt)
        return list(result.scalars().all())

    async def add_member(self, org_id: UUID, user_id: UUID, role: OrgRole = OrgRole.ANALYST) -> OrganizationMember:
        member = OrganizationMember(
            organization_id=org_id,
            user_id=user_id,
            role=role,
        )
        self.db.add(member)
        await self._commit()
        await self._refresh(member)
        return member

    async def update_member_role(self, member: OrganizationMember, new_role: OrgRole) -> OrganizationMember:
        member.role = new_role
        await self._commit()
        await self._refresh(member)
        return member

    async def remove_member(self, member: OrganizationMember) -> None:
        if self._is_async():
            await self.db.delete(member)
        else:
            self.db.delete(member)
        await self._commit()

    async def count_owners(self, org_id: UUID) -> int:
        stmt = (
            select(func.count(OrganizationMember.id))
            .where(
                OrganizationMember.organization_id == org_id,
                OrganizationMember.role == OrgRole.OWNER,
            )
        )
        result = await self._execute(stmt)
        return result.scalar() or 0

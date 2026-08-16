"""Repository layer for Phase 10.6 Governance Policies (Soft-Update / Permanent History)."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.governance.constants import (
    DEFAULT_POLICY_LIMIT,
    MAX_POLICY_LIMIT,
    GovernancePolicyType,
    GovernanceStatus,
)
from app.governance.models.governance_policy import GovernancePolicy


class GovernanceRepository:
    """
    Repository providing persistence, querying, version incrementing,
    and soft-disablement for platform and tenant governance policies.
    """

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db

    async def _execute(self, stmt):
        if isinstance(self.db, AsyncSession):
            return await self.db.execute(stmt)
        return self.db.execute(stmt)

    async def _commit(self):
        if isinstance(self.db, AsyncSession):
            await self.db.commit()
        else:
            self.db.commit()

    async def _flush(self):
        if isinstance(self.db, AsyncSession):
            await self.db.flush()
        else:
            self.db.flush()

    async def _refresh(self, instance):
        if isinstance(self.db, AsyncSession):
            await self.db.refresh(instance)
        else:
            self.db.refresh(instance)

    async def create_policy(
        self,
        policy_type: Union[GovernancePolicyType, str],
        policy_name: str,
        policy_value: Dict[str, Any],
        organization_id: Optional[uuid.UUID] = None,
        description: Optional[str] = None,
        effective_from: Optional[datetime] = None,
        created_by_user_id: Optional[uuid.UUID] = None,
    ) -> GovernancePolicy:
        """Create and persist a new governance policy entity."""
        pt_val = policy_type.value if isinstance(policy_type, GovernancePolicyType) else str(policy_type)

        policy = GovernancePolicy(
            organization_id=organization_id,
            policy_type=pt_val,
            policy_name=policy_name,
            policy_value=policy_value,
            description=description,
            status=GovernanceStatus.ACTIVE.value,
            policy_version=1,
            effective_from=effective_from,
            created_by_user_id=created_by_user_id,
            updated_by_user_id=created_by_user_id,
        )
        self.db.add(policy)
        await self._commit()
        await self._refresh(policy)
        return policy

    async def get_policy(
        self, policy_id: uuid.UUID, organization_id: Optional[uuid.UUID] = None
    ) -> Optional[GovernancePolicy]:
        """Fetch a single policy by ID, optionally enforcing organization scope."""
        query = select(GovernancePolicy).where(GovernancePolicy.id == policy_id)
        if organization_id is not None:
            query = query.where(
                (GovernancePolicy.organization_id == organization_id)
                | (GovernancePolicy.organization_id.is_(None))
            )
        res = await self._execute(query)
        return res.scalars().first()

    async def list_policies(
        self,
        organization_id: Optional[uuid.UUID] = None,
        policy_type: Optional[Union[GovernancePolicyType, str]] = None,
        status: Optional[Union[GovernanceStatus, str]] = None,
        limit: int = DEFAULT_POLICY_LIMIT,
        offset: int = 0,
    ) -> Tuple[List[GovernancePolicy], int]:
        """List policies with filtering and pagination."""
        clamped_limit = max(1, min(limit, MAX_POLICY_LIMIT))
        query = select(GovernancePolicy)
        count_query = select(func.count(GovernancePolicy.id))

        if organization_id is not None:
            query = query.where(
                (GovernancePolicy.organization_id == organization_id)
                | (GovernancePolicy.organization_id.is_(None))
            )
            count_query = count_query.where(
                (GovernancePolicy.organization_id == organization_id)
                | (GovernancePolicy.organization_id.is_(None))
            )

        if policy_type is not None:
            pt_val = policy_type.value if isinstance(policy_type, GovernancePolicyType) else str(policy_type)
            query = query.where(GovernancePolicy.policy_type == pt_val)
            count_query = count_query.where(GovernancePolicy.policy_type == pt_val)

        if status is not None:
            st_val = status.value if isinstance(status, GovernanceStatus) else str(status)
            query = query.where(GovernancePolicy.status == st_val)
            count_query = count_query.where(GovernancePolicy.status == st_val)

        query = query.order_by(desc(GovernancePolicy.created_at)).offset(offset).limit(clamped_limit)

        total_res = await self._execute(count_query)
        total = total_res.scalar() or 0

        items_res = await self._execute(query)
        items = list(items_res.scalars().all())

        return items, total

    async def update_policy(
        self,
        policy_id: uuid.UUID,
        policy_name: Optional[str] = None,
        policy_value: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        status: Optional[Union[GovernanceStatus, str]] = None,
        effective_from: Optional[datetime] = None,
        updated_by_user_id: Optional[uuid.UUID] = None,
        organization_id: Optional[uuid.UUID] = None,
    ) -> Optional[GovernancePolicy]:
        """Update policy attributes, auto-incrementing policy_version."""
        policy = await self.get_policy(policy_id, organization_id=organization_id)
        if not policy:
            return None

        if policy_name is not None:
            policy.policy_name = policy_name
        if policy_value is not None:
            policy.policy_value = policy_value
        if description is not None:
            policy.description = description
        if status is not None:
            st_val = status.value if isinstance(status, GovernanceStatus) else str(status)
            policy.status = st_val
        if effective_from is not None:
            policy.effective_from = effective_from

        policy.policy_version += 1
        policy.updated_by_user_id = updated_by_user_id
        policy.updated_at = datetime.now(timezone.utc)

        await self._commit()
        await self._refresh(policy)
        return policy

    async def disable_policy(
        self,
        policy_id: uuid.UUID,
        updated_by_user_id: Optional[uuid.UUID] = None,
        organization_id: Optional[uuid.UUID] = None,
    ) -> Optional[GovernancePolicy]:
        """Soft-disable a policy without hard deleting historical records."""
        return await self.update_policy(
            policy_id=policy_id,
            status=GovernanceStatus.DISABLED.value,
            updated_by_user_id=updated_by_user_id,
            organization_id=organization_id,
        )

    async def get_policy_by_type(
        self,
        policy_type: Union[GovernancePolicyType, str],
        organization_id: Optional[uuid.UUID] = None,
        active_only: bool = True,
    ) -> Optional[GovernancePolicy]:
        """Fetch the latest active policy for a specific type and organization scope."""
        pt_val = policy_type.value if isinstance(policy_type, GovernancePolicyType) else str(policy_type)
        query = select(GovernancePolicy).where(GovernancePolicy.policy_type == pt_val)

        if organization_id is not None:
            query = query.where(GovernancePolicy.organization_id == organization_id)
        else:
            query = query.where(GovernancePolicy.organization_id.is_(None))

        if active_only:
            query = query.where(GovernancePolicy.status == GovernanceStatus.ACTIVE.value)

        query = query.order_by(desc(GovernancePolicy.created_at))
        res = await self._execute(query)
        return res.scalars().first()

"""Governance Policy Engine for Phase 10.6 Platform Administration & Governance."""

import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.governance.schemas.governance import EffectivePoliciesResponse, EffectivePolicyItem
from app.governance.constants import (
    DEFAULT_GOVERNANCE_POLICIES,
    EFFECTIVE_POLICY_CACHE_TTL_SECONDS,
    GovernancePolicyType,
    GovernanceStatus,
    PolicySource,
)
from app.governance.models.governance_policy import GovernancePolicy
from app.governance.repositories.governance_repository import GovernanceRepository


class EffectivePolicyCache:
    """Thread-safe in-memory cache for resolved effective policies with 60s TTL."""

    def __init__(self, ttl_seconds: int = EFFECTIVE_POLICY_CACHE_TTL_SECONDS):
        self._ttl_seconds = ttl_seconds
        self._cache: Dict[uuid.UUID, Tuple[EffectivePoliciesResponse, float]] = {}
        self._lock = threading.Lock()
        self.cache_hits: int = 0
        self.cache_misses: int = 0

    def get(self, organization_id: uuid.UUID) -> Optional[EffectivePoliciesResponse]:
        with self._lock:
            if organization_id not in self._cache:
                self.cache_misses += 1
                return None

            response, expiry = self._cache[organization_id]
            if time.time() > expiry:
                del self._cache[organization_id]
                self.cache_misses += 1
                return None

            self.cache_hits += 1
            # Return copy with cached=True
            cached_resp = response.model_copy()
            cached_resp.cached = True
            return cached_resp

    def set(self, organization_id: uuid.UUID, response: EffectivePoliciesResponse) -> None:
        with self._lock:
            expiry = time.time() + self._ttl_seconds
            self._cache[organization_id] = (response.model_copy(), expiry)

    def invalidate(self, organization_id: Optional[uuid.UUID] = None) -> None:
        with self._lock:
            if organization_id is not None:
                self._cache.pop(organization_id, None)
            else:
                self._cache.clear()

    def get_metrics(self) -> Dict[str, Any]:
        with self._lock:
            total = self.cache_hits + self.cache_misses
            hit_rate = round((self.cache_hits / total) * 100.0, 2) if total > 0 else 100.0
            return {
                "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses,
                "total_requests": total,
                "cache_hit_rate_percent": hit_rate,
                "cached_tenants_count": len(self._cache),
            }


# Singleton effective policy cache
effective_policy_cache = EffectivePolicyCache()


class GovernancePolicyEngine:
    """
    Core engine resolving effective governance policies through hierarchy:
    Tenant Organization Policy -> Global Platform Policy -> Safe Built-in Defaults.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db
        self.repo = GovernanceRepository(db)
        self.cache = effective_policy_cache

    async def get_effective_policy(
        self,
        organization_id: uuid.UUID,
        policy_type: Union[GovernancePolicyType, str],
    ) -> EffectivePolicyItem:
        """
        Resolve active effective policy for an organization.
        Respects effective_from dates (only active if effective_from is None or <= now).
        """
        pt_val = policy_type.value if isinstance(policy_type, GovernancePolicyType) else str(policy_type)
        now = datetime.now(timezone.utc)

        # 1. Organization-specific policy check
        org_policies, _ = await self.repo.list_policies(
            organization_id=organization_id,
            policy_type=pt_val,
            status=GovernanceStatus.ACTIVE.value,
            limit=10,
        )
        for p in org_policies:
            if p.organization_id == organization_id:
                eff_from = p.effective_from
                if eff_from is not None and eff_from.tzinfo is None:
                    eff_from = eff_from.replace(tzinfo=timezone.utc)
                if eff_from is None or eff_from <= now:
                    return EffectivePolicyItem(
                        source=PolicySource.ORGANIZATION,
                        policy_id=p.id,
                        policy_name=p.policy_name,
                        policy_version=p.policy_version,
                        effective_from=p.effective_from,
                        value=p.policy_value,
                    )

        # 2. Global platform policy check
        global_policies, _ = await self.repo.list_policies(
            organization_id=None,
            policy_type=pt_val,
            status=GovernanceStatus.ACTIVE.value,
            limit=10,
        )
        for p in global_policies:
            if p.organization_id is None:
                eff_from = p.effective_from
                if eff_from is not None and eff_from.tzinfo is None:
                    eff_from = eff_from.replace(tzinfo=timezone.utc)
                if eff_from is None or eff_from <= now:
                    return EffectivePolicyItem(
                        source=PolicySource.GLOBAL,
                        policy_id=p.id,
                        policy_name=p.policy_name,
                        policy_version=p.policy_version,
                        effective_from=p.effective_from,
                        value=p.policy_value,
                    )

        # 3. Built-in default fallback
        default_val = DEFAULT_GOVERNANCE_POLICIES.get(pt_val, {})
        return EffectivePolicyItem(
            source=PolicySource.DEFAULT,
            policy_id=None,
            policy_name=f"Default {pt_val.replace('_', ' ').title()} Policy",
            policy_version=1,
            effective_from=None,
            value=default_val,
        )

    async def get_all_effective_policies(
        self,
        organization_id: uuid.UUID,
        force_refresh: bool = False,
    ) -> EffectivePoliciesResponse:
        """
        Resolve all effective policies across every GovernancePolicyType for an organization,
        leveraging the 60s TTL effective policy cache.
        """
        if not force_refresh:
            cached = self.cache.get(organization_id)
            if cached is not None:
                return cached

        resolved_policies: Dict[str, EffectivePolicyItem] = {}
        for pt in GovernancePolicyType:
            resolved_policies[pt.value] = await self.get_effective_policy(organization_id, pt)

        response = EffectivePoliciesResponse(
            organization_id=organization_id,
            policies=resolved_policies,
            cached=False,
            generated_at=datetime.now(timezone.utc),
        )
        self.cache.set(organization_id, response)
        return response

    async def validate_job_execution(
        self,
        organization_id: uuid.UUID,
        active_running_jobs_count: int,
    ) -> Tuple[bool, Optional[str]]:
        """Validate if a new job can be dispatched under current governance execution policy."""
        policy_item = await self.get_effective_policy(organization_id, GovernancePolicyType.JOB_EXECUTION)
        max_jobs = policy_item.value.get("max_concurrent_jobs", 10)

        if active_running_jobs_count >= max_jobs:
            return False, f"Maximum concurrent jobs limit ({max_jobs}) reached for organization."
        return True, None

    async def validate_schedule_execution(
        self,
        organization_id: uuid.UUID,
        active_schedules_count: int,
    ) -> Tuple[bool, Optional[str]]:
        """Validate if a new schedule can be created under current governance policy."""
        policy_item = await self.get_effective_policy(organization_id, GovernancePolicyType.SCHEDULE_EXECUTION)
        max_scheds = policy_item.value.get("max_active_schedules", 20)

        if active_schedules_count >= max_scheds:
            return False, f"Maximum active schedules limit ({max_scheds}) reached for organization."
        return True, None

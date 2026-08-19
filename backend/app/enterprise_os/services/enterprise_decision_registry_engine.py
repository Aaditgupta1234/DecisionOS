"""Enterprise Decision Registry Engine for Phase 6.7."""

import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from app.enterprise_os.schemas.os_schemas import (
    EnterpriseDecisionResponse,
    EnterpriseDecisionCreateRequest,
)


class EnterpriseDecisionRegistryEngine:
    """Permanent corporate memory managing full decision lifecycles, business cases, and realized value."""

    @classmethod
    def create_decision(cls, payload: EnterpriseDecisionCreateRequest) -> EnterpriseDecisionResponse:
        """Register a new enterprise decision into the permanent corporate registry."""
        now = datetime.now(timezone.utc)
        return EnterpriseDecisionResponse(
            id=uuid.uuid4(),
            portfolio_id=payload.portfolio_id,
            decision_code=payload.decision_code,
            title=payload.title,
            decision_type=payload.decision_type,
            decision_owner=uuid.uuid4(),
            owner_role=payload.owner_role,
            business_case=payload.business_case,
            expected_value=payload.expected_value,
            approved_value=payload.expected_value,
            actual_value=None,
            status="DRAFT",
            created_at=now,
        )

    @classmethod
    def get_sample_decisions(cls, portfolio_id: uuid.UUID) -> List[EnterpriseDecisionResponse]:
        """Returns catalog of registered enterprise decisions."""
        now = datetime.now(timezone.utc)
        return [
            EnterpriseDecisionResponse(
                id=uuid.uuid4(),
                portfolio_id=portfolio_id,
                decision_code="DEC-2026-042",
                title="Southeastern Carrier Route Reallocation & SLA Penalty Enforcement",
                decision_type="STRATEGIC",
                decision_owner=uuid.uuid4(),
                owner_role="VP Operations",
                business_case="Reroute 40% parcel volume to northern fulfillment nodes and enforce 15% courier SLA billing penalties to recover customer retention.",
                expected_value=340000.0,
                approved_value=340000.0,
                actual_value=312000.0,
                status="IMPLEMENTED",
                created_at=now - timedelta(days=45),
            ),
            EnterpriseDecisionResponse(
                id=uuid.uuid4(),
                portfolio_id=portfolio_id,
                decision_code="DEC-2026-043",
                title="Q2 Dynamic Pricing & Courier Surcharge Hedging",
                decision_type="FINANCIAL",
                decision_owner=uuid.uuid4(),
                owner_role="CFO",
                business_case="Deploy dynamic fuel and freight surcharge indexing to protect gross margins across multi-tenant delivery tiers.",
                expected_value=180000.0,
                approved_value=180000.0,
                actual_value=None,
                status="APPROVED",
                created_at=now - timedelta(days=12),
            ),
            EnterpriseDecisionResponse(
                id=uuid.uuid4(),
                portfolio_id=portfolio_id,
                decision_code="DEC-2026-044",
                title="Secondary Regional Fulfillment Node Expansion",
                decision_type="BOARD",
                decision_owner=uuid.uuid4(),
                owner_role="Chief Executive Officer",
                business_case="Board directive to authorize $1.2M capital expenditure for autonomous sorting infrastructure in secondary hub.",
                expected_value=850000.0,
                approved_value=None,
                actual_value=None,
                status="UNDER_REVIEW",
                created_at=now - timedelta(days=2),
            ),
        ]

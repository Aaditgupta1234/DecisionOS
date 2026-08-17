"""REST API Endpoints for Phase 12.9: Executive Decision Support & Portfolio Optimization."""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_active_user
from app.database.session import get_db
from app.execution.schemas.decision_support import (
    ExecutiveDecisionItem,
    ExecutiveDecisionSupportResponse,
    ExecutiveInterventionQueueResponse,
    InvestmentPriorityItem,
    PortfolioBalanceMetrics,
)
from app.execution.services.decision_support_service import DecisionSupportService
from app.models.user import User

decision_support_router = APIRouter(
    prefix="/decision-support",
    tags=["Execution Decision Support & Portfolio Optimization"],
)


def _resolve_org_id(current_user: User, organization_id: Optional[uuid.UUID] = None) -> uuid.UUID:
    """Resolves and enforces multi-tenant organization boundaries."""
    if organization_id:
        return organization_id
    if getattr(current_user, "organization_id", None):
        return current_user.organization_id
    if getattr(current_user, "memberships", None) and len(current_user.memberships) > 0:
        return current_user.memberships[0].organization_id
    return current_user.id


@decision_support_router.get(
    "",
    response_model=ExecutiveDecisionSupportResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Portfolio-wide Executive Decision Support Intelligence",
)
async def get_executive_decision_support(
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ExecutiveDecisionSupportResponse:
    """Returns complete deterministic decision support, investment priorities, balance metrics, and readiness ratings."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = DecisionSupportService(db)
    return await service.get_executive_decision_support(org_id)


@decision_support_router.get(
    "/actions",
    response_model=List[ExecutiveDecisionItem],
    status_code=status.HTTP_200_OK,
    summary="Get Prioritized Executive Actions",
)
async def get_executive_actions(
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[ExecutiveDecisionItem]:
    """Returns prioritized executive action items with impact tiers, explainable drivers, and reason codes."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = DecisionSupportService(db)
    return await service.get_executive_actions(org_id)


@decision_support_router.get(
    "/investments",
    response_model=List[InvestmentPriorityItem],
    status_code=status.HTTP_200_OK,
    summary="Get Ranked Investment Priorities",
)
async def get_investment_priorities(
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[InvestmentPriorityItem]:
    """Returns ranked investment priority opportunities with expected value and risk-adjusted ROI."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = DecisionSupportService(db)
    return await service.get_investment_priorities(org_id)


@decision_support_router.get(
    "/balance",
    response_model=PortfolioBalanceMetrics,
    status_code=status.HTTP_200_OK,
    summary="Get Portfolio Structural Balance & Concentration",
)
async def get_portfolio_balance(
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PortfolioBalanceMetrics:
    """Returns portfolio balance score, risk/value dispersion, SPOF counts, and strategic exposure."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = DecisionSupportService(db)
    return await service.get_portfolio_balance(org_id)


@decision_support_router.get(
    "/interventions",
    response_model=ExecutiveInterventionQueueResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Segmented Executive Intervention Queue",
)
async def get_intervention_queue(
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ExecutiveInterventionQueueResponse:
    """Returns categorized intervention candidates (escalate, stabilize, accelerate, restructure) and pressure grade."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = DecisionSupportService(db)
    return await service.get_intervention_queue(org_id)

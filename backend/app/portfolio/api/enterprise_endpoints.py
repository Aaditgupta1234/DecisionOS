"""REST API Endpoints for Phase 5.2 Enterprise Portfolio Intelligence."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.dependencies.auth import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.portfolio.models.portfolio_entity import (
    Portfolio,
    BusinessUnit,
    Department,
    PortfolioDataset,
    PortfolioIntelligenceReport,
)
from app.portfolio.schemas.enterprise_portfolio import (
    PortfolioCreate,
    PortfolioResponse,
    PortfolioDetailResponse,
    PortfolioDatasetLinkRequest,
    PortfolioDatasetResponse,
    PortfolioHealthResponse,
    CrossDatasetBenchmarkResponse,
    DepartmentScorecardResponse,
    PortfolioIntelligenceSummaryResponse,
)
from app.portfolio.services.portfolio_health_engine import PortfolioHealthEngine
from app.portfolio.services.benchmarking_engine import CrossDatasetBenchmarkingEngine
from app.portfolio.services.department_scorecard_engine import DepartmentScorecardEngine
from app.portfolio.services.portfolio_summary_engine import PortfolioSummaryEngine

enterprise_portfolio_router = APIRouter(prefix="/enterprise", tags=["Enterprise Portfolio Intelligence"])


def _resolve_org_id(current_user: User) -> uuid.UUID:
    """Resolve active organization ID for user."""
    if getattr(current_user, "organization_id", None):
        return current_user.organization_id
    if getattr(current_user, "memberships", None) and len(current_user.memberships) > 0:
        return current_user.memberships[0].organization_id
    return current_user.id


@enterprise_portfolio_router.get(
    "/",
    response_model=List[PortfolioResponse],
    summary="List all enterprise portfolios",
)
async def list_portfolios(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[PortfolioResponse]:
    """Retrieve all active portfolios within the organization."""
    org_id = _resolve_org_id(current_user)
    stmt = select(Portfolio).where(Portfolio.organization_id == org_id, Portfolio.is_active == True)
    result = await db.execute(stmt)
    portfolios = result.scalars().all()
    return [PortfolioResponse.model_validate(p) for p in portfolios]


@enterprise_portfolio_router.post(
    "/",
    response_model=PortfolioDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new enterprise portfolio",
)
async def create_portfolio(
    payload: PortfolioCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PortfolioDetailResponse:
    """Create a new portfolio along with its initial business units and departments."""
    org_id = _resolve_org_id(current_user)

    portfolio = Portfolio(
        organization_id=org_id,
        name=payload.name,
        code=payload.code,
        description=payload.description,
        currency=payload.currency,
        is_active=payload.is_active,
    )
    db.add(portfolio)
    await db.flush()

    # Optional initial business units
    if payload.business_units:
        for bu_in in payload.business_units:
            bu = BusinessUnit(
                portfolio_id=portfolio.id,
                name=bu_in.name,
                code=bu_in.code,
                lead_owner=bu_in.lead_owner,
                budget_allocated=bu_in.budget_allocated,
                headcount=bu_in.headcount,
            )
            db.add(bu)
            await db.flush()

            if bu_in.departments:
                for dept_in in bu_in.departments:
                    dept = Department(
                        business_unit_id=bu.id,
                        name=dept_in.name,
                        code=dept_in.code,
                        lead_owner=dept_in.lead_owner,
                    )
                    db.add(dept)

    await db.commit()
    await db.refresh(portfolio)
    return PortfolioDetailResponse.model_validate(portfolio)


@enterprise_portfolio_router.get(
    "/{portfolio_id}",
    response_model=PortfolioDetailResponse,
    summary="Get enterprise portfolio details",
)
async def get_portfolio_detail(
    portfolio_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PortfolioDetailResponse:
    """Retrieve detailed portfolio structure including business units and linked datasets."""
    stmt = select(Portfolio).where(Portfolio.id == portfolio_id)
    result = await db.execute(stmt)
    portfolio = result.scalar_one_or_none()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with ID {portfolio_id} not found.",
        )

    return PortfolioDetailResponse.model_validate(portfolio)


@enterprise_portfolio_router.get(
    "/{portfolio_id}/health",
    response_model=PortfolioHealthResponse,
    summary="Get weighted enterprise portfolio health",
)
async def get_portfolio_health(
    portfolio_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PortfolioHealthResponse:
    """Calculate and return deterministic weighted health scores across business units."""
    return PortfolioHealthEngine.calculate_health(portfolio_id, [])


@enterprise_portfolio_router.get(
    "/{portfolio_id}/benchmarks",
    response_model=CrossDatasetBenchmarkResponse,
    summary="Generate cross-dataset comparative benchmarks",
)
async def get_cross_dataset_benchmarks(
    portfolio_id: uuid.UUID,
    baseline_dataset_id: Optional[uuid.UUID] = Query(None),
    target_dataset_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> CrossDatasetBenchmarkResponse:
    """Compare performance metrics between datasets deterministically."""
    b_id = baseline_dataset_id or uuid.uuid4()
    t_id = target_dataset_id or uuid.uuid4()
    return CrossDatasetBenchmarkingEngine.generate_benchmarks(portfolio_id, b_id, t_id)


@enterprise_portfolio_router.get(
    "/{portfolio_id}/scorecards",
    response_model=DepartmentScorecardResponse,
    summary="Retrieve department scorecards",
)
async def get_department_scorecards(
    portfolio_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> DepartmentScorecardResponse:
    """Generate department-level health and KPI scorecards."""
    return DepartmentScorecardEngine.generate_scorecards(portfolio_id)


@enterprise_portfolio_router.get(
    "/{portfolio_id}/summary",
    response_model=PortfolioIntelligenceSummaryResponse,
    summary="Get Executive Portfolio Intelligence Summary Memo",
)
async def get_portfolio_summary_report(
    portfolio_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PortfolioIntelligenceSummaryResponse:
    """Generate executive-level portfolio brief synthesizing health, benchmarks, and recovery."""
    return PortfolioSummaryEngine.generate_summary(portfolio_id)


@enterprise_portfolio_router.post(
    "/{portfolio_id}/datasets",
    response_model=PortfolioDatasetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Link a dataset to an enterprise portfolio",
)
async def link_dataset_to_portfolio(
    portfolio_id: uuid.UUID,
    payload: PortfolioDatasetLinkRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PortfolioDatasetResponse:
    """Link a dataset to a portfolio and assign it to an optional Business Unit and Department."""
    link = PortfolioDataset(
        portfolio_id=portfolio_id,
        dataset_id=payload.dataset_id,
        business_unit_id=payload.business_unit_id,
        department_id=payload.department_id,
        weight=payload.weight,
        is_primary_benchmark=payload.is_primary_benchmark,
    )
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return PortfolioDatasetResponse.model_validate(link)

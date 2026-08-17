"""FastAPI Router for Phase 12.8 Historical Snapshots & Time-Series Intelligence."""

import uuid
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_active_user
from app.database.session import get_db
from app.execution.constants import (
    SnapshotRetentionCategory,
    SnapshotTriggerSource,
)
from app.execution.schemas.snapshot import (
    CreateInitiativeSnapshotRequest,
    CreatePortfolioSnapshotRequest,
    CreateProgramSnapshotRequest,
    InitiativeReplayResponse,
    InitiativeSnapshotHistoryResponse,
    InitiativeSnapshotResponse,
    PortfolioReplayResponse,
    PortfolioSnapshotHistoryResponse,
    PortfolioSnapshotResponse,
    ProgramReplayResponse,
    ProgramSnapshotHistoryResponse,
    ProgramSnapshotResponse,
    SnapshotComparisonResponse,
)
from app.execution.services.snapshot_service import SnapshotService
from app.models.user import User

snapshot_router = APIRouter(prefix="/snapshots", tags=["Strategic Snapshots & Time-Series"])


def _resolve_org_id(current_user: User, organization_id: Optional[uuid.UUID] = None) -> uuid.UUID:
    """Resolves and enforces multi-tenant organization boundaries."""
    if organization_id:
        return organization_id
    if getattr(current_user, "organization_id", None):
        return current_user.organization_id
    if getattr(current_user, "memberships", None) and len(current_user.memberships) > 0:
        return current_user.memberships[0].organization_id
    return current_user.id


# ==============================================================================
# Portfolio Snapshot Endpoints
# ==============================================================================

@snapshot_router.post(
    "/portfolio",
    response_model=PortfolioSnapshotResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Portfolio Snapshot",
    description="Captures an immutable, cryptographically-hashed point-in-time snapshot of the portfolio state.",
)
async def create_portfolio_snapshot(
    request: Optional[CreatePortfolioSnapshotRequest] = None,
    organization_id: Optional[uuid.UUID] = Query(None, description="Super admin override org ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PortfolioSnapshotResponse:
    org_id = _resolve_org_id(current_user, organization_id)
    service = SnapshotService(db)
    return await service.create_portfolio_snapshot(
        organization_id=org_id,
        request=request,
        user_id=current_user.id,
    )


@snapshot_router.get(
    "/portfolio",
    response_model=PortfolioSnapshotResponse,
    summary="Get Latest Portfolio Snapshot",
    description="Retrieves the most recent portfolio snapshot or automatically captures one if none exist.",
)
async def get_latest_portfolio_snapshot(
    organization_id: Optional[uuid.UUID] = Query(None, description="Super admin override org ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PortfolioSnapshotResponse:
    org_id = _resolve_org_id(current_user, organization_id)
    service = SnapshotService(db)
    return await service.get_latest_portfolio_snapshot(org_id)


@snapshot_router.get(
    "/portfolio/baseline",
    response_model=PortfolioSnapshotResponse,
    summary="Get Baseline Portfolio Snapshot",
    description="Retrieves the designated baseline portfolio snapshot for the organization.",
)
async def get_baseline_portfolio_snapshot(
    organization_id: Optional[uuid.UUID] = Query(None, description="Super admin override org ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PortfolioSnapshotResponse:
    org_id = _resolve_org_id(current_user, organization_id)
    service = SnapshotService(db)
    return await service.get_baseline_portfolio_snapshot(org_id)


@snapshot_router.get(
    "/portfolio/history",
    response_model=PortfolioSnapshotHistoryResponse,
    summary="Get Portfolio Snapshot History & Time-Series",
    description="Retrieves historical snapshots with rolling statistical moments and portfolio momentum analytics.",
)
async def get_portfolio_snapshot_history(
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    retention_category: Optional[SnapshotRetentionCategory] = Query(None, description="Retention tier filter"),
    trigger_source: Optional[SnapshotTriggerSource] = Query(None, description="Trigger source filter"),
    limit: int = Query(100, ge=1, le=500, description="Max snapshots to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Super admin override org ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PortfolioSnapshotHistoryResponse:
    org_id = _resolve_org_id(current_user, organization_id)
    service = SnapshotService(db)
    return await service.list_portfolio_snapshots_history(
        organization_id=org_id,
        start_date=start_date,
        end_date=end_date,
        retention_category=retention_category,
        trigger_source=trigger_source,
        limit=limit,
        offset=offset,
    )


@snapshot_router.get(
    "/portfolio/{snapshot_id}",
    response_model=PortfolioSnapshotResponse,
    summary="Get Portfolio Snapshot by ID",
    description="Retrieves a specific portfolio snapshot with cryptographic integrity verification.",
)
async def get_portfolio_snapshot_by_id(
    snapshot_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Super admin override org ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PortfolioSnapshotResponse:
    org_id = _resolve_org_id(current_user, organization_id)
    service = SnapshotService(db)
    return await service.get_portfolio_snapshot(org_id, snapshot_id)


# ==============================================================================
# Program Snapshot Endpoints
# ==============================================================================

@snapshot_router.post(
    "/programs/{program_id}",
    response_model=ProgramSnapshotResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Program Snapshot",
    description="Captures a point-in-time snapshot for a specific strategic program.",
)
async def create_program_snapshot(
    program_id: uuid.UUID,
    request: Optional[CreateProgramSnapshotRequest] = None,
    organization_id: Optional[uuid.UUID] = Query(None, description="Super admin override org ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ProgramSnapshotResponse:
    org_id = _resolve_org_id(current_user, organization_id)
    service = SnapshotService(db)
    return await service.create_program_snapshot(
        organization_id=org_id,
        program_id=program_id,
        request=request,
        user_id=current_user.id,
    )


@snapshot_router.get(
    "/programs/{program_id}",
    response_model=ProgramSnapshotHistoryResponse,
    summary="Get Program Snapshots",
    description="Retrieves snapshot history for a specific strategic program.",
)
async def get_program_snapshots(
    program_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Super admin override org ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ProgramSnapshotHistoryResponse:
    org_id = _resolve_org_id(current_user, organization_id)
    service = SnapshotService(db)
    return await service.get_program_snapshot(org_id, program_id)


# ==============================================================================
# Initiative Snapshot Endpoints
# ==============================================================================

@snapshot_router.post(
    "/initiatives/{initiative_id}",
    response_model=InitiativeSnapshotResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Initiative Snapshot",
    description="Captures a point-in-time snapshot for a specific strategic initiative.",
)
async def create_initiative_snapshot(
    initiative_id: uuid.UUID,
    request: Optional[CreateInitiativeSnapshotRequest] = None,
    organization_id: Optional[uuid.UUID] = Query(None, description="Super admin override org ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> InitiativeSnapshotResponse:
    org_id = _resolve_org_id(current_user, organization_id)
    service = SnapshotService(db)
    return await service.create_initiative_snapshot(
        organization_id=org_id,
        initiative_id=initiative_id,
        request=request,
        user_id=current_user.id,
    )


@snapshot_router.get(
    "/initiatives/{initiative_id}",
    response_model=InitiativeSnapshotHistoryResponse,
    summary="Get Initiative Snapshots",
    description="Retrieves snapshot history for a specific strategic initiative.",
)
async def get_initiative_snapshots(
    initiative_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Super admin override org ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> InitiativeSnapshotHistoryResponse:
    org_id = _resolve_org_id(current_user, organization_id)
    service = SnapshotService(db)
    return await service.get_initiative_snapshot(org_id, initiative_id)


# ==============================================================================
# Replay Endpoints
# ==============================================================================

@snapshot_router.get(
    "/replay/portfolio/{snapshot_id}",
    response_model=PortfolioReplayResponse,
    summary="Replay Portfolio State",
    description="Reconstructs lossless historical execution, outcome, and ranking state from a PortfolioSnapshot.",
)
async def replay_portfolio_snapshot(
    snapshot_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Super admin override org ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PortfolioReplayResponse:
    org_id = _resolve_org_id(current_user, organization_id)
    service = SnapshotService(db)
    return await service.replay_portfolio_snapshot(org_id, snapshot_id)


@snapshot_router.get(
    "/replay/program/{snapshot_id}",
    response_model=ProgramReplayResponse,
    summary="Replay Program State",
    description="Reconstructs historical program state from a ProgramSnapshot.",
)
async def replay_program_snapshot(
    snapshot_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Super admin override org ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ProgramReplayResponse:
    org_id = _resolve_org_id(current_user, organization_id)
    service = SnapshotService(db)
    return await service.replay_program_snapshot(org_id, snapshot_id)


@snapshot_router.get(
    "/replay/initiative/{snapshot_id}",
    response_model=InitiativeReplayResponse,
    summary="Replay Initiative State",
    description="Reconstructs historical initiative state from an InitiativeSnapshot.",
)
async def replay_initiative_snapshot(
    snapshot_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Super admin override org ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> InitiativeReplayResponse:
    org_id = _resolve_org_id(current_user, organization_id)
    service = SnapshotService(db)
    return await service.replay_initiative_snapshot(org_id, snapshot_id)


# ==============================================================================
# Differential Comparison Endpoint
# ==============================================================================

@snapshot_router.get(
    "/compare",
    response_model=SnapshotComparisonResponse,
    summary="Compare Snapshots",
    description="Calculates deterministic metric deltas, trend shifts, and maturity adjustments between two snapshots.",
)
async def compare_snapshots(
    snapshot_a: Optional[uuid.UUID] = Query(None, description="Baseline / Older snapshot ID"),
    snapshot_b: Optional[uuid.UUID] = Query(None, description="Comparison / Newer snapshot ID"),
    baseline_compare: bool = Query(False, description="Auto-compare current state against baseline"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Super admin override org ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> SnapshotComparisonResponse:
    org_id = _resolve_org_id(current_user, organization_id)
    service = SnapshotService(db)
    return await service.compare_snapshots(
        organization_id=org_id,
        snapshot_a_id=snapshot_a,
        snapshot_b_id=snapshot_b,
        baseline_compare=baseline_compare,
    )

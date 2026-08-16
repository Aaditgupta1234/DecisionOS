"""REST API Endpoints for Outcomes & Benefits Realization Engine (Phase 12.6)."""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, Response, status

from app.api.dependencies.auth import get_current_active_user
from app.database.session import get_db
from app.execution.constants import (
    BenefitRealizationStatus,
    BenefitType,
    OutcomeCriticality,
    OutcomeMetricType,
    OutcomeStatus,
    TargetDateStatus,
)
from app.execution.schemas.outcomes import (
    BenefitRealizationCreate,
    BenefitRealizationListResponse,
    BenefitRealizationResponse,
    BenefitRealizationUpdate,
    InitiativeOutcomeSummary,
    OutcomeMeasurementCreate,
    OutcomeMeasurementListResponse,
    OutcomeMeasurementResponse,
    OutcomeMeasurementUpdate,
    PortfolioBenefitsSummary,
    ProgramOutcomeSummary,
    ROIMetrics,
)
from app.execution.services.outcome_service import OutcomeService
from app.models.user import User

outcome_router = APIRouter(tags=["Outcomes & Benefits Realization Engine (Phase 12.6)"])


def _resolve_org_id(current_user: User, organization_id: Optional[uuid.UUID] = None) -> uuid.UUID:
    """Resolve active organization ID for the authenticated user."""
    if organization_id:
        return organization_id
    if getattr(current_user, "organization_id", None):
        return current_user.organization_id
    if getattr(current_user, "memberships", None) and len(current_user.memberships) > 0:
        return current_user.memberships[0].organization_id
    return current_user.id


# ------------------------------------------------------------------------------
# 1. OUTCOME MEASUREMENTS ENDPOINTS
# ------------------------------------------------------------------------------

@outcome_router.post(
    "/outcomes",
    response_model=OutcomeMeasurementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record Outcome Measurement",
)
async def record_outcome(
    payload: OutcomeMeasurementCreate,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization scope override"),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> OutcomeMeasurementResponse:
    """Records a new outcome measurement against an initiative."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = OutcomeService(db)
    actor_name = getattr(current_user, "name", "User") or "User"
    return await service.record_outcome(
        organization_id=org_id,
        payload=payload,
        actor_name=actor_name,
        actor_id=current_user.id,
    )


@outcome_router.get(
    "/outcomes",
    response_model=OutcomeMeasurementListResponse,
    summary="List Outcome Measurements",
)
async def list_outcomes(
    initiative_id: Optional[uuid.UUID] = Query(None, description="Filter by strategic initiative"),
    status_filter: Optional[OutcomeStatus] = Query(None, alias="status", description="Filter by realization status"),
    metric_type: Optional[OutcomeMetricType] = Query(None, description="Filter by outcome dimension"),
    criticality: Optional[OutcomeCriticality] = Query(None, description="Filter by strategic criticality"),
    target_date_status: Optional[TargetDateStatus] = Query(None, description="Filter by timeline schedule status"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization scope override"),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> OutcomeMeasurementListResponse:
    """Lists outcome measurements with count rollups and filters."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = OutcomeService(db)
    return await service.list_outcomes(
        organization_id=org_id,
        initiative_id=initiative_id,
        status_filter=status_filter,
        metric_type=metric_type,
        criticality=criticality,
        target_date_status=target_date_status,
        limit=limit,
        offset=offset,
    )


@outcome_router.get(
    "/outcomes/{outcome_id}",
    response_model=OutcomeMeasurementResponse,
    summary="Get Outcome Measurement",
)
async def get_outcome(
    outcome_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization scope override"),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> OutcomeMeasurementResponse:
    """Retrieves a single outcome measurement."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = OutcomeService(db)
    return await service.get_outcome(organization_id=org_id, outcome_id=outcome_id)


@outcome_router.patch(
    "/outcomes/{outcome_id}",
    response_model=OutcomeMeasurementResponse,
    summary="Update Outcome Measurement",
)
async def update_outcome(
    outcome_id: uuid.UUID,
    payload: OutcomeMeasurementUpdate,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization scope override"),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> OutcomeMeasurementResponse:
    """Updates an outcome measurement (auto-increments version)."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = OutcomeService(db)
    actor_name = getattr(current_user, "name", "User") or "User"
    return await service.update_outcome(
        organization_id=org_id,
        outcome_id=outcome_id,
        payload=payload,
        actor_name=actor_name,
        actor_id=current_user.id,
    )


@outcome_router.delete(
    "/outcomes/{outcome_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Outcome Measurement",
)
async def delete_outcome(
    outcome_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization scope override"),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
):
    """Deletes an outcome measurement."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = OutcomeService(db)
    await service.delete_outcome(organization_id=org_id, outcome_id=outcome_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ------------------------------------------------------------------------------
# 2. BENEFITS REALIZATION ENDPOINTS
# ------------------------------------------------------------------------------

@outcome_router.post(
    "/benefits",
    response_model=BenefitRealizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record Benefit Realization",
)
async def record_benefit(
    payload: BenefitRealizationCreate,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization scope override"),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> BenefitRealizationResponse:
    """Records a new benefit realization record for an initiative."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = OutcomeService(db)
    actor_name = getattr(current_user, "name", "User") or "User"
    return await service.record_benefit(
        organization_id=org_id,
        payload=payload,
        actor_name=actor_name,
        actor_id=current_user.id,
    )


@outcome_router.get(
    "/benefits/summary",
    response_model=PortfolioBenefitsSummary,
    summary="Portfolio Benefits Summary Card",
)
async def get_portfolio_benefits_summary(
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization scope override"),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> PortfolioBenefitsSummary:
    """Retrieves portfolio-wide executive benefits and outcome realization summary."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = OutcomeService(db)
    return await service.get_portfolio_benefits_summary(organization_id=org_id)


@outcome_router.get(
    "/benefits",
    response_model=BenefitRealizationListResponse,
    summary="List Benefit Realizations",
)
async def list_benefits(
    initiative_id: Optional[uuid.UUID] = Query(None, description="Filter by strategic initiative"),
    benefit_type: Optional[BenefitType] = Query(None, description="Filter by benefit category"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization scope override"),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> BenefitRealizationListResponse:
    """Lists benefit realization records."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = OutcomeService(db)
    return await service.list_benefits(
        organization_id=org_id,
        initiative_id=initiative_id,
        benefit_type=benefit_type,
        limit=limit,
        offset=offset,
    )


@outcome_router.get(
    "/benefits/{benefit_id}",
    response_model=BenefitRealizationResponse,
    summary="Get Benefit Realization",
)
async def get_benefit(
    benefit_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization scope override"),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> BenefitRealizationResponse:
    """Retrieves a single benefit realization record."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = OutcomeService(db)
    return await service.get_benefit(organization_id=org_id, benefit_id=benefit_id)


@outcome_router.patch(
    "/benefits/{benefit_id}",
    response_model=BenefitRealizationResponse,
    summary="Update Benefit Realization",
)
async def update_benefit(
    benefit_id: uuid.UUID,
    payload: BenefitRealizationUpdate,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization scope override"),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> BenefitRealizationResponse:
    """Updates a benefit realization record."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = OutcomeService(db)
    actor_name = getattr(current_user, "name", "User") or "User"
    return await service.update_benefit(
        organization_id=org_id,
        benefit_id=benefit_id,
        payload=payload,
        actor_name=actor_name,
        actor_id=current_user.id,
    )


@outcome_router.delete(
    "/benefits/{benefit_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Benefit Realization",
)
async def delete_benefit(
    benefit_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization scope override"),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
):
    """Deletes a benefit realization record."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = OutcomeService(db)
    await service.delete_benefit(organization_id=org_id, benefit_id=benefit_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ------------------------------------------------------------------------------
# 3. EXECUTIVE SUMMARIES & ROI ENDPOINTS
# ------------------------------------------------------------------------------

@outcome_router.get(
    "/initiatives/{initiative_id}/outcomes",
    response_model=InitiativeOutcomeSummary,
    summary="Initiative Outcomes Realization Summary",
)
async def get_initiative_outcome_summary(
    initiative_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization scope override"),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> InitiativeOutcomeSummary:
    """Retrieves synthesized outcome profile and ROI for an initiative."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = OutcomeService(db)
    return await service.get_initiative_outcome_summary(organization_id=org_id, initiative_id=initiative_id)


@outcome_router.get(
    "/programs/{program_id}/outcomes",
    response_model=ProgramOutcomeSummary,
    summary="Program Outcomes Realization Summary",
)
async def get_program_outcome_summary(
    program_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization scope override"),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> ProgramOutcomeSummary:
    """Retrieves aggregated outcome summary across all initiatives in a program."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = OutcomeService(db)
    return await service.get_program_outcome_summary(organization_id=org_id, program_id=program_id)


@outcome_router.get(
    "/initiatives/{initiative_id}/roi",
    response_model=ROIMetrics,
    summary="Initiative ROI Intelligence",
)
async def get_initiative_roi(
    initiative_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization scope override"),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> ROIMetrics:
    """Retrieves ROI intelligence for an initiative."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = OutcomeService(db)
    return await service.get_initiative_roi(organization_id=org_id, initiative_id=initiative_id)

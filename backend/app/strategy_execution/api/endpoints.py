"""REST API Endpoints for Phase 6.5 Enterprise Strategy Execution & Value Realization Platform."""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies.auth import get_current_active_user
from app.models.user import User
from app.strategy_execution.schemas.strategy_schemas import (
    BenefitsRealizationReportResponse,
    CriticalPathResponse,
    ExecutiveDecisionRecordResponse,
    ExecutivePerformanceProfileResponse,
    ForecastAccuracyRecordResponse,
    InitiativeDependencyCreateRequest,
    InitiativeDependencyResponse,
    InitiativeMilestoneCreateRequest,
    InitiativeMilestoneResponse,
    InitiativeRiskCreateRequest,
    InitiativeRiskResponse,
    InitiativeVersionResponse,
    PortfolioValueRealizationResponse,
    StrategicInitiativeCreateRequest,
    StrategicInitiativeResponse,
    StrategicInitiativeUpdateRequest,
    StrategyReviewCycleCreateRequest,
    StrategyReviewCycleResponse,
)
from app.strategy_execution.services.strategy_execution_engine import StrategyExecutionEngine
from app.strategy_execution.services.dependency_intelligence_engine import DependencyIntelligenceEngine
from app.strategy_execution.services.benefits_realization_engine import BenefitsRealizationEngine
from app.strategy_execution.services.forecast_calibration_engine import ForecastCalibrationEngine
from app.strategy_execution.services.outcome_attribution_engine import OutcomeAttributionEngine
from app.strategy_execution.services.executive_accountability_engine import ExecutiveAccountabilityEngine
from app.strategy_execution.services.executive_performance_engine import ExecutivePerformanceEngine
from app.strategy_execution.services.strategy_review_engine import StrategyReviewEngine

strategy_execution_router = APIRouter(
    tags=["Enterprise Strategy Execution & Value Realization Platform"],
)


# --- 1. Strategic Initiatives Lifecycle ---

@strategy_execution_router.post(
    "/initiatives",
    response_model=StrategicInitiativeResponse,
    summary="Create a new strategic initiative",
)
async def create_initiative(
    payload: StrategicInitiativeCreateRequest,
    current_user: User = Depends(get_current_active_user),
) -> StrategicInitiativeResponse:
    """Register an approved strategic initiative."""
    now = datetime.now(timezone.utc)
    return StrategicInitiativeResponse(
        id=uuid.uuid4(),
        portfolio_id=payload.portfolio_id,
        initiative_code=payload.initiative_code,
        title=payload.title,
        description=payload.description,
        status="APPROVED",
        priority=payload.priority,
        owner_id=payload.owner_id,
        sponsor_id=payload.sponsor_id,
        expected_arr_impact=payload.expected_arr_impact,
        expected_health_impact=payload.expected_health_impact,
        expected_risk_reduction=payload.expected_risk_reduction,
        actual_arr_impact=None,
        actual_health_impact=None,
        actual_risk_reduction=None,
        completion_pct=0.0,
        version=1,
        target_completion_date=payload.target_completion_date,
        actual_completion_date=None,
        created_at=now,
        updated_at=now,
    )


@strategy_execution_router.get(
    "/initiatives",
    response_model=List[StrategicInitiativeResponse],
    summary="List all strategic initiatives",
)
async def list_initiatives(
    portfolio_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_active_user),
) -> List[StrategicInitiativeResponse]:
    """Retrieve initiatives across the portfolio."""
    p_id = portfolio_id or uuid.uuid4()
    return StrategyExecutionEngine.get_sample_initiatives(p_id)


@strategy_execution_router.get(
    "/initiatives/{id}",
    response_model=StrategicInitiativeResponse,
    summary="Get single strategic initiative",
)
async def get_initiative(
    id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
) -> StrategicInitiativeResponse:
    """Retrieve detailed initiative by ID."""
    now = datetime.now(timezone.utc)
    return StrategicInitiativeResponse(
        id=id,
        portfolio_id=uuid.uuid4(),
        initiative_code="INIT-2026-001",
        title="Secondary Hub Courier Rebalancing & Automated SLA Penalties",
        description="Enforce 15% courier SLA billing penalties and rebalance transit volume across Southeastern regional distribution nodes.",
        status="IN_PROGRESS",
        priority="CRITICAL",
        owner_id=uuid.uuid4(),
        sponsor_id=uuid.uuid4(),
        expected_arr_impact=124000.0,
        expected_health_impact=11.0,
        expected_risk_reduction=-10.2,
        actual_arr_impact=118000.0,
        actual_health_impact=10.5,
        actual_risk_reduction=-9.8,
        completion_pct=78.0,
        version=3,
        target_completion_date=now + timedelta(days=20),
        actual_completion_date=None,
        created_at=now - timedelta(days=60),
        updated_at=now,
    )


# --- 2. Initiative Versions, Risks & Milestones ---

@strategy_execution_router.get(
    "/initiatives/{id}/versions",
    response_model=List[InitiativeVersionResponse],
    summary="Get initiative historical revisions",
)
async def get_initiative_versions(
    id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
) -> List[InitiativeVersionResponse]:
    """Retrieve version audit trail for an initiative."""
    now = datetime.now(timezone.utc)
    return [
        InitiativeVersionResponse(
            id=uuid.uuid4(),
            initiative_id=id,
            version=3,
            created_by=current_user.id,
            change_summary="Calibrated ARR recovery expectation to +$118K based on actual Southeastern courier data.",
            expected_arr=118000.0,
            target_date=now + timedelta(days=20),
            created_at=now - timedelta(days=10),
        ),
        InitiativeVersionResponse(
            id=uuid.uuid4(),
            initiative_id=id,
            version=2,
            created_by=current_user.id,
            change_summary="Added $25.8K win-back tokens into scope.",
            expected_arr=95000.0,
            target_date=now + timedelta(days=35),
            created_at=now - timedelta(days=30),
        ),
        InitiativeVersionResponse(
            id=uuid.uuid4(),
            initiative_id=id,
            version=1,
            created_by=current_user.id,
            change_summary="Initial scope approved by Board of Directors.",
            expected_arr=124000.0,
            target_date=now + timedelta(days=60),
            created_at=now - timedelta(days=60),
        ),
    ]


@strategy_execution_router.get(
    "/initiatives/{id}/risks",
    response_model=List[InitiativeRiskResponse],
    summary="Get risk register for initiative",
)
async def get_initiative_risks(
    id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
) -> List[InitiativeRiskResponse]:
    """Retrieve risk register records."""
    now = datetime.now(timezone.utc)
    return [
        InitiativeRiskResponse(
            id=uuid.uuid4(),
            initiative_id=id,
            risk_title="Courier Churn During SLA Transition",
            risk_description="Couriers in bottom 20% latency bracket may terminate contracts upon penalty enforcement.",
            probability=0.25,
            impact=0.40,
            severity="HIGH",
            mitigation_plan="Dynamically route 30% volume to secondary regional carrier partners during transition.",
            status="MITIGATING",
            created_at=now,
        ),
        InitiativeRiskResponse(
            id=uuid.uuid4(),
            initiative_id=id,
            risk_title="Support Ticket Spikes",
            risk_description="Customer inquiry volume regarding delivery delay credits may surge during initial 14 days.",
            probability=0.15,
            impact=0.20,
            severity="MEDIUM",
            mitigation_plan="Deploy automated tracking webhook push alerts directly to customer mobile apps.",
            status="MITIGATED",
            created_at=now,
        ),
    ]


@strategy_execution_router.get(
    "/initiatives/{id}/milestones",
    response_model=List[InitiativeMilestoneResponse],
    summary="Get milestones for initiative",
)
async def get_initiative_milestones(
    id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
) -> List[InitiativeMilestoneResponse]:
    """Retrieve milestone checklist."""
    now = datetime.now(timezone.utc)
    return [
        InitiativeMilestoneResponse(
            id=uuid.uuid4(),
            initiative_id=id,
            title="Deploy Automated SLA Penalty Billing Rules",
            description="Configure 15% penalty trigger on shipments with >4.5 day latency.",
            target_date=now - timedelta(days=30),
            completed_date=now - timedelta(days=28),
            status="COMPLETED",
            completion_pct=100.0,
            order_index=1,
            created_at=now - timedelta(days=60),
        ),
        InitiativeMilestoneResponse(
            id=uuid.uuid4(),
            initiative_id=id,
            title="Southeastern Hub Load Rebalancing",
            description="Reroute 40% of parcel volume across 4 secondary regional nodes.",
            target_date=now - timedelta(days=10),
            completed_date=now - timedelta(days=12),
            status="COMPLETED",
            completion_pct=100.0,
            order_index=2,
            created_at=now - timedelta(days=60),
        ),
        InitiativeMilestoneResponse(
            id=uuid.uuid4(),
            initiative_id=id,
            title="Finalize 90-Day Retention Lift Audit",
            description="Confirm customer retention exceeds 84.0% threshold.",
            target_date=now + timedelta(days=20),
            completed_date=None,
            status="IN_PROGRESS",
            completion_pct=60.0,
            order_index=3,
            created_at=now - timedelta(days=60),
        ),
    ]


# --- 3. Dependency Intelligence & Critical Path ---

@strategy_execution_router.get(
    "/initiatives/critical-path",
    response_model=CriticalPathResponse,
    summary="Get initiative critical path DAG",
)
async def get_critical_path(
    portfolio_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_active_user),
) -> CriticalPathResponse:
    """Retrieve critical execution path and blocker graph."""
    p_id = portfolio_id or uuid.uuid4()
    return DependencyIntelligenceEngine.get_critical_path(p_id)


# --- 4. Value Realization & Forecast Calibration ---

@strategy_execution_router.get(
    "/value-realization",
    response_model=PortfolioValueRealizationResponse,
    summary="Get headline portfolio value realization",
)
async def get_portfolio_value_realization(
    portfolio_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_active_user),
) -> PortfolioValueRealizationResponse:
    """Retrieve portfolio-wide realized value metrics."""
    p_id = portfolio_id or uuid.uuid4()
    return BenefitsRealizationEngine.get_portfolio_value_realization(p_id)


@strategy_execution_router.get(
    "/value-realization/{initiative_id}",
    response_model=BenefitsRealizationReportResponse,
    summary="Get initiative-level benefits realization report",
)
async def get_initiative_value_realization(
    initiative_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
) -> BenefitsRealizationReportResponse:
    """Retrieve forecast vs actual realization report."""
    return BenefitsRealizationEngine.get_initiative_realization_report(initiative_id)


@strategy_execution_router.get(
    "/forecast-accuracy/{initiative_id}",
    response_model=ForecastAccuracyRecordResponse,
    summary="Get forecast accuracy record for initiative",
)
async def get_forecast_accuracy(
    initiative_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
) -> ForecastAccuracyRecordResponse:
    """Retrieve forecast accuracy calibration record."""
    return ForecastCalibrationEngine.get_forecast_accuracy(initiative_id)


@strategy_execution_router.get(
    "/forecast-accuracy",
    summary="Get portfolio calibration metrics",
)
async def get_portfolio_calibration(
    portfolio_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Retrieve portfolio-wide calibration parameters."""
    p_id = portfolio_id or uuid.uuid4()
    return ForecastCalibrationEngine.get_portfolio_calibration_metrics(p_id)


# --- 5. Executive Accountability, Performance & Strategy Reviews ---

@strategy_execution_router.get(
    "/accountability",
    response_model=List[ExecutiveDecisionRecordResponse],
    summary="Get full executive decision ledger",
)
async def get_accountability_ledger(
    portfolio_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_active_user),
) -> List[ExecutiveDecisionRecordResponse]:
    """Retrieve executive decision ledger."""
    p_id = portfolio_id or uuid.uuid4()
    return ExecutiveAccountabilityEngine.get_executive_decision_ledger(p_id)


@strategy_execution_router.get(
    "/executive-performance",
    response_model=List[ExecutivePerformanceProfileResponse],
    summary="Get executive performance scorecards and rankings",
)
async def get_executive_performance(
    portfolio_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_active_user),
) -> List[ExecutivePerformanceProfileResponse]:
    """Retrieve leadership performance scorecards and rankings."""
    p_id = portfolio_id or uuid.uuid4()
    return ExecutivePerformanceEngine.get_executive_performance_profiles(p_id)


@strategy_execution_router.get(
    "/strategy-reviews",
    response_model=List[StrategyReviewCycleResponse],
    summary="Get quarterly institutional strategy reviews",
)
async def get_strategy_reviews(
    portfolio_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_active_user),
) -> List[StrategyReviewCycleResponse]:
    """Retrieve historical strategy review cycles."""
    p_id = portfolio_id or uuid.uuid4()
    return StrategyReviewEngine.get_review_cycles(p_id)

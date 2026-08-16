"""Unit tests for Execution Risk Engine (Phase 12.4)."""

from datetime import datetime, timezone
import uuid
import pytest

from app.execution.constants import (
    EXECUTION_RISK_ENGINE_VERSION,
    BudgetHealth,
    ExecutionRiskFactor,
    ExecutionRiskSeverity,
    MilestoneCriticality,
    MilestoneStatus,
    RiskTrend,
    ScheduleStatus,
    TimelineRiskLevel,
    VelocityGrade,
)
from app.execution.models.initiative import StrategicInitiative
from app.execution.models.milestone import InitiativeMilestone
from app.execution.schemas.progress import (
    BudgetIntelligenceMetrics,
    ExecutionVelocityMetrics,
    ScheduleAdherenceMetrics,
)
from app.execution.schemas.timeline import (
    CriticalPathMetrics,
    MilestoneMetrics,
    TimelineRiskMetrics,
)
from app.execution.services.execution_risk_engine import ExecutionRiskEngine


def test_execution_risk_engine_low_risk():
    """Verifies that an initiative on schedule with no blockers achieves LOW risk severity."""
    now = datetime(2026, 8, 16, 12, 0, 0, tzinfo=timezone.utc)
    init = StrategicInitiative(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        title="Mobile App Release",
        description="Release iOS and Android native apps.",
        objective="Deliver 5-star mobile experience.",
    )

    tr_m = TimelineRiskMetrics(
        timeline_risk_score=10.0,
        timeline_risk_level=TimelineRiskLevel.LOW,
        top_risk_factors=[],
    )
    cp_m = CriticalPathMetrics(
        critical_path_length=3,
        critical_milestone_count=3,
        critical_initiative_count=1,
        critical_path_duration_days=21,
        projected_delay_days=0,
        critical_path_stability_score=100.0,
    )
    s_m = ScheduleAdherenceMetrics(
        planned_progress=50.0,
        actual_progress=55.0,
        schedule_variance=5.0,
        schedule_status=ScheduleStatus.AHEAD,
        on_track=True,
        deadline_risk_score=5.0,
    )
    v_m = ExecutionVelocityMetrics(
        velocity_score=80.0,
        milestones_completed_per_week=1.0,
        milestones_completed_per_month=4.0,
        average_completion_time_days=7.0,
        velocity_grade=VelocityGrade.GOOD,
        data_sufficient=True,
    )
    b_m = BudgetIntelligenceMetrics(
        budget_allocated=50000.0,
        budget_spent=25000.0,
        budget_utilization_percentage=50.0,
        budget_variance=25000.0,
        daily_burn_rate=500.0,
        projected_completion_spend=50000.0,
        budget_score=90.0,
        budget_health=BudgetHealth.HEALTHY,
        projection_confidence="HIGH",
    )

    risk = ExecutionRiskEngine.calculate_risk(
        initiative=init,
        milestones=[],
        dependencies=[],
        timeline_risk_metrics=tr_m,
        critical_path_metrics=cp_m,
        schedule_metrics=s_m,
        velocity_metrics=v_m,
        budget_metrics=b_m,
        previous_risk_score=15.0,
        as_of_date=now,
    )

    assert risk.risk_score < 30.0
    assert risk.risk_severity == ExecutionRiskSeverity.LOW
    assert risk.risk_trend in (RiskTrend.STABLE, RiskTrend.IMPROVING)
    assert risk.blocked_milestone_count == 0
    assert risk.engine_version == EXECUTION_RISK_ENGINE_VERSION
    assert risk.snapshot_compatible is True


def test_execution_risk_engine_critical_risk_and_factors():
    """Verifies that multiple blocked critical milestones and severe slippage yield CRITICAL risk severity with typed factors."""
    now = datetime(2026, 8, 16, 12, 0, 0, tzinfo=timezone.utc)
    org_id = uuid.uuid4()
    init = StrategicInitiative(
        id=uuid.uuid4(),
        organization_id=org_id,
        title="Core Banking Engine Upgrade",
        description="Migrate core banking transactional engine.",
        objective="Zero-downtime core banking migration.",
    )

    # 2 blocked critical milestones
    m1 = InitiativeMilestone(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init.id,
        title="Audit Certification",
        criticality=MilestoneCriticality.CRITICAL,
        status=MilestoneStatus.BLOCKED,
    )
    m2 = InitiativeMilestone(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init.id,
        title="Data Reconciliation",
        criticality=MilestoneCriticality.CRITICAL,
        status=MilestoneStatus.BLOCKED,
    )

    tr_m = TimelineRiskMetrics(
        timeline_risk_score=90.0,
        timeline_risk_level=TimelineRiskLevel.CRITICAL,
        top_risk_factors=["Critical blocker active"],
    )
    cp_m = CriticalPathMetrics(
        critical_path_length=4,
        critical_milestone_count=4,
        critical_initiative_count=1,
        critical_path_duration_days=30,
        projected_delay_days=21,
        critical_path_stability_score=30.0,
    )
    s_m = ScheduleAdherenceMetrics(
        planned_progress=75.0,
        actual_progress=20.0,
        schedule_variance=-55.0,
        schedule_status=ScheduleStatus.CRITICAL_DELAY,
        on_track=False,
        deadline_risk_score=90.0,
    )
    v_m = ExecutionVelocityMetrics(
        velocity_score=15.0,
        milestones_completed_per_week=0.1,
        milestones_completed_per_month=0.4,
        average_completion_time_days=30.0,
        velocity_grade=VelocityGrade.CRITICAL,
        data_sufficient=True,
    )
    b_m = BudgetIntelligenceMetrics(
        budget_allocated=100000.0,
        budget_spent=130000.0,
        budget_utilization_percentage=130.0,
        budget_variance=-30000.0,
        daily_burn_rate=2000.0,
        projected_completion_spend=200000.0,
        budget_score=15.0,
        budget_health=BudgetHealth.OVER_BUDGET,
        projection_confidence="LOW",
    )

    risk = ExecutionRiskEngine.calculate_risk(
        initiative=init,
        milestones=[m1, m2],
        dependencies=[],
        timeline_risk_metrics=tr_m,
        critical_path_metrics=cp_m,
        schedule_metrics=s_m,
        velocity_metrics=v_m,
        budget_metrics=b_m,
        previous_risk_score=50.0,
        as_of_date=now,
    )

    assert risk.risk_score >= 80.0
    assert risk.risk_severity == ExecutionRiskSeverity.CRITICAL
    assert risk.risk_trend == RiskTrend.DETERIORATING
    assert ExecutionRiskFactor.BLOCKED_MILESTONE in risk.risk_factors
    assert ExecutionRiskFactor.TIMELINE_DELAY in risk.risk_factors
    assert ExecutionRiskFactor.CRITICAL_PATH_EXPOSURE in risk.risk_factors
    assert ExecutionRiskFactor.BUDGET_OVERRUN in risk.risk_factors
    assert risk.blocked_milestone_count == 2

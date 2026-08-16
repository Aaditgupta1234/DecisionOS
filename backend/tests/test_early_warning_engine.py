"""Unit tests for Early Warning Engine (Phase 12.4)."""

from datetime import datetime, timezone
import uuid
import pytest

from app.execution.constants import (
    BudgetHealth,
    EarlyWarningType,
    ExecutionHealthGrade,
    ExecutionRiskSeverity,
    MilestoneCriticality,
    MilestoneStatus,
    TimelineRiskLevel,
    WarningSeverity,
)
from app.execution.models.initiative import StrategicInitiative
from app.execution.models.milestone import InitiativeMilestone
from app.execution.schemas.health import ExecutionHealthMetrics, ExecutionRiskMetrics
from app.execution.schemas.progress import (
    BudgetIntelligenceMetrics,
    ExecutionVelocityMetrics,
)
from app.execution.schemas.timeline import (
    CriticalPathMetrics,
    TimelineRiskMetrics,
)
from app.execution.services.early_warning_engine import EarlyWarningEngine


def test_early_warning_zero_warnings_when_healthy():
    """Verifies that no early warnings are triggered on a healthy initiative."""
    now = datetime(2026, 8, 16, 12, 0, 0, tzinfo=timezone.utc)
    init = StrategicInitiative(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        title="Healthy Project",
        objective="Maintain operational perfection.",
    )

    h_m = ExecutionHealthMetrics(health_score=85.0, health_grade=ExecutionHealthGrade.GOOD)
    r_m = ExecutionRiskMetrics(risk_score=15.0, risk_severity=ExecutionRiskSeverity.LOW)
    tr_m = TimelineRiskMetrics(timeline_risk_score=10.0, timeline_risk_level=TimelineRiskLevel.LOW)
    cp_m = CriticalPathMetrics(critical_path_stability_score=95.0, projected_delay_days=0)
    b_m = BudgetIntelligenceMetrics(
        budget_allocated=100000.0,
        budget_spent=60000.0,
        budget_utilization_percentage=60.0,
        budget_variance=40000.0,
        daily_burn_rate=500.0,
        projected_completion_spend=80000.0,
        budget_score=90.0,
        budget_health=BudgetHealth.HEALTHY,
        projection_confidence="HIGH",
    )
    v_m = ExecutionVelocityMetrics(
        velocity_score=85.0,
        milestones_completed_per_week=1.5,
        milestones_completed_per_month=6.0,
        average_completion_time_days=5.0,
        velocity_grade="EXCELLENT",
        data_sufficient=True,
    )

    warnings = EarlyWarningEngine.evaluate_warnings(
        initiative=init,
        milestones=[],
        health_metrics=h_m,
        risk_metrics=r_m,
        timeline_risk_metrics=tr_m,
        critical_path_metrics=cp_m,
        budget_metrics=b_m,
        velocity_metrics=v_m,
        as_of_date=now,
    )

    assert len(warnings) == 0


def test_early_warning_multiple_triggers_and_severities():
    """Verifies that multiple failure criteria trigger distinct typed warnings with correct severity."""
    now = datetime(2026, 8, 16, 12, 0, 0, tzinfo=timezone.utc)
    org_id = uuid.uuid4()
    init = StrategicInitiative(
        id=uuid.uuid4(),
        organization_id=org_id,
        title="Distressed Project",
        objective="Rescue distressed migration.",
    )

    blocked_ms = InitiativeMilestone(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init.id,
        title="Security Audit",
        criticality=MilestoneCriticality.CRITICAL,
        status=MilestoneStatus.BLOCKED,
    )

    h_m = ExecutionHealthMetrics(health_score=35.0, health_grade=ExecutionHealthGrade.CRITICAL)
    r_m = ExecutionRiskMetrics(risk_score=85.0, risk_severity=ExecutionRiskSeverity.CRITICAL)
    tr_m = TimelineRiskMetrics(timeline_risk_score=80.0, timeline_risk_level=TimelineRiskLevel.CRITICAL)
    cp_m = CriticalPathMetrics(critical_path_stability_score=40.0, projected_delay_days=20)
    b_m = BudgetIntelligenceMetrics(
        budget_allocated=100000.0,
        budget_spent=125000.0,
        budget_utilization_percentage=125.0,
        budget_variance=-25000.0,
        daily_burn_rate=2500.0,
        projected_completion_spend=180000.0,
        budget_score=20.0,
        budget_health=BudgetHealth.OVER_BUDGET,
        projection_confidence="LOW",
    )
    v_m = ExecutionVelocityMetrics(
        velocity_score=20.0,
        milestones_completed_per_week=0.2,
        milestones_completed_per_month=0.8,
        average_completion_time_days=25.0,
        velocity_grade="CRITICAL",
        data_sufficient=True,
    )

    warnings = EarlyWarningEngine.evaluate_warnings(
        initiative=init,
        milestones=[blocked_ms],
        health_metrics=h_m,
        risk_metrics=r_m,
        timeline_risk_metrics=tr_m,
        critical_path_metrics=cp_m,
        budget_metrics=b_m,
        velocity_metrics=v_m,
        as_of_date=now,
    )

    warning_types = [w.warning_type for w in warnings]
    assert EarlyWarningType.CRITICAL_BLOCKER in warning_types
    assert EarlyWarningType.HEALTH_DETERIORATION in warning_types
    assert EarlyWarningType.TIMELINE_RISK in warning_types
    assert EarlyWarningType.CRITICAL_PATH_INSTABILITY in warning_types
    assert EarlyWarningType.BUDGET_RISK in warning_types
    assert EarlyWarningType.VELOCITY_COLLAPSE in warning_types

    blocker_w = next(w for w in warnings if w.warning_type == EarlyWarningType.CRITICAL_BLOCKER)
    assert blocker_w.severity == WarningSeverity.CRITICAL

    health_w = next(w for w in warnings if w.warning_type == EarlyWarningType.HEALTH_DETERIORATION)
    assert health_w.severity == WarningSeverity.HIGH

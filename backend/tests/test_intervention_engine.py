"""Unit tests for Intervention Prioritization Engine (Phase 12.4)."""

from datetime import datetime, timezone
import uuid
import pytest

from app.execution.constants import (
    ExecutionHealthGrade,
    ExecutionRiskSeverity,
    InitiativePriority,
    InterventionCategory,
    InterventionPriority,
    MilestoneCriticality,
    MilestoneStatus,
    TimelineRiskLevel,
)
from app.execution.models.initiative import StrategicInitiative
from app.execution.models.milestone import InitiativeMilestone
from app.execution.schemas.health import (
    ExecutionHealthMetrics,
    ExecutionRiskMetrics,
    InterventionRecommendation,
)
from app.execution.schemas.progress import BudgetIntelligenceMetrics
from app.execution.schemas.timeline import CriticalPathMetrics, TimelineRiskMetrics
from app.execution.services.intervention_engine import InterventionPrioritizationEngine


def test_intervention_engine_p1_blocker_triage():
    """Verifies that high-risk blocked initiative generates P1 tier with BLOCKER_RESOLUTION category."""
    now = datetime(2026, 8, 16, 12, 0, 0, tzinfo=timezone.utc)
    org_id = uuid.uuid4()
    init = StrategicInitiative(
        id=uuid.uuid4(),
        organization_id=org_id,
        title="Payment Processor V2",
        priority=InitiativePriority.P1,
        budget_allocated=200000.0,
        budget_spent=150000.0,
        objective="Deploy Payment Processor V2.",
    )

    blocked_ms1 = InitiativeMilestone(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init.id,
        title="PCI-DSS Compliance Certification",
        criticality=MilestoneCriticality.CRITICAL,
        status=MilestoneStatus.BLOCKED,
    )
    blocked_ms2 = InitiativeMilestone(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init.id,
        title="Hardware Security Module Provisioning",
        criticality=MilestoneCriticality.CRITICAL,
        status=MilestoneStatus.BLOCKED,
    )
    blocked_ms3 = InitiativeMilestone(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init.id,
        title="Master Key Exchange",
        criticality=MilestoneCriticality.CRITICAL,
        status=MilestoneStatus.BLOCKED,
    )

    h_m = ExecutionHealthMetrics(health_score=15.0, health_grade=ExecutionHealthGrade.CRITICAL)
    r_m = ExecutionRiskMetrics(risk_score=95.0, risk_severity=ExecutionRiskSeverity.CRITICAL)
    tr_m = TimelineRiskMetrics(timeline_risk_score=90.0, timeline_risk_level=TimelineRiskLevel.CRITICAL)
    cp_m = CriticalPathMetrics(projected_delay_days=14, critical_path_stability_score=40.0)
    b_m = BudgetIntelligenceMetrics(
        budget_allocated=200000.0,
        budget_spent=150000.0,
        budget_utilization_percentage=75.0,
        budget_variance=50000.0,
        daily_burn_rate=1500.0,
        projected_completion_spend=210000.0,
        budget_score=60.0,
        budget_health="WATCH",
        projection_confidence="HIGH",
    )

    inv = InterventionPrioritizationEngine.evaluate_intervention(
        initiative=init,
        milestones=[blocked_ms1, blocked_ms2, blocked_ms3],
        health_metrics=h_m,
        risk_metrics=r_m,
        timeline_risk_metrics=tr_m,
        critical_path_metrics=cp_m,
        budget_metrics=b_m,
        as_of_date=now,
    )

    assert inv.priority_level == InterventionPriority.P1
    assert inv.priority_score >= 90.0
    assert inv.estimated_business_impact_score >= 80.0
    assert inv.category == InterventionCategory.BLOCKER_RESOLUTION
    assert len(inv.recommended_actions) > 0
    assert "blocker triage" in inv.recommended_actions[0].lower()


def test_intervention_queue_deterministic_ranking():
    """Verifies that rank_interventions orders by priority_score, business impact, and risk score."""
    rec_low = InterventionRecommendation(
        initiative_id=uuid.uuid4(),
        initiative_title="Routine Task",
        priority_level=InterventionPriority.P4,
        priority_score=35.0,
        estimated_business_impact_score=30.0,
        category=InterventionCategory.RESOURCE_REALLOCATION,
        risk_severity=ExecutionRiskSeverity.LOW,
        health_score=85.0,
        risk_score=20.0,
    )
    rec_high = InterventionRecommendation(
        initiative_id=uuid.uuid4(),
        initiative_title="Critical Outage Fix",
        priority_level=InterventionPriority.P1,
        priority_score=95.0,
        estimated_business_impact_score=92.0,
        category=InterventionCategory.BLOCKER_RESOLUTION,
        risk_severity=ExecutionRiskSeverity.CRITICAL,
        health_score=25.0,
        risk_score=95.0,
    )
    rec_med = InterventionRecommendation(
        initiative_id=uuid.uuid4(),
        initiative_title="Schedule Recovery",
        priority_level=InterventionPriority.P2,
        priority_score=80.0,
        estimated_business_impact_score=75.0,
        category=InterventionCategory.TIMELINE_RECOVERY,
        risk_severity=ExecutionRiskSeverity.HIGH,
        health_score=55.0,
        risk_score=75.0,
    )

    ranked = InterventionPrioritizationEngine.rank_interventions([rec_low, rec_high, rec_med])

    assert ranked[0].initiative_title == "Critical Outage Fix"
    assert ranked[1].initiative_title == "Schedule Recovery"
    assert ranked[2].initiative_title == "Routine Task"

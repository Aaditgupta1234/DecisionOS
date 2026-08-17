"""Unit tests for Phase 12.9 ExecutiveInterventionEngine."""

import uuid
from datetime import datetime, timezone
from app.execution.constants import (
    ExecutiveActionPriority,
    ExecutiveImpactTier,
    InterventionRecommendation,
    PortfolioExecutionPressureGrade,
    StrategicConfidenceLevel,
)
from app.execution.schemas.decision_support import ExecutiveDecisionItem
from app.execution.services.executive_intervention_engine import ExecutiveInterventionEngine


def test_executive_intervention_engine_segmentation_and_pressure():
    """Tests 5-way intervention categorization and pressure rating calculations."""
    engine = ExecutiveInterventionEngine()
    org_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    item_escalate = ExecutiveDecisionItem(
        initiative_id=uuid.uuid4(),
        initiative_name="At-Risk Initiative",
        decision_priority=ExecutiveActionPriority.CRITICAL,
        impact_tier=ExecutiveImpactTier.HIGH,
        recommended_action=InterventionRecommendation.ESCALATE,
        decision_score=85.0,
        decision_confidence_score=90.0,
        decision_confidence_level=StrategicConfidenceLevel.HIGH,
        created_at=now,
    )

    item_stabilize = ExecutiveDecisionItem(
        initiative_id=uuid.uuid4(),
        initiative_name="Unstable Initiative",
        decision_priority=ExecutiveActionPriority.MEDIUM,
        impact_tier=ExecutiveImpactTier.MEDIUM,
        recommended_action=InterventionRecommendation.STABILIZE,
        decision_score=60.0,
        decision_confidence_score=80.0,
        decision_confidence_level=StrategicConfidenceLevel.MEDIUM,
        created_at=now,
    )

    item_accelerate = ExecutiveDecisionItem(
        initiative_id=uuid.uuid4(),
        initiative_name="High Momentum Project",
        decision_priority=ExecutiveActionPriority.HIGH,
        impact_tier=ExecutiveImpactTier.TRANSFORMATIONAL,
        recommended_action=InterventionRecommendation.ACCELERATE,
        decision_score=88.0,
        decision_confidence_score=95.0,
        decision_confidence_level=StrategicConfidenceLevel.HIGH,
        created_at=now,
    )

    item_monitor = ExecutiveDecisionItem(
        initiative_id=uuid.uuid4(),
        initiative_name="Steady State Project",
        decision_priority=ExecutiveActionPriority.LOW,
        impact_tier=ExecutiveImpactTier.LOW,
        recommended_action=InterventionRecommendation.MONITOR,
        decision_score=40.0,
        decision_confidence_score=75.0,
        decision_confidence_level=StrategicConfidenceLevel.MEDIUM,
        created_at=now,
    )

    queue = engine.build_intervention_queue(
        organization_id=org_id,
        decision_items=[item_escalate, item_stabilize, item_accelerate, item_monitor],
    )

    assert queue.total_interventions == 3  # escalate + stabilize + accelerate
    assert queue.critical_count == 1
    assert queue.stabilize_count == 1
    assert queue.accelerate_count == 1
    assert queue.monitor_count == 1
    assert len(queue.critical_escalations) == 1
    assert len(queue.stabilization_candidates) == 1
    assert len(queue.acceleration_candidates) == 1
    assert len(queue.monitored_initiatives) == 1
    assert queue.intervention_pressure_score > 0.0
    assert queue.intervention_pressure_grade in [
        PortfolioExecutionPressureGrade.LOW,
        PortfolioExecutionPressureGrade.MODERATE,
        PortfolioExecutionPressureGrade.HIGH,
        PortfolioExecutionPressureGrade.CRITICAL,
    ]

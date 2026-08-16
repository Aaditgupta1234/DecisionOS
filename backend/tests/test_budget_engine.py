"""
Comprehensive test suite for Phase 12.2.4: Budget Intelligence Engine.
Tests financial utilization %, daily burn rate, projected final spend,
projection confidence ratings, budget scores (0-100), and BudgetHealth classifications.
"""

import uuid
import pytest

from app.execution.constants import (
    BUDGET_ENGINE_VERSION,
    BudgetHealth,
    OutcomeMeasurementConfidence,
)
from app.execution.models.initiative import StrategicInitiative
from app.execution.services.budget_engine import BudgetIntelligenceEngine


def test_budget_engine_healthy_execution():
    """Validates healthy budget execution with high projection confidence and spend within bounds."""
    org_id = uuid.uuid4()
    init = StrategicInitiative(
        id=uuid.uuid4(),
        organization_id=org_id,
        title="Frugal Architecture Sprint",
        description="Low cost execution.",
        objective="Stay well under allocated cap.",
        budget_allocated=100000.0,
        budget_spent=45000.0,
    )

    # 60% progress achieved over 35 days with 45k spent (Projected = 45k / 0.60 = 75k)
    metrics = BudgetIntelligenceEngine.calculate_budget(init, actual_progress=60.0, days_elapsed=35)

    assert metrics.budget_allocated == 100000.0
    assert metrics.budget_spent == 45000.0
    assert metrics.remaining_budget == 55000.0
    assert metrics.budget_variance == 55000.0
    assert metrics.budget_utilization_percentage == 45.0
    assert metrics.budget_burn_rate == round(45000.0 / 35, 2)
    assert metrics.projected_budget_completion == 75000.0
    assert metrics.projection_confidence == OutcomeMeasurementConfidence.HIGH
    assert metrics.budget_score >= 90.0
    assert metrics.budget_health == BudgetHealth.HEALTHY
    assert metrics.engine_version == BUDGET_ENGINE_VERSION


def test_budget_engine_overrun_and_low_confidence():
    """Validates budget overrun penalties and low projection confidence for early stage initiatives."""
    org_id = uuid.uuid4()
    init = StrategicInitiative(
        id=uuid.uuid4(),
        organization_id=org_id,
        title="Over Budget Initiative",
        description="High expenditures early on.",
        objective="Deliver regardless of cost.",
        budget_allocated=50000.0,
        budget_spent=60000.0,
    )

    # 10% progress over 5 days with 60k spent (utilization = 120%, projected = 600k)
    metrics = BudgetIntelligenceEngine.calculate_budget(init, actual_progress=10.0, days_elapsed=5)

    assert metrics.budget_allocated == 50000.0
    assert metrics.budget_spent == 60000.0
    assert metrics.remaining_budget == -10000.0
    assert metrics.budget_variance == -10000.0
    assert metrics.budget_utilization_percentage == 120.0
    assert metrics.projected_budget_completion == 600000.0
    assert metrics.projection_confidence == OutcomeMeasurementConfidence.LOW
    assert metrics.budget_score < 40.0
    assert metrics.budget_health == BudgetHealth.OVER_BUDGET
    assert metrics.engine_version == BUDGET_ENGINE_VERSION

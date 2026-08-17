"""Unit tests for Phase 12.7 Value Diagnostics Engine."""

import uuid
import pytest
from app.execution.services.value_diagnostics_engine import ValueDiagnosticsEngine


def test_value_diagnostics_empty_case():
    """Validates graceful handling of empty initiatives list."""
    res = ValueDiagnosticsEngine.diagnose_portfolio([])
    assert res["high_value_initiatives"] == []
    assert res["value_concentration"]["top_10_percent_value_share"] == 0.0
    assert len(res["data_quality_warnings"]) > 0


def test_value_diagnostics_cohort_classification():
    """Validates classification into 7 strategic cohorts."""
    id1, id2, id3, id4 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    initiatives = [
        {
            "id": id1,
            "title": "High Yield Core",
            "strategic_value_score": 88.0,
            "roi_score": 85.0,
            "health_score": 90.0,
            "risk_score": 10.0,
            "actual_cost": 100000.0,
        },
        {
            "id": id2,
            "title": "Underperforming Driver",
            "strategic_value_score": 45.0,
            "roi_score": 40.0,
            "health_score": 45.0,
            "risk_score": 75.0,
            "actual_cost": 500000.0,
            "outcome_achievement": 35.0,
        },
        {
            "id": id3,
            "title": "High Risk Low Value",
            "strategic_value_score": 30.0,
            "roi_score": 20.0,
            "health_score": 65.0,
            "risk_score": 70.0,
            "actual_cost": 300000.0,
        },
        {
            "id": id4,
            "title": "Governance Checkpoint Lag",
            "strategic_value_score": 60.0,
            "roi_score": 50.0,
            "health_score": 75.0,
            "risk_score": 20.0,
            "governance_maturity_score": 40.0,
            "actual_cost": 50000.0,
        },
    ]

    dependencies = [
        {"source_initiative_id": id1, "target_initiative_id": id2},
        {"source_initiative_id": id1, "target_initiative_id": id3},
        {"source_initiative_id": id1, "target_initiative_id": id4},
    ]

    res = ValueDiagnosticsEngine.diagnose_portfolio(initiatives=initiatives, dependencies=dependencies)

    assert len(res["high_value_initiatives"]) >= 1
    assert res["high_value_initiatives"][0]["initiative_id"] == id1

    assert len(res["high_roi_initiatives"]) >= 1
    assert res["high_roi_initiatives"][0]["initiative_id"] == id1

    assert len(res["underperforming_initiatives"]) >= 1
    assert res["underperforming_initiatives"][0]["initiative_id"] == id2

    assert len(res["high_risk_low_value_initiatives"]) >= 1
    assert res["high_risk_low_value_initiatives"][0]["initiative_id"] in (id2, id3)

    assert len(res["governance_bottlenecks"]) >= 1
    assert res["governance_bottlenecks"][0]["initiative_id"] == id4

    # Dependency Concentration
    assert res["dependency_concentration"]["max_dependent_initiatives"] == 3
    assert res["dependency_concentration"]["single_point_of_failure_count"] >= 1

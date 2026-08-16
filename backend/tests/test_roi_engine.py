"""Unit tests for Phase 12.6 ROIIntelligenceEngine."""

import pytest
from app.execution.constants import ROIClassification, ROITrend
from app.execution.services.roi_engine import ROIIntelligenceEngine


def test_exceptional_roi_calculation():
    """Test ROI >= 200% maps to EXCEPTIONAL with positive payback."""
    res = ROIIntelligenceEngine.calculate_roi(
        realized_value=300_000.0,
        investment_cost=100_000.0,
        benefit_confidence=90.0,
        outcome_confidence=85.0,
    )
    assert res["roi_percentage"] == 200.0
    assert res["payback_ratio"] == 3.0
    assert res["net_value_delivered"] == 200_000.0
    assert res["roi_classification"] == ROIClassification.EXCEPTIONAL
    assert res["roi_confidence_score"] > 80.0
    assert res["snapshot_metric_version"] == "1.0"


def test_negative_roi_and_trends():
    """Test negative ROI and trend detection."""
    res = ROIIntelligenceEngine.calculate_roi(
        realized_value=30_000.0,
        investment_cost=100_000.0,
        previous_roi=-50.0,
    )
    assert res["roi_percentage"] == -70.0
    assert res["payback_ratio"] == 0.3
    assert res["net_value_delivered"] == -70_000.0
    assert res["roi_classification"] == ROIClassification.NEGATIVE
    assert res["roi_trend"] == ROITrend.DECLINING

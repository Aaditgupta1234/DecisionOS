"""Unit tests for Phase 5.5 diagnostic severity, confidence calculations, and evidence builders."""

import pytest
from app.core.constants import FindingCategory, FindingSeverity, FindingSubtype
from app.diagnostics.evidence_builder import EvidenceBuilder
from app.diagnostics.metric_keys import MetricKeys
from app.diagnostics.severity import calculate_confidence, calculate_severity


def test_calculate_severity_tiers():
    """Test standard severity scaling across medium, high, critical, and low thresholds."""
    base_threshold = 0.15

    # 1. Below threshold -> LOW
    assert calculate_severity(0.05, base_threshold) == FindingSeverity.LOW
    assert calculate_severity(0.14, base_threshold) == FindingSeverity.LOW

    # 2. Base threshold -> MEDIUM (1.0x - 1.99x)
    assert calculate_severity(0.15, base_threshold) == FindingSeverity.MEDIUM
    assert calculate_severity(0.25, base_threshold) == FindingSeverity.MEDIUM

    # 3. High multiplier -> HIGH (>= 2.0x, so >= 0.30)
    assert calculate_severity(0.30, base_threshold) == FindingSeverity.HIGH
    assert calculate_severity(0.40, base_threshold) == FindingSeverity.HIGH

    # 4. Critical multiplier -> CRITICAL (>= 3.0x, so >= 0.45)
    assert calculate_severity(0.45, base_threshold) == FindingSeverity.CRITICAL
    assert calculate_severity(0.80, base_threshold) == FindingSeverity.CRITICAL


def test_calculate_severity_positive_opportunity():
    """Test that positive business opportunities evaluate as LOW severity."""
    # Even if observed deviation is massive, positive gains are LOW severity
    assert calculate_severity(0.50, 0.15, is_positive_opportunity=True) == FindingSeverity.LOW
    assert calculate_severity(1.50, 0.15, is_positive_opportunity=True) == FindingSeverity.LOW


def test_calculate_severity_edge_cases():
    """Test boundary and zero-value edge cases for severity calculation."""
    # Zero threshold
    assert calculate_severity(0.10, 0.0) == FindingSeverity.LOW
    # Negative deviation uses absolute value
    assert calculate_severity(-0.50, 0.15) == FindingSeverity.CRITICAL
    # Zero deviation
    assert calculate_severity(0.0, 0.15) == FindingSeverity.LOW


def test_calculate_confidence_scaling():
    """Test statistical confidence score scaling with sample sizes and variance."""
    # Zero or negative sample size -> 0.50 baseline
    assert calculate_confidence(0) == 0.50
    assert calculate_confidence(-5) == 0.50

    # Small sample size (e.g. 5)
    score_small = calculate_confidence(5, min_samples=5, target_samples=50)
    assert 0.60 <= score_small <= 0.70

    # Halfway sample size (e.g. 25)
    score_mid = calculate_confidence(25, min_samples=5, target_samples=50)
    assert 0.75 <= score_mid <= 0.85

    # Target sample size (e.g. 50+) -> 1.00
    assert calculate_confidence(50, min_samples=5, target_samples=50) == 1.00
    assert calculate_confidence(100, min_samples=5, target_samples=50) == 1.00

    # High variance penalty
    score_high_var = calculate_confidence(50, variance=3.5, min_samples=5, target_samples=50)
    assert score_high_var < 1.00
    assert score_high_var >= 0.80


def test_evidence_builder_common_schema():
    """Test that EvidenceBuilder produces the required common schema."""
    evidence = EvidenceBuilder.build_evidence(
        category=FindingCategory.REVENUE.value,
        subtype=FindingSubtype.DECLINE.value,
        metric_name=MetricKeys.TOTAL_REVENUE,
        observed=15.5,
        threshold=10.0,
        confidence=0.92,
        sample_size=12,
        recommendation="Audit sales funnel.",
        context={"previous_revenue": 50000.0, "current_revenue": 42250.0},
    )

    expected_keys = {
        "category",
        "subtype",
        "metric_name",
        "observed",
        "threshold",
        "confidence",
        "sample_size",
        "recommendation",
        "context",
    }
    assert set(evidence.keys()) == expected_keys
    assert evidence["category"] == "REVENUE"
    assert evidence["subtype"] == "DECLINE"
    assert evidence["metric_name"] == "total_revenue"
    assert evidence["observed"] == 15.5
    assert evidence["threshold"] == 10.0
    assert evidence["confidence"] == 0.92
    assert evidence["sample_size"] == 12
    assert evidence["recommendation"] == "Audit sales funnel."
    assert evidence["context"]["previous_revenue"] == 50000.0


def test_evidence_builder_specialized_helpers():
    """Test time-series and distribution specialized evidence builder helpers."""
    # 1. Time-Series helper
    ts_ev = EvidenceBuilder.build_time_series_evidence(
        category=FindingCategory.REVENUE.value,
        subtype=FindingSubtype.VOLATILITY.value,
        metric_name=MetricKeys.TOTAL_REVENUE,
        current_value=12000.0,
        previous_value=8000.0,
        change_percent=50.0,
        threshold=30.0,
        confidence=0.88,
        period_count=6,
        trend="volatile",
        recommendation="Hedge cash flows.",
        volatility=0.45,
    )
    assert ts_ev["context"]["change_percent"] == 50.0
    assert ts_ev["context"]["volatility_cv"] == 0.45
    assert ts_ev["observed"] == 50.0

    # 2. Distribution helper
    dist_ev = EvidenceBuilder.build_distribution_evidence(
        category=FindingCategory.PRODUCT.value,
        subtype=FindingSubtype.PRODUCT_CONCENTRATION_RISK.value,
        dimension_name=MetricKeys.PRODUCT_CATEGORY,
        top_entity="Electronics",
        concentration_ratio=65.0,
        threshold=50.0,
        confidence=0.95,
        total_entities=5,
        recommendation="Expand product line.",
    )
    assert dist_ev["context"]["top_entity"] == "Electronics"
    assert dist_ev["context"]["concentration_ratio"] == 65.0
    assert dist_ev["context"]["total_entities"] == 5

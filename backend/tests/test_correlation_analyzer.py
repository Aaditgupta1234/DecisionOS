"""Unit tests for CorrelationAnalyzer and strict separation of correlation from causation."""

import uuid
import pytest

from app.core.constants import FindingSeverity, FindingSubtype, FindingType, RelationshipType
from app.models.diagnostic_finding import DiagnosticFinding
from app.root_cause.correlation_analyzer import CorrelationAnalyzer, CorrelationResult
from app.root_cause.rule_model import RootCauseRule


def test_compute_pearson_correlation():
    """Verifies Pearson r calculation on standard linear and inverse series."""
    # Perfectly aligned series (r = +1.0)
    x = [10.0, 20.0, 30.0, 40.0, 50.0]
    y = [100.0, 200.0, 300.0, 400.0, 500.0]
    r_pos = CorrelationAnalyzer.compute_pearson_correlation(x, y)
    assert r_pos is not None
    assert round(r_pos, 2) == 1.00

    # Inverse series (r = -1.0)
    z = [500.0, 400.0, 300.0, 200.0, 100.0]
    r_neg = CorrelationAnalyzer.compute_pearson_correlation(x, z)
    assert r_neg is not None
    assert round(r_neg, 2) == -1.00

    # Less than 3 points returns None
    assert CorrelationAnalyzer.compute_pearson_correlation([1.0, 2.0], [3.0, 4.0]) is None


def test_correlation_analysis_with_rule_corroboration():
    """Verifies that an inverse correlation corroborates a NEGATIVE-expected rule."""
    rule = RootCauseRule(
        cause_subtype=FindingSubtype.CHURN_INCREASE,
        effect_subtype=FindingSubtype.DECLINE,
        relationship_type=RelationshipType.CAUSES,
        relationship_strength=0.90,
        description="Churn spike causes revenue decline.",
        expected_correlation="NEGATIVE",
    )

    # Churn goes up: [10, 15, 20, 25, 30]
    # Revenue goes down: [500, 420, 350, 290, 210]
    cause_f = DiagnosticFinding(
        id=uuid.uuid4(),
        dataset_id=uuid.uuid4(),
        finding_type=FindingType.CUSTOMER_CONCENTRATION,
        severity=FindingSeverity.HIGH,
        title="High Churn",
        description="...",
        business_impact="...",
        confidence_score=0.90,
        supporting_data={
            "category": "CUSTOMER",
            "subtype": "CHURN_INCREASE",
            "context": {"time_series": [10.0, 15.0, 20.0, 25.0, 30.0]},
        },
    )
    effect_f = DiagnosticFinding(
        id=uuid.uuid4(),
        dataset_id=uuid.uuid4(),
        finding_type=FindingType.REVENUE_DROP,
        severity=FindingSeverity.HIGH,
        title="Revenue Decline",
        description="...",
        business_impact="...",
        confidence_score=0.90,
        supporting_data={
            "category": "REVENUE",
            "subtype": "DECLINE",
            "context": {"time_series": [500.0, 420.0, 350.0, 290.0, 210.0]},
        },
    )

    result = CorrelationAnalyzer.analyze_finding_pair(cause_f, effect_f, rule)
    assert result.coefficient is not None
    assert result.coefficient < -0.90
    assert result.correlation_direction == "NEGATIVE"
    assert result.correlation_strength == "STRONG"
    assert result.supports_rule is True
    assert result.sample_size == 5


def test_correlation_contradicting_rule():
    """Verifies that an unexpected positive correlation sets supports_rule=False."""
    rule = RootCauseRule(
        cause_subtype=FindingSubtype.COST_SPIKE,
        effect_subtype=FindingSubtype.MARGIN_COMPRESSION,
        relationship_type=RelationshipType.CAUSES,
        relationship_strength=0.95,
        description="Cost spike compresses margin.",
        expected_correlation="NEGATIVE",  # Cost up -> Margin down
    )

    # Both going up simultaneously (contradiction)
    cause_f = DiagnosticFinding(
        id=uuid.uuid4(),
        dataset_id=uuid.uuid4(),
        finding_type=FindingType.REVENUE_DROP,
        severity=FindingSeverity.HIGH,
        title="Cost Spike",
        description="...",
        business_impact="...",
        confidence_score=0.90,
        supporting_data={
            "category": "OPERATIONAL",
            "subtype": "COST_SPIKE",
            "context": {"time_series": [10.0, 20.0, 30.0, 40.0, 50.0]},
        },
    )
    effect_f = DiagnosticFinding(
        id=uuid.uuid4(),
        dataset_id=uuid.uuid4(),
        finding_type=FindingType.REVENUE_DROP,
        severity=FindingSeverity.HIGH,
        title="Margin Up",
        description="...",
        business_impact="...",
        confidence_score=0.90,
        supporting_data={
            "category": "OPERATIONAL",
            "subtype": "MARGIN_COMPRESSION",
            "context": {"time_series": [10.0, 20.0, 30.0, 40.0, 50.0]},
        },
    )

    result = CorrelationAnalyzer.analyze_finding_pair(cause_f, effect_f, rule)
    assert result.coefficient == 1.00
    assert result.correlation_direction == "POSITIVE"
    assert result.supports_rule is False


def test_correlation_missing_data_neutral_fallback():
    """Verifies that findings lacking time-series data produce a neutral fallback."""
    cause_f = DiagnosticFinding(
        id=uuid.uuid4(),
        dataset_id=uuid.uuid4(),
        finding_type=FindingType.CUSTOMER_CONCENTRATION,
        severity=FindingSeverity.MEDIUM,
        title="Churn",
        description="...",
        business_impact="...",
        confidence_score=0.80,
        supporting_data={"category": "CUSTOMER", "subtype": "CHURN_INCREASE"},
    )
    effect_f = DiagnosticFinding(
        id=uuid.uuid4(),
        dataset_id=uuid.uuid4(),
        finding_type=FindingType.REVENUE_DROP,
        severity=FindingSeverity.MEDIUM,
        title="Decline",
        description="...",
        business_impact="...",
        confidence_score=0.80,
        supporting_data={"category": "REVENUE", "subtype": "DECLINE"},
    )

    result = CorrelationAnalyzer.analyze_finding_pair(cause_f, effect_f, rule=None)
    assert result.coefficient is None
    assert result.correlation_direction == "NEUTRAL"
    assert result.correlation_strength == "NONE"
    assert result.supports_rule is None

"""Unit tests for RootCauseExplanationBuilder."""

import uuid
import pytest

from app.core.constants import FindingSeverity, FindingSubtype, FindingType, RelationshipType
from app.models.diagnostic_finding import DiagnosticFinding
from app.root_cause.correlation_analyzer import CorrelationResult
from app.root_cause.explanation_builder import RootCauseExplanationBuilder
from app.root_cause.rule_model import RootCauseRule


def test_build_explanation_with_strong_correlation():
    """Verifies detailed explanation narrative synthesis with statistical corroboration."""
    rule = RootCauseRule(
        cause_subtype=FindingSubtype.CHURN_INCREASE,
        effect_subtype=FindingSubtype.DECLINE,
        relationship_type=RelationshipType.CAUSES,
        relationship_strength=0.90,
        description="Customer churn spike directly decreases recurring and repeat revenue streams.",
        expected_correlation="NEGATIVE",
    )

    cause_f = DiagnosticFinding(
        id=uuid.uuid4(),
        dataset_id=uuid.uuid4(),
        finding_type=FindingType.CUSTOMER_CONCENTRATION,
        severity=FindingSeverity.HIGH,
        title="High Customer Churn Rate (22.0%)",
        description="...",
        business_impact="...",
        confidence_score=0.95,
        supporting_data={"category": "CUSTOMER", "subtype": "CHURN_INCREASE"},
    )
    effect_f = DiagnosticFinding(
        id=uuid.uuid4(),
        dataset_id=uuid.uuid4(),
        finding_type=FindingType.REVENUE_DROP,
        severity=FindingSeverity.CRITICAL,
        title="Significant Revenue Decline (-24.5%)",
        description="...",
        business_impact="...",
        confidence_score=0.90,
        supporting_data={"category": "REVENUE", "subtype": "DECLINE"},
    )

    corr = CorrelationResult(
        coefficient=-0.88,
        correlation_direction="NEGATIVE",
        correlation_strength="STRONG",
        supports_rule=True,
        sample_size=6,
    )

    explanation = RootCauseExplanationBuilder.build_explanation(
        cause_finding=cause_f,
        effect_finding=effect_f,
        rule=rule,
        correlation_result=corr,
    )

    assert "Significant Revenue Decline (-24.5%)" in explanation
    assert "CRITICAL severity" in explanation
    assert "High Customer Churn Rate (22.0%)" in explanation
    assert "HIGH severity" in explanation
    assert "Customer churn spike directly decreases recurring" in explanation
    assert "r = -0.88" in explanation
    assert "sample size = 6" in explanation


def test_build_explanation_without_correlation_data():
    """Verifies domain rule mechanism narrative when time-series data is missing."""
    rule = RootCauseRule(
        cause_subtype=FindingSubtype.COST_SPIKE,
        effect_subtype=FindingSubtype.MARGIN_COMPRESSION,
        relationship_type=RelationshipType.CAUSES,
        relationship_strength=0.95,
        description="Surges in operating costs compress gross margins.",
    )

    cause_f = DiagnosticFinding(
        id=uuid.uuid4(),
        dataset_id=uuid.uuid4(),
        finding_type=FindingType.REVENUE_DROP,
        severity=FindingSeverity.HIGH,
        title="Cost Surge",
        description="...",
        business_impact="...",
        confidence_score=0.90,
    )
    effect_f = DiagnosticFinding(
        id=uuid.uuid4(),
        dataset_id=uuid.uuid4(),
        finding_type=FindingType.REVENUE_DROP,
        severity=FindingSeverity.HIGH,
        title="Margin Compression",
        description="...",
        business_impact="...",
        confidence_score=0.90,
    )

    explanation = RootCauseExplanationBuilder.build_explanation(
        cause_finding=cause_f,
        effect_finding=effect_f,
        rule=rule,
        correlation_result=None,
    )

    assert "Domain rule validation confirms this very_strong causes linkage" in explanation

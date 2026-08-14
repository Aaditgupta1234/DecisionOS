"""Unit tests for the RootCauseAnalysis SQLAlchemy model."""

import uuid
import pytest
from sqlalchemy.exc import IntegrityError

from app.core.constants import FindingSeverity, FindingType, RelationshipStrength, RelationshipType
from app.models.dataset import Dataset
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.root_cause_analysis import RootCauseAnalysis


@pytest.fixture
def sample_dataset(db_session, admin_user):
    """Creates a basic Dataset fixture."""
    dataset = Dataset(
        name="RCA Test Dataset",
        original_filename="rca_test.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_rca.csv",
        file_path="/tmp/rca.csv",
        file_size=1024,
        uploaded_by=admin_user.id,
    )
    db_session.add(dataset)
    db_session.commit()
    db_session.refresh(dataset)
    return dataset


@pytest.fixture
def sample_findings(db_session, sample_dataset):
    """Creates a pair of DiagnosticFinding entities (cause and effect)."""
    cause_f = DiagnosticFinding(
        dataset_id=sample_dataset.id,
        finding_type=FindingType.CUSTOMER_CONCENTRATION,
        severity=FindingSeverity.HIGH,
        title="High Customer Churn Rate (22.0%)",
        description="Churn rate increased by 12.0 percentage points.",
        business_impact="Reduces recurring customer lifetime value.",
        confidence_score=0.95,
        supporting_data={"category": "CUSTOMER", "subtype": "CHURN_INCREASE", "observed": 22.0},
    )
    effect_f = DiagnosticFinding(
        dataset_id=sample_dataset.id,
        finding_type=FindingType.REVENUE_DROP,
        severity=FindingSeverity.HIGH,
        title="Significant Revenue Decline (-24.5%)",
        description="Revenue dropped by 24.5% period-over-period.",
        business_impact="Threatens operating margin profitability.",
        confidence_score=0.90,
        supporting_data={"category": "REVENUE", "subtype": "DECLINE", "observed": -24.5},
    )
    db_session.add_all([cause_f, effect_f])
    db_session.commit()
    db_session.refresh(cause_f)
    db_session.refresh(effect_f)
    return cause_f, effect_f


def test_create_root_cause_analysis_model(db_session, sample_dataset, sample_findings):
    """Verifies persisting a RootCauseAnalysis record with full relational wiring."""
    cause_f, effect_f = sample_findings

    rca = RootCauseAnalysis(
        dataset_id=sample_dataset.id,
        primary_finding_id=effect_f.id,
        root_cause_finding_id=cause_f.id,
        relationship_type=RelationshipType.CAUSES,
        relationship_strength=RelationshipStrength.VERY_STRONG,
        confidence_score=0.88,
        impact_score=0.92,
        explanation="Customer churn directly eroded top-line recurring revenue.",
        supporting_evidence={"correlation": -0.84, "rule": "CHURN_TO_REVENUE"},
    )
    db_session.add(rca)
    db_session.commit()
    db_session.refresh(rca)

    assert rca.id is not None
    assert rca.relationship_type == RelationshipType.CAUSES
    assert rca.relationship_strength == RelationshipStrength.VERY_STRONG
    assert rca.confidence_score == 0.88
    assert rca.impact_score == 0.92
    assert rca.primary_finding.id == effect_f.id
    assert rca.root_cause_finding.id == cause_f.id
    assert rca in sample_dataset.root_cause_analyses
    assert rca in effect_f.primary_causes
    assert rca in cause_f.root_effects


def test_root_cause_confidence_constraint(db_session, sample_dataset, sample_findings):
    """Verifies that confidence_score must satisfy 0.0 <= score <= 1.0."""
    cause_f, effect_f = sample_findings

    invalid_rca = RootCauseAnalysis(
        dataset_id=sample_dataset.id,
        primary_finding_id=effect_f.id,
        root_cause_finding_id=cause_f.id,
        relationship_type=RelationshipType.CAUSES,
        confidence_score=1.5,  # Invalid
        impact_score=0.8,
        explanation="Invalid confidence",
    )
    db_session.add(invalid_rca)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

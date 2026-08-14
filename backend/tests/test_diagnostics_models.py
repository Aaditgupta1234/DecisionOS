"""Unit tests for Phase 5.1 DiagnosticFinding model, enums, constraints, and dataset relationships."""

import uuid
from datetime import datetime, timezone
import pytest
from sqlalchemy.exc import IntegrityError

from app.core.constants import (
    DiagnosticGenerationStatus,
    FindingSeverity,
    FindingType,
    UserRole,
)
from app.models.dataset import Dataset
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.user import User


def test_diagnostic_finding_creation_and_relationship(db_session):
    """Test DiagnosticFinding creation, relationships, and JSONB supporting_data."""
    # 1. Create User
    user = User(
        email="diag_test@example.com",
        full_name="Diag Tester",
        hashed_password="hashedpassword",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()

    # 2. Create Dataset
    dataset = Dataset(
        name="Diagnostic Sales Q1",
        original_filename="sales_q1.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_sales_q1.csv",
        file_path="/tmp/sales_q1.csv",
        file_size=1024,
        uploaded_by=user.id,
        diagnostics_generation_status=DiagnosticGenerationStatus.GENERATED,
        diagnostics_generated_at=datetime.now(timezone.utc),
    )
    db_session.add(dataset)
    db_session.commit()

    # 3. Create DiagnosticFindings with different severities and timestamps
    finding1 = DiagnosticFinding(
        dataset_id=dataset.id,
        finding_type=FindingType.HIGH_CANCELLATION_RATE,
        severity=FindingSeverity.HIGH,
        title="High Order Cancellation Rate Detected",
        description="Cancellation rate of 24.3% exceeds the acceptable threshold of 10%.",
        business_impact="Estimated loss of $18,400 in unrealized revenue across apparel segment.",
        metric_key="completion_rate",
        confidence_score=0.95,
        supporting_data={
            "cancellation_rate": 24.3,
            "cancelled_orders": 243,
            "total_orders": 1000,
        },
        generated_at=datetime(2026, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
    )
    finding2 = DiagnosticFinding(
        dataset_id=dataset.id,
        finding_type=FindingType.REVENUE_CONCENTRATION,
        severity=FindingSeverity.CRITICAL,
        title="Excessive Customer Revenue Concentration",
        description="Top 3 customers generate 68% of total quarterly revenue.",
        business_impact="Critical revenue vulnerability if top client churns.",
        metric_key="revenue",
        confidence_score=1.0,
        supporting_data={
            "top_3_revenue_pct": 68.0,
            "top_customer_id": "CUST_991",
        },
        generated_at=datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
    )
    db_session.add_all([finding1, finding2])
    db_session.commit()

    # 4. Verify back_populates relationship & descending order by generated_at
    db_session.refresh(dataset)
    assert len(dataset.diagnostic_findings) == 2
    # finding2 has newer timestamp (12:00 > 10:00), so should be first
    assert dataset.diagnostic_findings[0].finding_type == FindingType.REVENUE_CONCENTRATION
    assert dataset.diagnostic_findings[0].severity == FindingSeverity.CRITICAL
    assert dataset.diagnostic_findings[1].finding_type == FindingType.HIGH_CANCELLATION_RATE

    # 5. Verify supporting_data JSON structure
    assert dataset.diagnostic_findings[0].supporting_data["top_3_revenue_pct"] == 68.0
    assert dataset.diagnostic_findings[1].supporting_data["cancellation_rate"] == 24.3

    # 6. Verify back-reference from finding to dataset
    assert finding1.dataset.name == "Diagnostic Sales Q1"


def test_diagnostic_findings_cascade_delete(db_session):
    """Test deleting a Dataset cascades and removes all associated DiagnosticFindings."""
    user = User(
        email="cascade_test@example.com",
        full_name="Cascade Tester",
        hashed_password="hashedpassword",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()

    dataset = Dataset(
        name="Cascade Test Dataset",
        original_filename="test.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_test.csv",
        file_path="/tmp/test.csv",
        file_size=512,
        uploaded_by=user.id,
    )
    db_session.add(dataset)
    db_session.commit()

    finding = DiagnosticFinding(
        dataset_id=dataset.id,
        finding_type=FindingType.DELIVERY_DELAY,
        severity=FindingSeverity.MEDIUM,
        title="Delivery Delays in Region East",
        description="Average delivery duration increased to 6.2 days.",
        business_impact="Potential CSAT rating drop.",
        metric_key="average_delivery_time",
        confidence_score=0.88,
    )
    db_session.add(finding)
    db_session.commit()

    # Delete dataset
    db_session.delete(dataset)
    db_session.commit()

    # Verify finding was cascade deleted
    remaining = db_session.query(DiagnosticFinding).filter(DiagnosticFinding.id == finding.id).first()
    assert remaining is None


def test_confidence_score_check_constraint(db_session):
    """Test confidence_score CheckConstraint rejects values outside [0.0, 1.0]."""
    user = User(
        email="constraint_test@example.com",
        full_name="Constraint Tester",
        hashed_password="hashedpassword",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()

    dataset = Dataset(
        name="Constraint Test Dataset",
        original_filename="test2.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_test2.csv",
        file_path="/tmp/test2.csv",
        file_size=512,
        uploaded_by=user.id,
    )
    db_session.add(dataset)
    db_session.commit()

    # Attempt to insert confidence_score = 1.5 (violates constraint)
    invalid_finding = DiagnosticFinding(
        dataset_id=dataset.id,
        finding_type=FindingType.DATA_QUALITY_RISK,
        severity=FindingSeverity.LOW,
        title="Invalid Confidence Score Finding",
        description="Testing DB constraint.",
        business_impact="None",
        confidence_score=1.5,  # Invalid
    )
    db_session.add(invalid_finding)

    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

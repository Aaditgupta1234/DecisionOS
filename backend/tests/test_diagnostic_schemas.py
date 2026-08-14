"""Unit tests for Phase 5.2 Diagnostic Intelligence Pydantic schemas, validation rules, and ORM serialization."""

import uuid
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from app.core.constants import (
    DiagnosticGenerationStatus,
    FindingSeverity,
    FindingType,
)
from app.models.diagnostic_finding import DiagnosticFinding
from app.schemas.diagnostic import (
    DiagnosticFindingListResponse,
    DiagnosticFindingResponse,
    DiagnosticGenerationResponse,
    DiagnosticGenerationStatusResponse,
    DiagnosticSeverityBreakdown,
    DiagnosticSummaryResponse,
)


def test_diagnostic_finding_response_from_orm():
    """Test DiagnosticFindingResponse ORM serialization from SQLAlchemy model instance."""
    now = datetime.now(timezone.utc)
    finding_id = uuid.uuid4()
    dataset_id = uuid.uuid4()

    finding_orm = DiagnosticFinding(
        id=finding_id,
        dataset_id=dataset_id,
        finding_type=FindingType.HIGH_CANCELLATION_RATE,
        severity=FindingSeverity.HIGH,
        title="High Order Cancellation Rate",
        description="Cancellation rate of 24.3% exceeds acceptable threshold of 10%.",
        business_impact="Estimated loss of $18,400 in unrealized revenue.",
        metric_key="completion_rate",
        confidence_score=0.95,
        supporting_data={"cancellation_rate": 24.3, "cancelled_orders": 243},
        generated_at=now,
    )

    schema = DiagnosticFindingResponse.model_validate(finding_orm)
    assert schema.id == finding_id
    assert schema.dataset_id == dataset_id
    assert schema.finding_type == FindingType.HIGH_CANCELLATION_RATE
    assert schema.severity == FindingSeverity.HIGH
    assert schema.title == "High Order Cancellation Rate"
    assert schema.confidence_score == 0.95
    assert schema.supporting_data["cancellation_rate"] == 24.3
    assert schema.generated_at == now


def test_confidence_score_boundaries():
    """Test boundary validation on confidence_score (valid: [0.0, 1.0], invalid: <0.0 or >1.0)."""
    base_kwargs = {
        "id": uuid.uuid4(),
        "dataset_id": uuid.uuid4(),
        "finding_type": FindingType.REVENUE_DROP,
        "severity": FindingSeverity.CRITICAL,
        "title": "Revenue Drop Finding",
        "description": "Valid description.",
        "business_impact": "Valid impact.",
        "generated_at": datetime.now(timezone.utc),
    }

    # Valid boundaries: 0.0, 1.0, 0.5
    valid_0 = DiagnosticFindingResponse(**base_kwargs, confidence_score=0.0)
    assert valid_0.confidence_score == 0.0

    valid_1 = DiagnosticFindingResponse(**base_kwargs, confidence_score=1.0)
    assert valid_1.confidence_score == 1.0

    valid_half = DiagnosticFindingResponse(**base_kwargs, confidence_score=0.5)
    assert valid_half.confidence_score == 0.5

    # Invalid boundary: 1.01
    with pytest.raises(ValidationError) as exc_info_high:
        DiagnosticFindingResponse(**base_kwargs, confidence_score=1.01)
    assert "confidence_score" in str(exc_info_high.value)

    # Invalid boundary: -0.01
    with pytest.raises(ValidationError) as exc_info_low:
        DiagnosticFindingResponse(**base_kwargs, confidence_score=-0.01)
    assert "confidence_score" in str(exc_info_low.value)


def test_non_negative_counts_validation():
    """Test Field(ge=0) validation prevents negative counts in list, summary, and generation schemas."""
    dataset_id = uuid.uuid4()

    # 1. DiagnosticFindingListResponse
    with pytest.raises(ValidationError):
        DiagnosticFindingListResponse(total=-1)

    # 2. DiagnosticSeverityBreakdown
    with pytest.raises(ValidationError):
        DiagnosticSeverityBreakdown(severity=FindingSeverity.LOW, count=-5)

    # 3. DiagnosticSummaryResponse
    with pytest.raises(ValidationError):
        DiagnosticSummaryResponse(dataset_id=dataset_id, critical=-1)

    with pytest.raises(ValidationError):
        DiagnosticSummaryResponse(dataset_id=dataset_id, total_findings=-10)

    # 4. DiagnosticGenerationResponse
    with pytest.raises(ValidationError):
        DiagnosticGenerationResponse(
            message="Done",
            dataset_id=dataset_id,
            findings_generated=-1,
            generated_at=datetime.now(timezone.utc),
        )


def test_required_string_fields_validation():
    """Test non-empty strings and length boundaries for title, description, and business_impact."""
    base_kwargs = {
        "id": uuid.uuid4(),
        "dataset_id": uuid.uuid4(),
        "finding_type": FindingType.DELIVERY_DELAY,
        "severity": FindingSeverity.MEDIUM,
        "generated_at": datetime.now(timezone.utc),
    }

    # Empty title
    with pytest.raises(ValidationError):
        DiagnosticFindingResponse(**base_kwargs, title="", description="Desc", business_impact="Impact")

    # Title exceeding 255 chars
    with pytest.raises(ValidationError):
        DiagnosticFindingResponse(**base_kwargs, title="T" * 256, description="Desc", business_impact="Impact")

    # Empty description
    with pytest.raises(ValidationError):
        DiagnosticFindingResponse(**base_kwargs, title="Title", description="", business_impact="Impact")

    # Empty business_impact
    with pytest.raises(ValidationError):
        DiagnosticFindingResponse(**base_kwargs, title="Title", description="Desc", business_impact="")


def test_enum_json_serialization():
    """Test that Enums serialize cleanly to their string representations in JSON."""
    finding_id = uuid.uuid4()
    dataset_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    schema = DiagnosticFindingResponse(
        id=finding_id,
        dataset_id=dataset_id,
        finding_type=FindingType.CUSTOMER_CONCENTRATION,
        severity=FindingSeverity.HIGH,
        title="Customer Concentration",
        description="Top client generates majority revenue.",
        business_impact="Revenue vulnerability.",
        generated_at=now,
    )

    data_dict = schema.model_dump()
    assert data_dict["finding_type"] == "CUSTOMER_CONCENTRATION"
    assert data_dict["severity"] == "HIGH"

    json_str = schema.model_dump_json()
    assert '"finding_type":"CUSTOMER_CONCENTRATION"' in json_str
    assert '"severity":"HIGH"' in json_str


def test_default_empty_list_and_summary_schemas():
    """Test default values and composition for List and Summary schemas."""
    # 1. Empty List Response
    list_res = DiagnosticFindingListResponse()
    assert list_res.items == []
    assert list_res.total == 0

    # 2. Summary Response with severity breakdown
    dataset_id = uuid.uuid4()
    summary = DiagnosticSummaryResponse(
        dataset_id=dataset_id,
        critical=1,
        high=2,
        medium=3,
        low=0,
        total_findings=6,
        severity_breakdown=[
            DiagnosticSeverityBreakdown(severity=FindingSeverity.CRITICAL, count=1),
            DiagnosticSeverityBreakdown(severity=FindingSeverity.HIGH, count=2),
            DiagnosticSeverityBreakdown(severity=FindingSeverity.MEDIUM, count=3),
            DiagnosticSeverityBreakdown(severity=FindingSeverity.LOW, count=0),
        ],
    )
    assert summary.total_findings == 6
    assert len(summary.severity_breakdown) == 4
    assert summary.severity_breakdown[0].severity == FindingSeverity.CRITICAL


def test_generation_and_status_schemas():
    """Test instantiation and serialization of Generation and Status schemas."""
    dataset_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    # 1. Generation Response
    gen_res = DiagnosticGenerationResponse(
        message="Diagnostics successfully generated.",
        dataset_id=dataset_id,
        findings_generated=5,
        generated_at=now,
    )
    assert gen_res.findings_generated == 5
    assert gen_res.dataset_id == dataset_id

    # 2. Status Response
    status_res = DiagnosticGenerationStatusResponse(
        status=DiagnosticGenerationStatus.GENERATED,
        generated_at=now,
        error=None,
    )
    assert status_res.status == DiagnosticGenerationStatus.GENERATED
    assert status_res.error is None

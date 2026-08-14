"""Unit tests for IntelligenceService layer."""

import uuid
import pytest
from fastapi import HTTPException

from app.core.constants import (
    FindingSeverity,
    FindingType,
    RecommendationPriority,
    RecommendationStatus,
    RecommendationType,
    RelationshipStrength,
    RelationshipType,
)
from app.models.dataset import Dataset
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.recommendation import Recommendation
from app.models.root_cause_analysis import RootCauseAnalysis
from app.services.intelligence_service import IntelligenceService


@pytest.fixture
def service_dataset(db_session, admin_user):
    dataset = Dataset(
        name="Service Test Dataset",
        original_filename="service.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_service.csv",
        file_path="/tmp/service.csv",
        file_size=1024,
        uploaded_by=admin_user.id,
    )
    db_session.add(dataset)
    db_session.commit()
    db_session.refresh(dataset)

    f1 = DiagnosticFinding(
        dataset_id=dataset.id,
        finding_type=FindingType.REVENUE_DROP,
        severity=FindingSeverity.HIGH,
        title="Revenue Dip",
        description="...",
        business_impact="Reduces operating margins.",
        confidence_score=0.90,
    )
    db_session.add(f1)
    db_session.commit()
    db_session.refresh(f1)

    rec = Recommendation(
        dataset_id=dataset.id,
        finding_id=f1.id,
        recommendation_type=RecommendationType.REVENUE_GROWTH,
        priority=RecommendationPriority.HIGH,
        status=RecommendationStatus.PENDING,
        title="Revenue Recovery Campaign",
        description="...",
        why_recommended="...",
        confidence_score=0.85,
        estimated_impact_score=0.80,
        estimated_effort_score=0.40,
    )
    db_session.add(rec)
    db_session.commit()

    return dataset


@pytest.mark.anyio
async def test_intelligence_service_health_and_reports(db_session, service_dataset):
    """Verifies service layer health scoring, summary creation, and report compilation."""
    service = IntelligenceService(db_session)

    # 1. Health Score
    health_res = await service.get_health_score(service_dataset.id)
    assert health_res.dataset_id == service_dataset.id
    assert 70 <= health_res.score <= 100

    # 2. Executive Summary
    summary_res = await service.get_executive_summary(service_dataset.id)
    assert summary_res.dataset_id == service_dataset.id
    assert summary_res.primary_issue == "Revenue Dip"
    assert summary_res.top_recommendation == "Revenue Recovery Campaign"

    # 3. Full Intelligence Report
    report_res = await service.get_intelligence_report(service_dataset.id)
    assert report_res.dataset_id == service_dataset.id
    assert report_res.report_version == "1.0"
    assert report_res.artifact_counts["findings"] == 1
    assert report_res.artifact_counts["recommendations"] == 1


@pytest.mark.anyio
async def test_intelligence_service_404_not_found(db_session):
    """Verifies 404 raises for nonexistent dataset."""
    service = IntelligenceService(db_session)
    random_id = uuid.uuid4()

    with pytest.raises(HTTPException) as exc_info:
        await service.get_health_score(random_id)
    assert exc_info.value.status_code == 404

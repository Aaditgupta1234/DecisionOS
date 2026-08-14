"""Unit tests for AIInsightService layer."""

import uuid
import pytest
from fastapi import HTTPException

from app.ai_insights.providers.mock_provider import MockLLMProvider
from app.ai_insights.services.ai_insight_service import AIInsightService
from app.core.constants import (
    FindingSeverity,
    FindingType,
    RecommendationPriority,
    RecommendationStatus,
    RecommendationType,
)
from app.models.dataset import Dataset
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.recommendation import Recommendation


@pytest.fixture
def service_dataset(db_session, admin_user):
    dataset = Dataset(
        name="AI Service Test Dataset",
        original_filename="ai_service.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_service.csv",
        file_path="/tmp/ai_service.csv",
        file_size=1024,
        uploaded_by=admin_user.id,
    )
    db_session.add(dataset)
    db_session.commit()
    db_session.refresh(dataset)

    finding = DiagnosticFinding(
        dataset_id=dataset.id,
        finding_type=FindingType.REVENUE_DROP,
        severity=FindingSeverity.HIGH,
        title="Revenue Contraction (-18.0%)",
        description="Top-line dropped.",
        business_impact="Reduces cash flow.",
        confidence_score=0.90,
    )
    db_session.add(finding)
    db_session.commit()
    db_session.refresh(finding)

    rec = Recommendation(
        dataset_id=dataset.id,
        finding_id=finding.id,
        recommendation_type=RecommendationType.REVENUE_GROWTH,
        priority=RecommendationPriority.HIGH,
        status=RecommendationStatus.PENDING,
        title="Execute Top-Line Recovery",
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
async def test_ai_insight_service_caching_and_regeneration(db_session, service_dataset):
    """Verifies service caching, forced regeneration, and history tracking."""
    provider = MockLLMProvider()
    service = AIInsightService(db=db_session, provider=provider)

    # 1. First call: Generates and caches
    res1 = await service.get_insights(service_dataset.id)
    assert res1.dataset_id == service_dataset.id
    assert res1.insight_version == "1.0"
    assert len(res1.executive_narrative.headline) > 5

    # 2. Second call without force_regenerate: Returns cached instance
    res2 = await service.get_insights(service_dataset.id, force_regenerate=False)
    assert res2.id == res1.id

    # 3. Forced regeneration: Creates new historical revision
    res3 = await service.regenerate_insights(service_dataset.id)
    assert res3.id != res1.id

    # 4. List History
    history = await service.list_history(service_dataset.id)
    assert len(history) == 2
    assert history[0].id == res3.id
    assert history[1].id == res1.id


@pytest.mark.anyio
async def test_ai_insight_service_404_not_found(db_session):
    """Verifies 404 for invalid dataset."""
    service = AIInsightService(db=db_session, provider=MockLLMProvider())
    with pytest.raises(HTTPException) as exc_info:
        await service.get_insights(uuid.uuid4())
    assert exc_info.value.status_code == 404


@pytest.mark.anyio
async def test_ai_insight_service_provider_override(db_session, service_dataset):
    """Verifies custom model provider and name override handling."""
    service = AIInsightService(db=db_session)
    res = await service.get_insights(
        service_dataset.id,
        force_regenerate=True,
        provider_name="mock",
        model_name="custom-executive-model",
    )
    assert res.model_provider == "mock"
    assert res.model_name == "custom-executive-model"


@pytest.mark.anyio
async def test_ai_insight_service_history_pagination(db_session, service_dataset):
    """Verifies history list pagination limits."""
    service = AIInsightService(db=db_session, provider=MockLLMProvider())
    # Generate multiple revisions
    await service.regenerate_insights(service_dataset.id)
    await service.regenerate_insights(service_dataset.id)

    history_page1 = await service.list_history(service_dataset.id, limit=1, offset=0)
    assert len(history_page1) == 1

    history_all = await service.list_history(service_dataset.id, limit=10, offset=0)
    assert len(history_all) >= 2

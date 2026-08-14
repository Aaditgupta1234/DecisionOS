"""Unit tests for StrategyPlannerService business logic and orchestration."""

import uuid
import pytest
from fastapi import HTTPException

from app.ai_insights.providers.mock_provider import MockLLMProvider
from app.core.constants import (
    FindingSeverity,
    FindingType,
    RecommendationPriority,
    RecommendationStatus,
    RecommendationType,
    StrategyPlanStatus,
)
from app.models.dataset import Dataset
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.recommendation import Recommendation
from app.strategy_planner.services.strategy_planner_service import StrategyPlannerService


class FailingStrategyProvider(MockLLMProvider):
    """Mock provider that simulates an exception during generation."""
    async def generate_json(self, prompt, system_prompt=None, temperature=0.2):
        raise RuntimeError("OpenAI API unreachable")


class InvalidTraceabilityProvider(MockLLMProvider):
    """Mock provider that returns an action with an unknown recommendation ID."""
    async def generate_json(self, prompt, system_prompt=None, temperature=0.2):
        return {
            "title": "Strategy with Bad Traceability",
            "objective": "Objective",
            "executive_summary": "Summary",
            "strategic_priorities": [
                {
                    "title": "Priority 1",
                    "priority": "HIGH",
                    "source_recommendation_ids": ["rec-fake-uuid-000000000000"],
                    "rationale": "Rationale",
                }
            ],
            "action_items": [
                {
                    "title": "Bad Action",
                    "description": "Description",
                    "time_horizon": "IMMEDIATE",
                    "source_recommendation_id": "rec-fake-uuid-000000000000",
                }
            ],
            "milestones": [],
            "success_criteria": [],
            "source_recommendation_ids": ["rec-fake-uuid-000000000000"],
        }


@pytest.fixture
def strategy_dataset(db_session, admin_user):
    dataset = Dataset(
        name="Strategy Service Test Dataset",
        original_filename="strategy_service.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_strat_srv.csv",
        file_path="/tmp/strat_srv.csv",
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
        title="Revenue Drop (-15%)",
        description="Top-line contraction.",
        business_impact="ARR erosion.",
        confidence_score=0.91,
    )
    db_session.add(finding)
    db_session.commit()
    db_session.refresh(finding)

    rec = Recommendation(
        dataset_id=dataset.id,
        finding_id=finding.id,
        recommendation_type=RecommendationType.CUSTOMER_RETENTION,
        priority=RecommendationPriority.CRITICAL,
        status=RecommendationStatus.PENDING,
        title="Deploy VIP Customer Taskforce",
        description="Stabilize top churn cohorts.",
        why_recommended="Target high ARR accounts.",
        confidence_score=0.89,
        estimated_impact_score=0.86,
        estimated_effort_score=0.38,
    )
    db_session.add(rec)
    db_session.commit()

    return dataset


@pytest.mark.anyio
async def test_strategy_service_get_or_generate_plan(db_session, strategy_dataset):
    """Verifies auto-generating and caching the latest strategic plan."""
    service = StrategyPlannerService(db=db_session, provider=MockLLMProvider())

    plan = await service.get_or_generate_plan(dataset_id=strategy_dataset.id)
    assert plan.id is not None
    assert plan.dataset_id == strategy_dataset.id
    assert plan.plan_version == "1.0"
    assert len(plan.action_items) > 0
    assert len(plan.milestones) > 0
    assert len(plan.success_criteria) > 0

    # Getting plan again returns the cached instance
    cached = await service.get_or_generate_plan(dataset_id=strategy_dataset.id)
    assert cached.id == plan.id


@pytest.mark.anyio
async def test_strategy_service_regenerate_plan_version_increment(db_session, strategy_dataset):
    """Verifies deterministic version increments: 1.0 -> 2.0 -> 3.0 with history preservation."""
    service = StrategyPlannerService(db=db_session, provider=MockLLMProvider())

    p1 = await service.get_or_generate_plan(dataset_id=strategy_dataset.id)
    assert p1.plan_version == "1.0"

    p2 = await service.regenerate_plan(dataset_id=strategy_dataset.id, custom_title="Revised Plan v2")
    assert p2.plan_version == "2.0"
    assert p2.title == "Revised Plan v2"

    p3 = await service.regenerate_plan(dataset_id=strategy_dataset.id)
    assert p3.plan_version == "3.0"

    # Verify history contains all 3 versions
    history = await service.list_history(dataset_id=strategy_dataset.id)
    assert history.total_count == 3
    assert len(history.plans) == 3


@pytest.mark.anyio
async def test_strategy_service_degraded_without_ai_insight(db_session, strategy_dataset):
    """Verifies Strategy Planner operates seamlessly when AIInsight is absent."""
    service = StrategyPlannerService(db=db_session, provider=MockLLMProvider())

    plan = await service.generate_new_plan(dataset_id=strategy_dataset.id)
    assert plan.id is not None
    assert len(plan.action_items) > 0


@pytest.mark.anyio
async def test_strategy_service_rejection_no_recommendations(db_session, admin_user):
    """Verifies HTTP 400 rejection when dataset has no recommendations."""
    empty_ds = Dataset(
        name="Empty Recs Dataset",
        original_filename="empty_recs.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_empty.csv",
        file_path="/tmp/empty.csv",
        file_size=1024,
        uploaded_by=admin_user.id,
    )
    db_session.add(empty_ds)
    db_session.commit()

    service = StrategyPlannerService(db=db_session, provider=MockLLMProvider())

    with pytest.raises(HTTPException) as exc_info:
        await service.generate_new_plan(dataset_id=empty_ds.id)
    assert exc_info.value.status_code == 400
    assert "No approved recommendations found" in str(exc_info.value.detail)


@pytest.mark.anyio
async def test_strategy_service_rejection_missing_dataset(db_session):
    """Verifies HTTP 404 rejection when dataset does not exist."""
    service = StrategyPlannerService(db=db_session, provider=MockLLMProvider())

    with pytest.raises(HTTPException) as exc_info:
        await service.get_or_generate_plan(dataset_id=uuid.uuid4())
    assert exc_info.value.status_code == 404


@pytest.mark.anyio
async def test_strategy_service_rejection_invalid_recommendation_traceability(db_session, strategy_dataset):
    """Verifies strict HTTP 503 rejection when LLM generates action with unknown recommendation ID."""
    service = StrategyPlannerService(db=db_session, provider=InvalidTraceabilityProvider())

    with pytest.raises(HTTPException) as exc_info:
        await service.generate_new_plan(dataset_id=strategy_dataset.id)
    assert exc_info.value.status_code == 503
    assert "deterministic boundaries" in str(exc_info.value.detail)


@pytest.mark.anyio
async def test_strategy_service_update_status(db_session, strategy_dataset):
    """Verifies updating plan status."""
    service = StrategyPlannerService(db=db_session, provider=MockLLMProvider())
    plan = await service.get_or_generate_plan(dataset_id=strategy_dataset.id)

    updated = await service.update_plan_status(plan_id=plan.id, new_status=StrategyPlanStatus.ACTIVE)
    assert updated.status == StrategyPlanStatus.ACTIVE


@pytest.mark.anyio
async def test_strategy_service_llm_failure(db_session, strategy_dataset):
    """Verifies HTTP 503 handling when LLM provider raises an exception."""
    service = StrategyPlannerService(db=db_session, provider=FailingStrategyProvider())

    with pytest.raises(HTTPException) as exc_info:
        await service.generate_new_plan(dataset_id=strategy_dataset.id)
    assert exc_info.value.status_code == 503

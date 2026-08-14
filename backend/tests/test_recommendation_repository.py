"""Unit tests for RecommendationRepository layer."""

import uuid
import pytest

from app.core.constants import (
    ExpectedTimeToValue,
    FindingSeverity,
    FindingType,
    RecommendationPriority,
    RecommendationSource,
    RecommendationStatus,
    RecommendationType,
)
from app.models.dataset import Dataset
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.recommendation import Recommendation
from app.repositories.recommendation_repository import RecommendationRepository


@pytest.fixture
def repo_dataset(db_session, admin_user):
    dataset = Dataset(
        name="Rec Repo Test Dataset",
        original_filename="rec_repo.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_rec.csv",
        file_path="/tmp/rec.csv",
        file_size=1024,
        uploaded_by=admin_user.id,
    )
    db_session.add(dataset)
    db_session.commit()
    db_session.refresh(dataset)
    return dataset


@pytest.fixture
def repo_finding(db_session, repo_dataset):
    finding = DiagnosticFinding(
        dataset_id=repo_dataset.id,
        finding_type=FindingType.REVENUE_DROP,
        severity=FindingSeverity.CRITICAL,
        title="Revenue Decline",
        description="...",
        business_impact="...",
        confidence_score=0.90,
    )
    db_session.add(finding)
    db_session.commit()
    db_session.refresh(finding)
    return finding


@pytest.mark.anyio
async def test_recommendation_repository_crud_and_lifecycle(db_session, repo_dataset, repo_finding):
    """Verifies repository persistence, retrieval, status transition, and cascading deletion."""
    repo = RecommendationRepository(db_session)

    rec = Recommendation(
        dataset_id=repo_dataset.id,
        finding_id=repo_finding.id,
        recommendation_type=RecommendationType.CUSTOMER_RETENTION,
        priority=RecommendationPriority.CRITICAL,
        status=RecommendationStatus.PENDING,
        source=RecommendationSource.RULE_ENGINE,
        title="Launch Retention Campaign",
        description="Stabilize cohorts.",
        why_recommended="Driven by churn.",
        confidence_score=0.90,
        estimated_impact_score=0.85,
        estimated_effort_score=0.50,
        expected_time_to_value=ExpectedTimeToValue.SHORT_TERM,
        action_plan=["Step 1", "Step 2"],
        success_metrics=["Customer Retention Rate"],
        evidence={"finding": repo_finding.title},
        outcomes={"expected_metric": "Customer Retention Rate", "baseline": 0.68, "target": 0.78},
    )

    # 1. Create
    created = await repo.create(rec)
    assert created.id is not None
    assert created.status == RecommendationStatus.PENDING

    # 2. Get by ID (eager loading)
    fetched = await repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.title == "Launch Retention Campaign"
    assert fetched.finding.id == repo_finding.id

    # 3. Update status to ACCEPTED
    accepted = await repo.update_status(created.id, RecommendationStatus.ACCEPTED)
    assert accepted is not None
    assert accepted.status == RecommendationStatus.ACCEPTED
    assert accepted.accepted_at is not None

    # 4. Filter by dataset and status
    accepted_recs = await repo.get_by_dataset(repo_dataset.id, status=RecommendationStatus.ACCEPTED)
    assert len(accepted_recs) == 1

    # 5. Count
    total = await repo.count_by_dataset(repo_dataset.id)
    assert total == 1

    # 6. Delete
    deleted = await repo.delete_by_dataset(repo_dataset.id)
    assert deleted == 1
    assert await repo.count_by_dataset(repo_dataset.id) == 0

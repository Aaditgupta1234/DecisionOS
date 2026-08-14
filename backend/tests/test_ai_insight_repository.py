"""Unit tests for AIInsightRepository layer."""

import uuid
from datetime import datetime, timezone
import pytest

from app.models.ai_insight import AIInsight
from app.models.dataset import Dataset
from app.repositories.ai_insight_repository import AIInsightRepository


@pytest.fixture
def repo_dataset(db_session, admin_user):
    dataset = Dataset(
        name="AI Insight Repo Test Dataset",
        original_filename="ai_repo.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_ai_repo.csv",
        file_path="/tmp/ai_repo.csv",
        file_size=1024,
        uploaded_by=admin_user.id,
    )
    db_session.add(dataset)
    db_session.commit()
    db_session.refresh(dataset)
    return dataset


@pytest.mark.anyio
async def test_ai_insight_repository_crud_and_history(db_session, repo_dataset):
    """Verifies persistence, latest record retrieval, and version history pagination."""
    repo = AIInsightRepository(db_session)

    insight1 = AIInsight(
        dataset_id=repo_dataset.id,
        insight_version="1.0",
        prompt_version="1.0",
        report_version="1.0",
        model_provider="mock",
        model_name="gpt-4o-mini",
        executive_narrative={"headline": "First Executive Insight"},
        business_assessment={"strengths": ["Strong cash balance"]},
        risk_analysis={"overall_risk_level": "LOW"},
        opportunities={"growth_opportunities": []},
        strategic_priorities={"immediate_priorities": []},
        action_plan={"immediate_actions": {}},
        metadata_info={"score": 88},
        generated_at=datetime.now(timezone.utc),
    )

    # 1. Create
    created1 = await repo.create(insight1)
    assert created1.id is not None

    # 2. Get by ID
    fetched = await repo.get_by_id(created1.id)
    assert fetched is not None
    assert fetched.executive_narrative["headline"] == "First Executive Insight"

    # 3. Create second revision
    insight2 = AIInsight(
        dataset_id=repo_dataset.id,
        insight_version="1.1",
        prompt_version="1.0",
        report_version="1.0",
        model_provider="mock",
        model_name="gpt-4o",
        executive_narrative={"headline": "Second Executive Insight Revision"},
        business_assessment={"strengths": ["Strong cash balance"]},
        risk_analysis={"overall_risk_level": "LOW"},
        opportunities={"growth_opportunities": []},
        strategic_priorities={"immediate_priorities": []},
        action_plan={"immediate_actions": {}},
        metadata_info={"score": 90},
        generated_at=datetime.now(timezone.utc),
    )
    created2 = await repo.create(insight2)

    # 4. Get Latest (should return insight2)
    latest = await repo.get_latest_by_dataset(repo_dataset.id)
    assert latest is not None
    assert latest.id == created2.id
    assert latest.insight_version == "1.1"

    # 5. List History
    history = await repo.list_history_by_dataset(repo_dataset.id, limit=10)
    assert len(history) == 2
    assert history[0].id == created2.id
    assert history[1].id == created1.id

    # 6. Count and Delete
    count = await repo.count_by_dataset(repo_dataset.id)
    assert count == 2

    deleted = await repo.delete_by_dataset(repo_dataset.id)
    assert deleted == 2
    assert await repo.count_by_dataset(repo_dataset.id) == 0

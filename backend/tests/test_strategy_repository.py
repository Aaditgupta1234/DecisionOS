"""Unit tests for StrategyPlanRepository data access layer."""

import uuid
import pytest

from app.core.constants import StrategyPlanStatus
from app.models.dataset import Dataset
from app.models.strategy_plan import StrategyPlan
from app.strategy_planner.repositories.strategy_plan_repository import StrategyPlanRepository


@pytest.fixture
def repo_dataset_a(db_session, admin_user):
    ds = Dataset(
        name="Strategy Repo Dataset A",
        original_filename="strat_a.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_strat_a.csv",
        file_path="/tmp/strat_a.csv",
        file_size=1024,
        uploaded_by=admin_user.id,
    )
    db_session.add(ds)
    db_session.commit()
    db_session.refresh(ds)
    return ds


@pytest.fixture
def repo_dataset_b(db_session, admin_user):
    ds = Dataset(
        name="Strategy Repo Dataset B",
        original_filename="strat_b.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_strat_b.csv",
        file_path="/tmp/strat_b.csv",
        file_size=1024,
        uploaded_by=admin_user.id,
    )
    db_session.add(ds)
    db_session.commit()
    db_session.refresh(ds)
    return ds


@pytest.mark.anyio
async def test_create_and_get_plan_by_id(db_session, repo_dataset_a):
    """Verifies strategy plan persistence and lookup by primary key."""
    repo = StrategyPlanRepository(db_session)
    plan = StrategyPlan(
        dataset_id=repo_dataset_a.id,
        plan_version="1.0",
        title="Q3 Turnaround Strategy",
        objective="Improve retention",
        executive_summary="Executive summary...",
    )
    created = await repo.create(plan)

    assert created.id is not None
    assert created.title == "Q3 Turnaround Strategy"
    assert created.plan_version == "1.0"

    fetched = await repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.dataset_id == repo_dataset_a.id


@pytest.mark.anyio
async def test_get_latest_by_dataset(db_session, repo_dataset_a):
    """Verifies retrieval of the most recently created strategy plan."""
    repo = StrategyPlanRepository(db_session)
    p1 = StrategyPlan(
        dataset_id=repo_dataset_a.id,
        plan_version="1.0",
        title="Plan v1",
    )
    await repo.create(p1)

    p2 = StrategyPlan(
        dataset_id=repo_dataset_a.id,
        plan_version="2.0",
        title="Plan v2",
    )
    await repo.create(p2)

    latest = await repo.get_latest_by_dataset(repo_dataset_a.id)
    assert latest is not None
    assert latest.id == p2.id
    assert latest.plan_version == "2.0"


@pytest.mark.anyio
async def test_list_history_by_dataset_and_count(db_session, repo_dataset_a):
    """Verifies historical version listing and total count."""
    repo = StrategyPlanRepository(db_session)
    await repo.create(StrategyPlan(dataset_id=repo_dataset_a.id, plan_version="1.0", title="v1"))
    await repo.create(StrategyPlan(dataset_id=repo_dataset_a.id, plan_version="2.0", title="v2"))

    count = await repo.count_by_dataset(repo_dataset_a.id)
    assert count == 2

    history = await repo.list_history_by_dataset(repo_dataset_a.id, limit=10)
    assert len(history) == 2
    assert history[0].plan_version == "2.0"
    assert history[1].plan_version == "1.0"


@pytest.mark.anyio
async def test_update_plan_status(db_session, repo_dataset_a):
    """Verifies updating the lifecycle status of a strategy plan."""
    repo = StrategyPlanRepository(db_session)
    plan = await repo.create(StrategyPlan(dataset_id=repo_dataset_a.id, title="Status Test"))
    assert plan.status == StrategyPlanStatus.DRAFT

    updated = await repo.update_status(plan.id, StrategyPlanStatus.ACTIVE)
    assert updated is not None
    assert updated.status == StrategyPlanStatus.ACTIVE


@pytest.mark.anyio
async def test_delete_by_dataset(db_session, repo_dataset_a):
    """Verifies deleting all strategy plans for a dataset."""
    repo = StrategyPlanRepository(db_session)
    await repo.create(StrategyPlan(dataset_id=repo_dataset_a.id, title="Plan to delete"))

    count_before = await repo.count_by_dataset(repo_dataset_a.id)
    assert count_before == 1

    deleted_count = await repo.delete_by_dataset(repo_dataset_a.id)
    assert deleted_count == 1

    count_after = await repo.count_by_dataset(repo_dataset_a.id)
    assert count_after == 0


@pytest.mark.anyio
async def test_list_history_pagination(db_session, repo_dataset_a):
    """Verifies offset and limit pagination on historical versions."""
    repo = StrategyPlanRepository(db_session)
    for i in range(5):
        await repo.create(StrategyPlan(dataset_id=repo_dataset_a.id, plan_version=f"{i+1}.0", title=f"v{i+1}"))

    page1 = await repo.list_history_by_dataset(repo_dataset_a.id, limit=2, offset=0)
    assert len(page1) == 2
    assert page1[0].plan_version == "5.0"

    page2 = await repo.list_history_by_dataset(repo_dataset_a.id, limit=2, offset=2)
    assert len(page2) == 2
    assert page2[0].plan_version == "3.0"


@pytest.mark.anyio
async def test_dataset_isolation(db_session, repo_dataset_a, repo_dataset_b):
    """Verifies dataset isolation for strategy plan repositories."""
    repo = StrategyPlanRepository(db_session)
    p_a = await repo.create(StrategyPlan(dataset_id=repo_dataset_a.id, title="Dataset A Plan"))

    # Plan for A should not appear in B's history
    history_b = await repo.list_history_by_dataset(repo_dataset_b.id)
    assert len(history_b) == 0

    latest_b = await repo.get_latest_by_dataset(repo_dataset_b.id)
    assert latest_b is None

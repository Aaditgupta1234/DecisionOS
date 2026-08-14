"""Unit tests for ScenarioRepository data access layer and dataset isolation."""

import uuid
import pytest

from app.core.constants import ScenarioStatus
from app.models.dataset import Dataset
from app.models.scenario import Scenario
from app.scenario_simulation.repositories.scenario_repository import ScenarioRepository


@pytest.fixture
def repo_dataset_a(db_session, admin_user):
    ds = Dataset(
        name="Scenario Repo Dataset A",
        original_filename="sc_a.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_sc_a.csv",
        file_path="/tmp/sc_a.csv",
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
        name="Scenario Repo Dataset B",
        original_filename="sc_b.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_sc_b.csv",
        file_path="/tmp/sc_b.csv",
        file_size=1024,
        uploaded_by=admin_user.id,
    )
    db_session.add(ds)
    db_session.commit()
    db_session.refresh(ds)
    return ds


@pytest.mark.anyio
async def test_create_and_get_scenario_by_id(db_session, repo_dataset_a):
    """Verifies scenario simulation persistence and primary key retrieval."""
    repo = ScenarioRepository(db_session)
    sc = Scenario(
        dataset_id=repo_dataset_a.id,
        name="Churn -5%",
        scenario_version="1.0",
        assumptions=[{"metric_key": "customer_churn_rate", "adjustment_type": "PERCENTAGE_POINTS", "adjustment_value": -5}],
        projected_health={"baseline_score": 70, "projected_score": 80},
    )
    created = await repo.create(sc)

    assert created.id is not None
    assert created.name == "Churn -5%"

    fetched = await repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.dataset_id == repo_dataset_a.id


@pytest.mark.anyio
async def test_get_latest_and_history(db_session, repo_dataset_a):
    """Verifies latest lookup and paginated history."""
    repo = ScenarioRepository(db_session)
    s1 = await repo.create(Scenario(dataset_id=repo_dataset_a.id, name="Sc 1", projected_health={}))
    s2 = await repo.create(Scenario(dataset_id=repo_dataset_a.id, name="Sc 2", projected_health={}))

    latest = await repo.get_latest_by_dataset(repo_dataset_a.id)
    assert latest.id == s2.id

    history = await repo.list_history_by_dataset(repo_dataset_a.id, limit=10)
    assert len(history) == 2
    assert history[0].id == s2.id

    count = await repo.count_by_dataset(repo_dataset_a.id)
    assert count == 2


@pytest.mark.anyio
async def test_get_by_ids_strict_isolation(db_session, repo_dataset_a, repo_dataset_b):
    """Verifies get_by_ids strictly filters out scenarios from other datasets."""
    repo = ScenarioRepository(db_session)
    s_a = await repo.create(Scenario(dataset_id=repo_dataset_a.id, name="Sc A", projected_health={}))
    s_b = await repo.create(Scenario(dataset_id=repo_dataset_b.id, name="Sc B", projected_health={}))

    # Querying Dataset A with both IDs must only return s_a
    results = await repo.get_by_ids(dataset_id=repo_dataset_a.id, scenario_ids=[s_a.id, s_b.id])
    assert len(results) == 1
    assert results[0].id == s_a.id


@pytest.mark.anyio
async def test_delete_scenario(db_session, repo_dataset_a):
    """Verifies deleting scenario by ID."""
    repo = ScenarioRepository(db_session)
    sc = await repo.create(Scenario(dataset_id=repo_dataset_a.id, name="To Delete", projected_health={}))

    deleted = await repo.delete_by_id(sc.id)
    assert deleted is True

    fetched = await repo.get_by_id(sc.id)
    assert fetched is None

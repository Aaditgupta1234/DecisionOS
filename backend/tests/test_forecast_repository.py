"""Unit tests for ForecastRepository data access layer and dataset isolation."""

import uuid
import pytest

from app.core.constants import ForecastStatus
from app.models.dataset import Dataset
from app.models.forecast import Forecast
from app.forecasting.repositories.forecast_repository import ForecastRepository


@pytest.fixture
def forecast_repo_dataset_a(db_session, admin_user):
    ds = Dataset(
        name="Forecast Repo Dataset A",
        original_filename="fc_a.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_fc_a.csv",
        file_path="/tmp/fc_a.csv",
        file_size=1024,
        uploaded_by=admin_user.id,
    )
    db_session.add(ds)
    db_session.commit()
    db_session.refresh(ds)
    return ds


@pytest.fixture
def forecast_repo_dataset_b(db_session, admin_user):
    ds = Dataset(
        name="Forecast Repo Dataset B",
        original_filename="fc_b.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_fc_b.csv",
        file_path="/tmp/fc_b.csv",
        file_size=1024,
        uploaded_by=admin_user.id,
    )
    db_session.add(ds)
    db_session.commit()
    db_session.refresh(ds)
    return ds


@pytest.mark.anyio
async def test_create_and_get_forecast_by_id(db_session, forecast_repo_dataset_a):
    """Verifies forecast persistence and primary key retrieval."""
    repo = ForecastRepository(db_session)
    fc = Forecast(
        dataset_id=forecast_repo_dataset_a.id,
        metric_key="total_revenue",
        horizon="90_DAYS",
        frequency="MONTHLY",
        model_name="NAIVE",
        forecast_version="1.0",
        forecast_points=[{"period": "2026-01", "predicted_value": 1000.0}],
        model_metrics={"mae": 10.0, "rmse": 12.0},
    )
    created = await repo.create(fc)

    assert created.id is not None
    assert created.metric_key == "total_revenue"

    fetched = await repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.dataset_id == forecast_repo_dataset_a.id


@pytest.mark.anyio
async def test_get_latest_by_metric_and_history(db_session, forecast_repo_dataset_a):
    """Verifies latest lookup and paginated history."""
    repo = ForecastRepository(db_session)
    f1 = await repo.create(Forecast(
        dataset_id=forecast_repo_dataset_a.id,
        metric_key="total_revenue",
        horizon="90_DAYS",
        frequency="MONTHLY",
        forecast_version="1.0",
        forecast_points=[],
        model_metrics={"mae": 1.0, "rmse": 1.0},
    ))
    f2 = await repo.create(Forecast(
        dataset_id=forecast_repo_dataset_a.id,
        metric_key="total_revenue",
        horizon="90_DAYS",
        frequency="MONTHLY",
        forecast_version="2.0",
        forecast_points=[],
        model_metrics={"mae": 0.8, "rmse": 0.9},
    ))

    latest = await repo.get_latest_by_metric(forecast_repo_dataset_a.id, "total_revenue")
    assert latest is not None
    assert latest.id == f2.id
    assert latest.forecast_version == "2.0"

    history = await repo.list_history_by_dataset(forecast_repo_dataset_a.id, metric_key="total_revenue")
    assert len(history) == 2
    assert history[0].id == f2.id


@pytest.mark.anyio
async def test_get_by_ids_strict_isolation(db_session, forecast_repo_dataset_a, forecast_repo_dataset_b):
    """Verifies get_by_ids strictly filters out forecasts belonging to other datasets."""
    repo = ForecastRepository(db_session)
    f_a = await repo.create(Forecast(
        dataset_id=forecast_repo_dataset_a.id,
        metric_key="total_revenue",
        horizon="90_DAYS",
        frequency="MONTHLY",
        forecast_points=[],
        model_metrics={},
    ))
    f_b = await repo.create(Forecast(
        dataset_id=forecast_repo_dataset_b.id,
        metric_key="total_revenue",
        horizon="90_DAYS",
        frequency="MONTHLY",
        forecast_points=[],
        model_metrics={},
    ))

    results = await repo.get_by_ids(dataset_id=forecast_repo_dataset_a.id, forecast_ids=[f_a.id, f_b.id])
    assert len(results) == 1
    assert results[0].id == f_a.id


@pytest.mark.anyio
async def test_delete_forecast(db_session, forecast_repo_dataset_a):
    """Verifies deleting forecast by ID."""
    repo = ForecastRepository(db_session)
    fc = await repo.create(Forecast(
        dataset_id=forecast_repo_dataset_a.id,
        metric_key="total_revenue",
        horizon="90_DAYS",
        frequency="MONTHLY",
        forecast_points=[],
        model_metrics={},
    ))

    deleted = await repo.delete_by_id(fc.id)
    assert deleted is True

    fetched = await repo.get_by_id(fc.id)
    assert fetched is None

"""Unit tests for ForecastingService orchestration, determinism, and data immutability."""

import os
import uuid
import pandas as pd
import pytest
from fastapi import HTTPException

from app.core.constants import ForecastHorizon, MetricCategory
from app.models.dataset import Dataset
from app.models.dataset_column import DatasetColumn
from app.models.dataset_metric import DatasetMetric
from app.models.metric_definition import MetricDefinition
from app.forecasting.schemas.forecast_schema import ForecastRequest
from app.forecasting.services.forecasting_service import ForecastingService


@pytest.fixture
def service_forecast_dataset(db_session, admin_user, tmp_path):
    """Creates a dataset with 12 months of historical CSV data on disk."""
    csv_file = tmp_path / "service_fc_data.csv"
    dates = pd.date_range(start="2025-01-01", periods=12, freq="MS")
    df = pd.DataFrame({
        "order_date": dates,
        "revenue": [10000.0 + (i * 250.0) for i in range(12)],
        "order_id": [f"ORD_{i}" for i in range(12)],
    })
    df.to_csv(csv_file, index=False)

    ds = Dataset(
        name="Service Forecast Dataset",
        original_filename="fc_data.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_fc_data.csv",
        file_path=str(csv_file),
        file_size=1024,
        uploaded_by=admin_user.id,
    )
    db_session.add(ds)
    db_session.commit()
    db_session.refresh(ds)

    col1 = DatasetColumn(dataset_id=ds.id, original_name="order_date", normalized_name="order_date", mapped_field="order_date", data_type="datetime")
    col2 = DatasetColumn(dataset_id=ds.id, original_name="revenue", normalized_name="revenue", mapped_field="revenue", data_type="float")
    db_session.add_all([col1, col2])

    mdef = db_session.query(MetricDefinition).filter_by(metric_key="total_revenue").first()
    if not mdef:
        mdef = MetricDefinition(metric_key="total_revenue", name="Total Revenue", metric_category=MetricCategory.REVENUE, required_field="revenue")
        db_session.add(mdef)
        db_session.commit()
        db_session.refresh(mdef)

    from datetime import datetime, timezone
    m = DatasetMetric(
        dataset_id=ds.id,
        metric_definition_id=mdef.id,
        metric_key="total_revenue",
        metric_name="Total Revenue",
        metric_category=MetricCategory.REVENUE,
        metric_value=135000.0,
        calculated_at=datetime.now(timezone.utc),
    )
    db_session.add(m)
    db_session.commit()

    return ds


@pytest.mark.anyio
async def test_generate_forecast_service_success(db_session, service_forecast_dataset):
    """Verifies end-to-end forecast generation via service layer."""
    service = ForecastingService(db_session)
    req = ForecastRequest(
        metric_key="total_revenue",
        horizon=ForecastHorizon.HORIZON_90_DAYS,
        confidence_level=0.80,
    )

    res = await service.generate_forecast(dataset_id=service_forecast_dataset.id, request=req)
    assert res.id is not None
    assert res.metric_key == "total_revenue"
    assert res.forecast_version == "1.0"
    assert len(res.forecast_points) == 3
    assert res.historical_observation_count == 12


@pytest.mark.anyio
async def test_generate_forecast_immutability_of_historical_data(db_session, service_forecast_dataset):
    """
    CRITICAL TEST: Proves that generating a forecast NEVER modifies actual historical
    DatasetMetric records in the database.
    """
    service = ForecastingService(db_session)
    req = ForecastRequest(
        metric_key="total_revenue",
        horizon=ForecastHorizon.HORIZON_90_DAYS,
    )

    await service.generate_forecast(dataset_id=service_forecast_dataset.id, request=req)

    # Directly query actual database record
    db_metric = (
        db_session.query(DatasetMetric)
        .filter(DatasetMetric.dataset_id == service_forecast_dataset.id, DatasetMetric.metric_key == "total_revenue")
        .first()
    )
    assert db_metric.metric_value == 135000.0


@pytest.mark.anyio
async def test_generate_forecast_determinism(db_session, service_forecast_dataset):
    """
    CRITICAL TEST: Proves that repeated execution with identical inputs produces
    exact, identical numerical forecast points.
    """
    service = ForecastingService(db_session)
    req = ForecastRequest(
        metric_key="total_revenue",
        horizon=ForecastHorizon.HORIZON_90_DAYS,
        confidence_level=0.80,
    )

    res1 = await service.generate_forecast(dataset_id=service_forecast_dataset.id, request=req)
    res2 = await service.generate_forecast(dataset_id=service_forecast_dataset.id, request=req)

    # Point predictions must be identical
    assert len(res1.forecast_points) == len(res2.forecast_points)
    for p1, p2 in zip(res1.forecast_points, res2.forecast_points):
        assert p1.predicted_value == p2.predicted_value
        assert p1.lower_bound == p2.lower_bound
        assert p1.upper_bound == p2.upper_bound

    # Version should increment: 1.0 -> 2.0
    assert res1.forecast_version == "1.0"
    assert res2.forecast_version == "2.0"


@pytest.mark.anyio
async def test_generate_forecast_404_dataset_not_found(db_session):
    """Verifies 404 when dataset does not exist."""
    service = ForecastingService(db_session)
    req = ForecastRequest(
        metric_key="total_revenue",
        horizon=ForecastHorizon.HORIZON_90_DAYS,
    )
    with pytest.raises(HTTPException) as exc:
        await service.generate_forecast(dataset_id=uuid.uuid4(), request=req)
    assert exc.value.status_code == 404

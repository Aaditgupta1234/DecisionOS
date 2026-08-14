"""Integration tests for Forecasting Engine REST API endpoints."""

import os
from datetime import datetime, timezone
import uuid
import pandas as pd
import pytest

from app.core.constants import ForecastHorizon, MetricCategory
from app.models.dataset import Dataset
from app.models.dataset_column import DatasetColumn
from app.models.dataset_metric import DatasetMetric
from app.models.metric_definition import MetricDefinition


@pytest.fixture
def api_forecast_dataset_a(db_session, admin_user, tmp_path):
    csv_file = tmp_path / "api_fc_a.csv"
    dates = pd.date_range(start="2025-01-01", periods=12, freq="MS")
    df = pd.DataFrame({
        "order_date": dates,
        "revenue": [50000.0 + (i * 1000.0) for i in range(12)],
    })
    df.to_csv(csv_file, index=False)

    ds = Dataset(
        name="Forecast API Dataset A",
        original_filename="api_fc_a.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_api_fc_a.csv",
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

    m = DatasetMetric(
        dataset_id=ds.id,
        metric_definition_id=mdef.id,
        metric_key="total_revenue",
        metric_name="Total Revenue",
        metric_category=MetricCategory.REVENUE,
        metric_value=660000.0,
        calculated_at=datetime.now(timezone.utc),
    )
    db_session.add(m)
    db_session.commit()

    return ds


@pytest.fixture
def api_forecast_dataset_b(db_session, admin_user, tmp_path):
    csv_file = tmp_path / "api_fc_b.csv"
    dates = pd.date_range(start="2025-01-01", periods=12, freq="MS")
    df = pd.DataFrame({
        "order_date": dates,
        "revenue": [20000.0 + (i * 500.0) for i in range(12)],
    })
    df.to_csv(csv_file, index=False)

    ds = Dataset(
        name="Forecast API Dataset B",
        original_filename="api_fc_b.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_api_fc_b.csv",
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
    m = DatasetMetric(
        dataset_id=ds.id,
        metric_definition_id=mdef.id,
        metric_key="total_revenue",
        metric_name="Total Revenue",
        metric_category=MetricCategory.REVENUE,
        metric_value=270000.0,
        calculated_at=datetime.now(timezone.utc),
    )
    db_session.add(m)
    db_session.commit()

    return ds


def test_create_forecast_api(client, admin_headers, api_forecast_dataset_a):
    """Test POST /api/v1/datasets/{dataset_id}/forecasts."""
    dataset_id = str(api_forecast_dataset_a.id)
    response = client.post(
        f"/api/v1/datasets/{dataset_id}/forecasts",
        headers=admin_headers,
        json={
            "metric_key": "total_revenue",
            "horizon": "90_DAYS",
            "confidence_level": 0.80,
        },
    )
    assert response.status_code == 201
    res_json = response.json()
    assert res_json["success"] is True
    data = res_json["data"]
    assert data["metric_key"] == "total_revenue"
    assert len(data["forecast_points"]) == 3


def test_get_forecast_by_id_api(client, admin_headers, api_forecast_dataset_a):
    """Test GET /api/v1/datasets/{dataset_id}/forecasts/{forecast_id}."""
    dataset_id = str(api_forecast_dataset_a.id)
    create_res = client.post(
        f"/api/v1/datasets/{dataset_id}/forecasts",
        headers=admin_headers,
        json={"metric_key": "total_revenue", "horizon": "30_DAYS"},
    )
    forecast_id = create_res.json()["data"]["id"]

    response = client.get(
        f"/api/v1/datasets/{dataset_id}/forecasts/{forecast_id}",
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["data"]["id"] == forecast_id


def test_list_forecasts_and_history_api(client, admin_headers, api_forecast_dataset_a):
    """Test GET /api/v1/datasets/{dataset_id}/forecasts and /history."""
    dataset_id = str(api_forecast_dataset_a.id)

    client.post(
        f"/api/v1/datasets/{dataset_id}/forecasts",
        headers=admin_headers,
        json={"metric_key": "total_revenue", "horizon": "30_DAYS"},
    )

    res_list = client.get(f"/api/v1/datasets/{dataset_id}/forecasts", headers=admin_headers)
    assert res_list.status_code == 200
    assert res_list.json()["data"]["total_count"] >= 1

    res_hist = client.get(f"/api/v1/datasets/{dataset_id}/forecasts/history", headers=admin_headers)
    assert res_hist.status_code == 200
    assert len(res_hist.json()["data"]["forecasts"]) >= 1


def test_compare_forecasts_api(client, admin_headers, api_forecast_dataset_a):
    """Test GET /api/v1/datasets/{dataset_id}/forecasts/compare."""
    dataset_id = str(api_forecast_dataset_a.id)

    f1 = client.post(
        f"/api/v1/datasets/{dataset_id}/forecasts",
        headers=admin_headers,
        json={"metric_key": "total_revenue", "horizon": "90_DAYS", "model_name": "NAIVE"},
    ).json()["data"]["id"]

    f2 = client.post(
        f"/api/v1/datasets/{dataset_id}/forecasts",
        headers=admin_headers,
        json={"metric_key": "total_revenue", "horizon": "90_DAYS", "model_name": "MOVING_AVERAGE"},
    ).json()["data"]["id"]

    response = client.get(
        f"/api/v1/datasets/{dataset_id}/forecasts/compare?forecast_ids={f1}&forecast_ids={f2}",
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["forecasts"]) == 2
    assert "comparison_matrix" in data


def test_compare_forecasts_cross_dataset_rejection(client, admin_headers, api_forecast_dataset_a, api_forecast_dataset_b):
    """
    CRITICAL TEST: Verifies that passing a forecast ID from Dataset B when comparing on Dataset A
    is strictly rejected.
    """
    f_b_id = client.post(
        f"/api/v1/datasets/{str(api_forecast_dataset_b.id)}/forecasts",
        headers=admin_headers,
        json={"metric_key": "total_revenue", "horizon": "90_DAYS"},
    ).json()["data"]["id"]

    response = client.get(
        f"/api/v1/datasets/{str(api_forecast_dataset_a.id)}/forecasts/compare?forecast_ids={f_b_id}",
        headers=admin_headers,
    )
    assert response.status_code == 400
    assert "do not belong to the requested dataset" in response.json()["detail"]


def test_delete_forecast_api(client, admin_headers, api_forecast_dataset_a):
    """Test DELETE /api/v1/forecasts/{forecast_id}."""
    dataset_id = str(api_forecast_dataset_a.id)
    create_res = client.post(
        f"/api/v1/datasets/{dataset_id}/forecasts",
        headers=admin_headers,
        json={"metric_key": "total_revenue", "horizon": "30_DAYS"},
    )
    forecast_id = create_res.json()["data"]["id"]

    del_res = client.delete(f"/api/v1/forecasts/{forecast_id}", headers=admin_headers)
    assert del_res.status_code == 200
    assert del_res.json()["data"]["deleted"] is True

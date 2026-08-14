"""Unit and integration tests for Phase 4 KPI Engine, metrics calculation, summary reporting, and RBAC."""

import io
from app.core.constants import DatasetStatus, MetricsGenerationStatus

FULL_SAMPLE_CSV = (
    "OrderID,CustomerID,Order Date,Revenue Amount,Order Status,Review Score,Delivery Time,Product Category\n"
    "ORD001,C001,2026-01-15,150.50,completed,5,2.5,Electronics\n"
    "ORD002,C002,2026-01-16,230.00,completed,4,3.0,Home\n"
    "ORD003,C003,2026-01-17,45.00,returned,2,5.0,Apparel\n"
    "ORD004,C004,2026-01-18,310.25,completed,5,1.5,Electronics\n"
    "ORD005,C005,2026-01-19,89.90,pending,3,4.0,Home\n"
).encode("utf-8")


def upload_and_map_sample_dataset(client, admin_headers, csv_bytes=FULL_SAMPLE_CSV):
    """Helper function that uploads a dataset and confirms canonical business mappings."""
    files = {
        "file": ("metrics_sales.csv", io.BytesIO(csv_bytes), "text/csv"),
    }
    upload_res = client.post("/api/v1/datasets/upload", headers=admin_headers, files=files)
    dataset_id = upload_res.json()["data"]["dataset_id"]

    # Confirm standard business mappings
    mapping_payload = {
        "mappings": {
            "OrderID": "order_id",
            "CustomerID": "customer_id",
            "Order Date": "order_date",
            "Revenue Amount": "revenue",
            "Order Status": "status",
            "Review Score": "review_score",
            "Delivery Time": "delivery_time",
            "Product Category": "product_category",
        }
    }
    client.post(f"/api/v1/datasets/{dataset_id}/mapping", headers=admin_headers, json=mapping_payload)
    return dataset_id


def test_generate_metrics_admin_success(client, admin_headers):
    """Test Admin can trigger KPI generation on a READY dataset."""
    dataset_id = upload_and_map_sample_dataset(client, admin_headers)

    response = client.post(f"/api/v1/datasets/{dataset_id}/metrics/generate", headers=admin_headers)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    data = res_json["data"]
    assert data["dataset_id"] == dataset_id
    assert data["metrics_generated"] == 15  # All 15 standard KPIs
    assert len(data["metrics"]) == 15

    # Verify Dataset status updated
    detail_res = client.get(f"/api/v1/datasets/{dataset_id}", headers=admin_headers)
    dataset_detail = detail_res.json()["data"]
    assert dataset_detail["metrics_generation_status"] == MetricsGenerationStatus.GENERATED
    assert dataset_detail["metrics_generated_at"] is not None


def test_revenue_and_customer_metrics_values(client, admin_headers):
    """Test accuracy of calculated Revenue and Customer KPIs."""
    dataset_id = upload_and_map_sample_dataset(client, admin_headers)

    client.post(f"/api/v1/datasets/{dataset_id}/metrics/generate", headers=admin_headers)
    summary_res = client.get(f"/api/v1/datasets/{dataset_id}/metrics/summary", headers=admin_headers)
    assert summary_res.status_code == 200
    summary = summary_res.json()["data"]

    # Revenue values from sample: 150.50, 230.00, 45.00, 310.25, 89.90 -> Total: 825.65
    rev = summary["revenue"]
    assert rev["total_revenue"] == 825.65
    assert rev["average_revenue"] == 165.13
    assert rev["maximum_revenue"] == 310.25
    assert rev["minimum_revenue"] == 45.00
    assert rev["revenue_per_customer"] == 165.13  # 825.65 / 5

    # Customers
    cust = summary["customers"]
    assert cust["unique_customers"] == 5


def test_order_and_quality_metrics_values(client, admin_headers):
    """Test accuracy of calculated Order, Quality, Review, and Delivery KPIs."""
    # CSV has 5 rows: 3 completed (150.50, 230.00, 310.25), 1 returned, 1 pending
    dataset_id = upload_and_map_sample_dataset(client, admin_headers)

    client.post(f"/api/v1/datasets/{dataset_id}/metrics/generate", headers=admin_headers)
    summary_res = client.get(f"/api/v1/datasets/{dataset_id}/metrics/summary", headers=admin_headers)
    summary = summary_res.json()["data"]

    orders = summary["orders"]
    assert orders["total_orders"] == 5
    assert orders["completed_orders"] == 3
    assert orders["cancelled_orders"] == 1  # returned
    assert orders["completion_rate"] == 60.0  # 3/5 * 100

    quality = summary["quality"]
    assert quality["record_count"] == 5
    assert quality["column_count"] == 8
    assert quality["completeness_percentage"] == 100.0

    reviews = summary["reviews"]
    assert reviews["average_review_score"] == 3.8  # (5+4+2+5+3)/5 = 19/5 = 3.8

    delivery = summary["delivery"]
    assert delivery["average_delivery_time"] == 3.2  # (2.5+3.0+5.0+1.5+4.0)/5 = 16/5 = 3.2


def test_generate_metrics_forbidden_analyst(client, admin_headers, analyst_headers):
    """Test Analyst is forbidden from calling /metrics/generate."""
    dataset_id = upload_and_map_sample_dataset(client, admin_headers)

    response = client.post(f"/api/v1/datasets/{dataset_id}/metrics/generate", headers=analyst_headers)
    assert response.status_code == 403


def test_get_metrics_analyst_allowed_for_ready_dataset(client, admin_headers, analyst_headers):
    """Test Analyst can view metrics and summary for READY datasets."""
    dataset_id = upload_and_map_sample_dataset(client, admin_headers)
    client.post(f"/api/v1/datasets/{dataset_id}/metrics/generate", headers=admin_headers)

    # 1. Analyst gets list of metrics
    list_res = client.get(f"/api/v1/datasets/{dataset_id}/metrics", headers=analyst_headers)
    assert list_res.status_code == 200
    assert len(list_res.json()["data"]) == 15

    # 2. Analyst gets categorized summary
    summary_res = client.get(f"/api/v1/datasets/{dataset_id}/metrics/summary", headers=analyst_headers)
    assert summary_res.status_code == 200
    assert "revenue" in summary_res.json()["data"]


def test_missing_mappings_gracefully_skipped(client, admin_headers):
    """Test dataset without review_score and delivery_time skips those categories cleanly."""
    partial_csv = (
        "OrderID,CustomerID,Revenue Amount,Order Status\n"
        "ORD001,C001,100.0,completed\n"
        "ORD002,C002,200.0,completed\n"
    ).encode("utf-8")

    files = {
        "file": ("partial.csv", io.BytesIO(partial_csv), "text/csv"),
    }
    upload_res = client.post("/api/v1/datasets/upload", headers=admin_headers, files=files)
    dataset_id = upload_res.json()["data"]["dataset_id"]

    client.post(
        f"/api/v1/datasets/{dataset_id}/mapping",
        headers=admin_headers,
        json={
            "mappings": {
                "OrderID": "order_id",
                "CustomerID": "customer_id",
                "Revenue Amount": "revenue",
                "Order Status": "status",
            }
        },
    )

    response = client.post(f"/api/v1/datasets/{dataset_id}/metrics/generate", headers=admin_headers)
    data = response.json()["data"]
    assert "reviews" in data["skipped_categories"]
    assert "delivery" in data["skipped_categories"]


def test_idempotent_regeneration(client, admin_headers):
    """Test running KPI generation multiple times replaces previous records without duplicates."""
    dataset_id = upload_and_map_sample_dataset(client, admin_headers)

    # Run 1
    res1 = client.post(f"/api/v1/datasets/{dataset_id}/metrics/generate", headers=admin_headers)
    count1 = res1.json()["data"]["metrics_generated"]

    # Run 2
    res2 = client.post(f"/api/v1/datasets/{dataset_id}/metrics/generate", headers=admin_headers)
    count2 = res2.json()["data"]["metrics_generated"]

    assert count1 == count2 == 15

    # Check database record count
    list_res = client.get(f"/api/v1/datasets/{dataset_id}/metrics", headers=admin_headers)
    assert len(list_res.json()["data"]) == 15


def test_dataset_readiness_validation(client, admin_headers):
    """Test attempting to generate KPIs on a non-READY dataset returns 400 Bad Request."""
    # Upload invalid empty CSV which becomes FAILED
    files = {
        "file": ("empty_metrics.csv", io.BytesIO(b""), "text/csv"),
    }
    upload_res = client.post("/api/v1/datasets/upload", headers=admin_headers, files=files)
    failed_id = upload_res.json()["detail"]["dataset_id"]

    response = client.post(f"/api/v1/datasets/{failed_id}/metrics/generate", headers=admin_headers)
    assert response.status_code == 400
    assert "must be in READY status" in response.json()["detail"]


def test_division_by_zero_safety(client, admin_headers):
    """Test zero denominators in ratios return 0.0 safely without errors."""
    csv_zero_cust = (
        "Revenue Amount,Order Status\n"
        "100.0,pending\n"
        "200.0,pending\n"
    ).encode("utf-8")

    files = {
        "file": ("zero_cust.csv", io.BytesIO(csv_zero_cust), "text/csv"),
    }
    upload_res = client.post("/api/v1/datasets/upload", headers=admin_headers, files=files)
    dataset_id = upload_res.json()["data"]["dataset_id"]

    # Map only revenue
    client.post(
        f"/api/v1/datasets/{dataset_id}/mapping",
        headers=admin_headers,
        json={"mappings": {"Revenue Amount": "revenue"}},
    )

    gen_res = client.post(f"/api/v1/datasets/{dataset_id}/metrics/generate", headers=admin_headers)
    assert gen_res.status_code == 200
    summary_res = client.get(f"/api/v1/datasets/{dataset_id}/metrics/summary", headers=admin_headers)
    summary = summary_res.json()["data"]
    assert summary["revenue"]["total_revenue"] == 300.0

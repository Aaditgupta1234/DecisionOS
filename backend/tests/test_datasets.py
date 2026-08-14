"""Unit and integration tests for dataset upload, validation, preview, and schema mapping endpoints."""

import io
from app.core.constants import DatasetStatus


def test_dataset_upload_success_admin(client, admin_headers, sample_csv_content):
    """Test Admin can upload a valid CSV dataset and receive parsed metadata."""
    files = {
        "file": ("sales_q1.csv", io.BytesIO(sample_csv_content), "text/csv"),
    }
    response = client.post("/api/v1/datasets/upload", headers=admin_headers, files=files)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["success"] is True
    data = res_data["data"]
    assert data["name"] == "Sales Q1"
    assert data["original_filename"] == "sales_q1.csv"
    assert data["status"] == DatasetStatus.READY
    assert data["record_count"] == 5
    assert data["column_count"] == 5
    assert data["version"] == 1


def test_dataset_upload_forbidden_analyst(client, analyst_headers, sample_csv_content):
    """Test Analyst users are forbidden from uploading datasets."""
    files = {
        "file": ("sales_analyst.csv", io.BytesIO(sample_csv_content), "text/csv"),
    }
    response = client.post("/api/v1/datasets/upload", headers=analyst_headers, files=files)
    assert response.status_code == 403


def test_dataset_upload_invalid_extension(client, admin_headers):
    """Test uploading non-CSV files is rejected."""
    files = {
        "file": ("report.txt", io.BytesIO(b"Some plain text report"), "text/plain"),
    }
    response = client.post("/api/v1/datasets/upload", headers=admin_headers, files=files)
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert any(err["type"] == "INVALID_FILE_TYPE" for err in detail["errors"])


def test_dataset_upload_empty_csv(client, admin_headers):
    """Test uploading an empty CSV is rejected with structured errors."""
    files = {
        "file": ("empty.csv", io.BytesIO(b""), "text/csv"),
    }
    response = client.post("/api/v1/datasets/upload", headers=admin_headers, files=files)
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert any(err["type"] in ["EMPTY_FILE", "EMPTY_DATASET"] for err in detail["errors"])


def test_dataset_upload_duplicate_columns(client, admin_headers):
    """Test uploading CSV with duplicate header names is rejected."""
    duplicate_csv = (
        "CustomerID,Revenue,Revenue\n"
        "C001,100,100\n"
    ).encode("utf-8")
    files = {
        "file": ("duplicates.csv", io.BytesIO(duplicate_csv), "text/csv"),
    }
    response = client.post("/api/v1/datasets/upload", headers=admin_headers, files=files)
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert any(err["type"] == "DUPLICATE_COLUMNS" for err in detail["errors"])


def test_list_datasets_role_scoping(client, admin_headers, analyst_headers, sample_csv_content):
    """Test that Analysts can view READY datasets uploaded by Admins."""
    # Upload via Admin
    files = {
        "file": ("company_sales.csv", io.BytesIO(sample_csv_content), "text/csv"),
    }
    client.post("/api/v1/datasets/upload", headers=admin_headers, files=files)

    # Admin lists datasets
    admin_list = client.get("/api/v1/datasets", headers=admin_headers)
    assert admin_list.status_code == 200
    assert len(admin_list.json()["data"]) >= 1

    # Analyst lists datasets
    analyst_list = client.get("/api/v1/datasets", headers=analyst_headers)
    assert analyst_list.status_code == 200
    assert len(analyst_list.json()["data"]) >= 1
    assert analyst_list.json()["data"][0]["status"] == DatasetStatus.READY


def test_get_dataset_detail_and_preview(client, admin_headers, sample_csv_content):
    """Test retrieving full dataset details and cached preview JSON rows."""
    files = {
        "file": ("preview_test.csv", io.BytesIO(sample_csv_content), "text/csv"),
    }
    upload_res = client.post("/api/v1/datasets/upload", headers=admin_headers, files=files)
    dataset_id = upload_res.json()["data"]["dataset_id"]

    # 1. Fetch details
    detail_res = client.get(f"/api/v1/datasets/{dataset_id}", headers=admin_headers)
    assert detail_res.status_code == 200
    detail_data = detail_res.json()["data"]
    assert len(detail_data["columns"]) == 5
    col_names = [c["original_name"] for c in detail_data["columns"]]
    assert "CustomerID" in col_names
    assert "Revenue Amount" in col_names

    # 2. Fetch preview
    preview_res = client.get(f"/api/v1/datasets/{dataset_id}/preview", headers=admin_headers)
    assert preview_res.status_code == 200
    preview_data = preview_res.json()["data"]
    assert preview_data["preview_records"] == 5
    assert len(preview_data["rows"]) == 5
    assert preview_data["rows"][0]["CustomerID"] == "C001"


def test_mapping_suggestions_and_confirmation(client, admin_headers, sample_csv_content):
    """Test generating mapping suggestions and confirming field mappings."""
    files = {
        "file": ("mapping_test.csv", io.BytesIO(sample_csv_content), "text/csv"),
    }
    upload_res = client.post("/api/v1/datasets/upload", headers=admin_headers, files=files)
    dataset_id = upload_res.json()["data"]["dataset_id"]

    # 1. Fetch suggestions
    sug_res = client.get(f"/api/v1/datasets/{dataset_id}/mapping-suggestions", headers=admin_headers)
    assert sug_res.status_code == 200
    suggestions = sug_res.json()["data"]
    assert len(suggestions) == 5

    sug_dict = {s["original_column"]: s for s in suggestions}
    assert sug_dict["CustomerID"]["suggested_field"] == "customer_id"
    assert sug_dict["CustomerID"]["confidence"] >= 0.9
    assert sug_dict["Revenue Amount"]["suggested_field"] == "revenue"
    assert sug_dict["Revenue Amount"]["confidence"] >= 0.9

    # 2. Confirm custom mapping
    confirm_payload = {
        "mappings": {
            "CustomerID": "customer_id",
            "Order Date": "order_date",
            "Revenue Amount": "revenue",
            "Order Status": "status",
            "Product Category": "product_category",
        }
    }
    map_res = client.post(
        f"/api/v1/datasets/{dataset_id}/mapping",
        headers=admin_headers,
        json=confirm_payload,
    )
    assert map_res.status_code == 200
    mapped_columns = map_res.json()["data"]["mapped_columns"]
    for col in mapped_columns:
        assert col["mapped_field"] is not None
        assert col["mapping_confidence"] >= 0.9


def test_soft_delete_dataset(client, admin_headers, analyst_headers, sample_csv_content):
    """Test soft delete hides dataset from listings while preserving records."""
    files = {
        "file": ("to_delete.csv", io.BytesIO(sample_csv_content), "text/csv"),
    }
    upload_res = client.post("/api/v1/datasets/upload", headers=admin_headers, files=files)
    dataset_id = upload_res.json()["data"]["dataset_id"]

    # Delete as Admin
    del_res = client.delete(f"/api/v1/datasets/{dataset_id}", headers=admin_headers)
    assert del_res.status_code == 200
    assert del_res.json()["data"]["deleted"] is True

    # List datasets - should not appear
    list_res = client.get("/api/v1/datasets", headers=admin_headers)
    active_ids = [d["id"] for d in list_res.json()["data"]]
    assert dataset_id not in active_ids

    # Direct retrieval - should return 404
    get_res = client.get(f"/api/v1/datasets/{dataset_id}", headers=admin_headers)
    assert get_res.status_code == 404

"""Unit and integration tests for CustomerDiagnosticAnalyzer."""

import os
import tempfile
import uuid
import pandas as pd
import pytest

from app.core.config import settings
from app.core.constants import FindingCategory, FindingSeverity, FindingSubtype, FindingType, MetricCategory
from app.diagnostics.customer_analyzer import CustomerDiagnosticAnalyzer
from app.diagnostics.metric_keys import MetricKeys
from app.models.dataset import Dataset
from app.models.dataset_column import DatasetColumn
from app.models.dataset_metric import DatasetMetric
from app.models.metric_definition import MetricDefinition


def create_temp_csv(df: pd.DataFrame) -> str:
    """Helper writing a DataFrame to a temporary CSV file."""
    tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
    df.to_csv(tmp.name, index=False)
    tmp.close()
    return tmp.name


@pytest.fixture
def test_dataset(db_session, admin_user):
    """Creates a basic test dataset."""
    dataset = Dataset(
        name="Customer Test Dataset",
        original_filename="customer_test.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_cust.csv",
        file_path="/tmp/non_existent.csv",
        file_size=1024,
        uploaded_by=admin_user.id,
    )
    db_session.add(dataset)
    db_session.commit()
    db_session.refresh(dataset)
    return dataset


@pytest.mark.anyio
async def test_customer_churn_metric_detection(db_session, test_dataset):
    """Test Tier 1: Detection of elevated customer churn from pre-calculated DatasetMetric."""
    analyzer = CustomerDiagnosticAnalyzer()

    # Query or create MetricDefinition for churn_rate
    m_def = db_session.query(MetricDefinition).filter(
        MetricDefinition.metric_key == MetricKeys.CHURN_RATE
    ).first()

    if not m_def:
        m_def = MetricDefinition(
            name="Churn Rate",
            metric_key=MetricKeys.CHURN_RATE,
            metric_category=MetricCategory.CUSTOMERS,
            required_field="customer_id",
        )
        db_session.add(m_def)
        db_session.commit()

    # 25.0% churn rate (exceeds 10% alert threshold -> HIGH severity)
    churn_metric = DatasetMetric(
        dataset_id=test_dataset.id,
        metric_definition_id=m_def.id,
        metric_key=MetricKeys.CHURN_RATE,
        metric_name="Churn Rate (%)",
        metric_category=MetricCategory.CUSTOMERS,
        metric_value=25.0,
        calculated_at=pd.Timestamp.now(tz="UTC"),
    )

    findings = await analyzer.analyze(test_dataset, [churn_metric])
    assert len(findings) == 1
    assert findings[0].supporting_data["subtype"] == FindingSubtype.CHURN_INCREASE.value
    assert findings[0].severity in (FindingSeverity.HIGH, FindingSeverity.CRITICAL)
    assert "Churn Rate (25.0%)" in findings[0].title
    assert findings[0].supporting_data["category"] == FindingCategory.CUSTOMER.value


@pytest.mark.anyio
async def test_customer_retention_weakness_from_dataframe(db_session, test_dataset):
    """Test Tier 2: Detection of low repeat purchase rate from raw transaction cohort data."""
    analyzer = CustomerDiagnosticAnalyzer()

    # 100 transactions from 90 unique customers (only 10 repeat customers -> 11.1% repeat rate < 25%)
    customers = [f"CUST_{i}" for i in range(1, 91)]
    repeats = [f"CUST_{i}" for i in range(1, 11)]
    all_custs = customers + repeats

    df = pd.DataFrame({
        "customer_id": all_custs,
        "order_date": ["2026-01-15"] * len(all_custs),
    })
    csv_path = create_temp_csv(df)
    test_dataset.file_path = csv_path
    test_dataset.columns = [
        DatasetColumn(dataset_id=test_dataset.id, original_name="customer_id", mapped_field="customer_id"),
        DatasetColumn(dataset_id=test_dataset.id, original_name="order_date", mapped_field="order_date"),
    ]

    try:
        findings = await analyzer.analyze(test_dataset, [])
        retention_findings = [f for f in findings if f.supporting_data.get("subtype") == FindingSubtype.RETENTION_PROBLEM.value]

        assert len(retention_findings) == 1
        finding = retention_findings[0]
        assert finding.severity in (FindingSeverity.MEDIUM, FindingSeverity.HIGH, FindingSeverity.CRITICAL)
        assert "Low Customer Retention Rate" in finding.title
        assert finding.supporting_data["observed"] < 25.0
        assert finding.supporting_data["context"]["total_unique_customers"] == 90
    finally:
        if os.path.exists(csv_path):
            os.remove(csv_path)


@pytest.mark.anyio
async def test_customer_acquisition_slowdown_and_surge(db_session, test_dataset):
    """Test time-series detection of acquisition surge vs slowdown."""
    analyzer = CustomerDiagnosticAnalyzer()

    # Jan: 10 new customers, Feb: 50 new customers (+400% surge)
    cust_jan = [f"JAN_CUST_{i}" for i in range(10)]
    cust_feb = [f"FEB_CUST_{i}" for i in range(50)]

    df = pd.DataFrame({
        "customer_id": cust_jan + cust_feb,
        "order_date": ["2026-01-15"] * 10 + ["2026-02-15"] * 50,
    })
    csv_path = create_temp_csv(df)
    test_dataset.file_path = csv_path
    test_dataset.columns = [
        DatasetColumn(dataset_id=test_dataset.id, original_name="customer_id", mapped_field="customer_id"),
        DatasetColumn(dataset_id=test_dataset.id, original_name="order_date", mapped_field="order_date"),
    ]

    try:
        findings = await analyzer.analyze(test_dataset, [])
        surge_findings = [f for f in findings if f.supporting_data.get("subtype") == FindingSubtype.ACQUISITION_ACCELERATION.value]

        assert len(surge_findings) == 1
        assert surge_findings[0].severity == FindingSeverity.LOW
        assert "Customer Acquisition Surge" in surge_findings[0].title
    finally:
        if os.path.exists(csv_path):
            os.remove(csv_path)

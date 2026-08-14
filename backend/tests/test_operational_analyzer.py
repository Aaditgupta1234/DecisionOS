"""Unit and integration tests for OperationalDiagnosticAnalyzer."""

import os
import tempfile
import uuid
import pandas as pd
import pytest

from app.core.config import settings
from app.core.constants import FindingCategory, FindingSeverity, FindingSubtype, FindingType, MetricCategory
from app.diagnostics.metric_keys import MetricKeys
from app.diagnostics.operational_analyzer import OperationalDiagnosticAnalyzer
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
def ops_dataset(db_session, admin_user):
    """Creates a basic operational test dataset."""
    dataset = Dataset(
        name="Operational Test Dataset",
        original_filename="ops_test.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_ops.csv",
        file_path="/tmp/non_existent.csv",
        file_size=1024,
        uploaded_by=admin_user.id,
    )
    db_session.add(dataset)
    db_session.commit()
    db_session.refresh(dataset)
    return dataset


@pytest.mark.anyio
async def test_operational_delivery_delay_and_high_cancellation_metrics(db_session, ops_dataset):
    """Test Tier 1: Delivery delays and excessive cancellation rates detected from DatasetMetrics."""
    analyzer = OperationalDiagnosticAnalyzer()

    # Query or create metric definitions
    def1 = db_session.query(MetricDefinition).filter(MetricDefinition.metric_key == MetricKeys.AVERAGE_DELIVERY_TIME).first()
    if not def1:
        def1 = MetricDefinition(name="Delivery Time", metric_key=MetricKeys.AVERAGE_DELIVERY_TIME, metric_category=MetricCategory.DELIVERY, required_field="delivery_time")
        db_session.add(def1)

    def2 = db_session.query(MetricDefinition).filter(MetricDefinition.metric_key == MetricKeys.COMPLETION_RATE).first()
    if not def2:
        def2 = MetricDefinition(name="Completion Rate", metric_key=MetricKeys.COMPLETION_RATE, metric_category=MetricCategory.ORDERS, required_field="order_id")
        db_session.add(def2)

    db_session.commit()

    now = pd.Timestamp.now(tz="UTC")
    # 7.2 days delivery (> 5.0 days) and 78% completion rate (= 22% cancellation rate > 15%)
    m1 = DatasetMetric(dataset_id=ops_dataset.id, metric_definition_id=def1.id, metric_key=MetricKeys.AVERAGE_DELIVERY_TIME, metric_name="Avg Delivery", metric_category=MetricCategory.DELIVERY, metric_value=7.2, calculated_at=now)
    m2 = DatasetMetric(dataset_id=ops_dataset.id, metric_definition_id=def2.id, metric_key=MetricKeys.COMPLETION_RATE, metric_name="Completion %", metric_category=MetricCategory.ORDERS, metric_value=78.0, calculated_at=now)

    findings = await analyzer.analyze(ops_dataset, [m1, m2])

    # Both delay and cancellation inefficiency emitted concurrently
    assert len(findings) == 2
    types = {f.finding_type for f in findings}
    assert FindingType.DELIVERY_DELAY in types
    assert FindingType.HIGH_CANCELLATION_RATE in types

    delay_f = next(f for f in findings if f.finding_type == FindingType.DELIVERY_DELAY)
    canc_f = next(f for f in findings if f.finding_type == FindingType.HIGH_CANCELLATION_RATE)

    assert delay_f.severity in (FindingSeverity.HIGH, FindingSeverity.CRITICAL)
    assert canc_f.severity in (FindingSeverity.MEDIUM, FindingSeverity.HIGH)
    assert delay_f.supporting_data["category"] == FindingCategory.OPERATIONAL.value
    assert canc_f.supporting_data["category"] == FindingCategory.OPERATIONAL.value


@pytest.mark.anyio
async def test_operational_cost_spike_and_margin_compression(db_session, ops_dataset):
    """Test Tier 2: Time-series cost spikes and gross margin compression from DataFrame."""
    analyzer = OperationalDiagnosticAnalyzer()

    # Jan: Revenue $20,000, Cost $5,000 (Margin 75%)
    # Feb: Revenue $20,000, Cost $19,500 (+290% cost spike -> Margin 2.5% < 5%)
    df = pd.DataFrame({
        "order_date": ["2026-01-10", "2026-01-20", "2026-02-10", "2026-02-20"],
        "revenue": [10000.0, 10000.0, 10000.0, 10000.0],
        "cost": [2500.0, 2500.0, 9750.0, 9750.0],
    })
    csv_path = create_temp_csv(df)
    ops_dataset.file_path = csv_path
    ops_dataset.columns = [
        DatasetColumn(dataset_id=ops_dataset.id, original_name="order_date", mapped_field="order_date"),
        DatasetColumn(dataset_id=ops_dataset.id, original_name="revenue", mapped_field="revenue"),
        DatasetColumn(dataset_id=ops_dataset.id, original_name="cost", mapped_field="cost"),
    ]

    try:
        findings = await analyzer.analyze(ops_dataset, [])
        subtypes = {f.supporting_data.get("subtype") for f in findings}

        # Both COST_SPIKE and MARGIN_COMPRESSION should be emitted concurrently
        assert FindingSubtype.COST_SPIKE.value in subtypes
        assert FindingSubtype.MARGIN_COMPRESSION.value in subtypes
    finally:
        if os.path.exists(csv_path):
            os.remove(csv_path)


@pytest.mark.anyio
async def test_operational_productivity_improvement(db_session, ops_dataset):
    """Test positive productivity finding when fulfillment completion is >= 95% and delivery <= 3.0 days."""
    analyzer = OperationalDiagnosticAnalyzer()

    def1 = db_session.query(MetricDefinition).filter(MetricDefinition.metric_key == MetricKeys.AVERAGE_DELIVERY_TIME).first()
    if not def1:
        def1 = MetricDefinition(name="Delivery Time", metric_key=MetricKeys.AVERAGE_DELIVERY_TIME, metric_category=MetricCategory.DELIVERY, required_field="delivery_time")
        db_session.add(def1)

    def2 = db_session.query(MetricDefinition).filter(MetricDefinition.metric_key == MetricKeys.COMPLETION_RATE).first()
    if not def2:
        def2 = MetricDefinition(name="Completion Rate", metric_key=MetricKeys.COMPLETION_RATE, metric_category=MetricCategory.ORDERS, required_field="order_id")
        db_session.add(def2)

    db_session.commit()

    now = pd.Timestamp.now(tz="UTC")
    m1 = DatasetMetric(dataset_id=ops_dataset.id, metric_definition_id=def1.id, metric_key=MetricKeys.AVERAGE_DELIVERY_TIME, metric_name="Avg Delivery", metric_category=MetricCategory.DELIVERY, metric_value=2.1, calculated_at=now)
    m2 = DatasetMetric(dataset_id=ops_dataset.id, metric_definition_id=def2.id, metric_key=MetricKeys.COMPLETION_RATE, metric_name="Completion %", metric_category=MetricCategory.ORDERS, metric_value=98.5, calculated_at=now)

    findings = await analyzer.analyze(ops_dataset, [m1, m2])
    assert len(findings) == 1
    assert findings[0].supporting_data["subtype"] == FindingSubtype.PRODUCTIVITY_IMPROVEMENT.value
    assert findings[0].severity == FindingSeverity.LOW
    assert "High Fulfillment Productivity" in findings[0].title

"""Unit and integration tests for RevenueDiagnosticAnalyzer."""

import os
import tempfile
import uuid
import pandas as pd
import pytest

from app.core.config import settings
from app.core.constants import FindingCategory, FindingSeverity, FindingSubtype, FindingType, MetricCategory
from app.diagnostics.metric_keys import MetricKeys
from app.diagnostics.revenue_analyzer import RevenueDiagnosticAnalyzer
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
def clean_dataset(db_session, admin_user):
    """Creates a basic test dataset."""
    dataset = Dataset(
        name="Revenue Test Dataset",
        original_filename="revenue_test.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_rev.csv",
        file_path="/tmp/non_existent.csv",
        file_size=1024,
        uploaded_by=admin_user.id,
    )
    db_session.add(dataset)
    db_session.commit()
    db_session.refresh(dataset)
    return dataset


@pytest.mark.anyio
async def test_revenue_analyzer_metrics_first_fallback(db_session, clean_dataset):
    """Test Tier 1: Analyzer evaluates summary metrics when raw DataFrame is unavailable."""
    analyzer = RevenueDiagnosticAnalyzer()

    # Query existing MetricDefinition from seeded definitions or create if missing
    m_def = db_session.query(MetricDefinition).filter(
        MetricDefinition.metric_key == MetricKeys.TOTAL_REVENUE
    ).first()

    if not m_def:
        m_def = MetricDefinition(
            name="Total Revenue",
            metric_key=MetricKeys.TOTAL_REVENUE,
            metric_category=MetricCategory.REVENUE,
            required_field="revenue",
        )
        db_session.add(m_def)
        db_session.commit()

    # 1. Zero revenue metric
    zero_metric = DatasetMetric(
        dataset_id=clean_dataset.id,
        metric_definition_id=m_def.id,
        metric_key=MetricKeys.TOTAL_REVENUE,
        metric_name="Total Revenue",
        metric_category=MetricCategory.REVENUE,
        metric_value=0.0,
        calculated_at=pd.Timestamp.now(tz="UTC"),
    )

    findings = await analyzer.analyze(clean_dataset, [zero_metric])
    assert len(findings) == 1
    assert findings[0].finding_type == FindingType.REVENUE_DROP
    assert findings[0].severity == FindingSeverity.CRITICAL
    assert findings[0].supporting_data["category"] == FindingCategory.REVENUE.value
    assert findings[0].supporting_data["subtype"] == FindingSubtype.DECLINE.value


@pytest.mark.anyio
async def test_revenue_decline_and_sustained_drop(db_session, clean_dataset):
    """Test Tier 2: Detection of significant period-over-period revenue drop and multi-period decline."""
    analyzer = RevenueDiagnosticAnalyzer()

    # Create 3-month dataset with sharp drop in Month 3
    df = pd.DataFrame({
        "order_date": [
            "2026-01-10", "2026-01-20",
            "2026-02-10", "2026-02-20",
            "2026-03-10", "2026-03-20",
        ],
        "revenue": [
            5000.0, 5000.0,   # Jan: $10,000
            4500.0, 4500.0,   # Feb: $9,000 (-10%)
            2500.0, 2500.0,   # Mar: $5,000 (-44.4% drop -> HIGH / CRITICAL)
        ],
    })
    csv_path = create_temp_csv(df)
    clean_dataset.file_path = csv_path

    col1 = DatasetColumn(dataset_id=clean_dataset.id, original_name="order_date", mapped_field="order_date")
    col2 = DatasetColumn(dataset_id=clean_dataset.id, original_name="revenue", mapped_field="revenue")
    clean_dataset.columns = [col1, col2]

    try:
        findings = await analyzer.analyze(clean_dataset, [])
        decline_findings = [f for f in findings if f.supporting_data.get("subtype") == FindingSubtype.DECLINE.value]

        assert len(decline_findings) == 1
        finding = decline_findings[0]
        assert finding.severity in (FindingSeverity.HIGH, FindingSeverity.CRITICAL)
        assert "Sustained Revenue Decline" in finding.title or "Significant Revenue Decline" in finding.title
        assert finding.supporting_data["observed"] < 0
        assert finding.supporting_data["context"]["current_period_value"] == 5000.0
        assert finding.supporting_data["context"]["previous_period_value"] == 9000.0
    finally:
        if os.path.exists(csv_path):
            os.remove(csv_path)


@pytest.mark.anyio
async def test_revenue_stagnation_detection(db_session, clean_dataset):
    """Test detection of flat/stagnant growth (< 2% growth across periods)."""
    analyzer = RevenueDiagnosticAnalyzer()

    # 4 periods with 1% growth
    df = pd.DataFrame({
        "order_date": [
            "2026-01-05", "2026-01-20",
            "2026-02-05", "2026-02-20",
            "2026-03-05", "2026-03-20",
            "2026-04-05", "2026-04-20",
        ],
        "revenue": [
            5000.0, 5000.0,   # Jan: 10,000
            5050.0, 5050.0,   # Feb: 10,100 (+1%)
            5100.0, 5100.0,   # Mar: 10,200 (+0.99%)
            5150.0, 5150.0,   # Apr: 10,300 (+0.98%)
        ],
    })
    csv_path = create_temp_csv(df)
    clean_dataset.file_path = csv_path
    clean_dataset.columns = [
        DatasetColumn(dataset_id=clean_dataset.id, original_name="order_date", mapped_field="order_date"),
        DatasetColumn(dataset_id=clean_dataset.id, original_name="revenue", mapped_field="revenue"),
    ]

    try:
        findings = await analyzer.analyze(clean_dataset, [])
        stagnation_findings = [f for f in findings if f.supporting_data.get("subtype") == FindingSubtype.STAGNATION.value]

        assert len(stagnation_findings) == 1
        f = stagnation_findings[0]
        assert f.severity == FindingSeverity.MEDIUM
        assert "Stagnation" in f.title
        assert f.supporting_data["observed"] <= 2.0
    finally:
        if os.path.exists(csv_path):
            os.remove(csv_path)


@pytest.mark.anyio
async def test_concurrent_growth_acceleration_and_volatility(db_session, clean_dataset):
    """Test analyzer emits MULTIPLE findings simultaneously (Growth Surge + High Volatility)."""
    analyzer = RevenueDiagnosticAnalyzer()

    # Extreme volatility with overall surge in latest month:
    # Jan: 1000, Feb: 8000, Mar: 2000, Apr: 9000 (+350% in Apr, but huge swings -> high CV)
    df = pd.DataFrame({
        "order_date": [
            "2026-01-15",
            "2026-02-15",
            "2026-03-15",
            "2026-04-15",
        ],
        "revenue": [
            1000.0,
            8000.0,
            2000.0,
            9000.0,
        ],
    })
    csv_path = create_temp_csv(df)
    clean_dataset.file_path = csv_path
    clean_dataset.columns = [
        DatasetColumn(dataset_id=clean_dataset.id, original_name="order_date", mapped_field="order_date"),
        DatasetColumn(dataset_id=clean_dataset.id, original_name="revenue", mapped_field="revenue"),
    ]

    try:
        findings = await analyzer.analyze(clean_dataset, [])
        subtypes = [f.supporting_data.get("subtype") for f in findings]

        # Both GROWTH_ACCELERATION and VOLATILITY should be emitted simultaneously!
        assert FindingSubtype.GROWTH_ACCELERATION.value in subtypes
        assert FindingSubtype.VOLATILITY.value in subtypes

        accel_f = next(f for f in findings if f.supporting_data.get("subtype") == FindingSubtype.GROWTH_ACCELERATION.value)
        vol_f = next(f for f in findings if f.supporting_data.get("subtype") == FindingSubtype.VOLATILITY.value)

        assert accel_f.severity == FindingSeverity.LOW  # Positive opportunity
        assert vol_f.severity in (FindingSeverity.HIGH, FindingSeverity.CRITICAL)  # Risk factor
    finally:
        if os.path.exists(csv_path):
            os.remove(csv_path)


@pytest.mark.anyio
async def test_revenue_analyzer_negative_case_steady_growth(db_session, clean_dataset):
    """Test negative case: Healthy, balanced growth produces zero anomaly findings."""
    analyzer = RevenueDiagnosticAnalyzer()

    # 4 periods of steady 8% growth (well above 2% stagnation, below 15% decline/20% surge, low CV)
    df = pd.DataFrame({
        "order_date": ["2026-01-15", "2026-02-15", "2026-03-15", "2026-04-15"],
        "revenue": [10000.0, 10800.0, 11664.0, 12597.0],
    })
    csv_path = create_temp_csv(df)
    clean_dataset.file_path = csv_path
    clean_dataset.columns = [
        DatasetColumn(dataset_id=clean_dataset.id, original_name="order_date", mapped_field="order_date"),
        DatasetColumn(dataset_id=clean_dataset.id, original_name="revenue", mapped_field="revenue"),
    ]

    try:
        findings = await analyzer.analyze(clean_dataset, [])
        assert len(findings) == 0
    finally:
        if os.path.exists(csv_path):
            os.remove(csv_path)

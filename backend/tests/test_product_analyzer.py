"""Unit and integration tests for ProductDiagnosticAnalyzer."""

import os
import tempfile
import uuid
import pandas as pd
import pytest

from app.core.config import settings
from app.core.constants import FindingCategory, FindingSeverity, FindingSubtype, FindingType, MetricCategory
from app.diagnostics.metric_keys import MetricKeys
from app.diagnostics.product_analyzer import ProductDiagnosticAnalyzer
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
def product_dataset(db_session, admin_user):
    """Creates a basic product test dataset."""
    dataset = Dataset(
        name="Product Test Dataset",
        original_filename="product_test.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_prod.csv",
        file_path="/tmp/non_existent.csv",
        file_size=1024,
        uploaded_by=admin_user.id,
    )
    db_session.add(dataset)
    db_session.commit()
    db_session.refresh(dataset)
    return dataset


@pytest.mark.anyio
async def test_product_concentration_risk_detection(db_session, product_dataset):
    """Test Tier 2: Detection of severe product concentration risk (single category > 50% revenue)."""
    analyzer = ProductDiagnosticAnalyzer()

    # Total revenue $100,000; Electronics generates $80,000 (80% concentration -> CRITICAL/HIGH)
    df = pd.DataFrame({
        "product_category": ["Electronics"] * 8 + ["Home"] * 1 + ["Apparel"] * 1,
        "revenue": [10000.0] * 8 + [10000.0] * 1 + [10000.0] * 1,
    })
    csv_path = create_temp_csv(df)
    product_dataset.file_path = csv_path
    product_dataset.columns = [
        DatasetColumn(dataset_id=product_dataset.id, original_name="product_category", mapped_field="product_category"),
        DatasetColumn(dataset_id=product_dataset.id, original_name="revenue", mapped_field="revenue"),
    ]

    try:
        findings = await analyzer.analyze(product_dataset, [])
        conc_findings = [f for f in findings if f.supporting_data.get("subtype") == FindingSubtype.PRODUCT_CONCENTRATION_RISK.value]

        assert len(conc_findings) == 1
        finding = conc_findings[0]
        assert finding.severity in (FindingSeverity.HIGH, FindingSeverity.CRITICAL)
        assert "Concentration Risk" in finding.title
        assert finding.supporting_data["observed"] == 80.0
        assert finding.supporting_data["context"]["top_entity"] == "Electronics"
        assert finding.supporting_data["category"] == FindingCategory.PRODUCT.value
    finally:
        if os.path.exists(csv_path):
            os.remove(csv_path)


@pytest.mark.anyio
async def test_product_growth_and_decline_time_series(db_session, product_dataset):
    """Test category time-series dynamics detecting both breakout growth and sharp decline."""
    analyzer = ProductDiagnosticAnalyzer()

    # Jan-Feb: Electronics: $1,000 ($200x5), Home: $5,000 ($1000x5)
    # Mar-Apr: Electronics: $4,000 ($800x5) (+300% surge), Home: $2,000 ($400x5) (-60% decline)
    df = pd.DataFrame({
        "product_category": (
            ["Electronics"] * 5 + ["Home"] * 5 +
            ["Electronics"] * 5 + ["Home"] * 5
        ),
        "revenue": (
            [200.0] * 5 + [1000.0] * 5 +
            [800.0] * 5 + [400.0] * 5
        ),
        "order_date": (
            ["2026-01-10", "2026-01-15", "2026-01-20", "2026-01-25", "2026-02-01"] +
            ["2026-01-10", "2026-01-15", "2026-01-20", "2026-01-25", "2026-02-01"] +
            ["2026-03-10", "2026-03-15", "2026-03-20", "2026-03-25", "2026-04-01"] +
            ["2026-03-10", "2026-03-15", "2026-03-20", "2026-03-25", "2026-04-01"]
        ),
    })
    csv_path = create_temp_csv(df)
    product_dataset.file_path = csv_path
    product_dataset.columns = [
        DatasetColumn(dataset_id=product_dataset.id, original_name="product_category", mapped_field="product_category"),
        DatasetColumn(dataset_id=product_dataset.id, original_name="revenue", mapped_field="revenue"),
        DatasetColumn(dataset_id=product_dataset.id, original_name="order_date", mapped_field="order_date"),
    ]

    try:
        findings = await analyzer.analyze(product_dataset, [])
        subtypes = {f.supporting_data.get("subtype") for f in findings}

        # Both RAPID_PRODUCT_GROWTH and PRODUCT_PERFORMANCE_DECLINE should be emitted
        assert FindingSubtype.RAPID_PRODUCT_GROWTH.value in subtypes
        assert FindingSubtype.PRODUCT_PERFORMANCE_DECLINE.value in subtypes

        surge_f = next(f for f in findings if f.supporting_data.get("subtype") == FindingSubtype.RAPID_PRODUCT_GROWTH.value)
        decline_f = next(f for f in findings if f.supporting_data.get("subtype") == FindingSubtype.PRODUCT_PERFORMANCE_DECLINE.value)

        assert surge_f.severity == FindingSeverity.LOW
        assert decline_f.severity in (FindingSeverity.HIGH, FindingSeverity.CRITICAL)
    finally:
        if os.path.exists(csv_path):
            os.remove(csv_path)


@pytest.mark.anyio
async def test_product_concentration_metrics_fallback(db_session, product_dataset):
    """Test Tier 1: Fallback product concentration evaluation from summary metric."""
    analyzer = ProductDiagnosticAnalyzer()

    m_def = db_session.query(MetricDefinition).filter(
        MetricDefinition.metric_key == MetricKeys.PRODUCT_CONCENTRATION_RATIO
    ).first()

    if not m_def:
        m_def = MetricDefinition(
            name="Product Concentration Ratio",
            metric_key=MetricKeys.PRODUCT_CONCENTRATION_RATIO,
            metric_category=MetricCategory.REVENUE,
            required_field="product_category",
        )
        db_session.add(m_def)
        db_session.commit()

    # 65% concentration ratio in metrics
    m1 = DatasetMetric(
        dataset_id=product_dataset.id,
        metric_definition_id=m_def.id,
        metric_key=MetricKeys.PRODUCT_CONCENTRATION_RATIO,
        metric_name="Product Concentration",
        metric_category=MetricCategory.REVENUE,
        metric_value=65.0,
        calculated_at=pd.Timestamp.now(tz="UTC"),
    )

    findings = await analyzer.analyze(product_dataset, [m1])
    assert len(findings) == 1
    assert findings[0].supporting_data["subtype"] == FindingSubtype.PRODUCT_CONCENTRATION_RISK.value
    assert findings[0].severity in (FindingSeverity.MEDIUM, FindingSeverity.HIGH, FindingSeverity.CRITICAL)

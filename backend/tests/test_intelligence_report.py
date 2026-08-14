"""Unit tests for IntelligenceReportBuilder."""

import uuid
from datetime import datetime, timezone
import pytest

from app.core.constants import (
    FindingSeverity,
    FindingType,
    MetricCategory,
    RecommendationPriority,
    RecommendationStatus,
    RecommendationType,
    RelationshipStrength,
    RelationshipType,
)
from app.intelligence.report_builder import IntelligenceReportBuilder
from app.models.dataset import Dataset
from app.models.dataset_metric import DatasetMetric
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.metric_definition import MetricDefinition
from app.models.recommendation import Recommendation
from app.models.root_cause_analysis import RootCauseAnalysis


def test_intelligence_report_aggregation_and_metadata():
    """Verifies complete IntelligenceReport assembly with artifact counts, versioning, and serialization."""
    dataset_id = uuid.uuid4()
    dataset = Dataset(
        id=dataset_id,
        name="Enterprise Sales Q1",
        original_filename="sales_q1.csv",
        stored_filename="sales_q1_stored.csv",
        file_path="/tmp/sales.csv",
        file_size=2048,
    )
    dataset.updated_at = datetime(2026, 8, 10, 12, 0, 0, tzinfo=timezone.utc)

    # Metrics
    metric_def = MetricDefinition(
        id=uuid.uuid4(),
        metric_key="total_revenue",
        name="Total Revenue",
        metric_category=MetricCategory.REVENUE,
    )
    metric = DatasetMetric(
        id=uuid.uuid4(),
        dataset_id=dataset_id,
        metric_definition_id=metric_def.id,
        metric_definition=metric_def,
        metric_key="total_revenue",
        metric_name="Total Revenue",
        metric_category=MetricCategory.REVENUE,
        metric_value={
            "current": 125000.0,
            "previous": 150000.0,
            "change_percentage": -16.67,
            "trend": "down",
        },
    )

    # Findings
    f_rev = DiagnosticFinding(
        id=uuid.uuid4(),
        dataset_id=dataset_id,
        finding_type=FindingType.REVENUE_DROP,
        severity=FindingSeverity.CRITICAL,
        title="Revenue Contraction",
        description="Significant drop in revenue.",
        business_impact="Reduces gross operating profit.",
        confidence_score=0.95,
    )

    # RCA
    f_churn = DiagnosticFinding(
        id=uuid.uuid4(),
        dataset_id=dataset_id,
        finding_type=FindingType.CUSTOMER_CONCENTRATION,
        severity=FindingSeverity.HIGH,
        title="Customer Churn",
        description="High churn rate.",
        business_impact="Reduces subscriber retention rate.",
        confidence_score=0.90,
    )
    rca = RootCauseAnalysis(
        id=uuid.uuid4(),
        dataset_id=dataset_id,
        primary_finding_id=f_rev.id,
        root_cause_finding_id=f_churn.id,
        relationship_type=RelationshipType.CAUSES,
        relationship_strength=RelationshipStrength.VERY_STRONG,
        confidence_score=0.88,
        impact_score=0.92,
        explanation="Churn caused drop.",
    )
    rca.primary_finding = f_rev
    rca.root_cause_finding = f_churn

    # Recommendations
    rec = Recommendation(
        id=uuid.uuid4(),
        dataset_id=dataset_id,
        finding_id=f_rev.id,
        recommendation_type=RecommendationType.CUSTOMER_RETENTION,
        priority=RecommendationPriority.CRITICAL,
        status=RecommendationStatus.PENDING,
        title="Launch Retention Program",
        description="...",
        why_recommended="...",
        confidence_score=0.90,
        estimated_impact_score=0.85,
        estimated_effort_score=0.50,
    )

    report = IntelligenceReportBuilder.build(
        dataset=dataset,
        metrics=[metric],
        findings=[f_rev, f_churn],
        root_causes=[rca],
        recommendations=[rec],
    )

    # Metadata Assertions
    assert report.report_version == "1.0"
    assert report.dataset_id == dataset_id
    assert report.dataset_name == "Enterprise Sales Q1"
    assert report.dataset_last_updated_at == dataset.updated_at

    # Artifact Counts
    assert report.artifact_counts["metrics"] == 1
    assert report.artifact_counts["findings"] == 2
    assert report.artifact_counts["root_causes"] == 1
    assert report.artifact_counts["recommendations"] == 1

    # Executive Summary Included
    assert report.executive_summary is not None
    assert report.executive_summary.primary_issue == "Revenue Contraction"

    # Serialization Check
    report_dict = report.to_dict()
    assert report_dict["report_version"] == "1.0"
    assert report_dict["dataset_id"] == str(dataset_id)
    assert len(report_dict["metrics"]) == 1
    assert len(report_dict["findings"]) == 2
    assert len(report_dict["root_causes"]) == 1
    assert len(report_dict["recommendations"]) == 1
    assert report_dict["executive_summary"]["primary_issue"] == "Revenue Contraction"

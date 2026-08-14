"""IntelligenceReportBuilder compiling unified multi-domain business intelligence reports."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.intelligence.constants import CANONICAL_REPORT_VERSION
from app.intelligence.executive_summary import ExecutiveSummaryBuilder
from app.intelligence.models import IntelligenceReport
from app.models.dataset import Dataset
from app.models.dataset_metric import DatasetMetric
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.recommendation import Recommendation
from app.models.root_cause_analysis import RootCauseAnalysis


class IntelligenceReportBuilder:
    """
    Constructs the canonical IntelligenceReport consolidating all computed
    KPI metrics, findings, root causes, recommendations, and executive summaries.
    """

    @classmethod
    def build(
        cls,
        dataset: Dataset,
        metrics: Optional[List[DatasetMetric]] = None,
        findings: Optional[List[DiagnosticFinding]] = None,
        root_causes: Optional[List[RootCauseAnalysis]] = None,
        recommendations: Optional[List[Recommendation]] = None,
    ) -> IntelligenceReport:
        """
        Compiles the full IntelligenceReport entity.
        """
        metric_list = metrics or []
        finding_list = findings or []
        rca_list = root_causes or []
        rec_list = recommendations or []

        # 1. Compute Artifact Counts
        artifact_counts: Dict[str, int] = {
            "metrics": len(metric_list),
            "findings": len(finding_list),
            "root_causes": len(rca_list),
            "recommendations": len(rec_list),
        }

        # 2. Build Executive Summary
        exec_summary = ExecutiveSummaryBuilder.build(
            dataset_id=dataset.id,
            findings=finding_list,
            root_causes=rca_list,
            recommendations=rec_list,
        )

        # 3. Serialize Metrics
        serialized_metrics: List[Dict[str, Any]] = [
            {
                "id": str(m.id),
                "metric_key": getattr(m, "metric_key", None) or (m.metric_definition.metric_key if m.metric_definition else "custom_metric"),
                "name": getattr(m, "metric_name", None) or (m.metric_definition.name if m.metric_definition else "Metric"),
                "category": (
                    m.metric_category.value if hasattr(m, "metric_category") and hasattr(m.metric_category, "value")
                    else (
                        m.metric_definition.metric_category.value
                        if m.metric_definition and hasattr(m.metric_definition, "metric_category") and hasattr(m.metric_definition.metric_category, "value")
                        else "general"
                    )
                ),
                "value": getattr(m, "metric_value", None),
            }
            for m in metric_list
        ]

        # 4. Serialize Findings
        serialized_findings: List[Dict[str, Any]] = [
            {
                "id": str(f.id),
                "title": f.title,
                "finding_type": f.finding_type.value,
                "severity": f.severity.value if hasattr(f.severity, "value") else str(f.severity),
                "confidence_score": f.confidence_score,
                "description": f.description,
                "business_impact": f.business_impact,
                "category": f.supporting_data.get("category", "GENERAL") if f.supporting_data else "GENERAL",
                "subtype": f.supporting_data.get("subtype", f.finding_type.value) if f.supporting_data else f.finding_type.value,
            }
            for f in finding_list
        ]

        # 5. Serialize Root Causes
        serialized_rcas: List[Dict[str, Any]] = [
            {
                "id": str(r.id),
                "primary_finding_id": str(r.primary_finding_id),
                "root_cause_finding_id": str(r.root_cause_finding_id),
                "relationship_type": r.relationship_type.value,
                "relationship_strength": r.relationship_strength.value,
                "confidence_score": r.confidence_score,
                "impact_score": r.impact_score,
                "explanation": r.explanation,
                "primary_finding_title": r.primary_finding.title if r.primary_finding else None,
                "root_cause_title": r.root_cause_finding.title if r.root_cause_finding else None,
            }
            for r in rca_list
        ]

        # 6. Serialize Recommendations
        serialized_recs: List[Dict[str, Any]] = [
            {
                "id": str(rec.id),
                "title": rec.title,
                "recommendation_type": rec.recommendation_type.value if hasattr(rec.recommendation_type, "value") else str(rec.recommendation_type),
                "priority": rec.priority.value if hasattr(rec.priority, "value") else str(rec.priority),
                "status": rec.status.value if hasattr(rec.status, "value") else str(rec.status),
                "source": rec.source.value if hasattr(rec, "source") and rec.source and hasattr(rec.source, "value") else "RULE_ENGINE",
                "confidence_score": rec.confidence_score,
                "estimated_impact_score": rec.estimated_impact_score,
                "estimated_effort_score": rec.estimated_effort_score,
                "expected_time_to_value": (
                    rec.expected_time_to_value.value
                    if hasattr(rec, "expected_time_to_value") and rec.expected_time_to_value and hasattr(rec.expected_time_to_value, "value")
                    else "SHORT_TERM"
                ),
                "action_plan": rec.action_plan or [],
                "success_metrics": rec.success_metrics or [],
                "why_recommended": rec.why_recommended or "",
                "outcomes": rec.outcomes or {},
            }
            for rec in rec_list
        ]

        return IntelligenceReport(
            report_version=CANONICAL_REPORT_VERSION,
            dataset_id=dataset.id,
            dataset_name=dataset.name,
            generated_at=datetime.now(timezone.utc),
            dataset_last_updated_at=dataset.updated_at,
            artifact_counts=artifact_counts,
            metrics=serialized_metrics,
            findings=serialized_findings,
            root_causes=serialized_rcas,
            recommendations=serialized_recs,
            executive_summary=exec_summary,
        )

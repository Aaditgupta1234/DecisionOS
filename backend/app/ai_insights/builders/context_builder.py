"""ContextBuilder converting IntelligenceReport entities into distilled LLM context."""

import json
from typing import Any, Dict, List, Union

from app.intelligence.models import IntelligenceReport
from app.schemas.intelligence import IntelligenceReportResponse


class ContextBuilder:
    """
    Transforms structured multi-domain IntelligenceReport outputs into a concise,
    information-dense context payload optimized for low LLM token overhead.
    """

    @classmethod
    def build_context(
        cls,
        report: Union[IntelligenceReport, IntelligenceReportResponse, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Extracts key analytical context without raw row-level tabular bulk.
        """
        if isinstance(report, (IntelligenceReport, IntelligenceReportResponse)):
            rep_dict = report.to_dict() if hasattr(report, "to_dict") else report.model_dump()
        elif isinstance(report, dict):
            rep_dict = report
        else:
            rep_dict = {}

        exec_summary = rep_dict.get("executive_summary") or {}

        # 1. Distill Health
        health_score = exec_summary.get("business_health_score", 100)
        health_status = exec_summary.get("business_health_status", "EXCELLENT")

        # 2. Distill Metrics
        raw_metrics = rep_dict.get("metrics") or []
        metrics_summary = [
            {
                "name": m.get("name") or m.get("metric_key"),
                "category": m.get("category"),
                "value": m.get("value") or m.get("current_value"),
                "change_percentage": m.get("change_percentage"),
                "trend": m.get("trend"),
            }
            for m in raw_metrics
        ]

        # 3. Distill Findings
        raw_findings = rep_dict.get("findings") or []
        findings_summary = [
            {
                "title": f.get("title"),
                "severity": f.get("severity"),
                "confidence": f.get("confidence_score"),
                "description": f.get("description"),
                "business_impact": f.get("business_impact"),
            }
            for f in raw_findings
        ]

        # 4. Distill Root Causes
        raw_rcas = rep_dict.get("root_causes") or []
        rcas_summary = [
            {
                "cause": r.get("root_cause_title") or r.get("explanation"),
                "effect": r.get("primary_finding_title"),
                "relationship": r.get("relationship_type"),
                "strength": r.get("relationship_strength"),
                "impact_score": r.get("impact_score"),
                "explanation": r.get("explanation"),
            }
            for r in raw_rcas
        ]

        # 5. Distill Recommendations
        raw_recs = rep_dict.get("recommendations") or []
        recs_summary = [
            {
                "title": rec.get("title"),
                "type": rec.get("recommendation_type"),
                "priority": rec.get("priority"),
                "impact": rec.get("estimated_impact_score"),
                "effort": rec.get("estimated_effort_score"),
                "time_to_value": rec.get("expected_time_to_value"),
                "action_plan": rec.get("action_plan"),
                "success_metrics": rec.get("success_metrics"),
                "outcomes": rec.get("outcomes"),
            }
            for rec in raw_recs
        ]

        return {
            "dataset_name": rep_dict.get("dataset_name", "Corporate Dataset"),
            "report_version": rep_dict.get("report_version", "1.0"),
            "business_health_score": health_score,
            "business_health_status": health_status,
            "primary_issue": exec_summary.get("primary_issue", "No critical anomalies"),
            "top_root_cause": exec_summary.get("top_root_cause"),
            "top_recommendation": exec_summary.get("top_recommendation"),
            "key_risks": exec_summary.get("key_risks", []),
            "confidence_breakdown": exec_summary.get("confidence_breakdown", {}),
            "metrics": metrics_summary,
            "findings": findings_summary,
            "root_causes": rcas_summary,
            "recommendations": recs_summary,
        }

    @classmethod
    def to_json_str(cls, context: Dict[str, Any]) -> str:
        """Converts context dictionary to formatted JSON string for prompt injection."""
        return json.dumps(context, indent=2)

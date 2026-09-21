"""IntelligenceReportBuilder compiling unified multi-domain business intelligence reports."""

from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from app.intelligence.constants import CANONICAL_REPORT_VERSION
from app.intelligence.executive_summary import ExecutiveSummaryBuilder
from app.intelligence.models import IntelligenceReport

if TYPE_CHECKING:
    from app.models.dataset import Dataset
    from app.models.dataset_metric import DatasetMetric
    from app.models.diagnostic_finding import DiagnosticFinding
    from app.models.recommendation import Recommendation
    from app.models.root_cause_analysis import RootCauseAnalysis

logger = logging.getLogger(__name__)


class IntelligenceReportBuilder:
    """
    Constructs the canonical IntelligenceReport consolidating all computed
    KPI metrics, findings, root causes, recommendations, and executive summaries.
    Ensures safe degradation when components are missing or empty.
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
        meta = getattr(dataset, "metadata_json", {}) or {}
        col_count = getattr(dataset, "column_count", None)
        if col_count is None and hasattr(dataset, "columns") and dataset.columns:
            col_count = len(dataset.columns)
        col_count = col_count if col_count is not None else 2

        is_quarantined = (
            meta.get("schema_verified") is False
            or meta.get("dataset_status") in ("UNVERIFIED_SCHEMA", "UNIVARIATE", "INVALID", "EMPTY")
            or col_count < 2
        )

        if is_quarantined:
            exec_summary = ExecutiveSummaryBuilder.build(
                dataset_id=dataset.id,
                findings=[],
                root_causes=[],
                recommendations=[],
                is_quarantined=True,
            )
            return IntelligenceReport(
                report_version=CANONICAL_REPORT_VERSION,
                dataset_id=dataset.id,
                dataset_name=getattr(dataset, "name", "Dataset") or "Dataset",
                generated_at=datetime.now(timezone.utc),
                dataset_last_updated_at=getattr(dataset, "updated_at", None) or datetime.now(timezone.utc),
                artifact_counts={"metrics": 0, "findings": 0, "root_causes": 0, "recommendations": 0},
                metrics=[],
                findings=[],
                root_causes=[],
                recommendations=[],
                executive_summary=exec_summary,
            )

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

        # 3. Serialize Metrics with safe attribute lookups
        serialized_metrics: List[Dict[str, Any]] = []
        for m in metric_list:
            try:
                metric_id = str(getattr(m, "id", "unknown"))
                metric_key = getattr(m, "metric_key", None)
                if not metric_key and getattr(m, "metric_definition", None):
                    metric_key = getattr(m.metric_definition, "metric_key", "custom_metric")
                metric_key = metric_key or "custom_metric"

                name = getattr(m, "metric_name", None)
                if not name and getattr(m, "metric_definition", None):
                    name = getattr(m.metric_definition, "name", "Metric")
                name = name or "Metric"

                category = "general"
                if hasattr(m, "metric_category") and hasattr(m.metric_category, "value"):
                    category = m.metric_category.value
                elif getattr(m, "metric_definition", None) and hasattr(m.metric_definition, "metric_category"):
                    mc = m.metric_definition.metric_category
                    category = mc.value if hasattr(mc, "value") else str(mc)

                value = getattr(m, "metric_value", None)
                serialized_metrics.append({
                    "id": metric_id,
                    "metric_key": metric_key,
                    "name": name,
                    "category": category,
                    "value": value,
                })
            except Exception as err:
                logger.warning(f"Error serializing metric: {err}")

        # 4. Serialize Findings with safe lookups
        serialized_findings: List[Dict[str, Any]] = []
        for f in finding_list:
            try:
                f_id = str(getattr(f, "id", "unknown"))
                title = getattr(f, "title", "Finding") or "Finding"
                ft = getattr(f, "finding_type", "GENERAL")
                ft_val = ft.value if hasattr(ft, "value") else str(ft or "GENERAL")
                sev = getattr(f, "severity", "LOW")
                sev_val = sev.value if hasattr(sev, "value") else str(sev or "LOW")
                conf = float(getattr(f, "confidence_score", 1.0) or 1.0)
                desc = getattr(f, "description", "") or ""
                impact = getattr(f, "business_impact", "") or ""
                supp = getattr(f, "supporting_data", {}) if isinstance(getattr(f, "supporting_data", None), dict) else {}
                cat = supp.get("category", "GENERAL") if supp else "GENERAL"
                sub = supp.get("subtype", ft_val) if supp else ft_val

                serialized_findings.append({
                    "id": f_id,
                    "title": title,
                    "finding_type": ft_val,
                    "severity": sev_val,
                    "confidence_score": conf,
                    "description": desc,
                    "business_impact": impact,
                    "category": cat,
                    "subtype": sub,
                })
            except Exception as err:
                logger.warning(f"Error serializing finding: {err}")

        # 5. Serialize Root Causes
        serialized_rcas: List[Dict[str, Any]] = []
        for r in rca_list:
            try:
                r_id = str(getattr(r, "id", "unknown"))
                pf_id = str(getattr(r, "primary_finding_id", "unknown"))
                rcf_id = str(getattr(r, "root_cause_finding_id", "unknown"))
                rel_type = getattr(r, "relationship_type", "CAUSAL")
                rel_val = rel_type.value if hasattr(rel_type, "value") else str(rel_type or "CAUSAL")
                rel_str = getattr(r, "relationship_strength", "STRONG")
                rel_str_val = rel_str.value if hasattr(rel_str, "value") else str(rel_str or "STRONG")
                conf = float(getattr(r, "confidence_score", 1.0) or 1.0)
                impact = float(getattr(r, "impact_score", 0.5) or 0.5)
                exp = getattr(r, "explanation", "") or ""
                pf_title = r.primary_finding.title if getattr(r, "primary_finding", None) else None
                rc_title = r.root_cause_finding.title if getattr(r, "root_cause_finding", None) else None

                serialized_rcas.append({
                    "id": r_id,
                    "primary_finding_id": pf_id,
                    "root_cause_finding_id": rcf_id,
                    "relationship_type": rel_val,
                    "relationship_strength": rel_str_val,
                    "confidence_score": conf,
                    "impact_score": impact,
                    "explanation": exp,
                    "primary_finding_title": pf_title,
                    "root_cause_title": rc_title,
                })
            except Exception as err:
                logger.warning(f"Error serializing RCA: {err}")

        # 6. Serialize Recommendations
        serialized_recs: List[Dict[str, Any]] = []
        for rec in rec_list:
            try:
                rec_id = str(getattr(rec, "id", "unknown"))
                title = getattr(rec, "title", "Recommendation") or "Recommendation"
                rtype = getattr(rec, "recommendation_type", "OPERATIONAL")
                rtype_val = rtype.value if hasattr(rtype, "value") else str(rtype or "OPERATIONAL")
                prio = getattr(rec, "priority", "MEDIUM")
                prio_val = prio.value if hasattr(prio, "value") else str(prio or "MEDIUM")
                stat = getattr(rec, "status", "PROPOSED")
                stat_val = stat.value if hasattr(stat, "value") else str(stat or "PROPOSED")
                src = getattr(rec, "source", "RULE_ENGINE")
                src_val = src.value if hasattr(src, "value") else str(src or "RULE_ENGINE")
                conf = float(getattr(rec, "confidence_score", 1.0) or 1.0)
                imp_score = float(getattr(rec, "estimated_impact_score", 0.5) or 0.5)
                eff_score = float(getattr(rec, "estimated_effort_score", 0.5) or 0.5)
                ttv = getattr(rec, "expected_time_to_value", "SHORT_TERM")
                ttv_val = ttv.value if hasattr(ttv, "value") else str(ttv or "SHORT_TERM")

                serialized_recs.append({
                    "id": rec_id,
                    "title": title,
                    "recommendation_type": rtype_val,
                    "priority": prio_val,
                    "status": stat_val,
                    "source": src_val,
                    "confidence_score": conf,
                    "estimated_impact_score": imp_score,
                    "estimated_effort_score": eff_score,
                    "expected_time_to_value": ttv_val,
                    "action_plan": getattr(rec, "action_plan", []) or [],
                    "success_metrics": getattr(rec, "success_metrics", []) or [],
                    "why_recommended": getattr(rec, "why_recommended", "") or "",
                    "outcomes": getattr(rec, "outcomes", {}) or {},
                })
            except Exception as err:
                logger.warning(f"Error serializing recommendation: {err}")

        return IntelligenceReport(
            report_version=CANONICAL_REPORT_VERSION,
            dataset_id=dataset.id,
            dataset_name=getattr(dataset, "name", "Dataset") or "Dataset",
            generated_at=datetime.now(timezone.utc),
            dataset_last_updated_at=getattr(dataset, "updated_at", None) or datetime.now(timezone.utc),
            artifact_counts=artifact_counts,
            metrics=serialized_metrics,
            findings=serialized_findings,
            root_causes=serialized_rcas,
            recommendations=serialized_recs,
            executive_summary=exec_summary,
        )

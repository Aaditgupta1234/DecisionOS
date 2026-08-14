"""StrategyContextBuilder extracting deterministic recommendations, available KPIs, and intelligence context."""

import json
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from app.ai_insights.schemas.ai_insight_schema import AIInsightResponse
from app.intelligence.models import IntelligenceReport
from app.models.ai_insight import AIInsight
from app.models.recommendation import Recommendation
from app.schemas.intelligence import IntelligenceReportResponse
from app.schemas.recommendation import RecommendationResponse


class StrategyContextBuilder:
    """
    Constructs a structured context payload containing approved recommendations,
    an explicit allowlist of existing DecisionOS KPIs, and supporting diagnostic telemetry.
    """

    @classmethod
    def build_context(
        cls,
        recommendations: List[Union[Recommendation, RecommendationResponse, Dict[str, Any]]],
        report: Optional[Union[IntelligenceReport, IntelligenceReportResponse, Dict[str, Any]]] = None,
        ai_insight: Optional[Union[AIInsight, AIInsightResponse, Dict[str, Any]]] = None,
        custom_objective: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Builds the unified Strategy Planner context.
        """
        # 1. Distill Recommendations (Primary Foundation & Traceability Anchors)
        recs_summary = []
        for r in recommendations:
            if isinstance(r, (Recommendation, RecommendationResponse)):
                rec_id = str(r.id)
                title = r.title
                description = r.description
                rec_type = r.recommendation_type.value if hasattr(r.recommendation_type, "value") else str(r.recommendation_type)
                priority = r.priority.value if hasattr(r.priority, "value") else str(r.priority)
                impact = float(r.estimated_impact_score) if r.estimated_impact_score is not None else 0.8
                effort = float(r.estimated_effort_score) if r.estimated_effort_score is not None else 0.5
                time_to_val = r.expected_time_to_value.value if hasattr(r.expected_time_to_value, "value") else str(r.expected_time_to_value)
                action_plan = r.action_plan or []
                success_metrics = r.success_metrics or []
                rec_status = r.status.value if hasattr(r.status, "value") else str(r.status)
                why = getattr(r, "why_recommended", "") or ""
            elif isinstance(r, dict):
                rec_id = str(r.get("id", ""))
                title = r.get("title", "")
                description = r.get("description", "")
                rec_type = str(r.get("recommendation_type", "GENERAL"))
                priority = str(r.get("priority", "HIGH"))
                impact = float(r.get("estimated_impact_score", 0.8) or 0.8)
                effort = float(r.get("estimated_effort_score", 0.5) or 0.5)
                time_to_val = str(r.get("expected_time_to_value", "SHORT_TERM"))
                action_plan = r.get("action_plan") or []
                success_metrics = r.get("success_metrics") or []
                rec_status = str(r.get("status", "PENDING"))
                why = str(r.get("why_recommended", ""))
            else:
                continue

            recs_summary.append({
                "id": rec_id,
                "title": title,
                "description": description,
                "recommendation_type": rec_type,
                "priority": priority,
                "estimated_impact_score": impact,
                "estimated_effort_score": effort,
                "expected_time_to_value": time_to_val,
                "action_plan": action_plan,
                "success_metrics": success_metrics,
                "status": rec_status,
                "why_recommended": why,
            })

        # 2. Distill Supporting Intelligence Report & KPI Allowlist
        rep_dict = {}
        if isinstance(report, (IntelligenceReport, IntelligenceReportResponse)):
            rep_dict = report.to_dict() if hasattr(report, "to_dict") else report.model_dump()
        elif isinstance(report, dict):
            rep_dict = report

        exec_summary = rep_dict.get("executive_summary") or {}
        health_score = exec_summary.get("business_health_score", 100)
        health_status = exec_summary.get("business_health_status", "EXCELLENT")

        # Explicit KPI allowlist for strict SuccessCriterion grounding
        kpis_allowlist = []
        for m in (rep_dict.get("metrics") or []):
            kpi_key = m.get("metric_key") or m.get("name") or ""
            if kpi_key:
                kpis_allowlist.append({
                    "metric_key": kpi_key,
                    "name": m.get("name") or kpi_key,
                    "category": m.get("category", "general"),
                    "current_value": m.get("current_value") or m.get("value"),
                    "trend": m.get("trend", "stable"),
                })

        findings_summary = [
            {
                "title": f.get("title"),
                "severity": f.get("severity"),
                "confidence_score": f.get("confidence_score"),
                "business_impact": f.get("business_impact"),
            }
            for f in (rep_dict.get("findings") or [])
        ]

        rcas_summary = [
            {
                "cause": r.get("root_cause_title") or r.get("explanation"),
                "effect": r.get("primary_finding_title"),
                "relationship": r.get("relationship_type"),
                "strength": r.get("relationship_strength"),
                "impact_score": r.get("impact_score"),
            }
            for r in (rep_dict.get("root_causes") or [])
        ]

        context: Dict[str, Any] = {
            "dataset_name": rep_dict.get("dataset_name", "Corporate Dataset"),
            "custom_objective": custom_objective,
            "business_health_score": health_score,
            "business_health_status": health_status,
            "primary_issue": exec_summary.get("primary_issue", "Operational Interventions"),
            "top_root_cause": exec_summary.get("top_root_cause"),
            "recommendations": recs_summary,
            "available_kpis": kpis_allowlist,
            "findings": findings_summary,
            "root_causes": rcas_summary,
        }

        # 3. Add AI Insight Enrichment (if available — graceful degradation if None)
        if ai_insight is not None:
            if isinstance(ai_insight, AIInsightResponse):
                insight_dict = ai_insight.model_dump()
            elif isinstance(ai_insight, AIInsight):
                insight_dict = {
                    "executive_narrative": ai_insight.executive_narrative,
                    "business_assessment": ai_insight.business_assessment,
                    "risk_analysis": ai_insight.risk_analysis,
                    "opportunities": ai_insight.opportunities,
                    "strategic_priorities": ai_insight.strategic_priorities,
                }
            elif isinstance(ai_insight, dict):
                insight_dict = ai_insight
            else:
                insight_dict = {}

            narrative = insight_dict.get("executive_narrative") or {}
            assessment = insight_dict.get("business_assessment") or {}
            risks = insight_dict.get("risk_analysis") or {}
            opportunities = insight_dict.get("opportunities") or {}

            context["ai_enrichment"] = {
                "headline": narrative.get("headline"),
                "executive_summary": narrative.get("executive_summary"),
                "strengths": assessment.get("strengths", []),
                "weaknesses": assessment.get("weaknesses", []),
                "top_risks": risks.get("top_risks", []),
                "growth_opportunities": opportunities.get("growth_opportunities", []),
            }

        return context

    @classmethod
    def to_json_str(cls, context: Dict[str, Any]) -> str:
        """Serializes context dictionary to JSON string."""
        return json.dumps(context, indent=2)

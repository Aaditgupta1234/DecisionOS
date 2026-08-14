"""ChatContextBuilder converting IntelligenceReport, optional AIInsight, and history into conversational context."""

import json
from typing import Any, Dict, List, Optional, Union

from app.ai_chat.constants import MAX_HISTORY_MESSAGES
from app.ai_insights.schemas.ai_insight_schema import AIInsightResponse
from app.intelligence.models import IntelligenceReport
from app.models.ai_insight import AIInsight
from app.models.chat_message import ChatMessage
from app.schemas.intelligence import IntelligenceReportResponse


class ChatContextBuilder:
    """
    Constructs a lean, information-dense context payload combining deterministic intelligence,
    optional AI narrative enrichments, and recent conversational history.
    """

    @classmethod
    def build_context(
        cls,
        report: Union[IntelligenceReport, IntelligenceReportResponse, Dict[str, Any]],
        ai_insight: Optional[Union[AIInsight, AIInsightResponse, Dict[str, Any]]] = None,
        history: Optional[List[Union[ChatMessage, Dict[str, Any]]]] = None,
    ) -> Dict[str, Any]:
        """
        Builds the unified context payload. Handles absent AIInsight cleanly.
        """
        # 1. Distill Deterministic Intelligence Report (Base Foundation)
        if isinstance(report, (IntelligenceReport, IntelligenceReportResponse)):
            rep_dict = report.to_dict() if hasattr(report, "to_dict") else report.model_dump()
        elif isinstance(report, dict):
            rep_dict = report
        else:
            rep_dict = {}

        exec_summary = rep_dict.get("executive_summary") or {}
        health_score = exec_summary.get("business_health_score", 100)
        health_status = exec_summary.get("business_health_status", "EXCELLENT")

        metrics_summary = [
            {
                "name": m.get("name") or m.get("metric_key"),
                "category": m.get("category"),
                "value": m.get("value") or m.get("current_value"),
                "change_percentage": m.get("change_percentage"),
                "trend": m.get("trend"),
            }
            for m in (rep_dict.get("metrics") or [])
        ]

        findings_summary = [
            {
                "title": f.get("title"),
                "severity": f.get("severity"),
                "confidence": f.get("confidence_score"),
                "business_impact": f.get("business_impact"),
                "description": f.get("description"),
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
                "explanation": r.get("explanation"),
            }
            for r in (rep_dict.get("root_causes") or [])
        ]

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
            }
            for rec in (rep_dict.get("recommendations") or [])
        ]

        context: Dict[str, Any] = {
            "dataset_name": rep_dict.get("dataset_name", "Corporate Dataset"),
            "report_version": rep_dict.get("report_version", "1.0"),
            "business_health_score": health_score,
            "business_health_status": health_status,
            "primary_issue": exec_summary.get("primary_issue", "No critical anomalies"),
            "top_root_cause": exec_summary.get("top_root_cause"),
            "top_recommendation": exec_summary.get("top_recommendation"),
            "key_risks": exec_summary.get("key_risks", []),
            "metrics": metrics_summary,
            "findings": findings_summary,
            "root_causes": rcas_summary,
            "recommendations": recs_summary,
        }

        # 2. Add AI Insight Enrichment (if available - graceful degradation if None)
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
                    "action_plan": ai_insight.action_plan,
                }
            elif isinstance(ai_insight, dict):
                insight_dict = ai_insight
            else:
                insight_dict = {}

            narrative = insight_dict.get("executive_narrative") or {}
            assessment = insight_dict.get("business_assessment") or {}
            risks = insight_dict.get("risk_analysis") or {}
            opportunities = insight_dict.get("opportunities") or {}
            priorities = insight_dict.get("strategic_priorities") or {}

            context["ai_enrichment"] = {
                "headline": narrative.get("headline"),
                "executive_summary": narrative.get("executive_summary"),
                "primary_issue_summary": narrative.get("primary_issue_summary"),
                "strengths": assessment.get("strengths", []),
                "weaknesses": assessment.get("weaknesses", []),
                "overall_risk_level": risks.get("overall_risk_level"),
                "top_risks": risks.get("top_risks", []),
                "growth_opportunities": opportunities.get("growth_opportunities", []),
                "immediate_priorities": priorities.get("immediate_priorities", []),
                "prioritization_rationale": priorities.get("prioritization_rationale"),
            }

        # 3. Add Recent Conversation History (last MAX_HISTORY_MESSAGES)
        history_list = []
        if history:
            # take recent messages
            recent_msgs = history[-MAX_HISTORY_MESSAGES:]
            for msg in recent_msgs:
                if isinstance(msg, ChatMessage):
                    history_list.append({
                        "role": msg.role.value if hasattr(msg.role, "value") else str(msg.role),
                        "content": msg.content,
                    })
                elif isinstance(msg, dict):
                    history_list.append({
                        "role": str(msg.get("role", "USER")),
                        "content": str(msg.get("content", "")),
                    })

        context["conversation_history"] = history_list

        return context

    @classmethod
    def to_json_str(cls, context: Dict[str, Any]) -> str:
        """Serializes context dictionary to JSON string."""
        return json.dumps(context, indent=2)

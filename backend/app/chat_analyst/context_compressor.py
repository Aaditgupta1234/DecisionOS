"""Context Compressor selecting top-relevant intelligence artifacts to minimize token load."""

from typing import Any, Dict, List
from app.chat_analyst.constants import (
    MAX_COMPRESSED_FINDINGS,
    MAX_COMPRESSED_FORECASTS,
    MAX_COMPRESSED_RECOMMENDATIONS,
    MAX_COMPRESSED_ROOT_CAUSES,
    MAX_COMPRESSED_SCENARIOS,
    QuestionType,
)


class ContextCompressor:
    """
    Compresses and prioritizes verified platform intelligence into compact,
    high-signal representations tailored for compact LLM context windows.
    """

    @classmethod
    def compress(
        cls,
        raw_bundle: Dict[str, Any],
        question_type: QuestionType,
    ) -> Dict[str, Any]:
        """
        Filters and compresses intelligence telemetry into top-ranked summaries.
        """
        dataset = raw_bundle["dataset"]
        metrics = raw_bundle.get("metrics") or []
        findings = raw_bundle.get("findings") or []
        root_causes = raw_bundle.get("root_causes") or []
        recommendations = raw_bundle.get("recommendations") or []
        forecasts = raw_bundle.get("forecasts") or []
        scenarios = raw_bundle.get("scenarios") or []
        narr_report = raw_bundle.get("narrative_report")
        insight_report = raw_bundle.get("executive_insight_report")

        # 1. Metrics summary
        metrics_summary = []
        for m in metrics[:8]:
            val = float(m.metric_value) if hasattr(m, "metric_value") and m.metric_value is not None else (
                float(m.current_value) if hasattr(m, "current_value") and m.current_value is not None else 0.0
            )
            cat = m.metric_category.value if hasattr(m, "metric_category") and hasattr(m.metric_category, "value") else str(getattr(m, "metric_category", "OPERATIONAL"))
            metrics_summary.append({
                "metric_key": m.metric_key,
                "metric_name": m.metric_name,
                "category": cat,
                "value": val,
            })

        # 2. Findings (Rank by severity and confidence)
        sev_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        sorted_findings = sorted(
            findings,
            key=lambda f: (
                sev_order.get(str(f.severity.value if hasattr(f.severity, "value") else f.severity).upper(), 0),
                float(f.confidence_score or 0.0),
            ),
            reverse=True,
        )
        compressed_findings = [
            {
                "id": str(f.id),
                "title": f.title,
                "severity": str(f.severity.value if hasattr(f.severity, "value") else f.severity).upper(),
                "impact": f.business_impact or f.description or "Operational variance.",
                "confidence": float(f.confidence_score or 0.85),
            }
            for f in sorted_findings[:MAX_COMPRESSED_FINDINGS]
        ]

        # 3. Root Causes (Rank by impact score)
        sorted_rcas = sorted(
            root_causes,
            key=lambda r: float(getattr(r, "impact_score", 0.0) or 0.0),
            reverse=True,
        )
        compressed_rcas = []
        for r in sorted_rcas[:MAX_COMPRESSED_ROOT_CAUSES]:
            cause = r.explanation or (r.root_cause_finding.title if getattr(r, "root_cause_finding", None) else "Operational Bottleneck")
            effect = (r.primary_finding.title if getattr(r, "primary_finding", None) else "Performance Contraction")
            compressed_rcas.append({
                "id": str(r.id),
                "cause": cause,
                "effect": effect,
                "strength": str(r.relationship_strength.value if hasattr(r.relationship_strength, "value") else r.relationship_strength),
                "impact_score": float(r.impact_score or 0.5),
            })

        # 4. Recommendations (Rank by priority)
        prio_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        sorted_recs = sorted(
            recommendations,
            key=lambda rec: (
                prio_order.get(str(rec.priority.value if hasattr(rec.priority, "value") else rec.priority).upper(), 0),
                float(getattr(rec, "confidence_score", 0.0) or 0.0),
            ),
            reverse=True,
        )
        compressed_recs = [
            {
                "id": str(r.id),
                "title": r.title,
                "priority": str(r.priority.value if hasattr(r.priority, "value") else r.priority).upper(),
                "rationale": getattr(r, "why_recommended", None) or getattr(r, "description", "Strategic action."),
                "confidence": float(getattr(r, "confidence_score", 0.85) or 0.85),
            }
            for r in sorted_recs[:MAX_COMPRESSED_RECOMMENDATIONS]
        ]

        # 5. Forecasts
        compressed_forecasts = []
        for fc in forecasts[:MAX_COMPRESSED_FORECASTS]:
            metrics_dict = fc.evaluation_metrics or {}
            compressed_forecasts.append({
                "id": str(fc.id),
                "metric_key": fc.metric_key,
                "model_type": fc.model_type.value if hasattr(fc.model_type, "value") else str(fc.model_type),
                "mape": metrics_dict.get("mape", 0.0),
                "periods": len(fc.forecast_data or []),
            })

        # 6. Scenarios
        compressed_scenarios = []
        for sc in scenarios[:MAX_COMPRESSED_SCENARIOS]:
            compressed_scenarios.append({
                "id": str(sc.id),
                "name": sc.name,
                "status": sc.status.value if hasattr(sc.status, "value") else str(sc.status),
                "assumptions_count": len(sc.assumptions or []),
            })

        # 7. Executive Insights (Top risks and opportunities if available)
        top_risks = []
        top_opps = []
        alerts = []
        if insight_report:
            top_risks = (insight_report.top_risks or [])[:3]
            top_opps = (insight_report.top_opportunities or [])[:3]
            alerts = (insight_report.executive_alerts or [])[:3]

        return {
            "dataset_id": str(dataset.id),
            "dataset_name": dataset.name,
            "business_health_score": raw_bundle.get("health_score", 85),
            "business_health_status": raw_bundle.get("health_status", "HEALTHY"),
            "question_type": question_type.value,
            "metrics": metrics_summary,
            "findings": compressed_findings,
            "root_causes": compressed_rcas,
            "recommendations": compressed_recs,
            "forecasts": compressed_forecasts,
            "scenarios": compressed_scenarios,
            "top_risks": top_risks,
            "top_opportunities": top_opps,
            "executive_alerts": alerts,
            "has_narrative": narr_report is not None,
            "has_executive_insights": insight_report is not None,
        }

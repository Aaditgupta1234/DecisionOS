"""Dashboard Read Model Layer for Phase 9.6 Executive Dashboard."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.dashboard.constants import HEALTH_STATUS_COLORS
from app.models.dataset import Dataset
from app.models.dataset_metric import DatasetMetric
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.root_cause_analysis import RootCauseAnalysis
from app.models.recommendation import Recommendation
from app.models.forecast import Forecast
from app.models.scenario import Scenario
from app.models.narrative_report import NarrativeReport
from app.models.executive_insight_report import ExecutiveInsightReport
from app.reporting.models.report_export import ReportExport
from app.models.chat_session import ChatSession


class DashboardReadModel:
    """
    Transforms persisted database entities into normalized read-model structures
    for dashboard snapshots and consumer endpoints.
    """

    @staticmethod
    def format_metric_value(val: Any) -> Tuple[float, str]:
        """Safely extract float and human-readable string from metric value."""
        if isinstance(val, (int, float)):
            num_val = float(val)
            if abs(num_val) >= 1_000_000:
                formatted = f"${num_val/1_000_000:.2f}M"
            elif abs(num_val) >= 1_000:
                formatted = f"${num_val/1_000:.1f}K"
            elif 0 < abs(num_val) < 1:
                formatted = f"{num_val * 100:.1f}%"
            else:
                formatted = f"{num_val:,.2f}"
            return num_val, formatted
        elif isinstance(val, dict):
            # Check for value key
            num = val.get("value") or val.get("current_value") or val.get("total") or 0.0
            try:
                num_val = float(num)
                return num_val, str(val.get("formatted_value") or f"{num_val:,.2f}")
            except (ValueError, TypeError):
                return 0.0, str(num)
        return 0.0, str(val) if val is not None else "0"

    @classmethod
    def build_kpis(cls, metrics: List[DatasetMetric]) -> List[Dict[str, Any]]:
        kpis = []
        for m in metrics:
            num_val, fmt_val = cls.format_metric_value(m.metric_value)
            category_str = m.metric_category.value if hasattr(m.metric_category, "value") else str(m.metric_category)
            
            # Extract trend if available in metric_value dict
            trend = "STABLE"
            trend_pct = 0.0
            hist = []
            if isinstance(m.metric_value, dict):
                trend = m.metric_value.get("trend", "STABLE")
                trend_pct = float(m.metric_value.get("trend_percentage", 0.0))
                hist = m.metric_value.get("historical_points", [])

            kpis.append({
                "metric_id": str(m.id),
                "metric_name": m.metric_name,
                "metric_key": m.metric_key,
                "category": category_str,
                "current_value": num_val,
                "formatted_value": fmt_val,
                "unit": getattr(m, "unit", "") or "",
                "target_value": getattr(m, "target_value", None),
                "historical_trend": hist,
                "trend": trend,
                "trend_percentage": trend_pct,
                "confidence_score": 0.95,
                "status": "HEALTHY" if trend != "DOWN" else "AT_RISK",
            })
        return kpis

    @classmethod
    def build_findings(cls, findings: List[DiagnosticFinding]) -> List[Dict[str, Any]]:
        result = []
        for f in findings:
            sev = f.severity.value if hasattr(f.severity, "value") else str(f.severity)
            ftype = f.finding_type.value if hasattr(f.finding_type, "value") else str(f.finding_type)
            
            # Derive impact score from severity if not explicitly present
            if hasattr(f, "impact_score") and f.impact_score is not None:
                impact_val = float(f.impact_score)
            else:
                impact_val = 0.95 if sev == "CRITICAL" else (0.80 if sev == "HIGH" else (0.50 if sev == "MEDIUM" else 0.25))

            metric_key = getattr(f, "primary_metric_key", None) or getattr(f, "metric_key", None)
            biz_impact = getattr(f, "business_impact", "") or (f.impact_description if hasattr(f, "impact_description") else "")

            result.append({
                "finding_id": str(f.id),
                "title": f.title,
                "finding_type": ftype,
                "severity": sev,
                "category": getattr(f, "category", "OPERATIONAL") or "OPERATIONAL",
                "description": f.description or "",
                "business_impact": biz_impact,
                "impact_score": impact_val,
                "confidence_score": float(getattr(f, "confidence_score", 0.9) or 0.9),
                "primary_metric_key": metric_key,
                "evidence_points": getattr(f, "evidence_points", []) or ([biz_impact] if biz_impact else []),
            })
        return result

    @classmethod
    def build_root_causes(cls, root_causes: List[RootCauseAnalysis]) -> List[Dict[str, Any]]:
        result = []
        for rc in root_causes:
            strength_str = rc.relationship_strength.value if hasattr(rc.relationship_strength, "value") else str(rc.relationship_strength)
            rel_type = rc.relationship_type.value if hasattr(rc.relationship_type, "value") else str(rc.relationship_type)
            title = getattr(rc, "title", None) or f"{rel_type} Causal Driver"
            expl = rc.explanation or ""
            
            # Build 4-stage causal chain
            causal_steps = [
                {"step_order": 1, "title": "Diagnostic Anomaly", "description": getattr(rc, "primary_symptom", None) or (expl[:60] if expl else "Observed KPI Variance"), "node_type": "ANOMALY"},
                {"step_order": 2, "title": "Primary Symptom", "description": getattr(rc, "symptom_description", None) or expl, "node_type": "SYMPTOM"},
                {"step_order": 3, "title": "Root Cause Driver", "description": title, "node_type": "ROOT_CAUSE"},
                {"step_order": 4, "title": "Strategic Remedy", "description": getattr(rc, "recommended_action", "Apply strategic intervention"), "node_type": "ACTION"},
            ]

            linked_findings = []
            if hasattr(rc, "primary_finding_id") and rc.primary_finding_id:
                linked_findings.append(str(rc.primary_finding_id))
            if hasattr(rc, "root_cause_finding_id") and rc.root_cause_finding_id:
                linked_findings.append(str(rc.root_cause_finding_id))
            elif hasattr(rc, "finding_id") and rc.finding_id:
                linked_findings.append(str(rc.finding_id))

            result.append({
                "root_cause_id": str(rc.id),
                "title": title,
                "primary_symptom": getattr(rc, "primary_symptom", "") or expl[:80],
                "causal_explanation": expl,
                "impact_score": float(rc.impact_score or 0.0),
                "attribution_percentage": float(getattr(rc, "attribution_percentage", rc.impact_score * 100) or (rc.impact_score * 100 if rc.impact_score else 25.0)),
                "confidence_score": float(rc.confidence_score or 0.9),
                "relationship_strength": strength_str,
                "causal_chain": causal_steps,
                "linked_finding_ids": linked_findings,
                "linked_recommendation_ids": [],
            })
        return result

    @classmethod
    def build_recommendations(cls, recommendations: List[Recommendation]) -> List[Dict[str, Any]]:
        result = []
        for r in recommendations:
            prio_str = r.priority.value if hasattr(r.priority, "value") else str(r.priority)
            action_type_str = r.recommendation_type.value if hasattr(r.recommendation_type, "value") else str(r.recommendation_type)
            ttv_str = r.expected_time_to_value.value if hasattr(r.expected_time_to_value, "value") else str(r.expected_time_to_value)
            status_str = r.status.value if hasattr(r.status, "value") else str(r.status)
            source_str = r.source.value if hasattr(r.source, "value") else str(r.source)

            impact = float(r.estimated_impact_score or 0.5)
            effort = float(r.estimated_effort_score or 0.5)

            # Assign 2x2 Matrix Quadrant
            if impact >= 0.5 and effort < 0.5:
                quadrant = "QUICK_WIN"
            elif impact >= 0.5 and effort >= 0.5:
                quadrant = "MAJOR_PROJECT"
            elif impact < 0.5 and effort < 0.5:
                quadrant = "FILL_IN"
            else:
                quadrant = "DEPRIORITIZED"

            result.append({
                "recommendation_id": str(r.id),
                "title": r.title,
                "action_type": action_type_str,
                "priority": prio_str,
                "quadrant": quadrant,
                "impact_score": impact,
                "effort_score": effort,
                "estimated_time_to_value": ttv_str,
                "expected_benefit": getattr(r, "expected_benefit", None) or r.description or "",
                "action_plan": r.action_plan or [],
                "status": status_str,
                "source": source_str,
                "linked_root_cause_id": str(r.root_cause_analysis_id) if hasattr(r, "root_cause_analysis_id") and r.root_cause_analysis_id else None,
            })
        return result

    @classmethod
    def build_forecasts(cls, forecasts: List[Forecast]) -> List[Dict[str, Any]]:
        result = []
        for fc in forecasts:
            horizon_str = fc.horizon.value if hasattr(fc.horizon, "value") else str(fc.horizon)
            trend_str = fc.trend.value if hasattr(fc.trend, "value") else str(fc.trend)
            metric_key = getattr(fc, "metric_key", None) or getattr(fc, "target_metric", "metric")
            
            # Extract MAPE
            mape_score = 4.2
            if hasattr(fc, "model_metrics") and isinstance(fc.model_metrics, dict):
                mape_score = float(fc.model_metrics.get("mape", 4.2))
            elif hasattr(fc, "mape") and fc.mape is not None:
                mape_score = float(fc.mape)

            # Build horizon projection points
            points = []
            projections_data = getattr(fc, "forecast_points", None) or getattr(fc, "projections", []) or []
            if isinstance(projections_data, list):
                for p in projections_data:
                    if isinstance(p, dict):
                        expected_val = float(p.get("expected") or p.get("forecast") or p.get("value") or 0.0)
                        points.append({
                            "horizon_label": p.get("date") or p.get("period") or p.get("label") or "Day",
                            "expected_value": expected_val,
                            "upper_bound": float(p.get("upper_bound") or p.get("upper") or (expected_val * 1.1)),
                            "lower_bound": float(p.get("lower_bound") or p.get("lower") or (expected_val * 0.9)),
                            "confidence_interval": float(p.get("confidence_interval") or getattr(fc, "confidence_level", 0.95) or 0.95),
                        })

            result.append({
                "forecast_id": str(fc.id),
                "target_metric": metric_key,
                "target_metric_name": metric_key.replace("_", " ").title(),
                "horizon": horizon_str,
                "model_used": getattr(fc, "model_name", "PROPHET_ENSEMBLE") or "PROPHET_ENSEMBLE",
                "mape_score": mape_score,
                "accuracy_percentage": round(100.0 - min(100.0, mape_score), 1),
                "trend": trend_str,
                "historical_actuals": getattr(fc, "historical_data", []) or [],
                "projections": points,
                "narrative_summary": getattr(fc, "summary", None),
            })
        return result

    @classmethod
    def build_scenarios(cls, scenarios: List[Scenario]) -> List[Dict[str, Any]]:
        result = []
        for sc in scenarios:
            impacted = []
            metrics_data = (
                getattr(sc, "projected_metrics", None)
                or (sc.results.get("impacted_metrics", []) if hasattr(sc, "results") and isinstance(sc.results, dict) else [])
                or []
            )
            for m in metrics_data:
                if isinstance(m, dict):
                    baseline = float(m.get("baseline") or m.get("baseline_value") or 100.0)
                    simulated = float(m.get("simulated") or m.get("simulated_value") or m.get("projected_value") or 110.0)
                    delta = float(m.get("delta") or (simulated - baseline))
                    pct = float(m.get("delta_percent") or m.get("delta_percentage") or ((delta / baseline * 100.0) if baseline else 0.0))
                    impacted.append({
                        "metric_name": m.get("name") or m.get("metric_name") or m.get("metric_key", "Metric"),
                        "metric_key": m.get("metric_key", "metric"),
                        "baseline_value": baseline,
                        "simulated_value": simulated,
                        "delta_value": delta,
                        "delta_percentage": round(pct, 2),
                        "unit": m.get("unit", ""),
                    })

            adjustments = getattr(sc, "assumptions", None) or (sc.parameters.get("adjustments", []) if hasattr(sc, "parameters") and isinstance(sc.parameters, dict) else []) or []
            summary_txt = (
                getattr(sc, "impact_summary", None)
                or (sc.results.get("executive_summary") if hasattr(sc, "results") and isinstance(sc.results, dict) else None)
                or sc.description
                or "Simulated scenario projection completed."
            )

            result.append({
                "scenario_id": str(sc.id),
                "name": sc.name,
                "description": sc.description or "",
                "scenario_type": getattr(sc, "scenario_type", "STRATEGIC_SIMULATION") or "STRATEGIC_SIMULATION",
                "status": "COMPLETED",
                "impact_summary": summary_txt,
                "confidence_score": float(getattr(sc, "confidence_score", 0.88) or 0.88),
                "impacted_metrics": impacted,
                "sensitivity_adjustments": adjustments,
            })
        return result

    @classmethod
    def build_narratives(cls, narratives: List[NarrativeReport]) -> List[Dict[str, Any]]:
        result = []
        for n in narratives:
            title = getattr(n, "title", None) or "Executive Strategic Narrative Briefing"
            ntype = getattr(n, "narrative_type", None) or "EXECUTIVE_SUMMARY"
            ntype_str = ntype.value if hasattr(ntype, "value") else str(ntype)
            
            content_html = getattr(n, "content_html", "")
            if not content_html and hasattr(n, "executive_summary") and isinstance(n.executive_summary, dict):
                content_html = n.executive_summary.get("narrative_html") or f"<p>{n.executive_summary.get('narrative_text', '')}</p>"
            if not content_html:
                content_html = "<p>Executive strategic briefing synthesized successfully.</p>"

            result.append({
                "report_id": str(n.id),
                "title": title,
                "narrative_type": ntype_str,
                "audience_level": str(getattr(n, "audience_level", "EXECUTIVE")),
                "content_html": content_html,
                "generated_at": n.created_at.isoformat() if n.created_at else datetime.now(timezone.utc).isoformat(),
            })
        return result

    @classmethod
    def build_insights(cls, insight_report: Optional[ExecutiveInsightReport]) -> Dict[str, Any]:
        if not insight_report:
            return {
                "executive_summary_html": "<p>No executive insights generated yet for this dataset.</p>",
                "strategic_themes": [],
                "risk_assessment": [],
                "growth_opportunities": [],
                "board_commentary": "Boardroom commentary will appear once insights generation completes.",
            }

        themes = []
        themes_data = getattr(insight_report, "strategic_themes", []) or []
        if isinstance(themes_data, list):
            for t in themes_data:
                if isinstance(t, dict):
                    themes.append({
                        "theme_title": t.get("theme_title") or t.get("title", "Strategic Objective"),
                        "impact_level": t.get("impact_level", "HIGH"),
                        "summary": t.get("summary") or t.get("description", ""),
                        "confidence_score": float(t.get("confidence_score", 0.92)),
                    })

        risks = getattr(insight_report, "top_risks", None) or getattr(insight_report, "risk_matrix", []) or []
        opps = getattr(insight_report, "top_opportunities", None) or getattr(insight_report, "growth_opportunities", []) or []

        commentary = ""
        if hasattr(insight_report, "board_commentary"):
            if isinstance(insight_report.board_commentary, dict):
                commentary = insight_report.board_commentary.get("summary") or insight_report.board_commentary.get("commentary", "")
            else:
                commentary = str(insight_report.board_commentary or "")
        if not commentary:
            commentary = getattr(insight_report, "boardroom_briefing", "Maintain proactive focus on key strategic objectives.")

        return {
            "executive_summary_html": insight_report.executive_summary or "<p>Executive insight analysis ready.</p>",
            "strategic_themes": themes,
            "risk_assessment": risks if isinstance(risks, list) else [],
            "growth_opportunities": opps if isinstance(opps, list) else [],
            "board_commentary": commentary,
        }

    @classmethod
    def build_reports_summary(cls, reports: List[ReportExport]) -> Dict[str, Any]:
        report_list = []
        for r in reports:
            fmt_str = r.export_format.value if hasattr(r.export_format, "value") else str(r.export_format)
            type_str = r.report_type.value if hasattr(r.report_type, "value") else str(r.report_type)
            status_str = r.status.value if hasattr(r.status, "value") else str(r.status)
            report_list.append({
                "report_id": str(r.id),
                "title": r.title,
                "report_type": type_str,
                "export_format": fmt_str,
                "status": status_str,
                "file_size_bytes": r.file_size_bytes,
                "generated_at": r.generated_at.isoformat() if r.generated_at else datetime.now(timezone.utc).isoformat(),
            })

        latest = reports[0] if reports else None
        return {
            "total_count": len(reports),
            "latest_report_id": str(latest.id) if latest else None,
            "latest_report_title": latest.title if latest else None,
            "latest_report_type": str(latest.report_type.value if hasattr(latest.report_type, "value") else latest.report_type) if latest else None,
            "latest_export_format": str(latest.export_format.value if hasattr(latest.export_format, "value") else latest.export_format) if latest else None,
            "latest_generated_at": latest.generated_at.isoformat() if latest and latest.generated_at else None,
            "reports": report_list,
        }

    @classmethod
    def build_suggested_questions(
        cls,
        findings: List[DiagnosticFinding],
        recommendations: List[Recommendation],
        forecasts: List[Forecast],
    ) -> List[str]:
        """Deterministically generate dynamic suggested chat questions from verified artifacts."""
        questions = []
        
        # 1. Top critical finding question
        crit_finding = next((f for f in findings if (f.severity.value if hasattr(f.severity, "value") else str(f.severity)) in ["CRITICAL", "HIGH"]), None)
        if crit_finding:
            questions.append(f"Why did '{crit_finding.title}' occur and what is the estimated impact?")
        else:
            questions.append("What are the primary operational bottlenecks identified in this dataset?")

        # 2. Recommendation priority question
        high_rec = next((r for r in recommendations if (r.priority.value if hasattr(r.priority, "value") else str(r.priority)) in ["CRITICAL", "HIGH"]), None)
        if high_rec:
            questions.append(f"How can we execute the recommendation for '{high_rec.title}'?")
        else:
            questions.append("Which strategic recommendation offers the highest ROI with lowest effort?")

        # 3. Forecast risk question
        if forecasts:
            fc = forecasts[0]
            target_m = getattr(fc, "metric_key", None) or getattr(fc, "target_metric", "metric")
            metric_name = target_m.replace("_", " ")
            questions.append(f"What is the projected {metric_name} trajectory over the next 90 days?")
        else:
            questions.append("What are the greatest future downside risks facing the business?")

        # 4. Executive summary question
        questions.append("Summarize the boardroom briefing and highlight key decision points.")
        return questions

    @classmethod
    def build_overview(
        cls,
        dataset: Dataset,
        metrics: List[DatasetMetric],
        findings: List[DiagnosticFinding],
        root_causes: List[RootCauseAnalysis],
        recommendations: List[Recommendation],
        forecasts: List[Forecast],
        scenarios: List[Scenario],
        reports: List[ReportExport],
        insight_report: Optional[ExecutiveInsightReport],
    ) -> Dict[str, Any]:
        # Health Score computation
        if insight_report and getattr(insight_report, "overall_health_score", None) is not None:
            overall_health = int(insight_report.overall_health_score)
        else:
            # Deterministic default based on finding severities
            crit_count = sum(1 for f in findings if (f.severity.value if hasattr(f.severity, "value") else str(f.severity)) == "CRITICAL")
            high_count = sum(1 for f in findings if (f.severity.value if hasattr(f.severity, "value") else str(f.severity)) == "HIGH")
            overall_health = max(35, 95 - (crit_count * 15 + high_count * 5))

        if overall_health >= 85:
            health_status = "OPTIMAL"
        elif overall_health >= 70:
            health_status = "HEALTHY"
        elif overall_health >= 55:
            health_status = "WATCH_LIST"
        elif overall_health >= 40:
            health_status = "AT_RISK"
        else:
            health_status = "CRITICAL"

        status_color = HEALTH_STATUS_COLORS.get(health_status, "#34D399")

        health_dim = {
            "overall_score": overall_health,
            "financial_score": min(100, overall_health + 2),
            "operational_score": max(30, overall_health - 4),
            "customer_score": overall_health,
            "growth_score": min(100, overall_health + 5),
            "status": health_status,
            "status_color": status_color,
            "previous_score": overall_health - 3,
            "delta": 3.0,
            "trend": "UP",
        }

        scorecard = {
            "business_health_score": overall_health,
            "revenue_health_score": health_dim["financial_score"],
            "operational_health_score": health_dim["operational_score"],
            "customer_health_score": health_dim["customer_score"],
            "forecast_confidence": 0.88,
            "risk_exposure_score": round(max(5.0, 100.0 - overall_health), 1),
            "health_status": health_status,
        }

        statistics = {
            "findings_count": len(findings),
            "root_causes_count": len(root_causes),
            "recommendations_count": len(recommendations),
            "forecasts_count": len(forecasts),
            "scenarios_count": len(scenarios),
            "reports_count": len(reports),
            "metrics_count": len(metrics),
        }

        # Top 3 Risks
        top_risks = []
        for f in findings[:3]:
            sev = f.severity.value if hasattr(f.severity, "value") else str(f.severity)
            top_risks.append({
                "id": str(f.id),
                "title": f.title,
                "severity": sev,
                "category": getattr(f, "category", "OPERATIONAL") or "OPERATIONAL",
                "impact": f.business_impact if hasattr(f, "business_impact") and f.business_impact else f.description or "Negative impact on KPI performance",
                "confidence": float(f.confidence_score or 0.9),
            })

        # Top 3 Opportunities
        top_opps = []
        for r in recommendations[:3]:
            top_opps.append({
                "id": str(r.id),
                "title": r.title,
                "impact_type": str(r.recommendation_type.value if hasattr(r.recommendation_type, "value") else r.recommendation_type),
                "potential_value": getattr(r, "expected_benefit", None) or f"Estimated {int((r.estimated_impact_score or 0.5) * 100)}% efficiency lift",
                "effort": "LOW" if (r.estimated_effort_score or 0.5) < 0.4 else "MEDIUM",
                "lever": r.action_plan[0] if r.action_plan else "Optimize operational parameters",
            })

        # Active Alerts (Critical & High findings)
        alerts = []
        for f in findings:
            sev = f.severity.value if hasattr(f.severity, "value") else str(f.severity)
            if sev in ["CRITICAL", "HIGH"]:
                alerts.append({
                    "id": str(f.id),
                    "severity": sev,
                    "title": f.title,
                    "description": f.description or "",
                    "source_type": "DIAGNOSTIC",
                    "created_at": f.created_at.isoformat() if f.created_at else datetime.now(timezone.utc).isoformat(),
                    "status": "ACTIVE",
                    "target_section": "findings",
                })

        # Watchlist KPIs
        watchlist = []
        for m in metrics[:4]:
            _, fmt_val = cls.format_metric_value(m.metric_value)
            trend = "STABLE"
            trend_pct = 0.0
            if isinstance(m.metric_value, dict):
                trend = m.metric_value.get("trend", "STABLE")
                trend_pct = float(m.metric_value.get("trend_percentage", 0.0))

            watchlist.append({
                "metric_key": m.metric_key,
                "metric_name": m.metric_name,
                "current_value": fmt_val,
                "trend": trend,
                "trend_percentage": trend_pct,
                "status": "IMPROVING" if trend == "UP" else ("DECLINING" if trend == "DOWN" else "STABLE"),
                "priority": "HIGH" if trend == "DOWN" else "MEDIUM",
            })

        return {
            "health_dimensions": health_dim,
            "scorecard": scorecard,
            "statistics": statistics,
            "top_risks": top_risks,
            "top_opportunities": top_opps,
            "active_alerts": alerts,
            "watchlist_metrics": watchlist,
            "executive_summary_brief": insight_report.executive_summary if insight_report and insight_report.executive_summary else f"Dataset '{dataset.name}' intelligence workspace hydrated with {len(metrics)} KPIs and {len(findings)} findings.",
        }

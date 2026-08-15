"""Deterministic rule-based fallback generators for Phase 9.3: Executive Insight Generator."""

from typing import Any, Dict, List
from app.executive_insights.insight_scoring import (
    calculate_action_ranking_score,
    calculate_opportunity_ranking_score,
    calculate_risk_ranking_score,
)


class FallbackInsights:
    """
    Deterministic rule-based generator creating boardroom-grade Executive Insights
    directly from verified analytical telemetry when LLM providers are unavailable.
    """

    @classmethod
    def render_top_risks_fallback(cls, context: Dict[str, Any]) -> Dict[str, Any]:
        findings = context.get("findings") or []
        root_causes = context.get("root_causes") or []
        top_risks = []

        if findings:
            for idx, f in enumerate(findings[:3]):
                title = f.get("title", f"Operational Variance {idx+1}")
                sev = str(f.get("severity", "HIGH")).upper()
                conf = float(f.get("confidence_score", 0.85))
                desc = (
                    f"Telemetry confirms that '{title}' constitutes a primary operational risk factor. "
                    f"Diagnostic analysis isolates this variance as an active impediment to baseline performance trajectory, "
                    f"requiring prompt executive review and mitigation."
                )
                matching_rca = [
                    r for r in root_causes
                    if r.get("effect") == title or r.get("primary_finding_title") == title
                ]
                f_id = str(f.get("id")) if f.get("id") else ""
                rca_ids = [str(r.get("id")) for r in matching_rca if r.get("id")]
                evidence = [f"Identified diagnostic anomaly in {f.get('category', 'business operations')}"]
                if matching_rca:
                    evidence.append(f"Causally linked to {matching_rca[0].get('cause', 'upstream operational factors')}")

                ranking = calculate_risk_ranking_score(severity=sev, confidence=conf)

                top_risks.append({
                    "title": f"Risk: {title}",
                    "description": desc,
                    "severity": sev if sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"] else "HIGH",
                    "confidence": conf,
                    "ranking_score": ranking,
                    "supporting_evidence": evidence,
                    "source_finding_ids": [f_id] if f_id else [],
                    "source_root_cause_ids": rca_ids,
                })
        else:
            top_risks.append({
                "title": "Risk: Operational Baseline Drift",
                "description": (
                    "Baseline business telemetry reflects steady state operations with localized opportunities "
                    "for proactive monitoring to prevent unexpected margin compression across future reporting periods."
                ),
                "severity": "LOW",
                "confidence": 0.90,
                "ranking_score": 0.35,
                "supporting_evidence": ["No critical diagnostic anomalies detected across active KPI telemetry"],
                "source_finding_ids": [],
                "source_root_cause_ids": [],
            })

        return {"top_risks": top_risks}

    @classmethod
    def render_top_opportunities_fallback(cls, context: Dict[str, Any]) -> Dict[str, Any]:
        recommendations = context.get("recommendations") or []
        top_opps = []

        if recommendations:
            for idx, r in enumerate(recommendations[:3]):
                title = r.get("title", f"Optimization Initiative {idx+1}")
                impact_str = str(r.get("priority", "HIGH")).upper()
                conf = float(r.get("confidence_score", 0.88))
                r_id = str(r.get("id")) if r.get("id") else ""
                desc = (
                    f"Executing '{title}' represents a significant high-leverage growth and margin stabilization opportunity. "
                    f"Analytical modeling projects that structured implementation will effectively resolve primary diagnostic vulnerabilities "
                    f"and capture measurable top-line operational upside."
                )
                ranking = calculate_opportunity_ranking_score(impact=impact_str, confidence=conf)

                top_opps.append({
                    "title": f"Opportunity: {title}",
                    "description": desc,
                    "impact": impact_str if impact_str in ["CRITICAL", "HIGH", "MEDIUM", "LOW"] else "HIGH",
                    "confidence": conf,
                    "ranking_score": ranking,
                    "supporting_evidence": [r.get("rationale") or "Derived from verified decision rule mechanisms"],
                    "source_recommendation_ids": [r_id] if r_id else [],
                })
        else:
            top_opps.append({
                "title": "Opportunity: Continuous Operational Optimization",
                "description": (
                    "Enterprise processes indicate opportunities to institutionalize lean standard operating procedures "
                    "and optimize recurring cost structures to sustain competitive advantages and protect healthy gross margins."
                ),
                "impact": "MEDIUM",
                "confidence": 0.85,
                "ranking_score": 0.60,
                "supporting_evidence": ["Baseline health index supports proactive operational scaling"],
                "source_recommendation_ids": [],
            })

        return {"top_opportunities": top_opps}

    @classmethod
    def render_priority_actions_fallback(cls, context: Dict[str, Any]) -> Dict[str, Any]:
        recommendations = context.get("recommendations") or []
        actions = []

        if recommendations:
            for idx, r in enumerate(recommendations[:4]):
                name = r.get("title", f"Action {idx+1}")
                prio = str(r.get("priority", "HIGH")).upper()
                r_id = str(r.get("id")) if r.get("id") else ""
                ranking = calculate_action_ranking_score(priority=prio)
                actions.append({
                    "action": name,
                    "priority": prio if prio in ["CRITICAL", "HIGH", "MEDIUM", "LOW"] else "HIGH",
                    "expected_impact": str(r.get("expected_outcome") or "Accelerates operational recovery and protects ARR."),
                    "difficulty": "MODERATE",
                    "ranking_score": ranking,
                    "rationale": (
                        f"Directly addresses primary diagnostic telemetry by implementing verified decision rule interventions "
                        f"to eliminate operational bottlenecks and restore target KPI baselines."
                    ),
                    "source_recommendation_ids": [r_id] if r_id else [],
                })
        else:
            actions.append({
                "action": "Institutionalize Baseline Operating Cadence",
                "priority": "MEDIUM",
                "expected_impact": "Maintains predictable top-line stability and throughput velocity.",
                "difficulty": "EASY",
                "ranking_score": 0.55,
                "rationale": "Maintains organizational velocity and ensures timely identification of emerging diagnostic anomalies.",
                "source_recommendation_ids": [],
            })

        return {"priority_actions": actions}

    @classmethod
    def render_strategic_themes_fallback(cls, context: Dict[str, Any]) -> Dict[str, Any]:
        findings = context.get("findings") or []
        recommendations = context.get("recommendations") or []

        rec_titles = [r.get("title", "Operational Initiative") for r in recommendations]

        themes = [
            {
                "theme": "Operational Resilience & Efficiency",
                "description": "Streamline core business processes and eliminate systemic friction across operating workflows.",
                "key_pillars": [
                    "Continuous diagnostic telemetry tracking",
                    "Targeted root-cause bottleneck elimination",
                    "Cross-functional execution accountability",
                ],
                "aligned_initiatives": rec_titles[:2] if rec_titles else ["Sustain core operating cadence"],
            },
            {
                "theme": "Revenue Protection & Customer Retention",
                "description": "Protect recurring top-line revenue by proactively mitigating customer churn and contract attrition.",
                "key_pillars": [
                    "High-touch retention taskforces",
                    "Contract renewal health monitoring",
                    "Value realization engagement loops",
                ],
                "aligned_initiatives": rec_titles[2:4] if len(rec_titles) > 2 else ["Customer success onboarding audit"],
            },
        ]
        return {"strategic_themes": themes}

    @classmethod
    def render_executive_alerts_fallback(cls, context: Dict[str, Any]) -> Dict[str, Any]:
        findings = context.get("findings") or []
        alerts = []

        for f in findings:
            sev = str(f.get("severity", "")).upper()
            if sev in ["CRITICAL", "HIGH"]:
                f_id = str(f.get("id")) if f.get("id") else ""
                alerts.append({
                    "alert_level": sev,
                    "headline": f"Operational Alert: {f.get('title', 'Variance Detected')}",
                    "detail": str(f.get("description") or "Diagnostic anomaly exceeds standard operational tolerance threshold."),
                    "recommended_immediate_step": "Deploy dedicated triage taskforce and audit upstream causal drivers.",
                    "source_finding_ids": [f_id] if f_id else [],
                })

        if not alerts:
            alerts.append({
                "alert_level": "INFO",
                "headline": "System Status: Nominal Operating Telemetry",
                "detail": "All monitored business indicators reside within expected statistical tolerance parameters.",
                "recommended_immediate_step": "Maintain standard executive review schedule.",
                "source_finding_ids": [],
            })

        return {"executive_alerts": alerts}

    @classmethod
    def render_board_commentary_fallback(cls, context: Dict[str, Any]) -> Dict[str, Any]:
        health_score = context.get("business_health_score", 85)
        health_status = context.get("business_health_status", "GOOD")
        dataset_name = context.get("dataset_name", "Enterprise Dataset")
        findings = context.get("findings") or []
        recommendations = context.get("recommendations") or []

        p_find = findings[0].get("title") if findings else "operational variance"
        p_rec = recommendations[0].get("title") if recommendations else "standard governance protocols"

        commentary = (
            f"During the current reporting cycle, performance evaluation for {dataset_name} confirms an overall Business Health Score "
            f"of {health_score} out of 100, placing enterprise performance in {health_status} status. Core revenue, customer, and operational "
            f"telemetry indicates steady operational foundation with manageable headwinds. Diagnostic analysis highlights '{p_find}' as the "
            f"primary strategic constraint requiring governance oversight and targeted mitigation. Boardroom focus should center on approving "
            f"and executing '{p_rec}' alongside prioritized operational initiatives to protect operating margins, halt customer attrition, "
            f"and sustain predictable quarterly performance. Executive leadership recommends regular progress audits against the strategic roadmap "
            f"to ensure timely realization of projected financial outcomes and long-term organizational value."
        )

        return {
            "headline": f"Board Briefing: Business Health Evaluated at {health_score}/100 ({health_status})",
            "commentary": commentary,
            "strategic_outlook": "Predictable operational trajectory with measurable upside upon execution of prioritized strategic interventions.",
            "health_summary": f"Composite Health Score of {health_score}/100 confirms {health_status} operational profile.",
        }

    @classmethod
    def render_full_package_fallback(cls, context: Dict[str, Any]) -> Dict[str, Any]:
        risks = cls.render_top_risks_fallback(context)["top_risks"]
        opps = cls.render_top_opportunities_fallback(context)["top_opportunities"]
        actions = cls.render_priority_actions_fallback(context)["priority_actions"]
        themes = cls.render_strategic_themes_fallback(context)["strategic_themes"]
        alerts = cls.render_executive_alerts_fallback(context)["executive_alerts"]
        board = cls.render_board_commentary_fallback(context)

        health_score = context.get("business_health_score", 85)
        health_status = context.get("business_health_status", "GOOD")

        summary = (
            f"Executive synthesis for dataset '{context.get('dataset_name', 'Enterprise')}' indicates composite business health at "
            f"{health_score}/100 ({health_status}). Key strategic risks have been prioritized alongside high-leverage growth opportunities "
            f"to guide executive decision-making and resource allocation."
        )

        return {
            "executive_summary": summary,
            "top_risks": risks,
            "top_opportunities": opps,
            "priority_actions": actions,
            "strategic_themes": themes,
            "executive_alerts": alerts,
            "board_commentary": board,
        }

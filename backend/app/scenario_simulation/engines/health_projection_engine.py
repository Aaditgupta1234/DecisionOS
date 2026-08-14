"""HealthProjectionEngine computing deterministic projected diagnostics, risk shifts, and health scores."""

from typing import Any, Dict, List, Optional, Tuple
from app.core.constants import BusinessHealthStatus, FindingSeverity
from app.intelligence.constants import (
    FINDING_SEVERITY_PENALTIES,
    MAX_FINDING_PENALTY,
    MAX_RCA_PENALTY,
    RCA_HIGH_IMPACT_PENALTY,
    RCA_HIGH_IMPACT_THRESHOLD,
    RCA_MODERATE_IMPACT_PENALTY,
    RCA_MODERATE_IMPACT_THRESHOLD,
    health_score_to_status,
)
from app.scenario_simulation.schemas.scenario_schema import ScenarioHealthProjection


class HealthProjectionEngine:
    """
    Deterministically computes projected diagnostic findings, risk shifts, opportunities,
    and recalculates the projected composite Business Health Score.
    
    GUARANTEE: Pure metric simulations are isolated from unearned recommendation recovery bonuses.
    """

    @classmethod
    def project_health_and_diagnostics(
        cls,
        baseline_health_score: int,
        baseline_health_status: BusinessHealthStatus,
        baseline_findings: List[Dict[str, Any]],
        baseline_root_causes: List[Dict[str, Any]],
        baseline_metrics: Dict[str, float],
        projected_metrics: Dict[str, float],
    ) -> Tuple[ScenarioHealthProjection, List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Re-evaluates findings and computes isolated projected health score.
        """
        projected_findings = []
        projected_risks = []
        projected_opportunities = []

        # 1. Re-evaluate Diagnostic Findings
        finding_penalty = 0

        for f in baseline_findings:
            title = f.get("title", "Diagnostic Finding")
            orig_sev = f.get("severity", "MEDIUM")
            f_type = f.get("finding_type") or f.get("type") or ""

            # Evaluate metric shifts relevant to finding
            proj_sev = orig_sev
            mitigation_note = None

            # Revenue decline finding
            if ("revenue" in title.lower() or "drop" in title.lower()) and "total_revenue" in projected_metrics:
                base_rev = baseline_metrics.get("total_revenue", 0.0)
                proj_rev = projected_metrics.get("total_revenue", 0.0)
                if proj_rev > base_rev:
                    pct_gain = ((proj_rev - base_rev) / base_rev) * 100.0 if base_rev > 0 else 0
                    if pct_gain >= 10.0:
                        proj_sev = FindingSeverity.LOW.value if orig_sev in ("CRITICAL", "HIGH") else orig_sev
                        mitigation_note = f"Top-line improvement (+{pct_gain:.1f}%) substantially alleviates revenue pressure."
                    elif pct_gain > 0:
                        proj_sev = FindingSeverity.MEDIUM.value if orig_sev == "CRITICAL" else orig_sev
                        mitigation_note = f"Top-line stabilization (+{pct_gain:.1f}%) partially reduces revenue drop severity."

            # Churn spike finding
            if ("churn" in title.lower() or "retention" in title.lower()) and "customer_churn_rate" in projected_metrics:
                base_churn = baseline_metrics.get("customer_churn_rate", 20.0)
                proj_churn = projected_metrics.get("customer_churn_rate", 20.0)
                if proj_churn < base_churn:
                    churn_drop = base_churn - proj_churn
                    if churn_drop >= 5.0 or proj_churn <= 10.0:
                        proj_sev = FindingSeverity.LOW.value
                        mitigation_note = f"Projected churn reduction ({proj_churn:.1f}%) resolves primary customer attrition finding."
                    elif churn_drop > 0:
                        proj_sev = FindingSeverity.MEDIUM.value if orig_sev in ("CRITICAL", "HIGH") else orig_sev
                        mitigation_note = f"Projected churn decline ({proj_churn:.1f}%) reduces attrition severity."

            # Delivery delays finding
            if ("delivery" in title.lower() or "shipping" in title.lower()) and "average_delivery_time" in projected_metrics:
                base_del = baseline_metrics.get("average_delivery_time", 5.0)
                proj_del = projected_metrics.get("average_delivery_time", 5.0)
                if proj_del < base_del:
                    del_drop = base_del - proj_del
                    if del_drop >= 1.0 or proj_del <= 3.0:
                        proj_sev = FindingSeverity.LOW.value
                        mitigation_note = f"Fulfillment speed improvement ({proj_del:.1f} days) resolves fulfillment delay finding."

            # Completion rate finding
            if ("completion" in title.lower() or "cancellation" in title.lower()) and "completion_rate" in projected_metrics:
                base_comp = baseline_metrics.get("completion_rate", 80.0)
                proj_comp = projected_metrics.get("completion_rate", 80.0)
                if proj_comp > base_comp:
                    if proj_comp >= 95.0:
                        proj_sev = FindingSeverity.LOW.value
                        mitigation_note = f"Order completion rate recovery ({proj_comp:.1f}%) mitigates cancellation finding."

            projected_findings.append({
                "title": title,
                "original_severity": orig_sev,
                "projected_severity": proj_sev,
                "severity_improved": proj_sev != orig_sev,
                "mitigation_note": mitigation_note,
            })

            # Tally finding penalty for projected health
            pen = FINDING_SEVERITY_PENALTIES.get(FindingSeverity(proj_sev) if proj_sev in FindingSeverity._value2member_map_ else FindingSeverity.MEDIUM, 5)
            finding_penalty += pen

        # 2. Re-evaluate Root Cause Penalties
        rca_penalty = 0
        for rca in baseline_root_causes:
            impact_score = float(rca.get("impact_score", 0.7) or 0.7)
            if impact_score >= RCA_HIGH_IMPACT_THRESHOLD:
                rca_penalty += RCA_HIGH_IMPACT_PENALTY
            elif impact_score >= RCA_MODERATE_IMPACT_THRESHOLD:
                rca_penalty += RCA_MODERATE_IMPACT_PENALTY

        # Cap deductions
        total_finding_pen = min(finding_penalty, MAX_FINDING_PENALTY)
        total_rca_pen = min(rca_penalty, MAX_RCA_PENALTY)

        # 3. Calculate Projected Health (Zero unearned recommendation implementation bonus)
        projected_score = max(0, min(100, 100 - total_finding_pen - total_rca_pen))
        projected_status = health_score_to_status(projected_score)

        health_proj = ScenarioHealthProjection(
            baseline_score=baseline_health_score,
            projected_score=projected_score,
            score_delta=projected_score - baseline_health_score,
            baseline_status=baseline_health_status,
            projected_status=projected_status,
            status_changed=projected_status != baseline_health_status,
        )

        # 4. Synthesize Projected Risks & Opportunities
        for f in projected_findings:
            if f.get("severity_improved"):
                projected_opportunities.append({
                    "title": f"Mitigate {f['title']}",
                    "impact": f["mitigation_note"] or "Severity downgraded under scenario assumptions.",
                })
            else:
                projected_risks.append({
                    "title": f["title"],
                    "current_severity": f["projected_severity"],
                    "status": "Remains active under current scenario parameters.",
                })

        return health_proj, projected_findings, projected_risks, projected_opportunities

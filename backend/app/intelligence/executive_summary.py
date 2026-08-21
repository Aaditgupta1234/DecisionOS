"""ExecutiveSummaryBuilder synthesizing high-level executive insights, risk rankings, and health scoring."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Dict, List, Optional
from uuid import UUID

from app.core.constants import FindingSeverity, RecommendationPriority
from app.intelligence.health_score import BusinessHealthScoreEngine
from app.intelligence.models import ExecutiveSummary

if TYPE_CHECKING:
    from app.models.diagnostic_finding import DiagnosticFinding
    from app.models.recommendation import Recommendation
    from app.models.root_cause_analysis import RootCauseAnalysis

SEVERITY_RANK = {
    FindingSeverity.CRITICAL: 4,
    FindingSeverity.HIGH: 3,
    FindingSeverity.MEDIUM: 2,
    FindingSeverity.LOW: 1,
}

PRIORITY_RANK = {
    RecommendationPriority.CRITICAL: 4,
    RecommendationPriority.HIGH: 3,
    RecommendationPriority.MEDIUM: 2,
    RecommendationPriority.LOW: 1,
}


class ExecutiveSummaryBuilder:
    """
    Synthesizes high-level executive decision summaries from findings,
    causal drivers, actionable recommendations, and business health scores.
    """

    @classmethod
    def build(
        cls,
        dataset_id: UUID,
        findings: Optional[List[DiagnosticFinding]] = None,
        root_causes: Optional[List[RootCauseAnalysis]] = None,
        recommendations: Optional[List[Recommendation]] = None,
    ) -> ExecutiveSummary:
        """
        Synthesizes a complete ExecutiveSummary data object.
        """
        finding_list = findings or []
        rca_list = root_causes or []
        rec_list = recommendations or []

        # 1. Determine Primary Business Issue
        if finding_list:
            sorted_findings = sorted(
                finding_list,
                key=lambda f: (
                    SEVERITY_RANK.get(f.severity, 1),
                    f.confidence_score,
                ),
                reverse=True,
            )
            primary_finding = sorted_findings[0]
            primary_issue = primary_finding.title
            primary_sev = (
                primary_finding.severity.value
                if hasattr(primary_finding.severity, "value")
                else str(primary_finding.severity)
            )
        else:
            primary_issue = "No critical business anomalies detected."
            primary_sev = "LOW"

        # 2. Determine Top Root Cause
        top_rca_title: Optional[str] = None
        if rca_list:
            sorted_rcas = sorted(
                rca_list,
                key=lambda r: (r.impact_score, r.confidence_score),
                reverse=True,
            )
            top_rca = sorted_rcas[0]
            if top_rca.root_cause_finding:
                top_rca_title = top_rca.root_cause_finding.title
            else:
                top_rca_title = top_rca.explanation[:80]

        # 3. Determine Top Recommendation
        top_rec_title: Optional[str] = None
        if rec_list:
            sorted_recs = sorted(
                rec_list,
                key=lambda r: (
                    PRIORITY_RANK.get(r.priority, 1),
                    r.estimated_impact_score,
                    r.confidence_score,
                ),
                reverse=True,
            )
            top_rec_title = sorted_recs[0].title

        # 4. Extract Key Risks (Top 3-5 high/critical finding statements)
        key_risks: List[str] = []
        for f in sorted_findings if finding_list else []:
            if f.severity in (FindingSeverity.CRITICAL, FindingSeverity.HIGH, FindingSeverity.MEDIUM):
                risk_desc = f"{f.title}: {f.description}" if f.description else f.title
                if risk_desc not in key_risks:
                    key_risks.append(risk_desc)
            if len(key_risks) >= 4:
                break

        if not key_risks and finding_list:
            key_risks = [f.title for f in finding_list[:3]]

        # 5. Compute Confidence Breakdown
        finding_conf = (
            sum(f.confidence_score for f in finding_list) / len(finding_list)
            if finding_list
            else 1.0
        )
        rca_conf = (
            sum(r.confidence_score for r in rca_list) / len(rca_list)
            if rca_list
            else 1.0
        )
        rec_conf = (
            sum(r.confidence_score for r in rec_list) / len(rec_list)
            if rec_list
            else 1.0
        )

        confidence_breakdown = {
            "findings": round(finding_conf, 4),
            "root_causes": round(rca_conf, 4),
            "recommendations": round(rec_conf, 4),
        }

        overall_conf = round(
            (0.40 * finding_conf) + (0.35 * rca_conf) + (0.25 * rec_conf),
            4,
        )

        # 6. Calculate Business Health Score with Full Explanation
        health_score, health_status, health_explanation = BusinessHealthScoreEngine.calculate_with_explanation(
            findings=finding_list,
            root_causes=rca_list,
            recommendations=rec_list,
        )

        # 7. Formulate Status-Driven Strategic Business Impact Narrative
        status_val = health_status.value if hasattr(health_status, "value") else str(health_status)

        if top_rca_title and top_rec_title:
            if status_val in ("CRITICAL", "AT_RISK"):
                expected_impact = (
                    f"Business performance is severely degraded across multiple dimensions (Health Score: {health_score}/100 - {status_val}). "
                    f"Primary operational risk '{primary_issue}' is driven by '{top_rca_title}'. "
                    f"Immediate emergency execution of '{top_rec_title}' is required to contain operational risk and prevent further deterioration."
                )
            elif status_val == "WATCH_LIST":
                expected_impact = (
                    f"Several operational indicators are under pressure (Health Score: {health_score}/100 - WATCH_LIST). "
                    f"Primary issue '{primary_issue}' is driven by '{top_rca_title}'. "
                    f"Targeted execution of '{top_rec_title}' is recommended to reverse emerging operational drag."
                )
            else:
                expected_impact = (
                    f"Business performance remains healthy (Health Score: {health_score}/100 - {status_val}). "
                    f"Primary driver '{primary_issue}' is linked to '{top_rca_title}'. "
                    f"Execution of '{top_rec_title}' is recommended to sustain baseline growth and optimize margins."
                )
        elif top_rec_title:
            if status_val in ("CRITICAL", "AT_RISK"):
                expected_impact = (
                    f"Business performance is severely degraded across multiple dimensions (Health Score: {health_score}/100 - {status_val}). "
                    f"Immediate corrective action via '{top_rec_title}' is recommended to contain operational risk and prevent further deterioration."
                )
            elif status_val == "WATCH_LIST":
                expected_impact = (
                    f"Several operational indicators are under pressure (Health Score: {health_score}/100 - WATCH_LIST). "
                    f"Targeted intervention via '{top_rec_title}' is recommended to address identified operational bottlenecks."
                )
            else:
                expected_impact = (
                    f"Business performance remains healthy (Health Score: {health_score}/100 - {status_val}). "
                    f"Executing '{top_rec_title}' is recommended to sustain baseline momentum and optimize efficiency."
                )
        else:
            if status_val in ("CRITICAL", "AT_RISK"):
                expected_impact = (
                    f"Business performance is severely degraded across multiple dimensions (Health Score: {health_score}/100 - {status_val}). "
                    f"Immediate corrective action is recommended to contain operational risk and prevent further deterioration."
                )
            elif status_val == "WATCH_LIST":
                expected_impact = (
                    f"Several operational indicators are under pressure with a health score of {health_score}/100 (WATCH_LIST). "
                    f"Targeted intervention is recommended to prevent further degradation."
                )
            elif status_val == "HEALTHY":
                expected_impact = (
                    f"Business performance remains healthy with a health score of {health_score}/100 (HEALTHY). "
                    f"Address identified issues to sustain baseline momentum."
                )
            else:
                expected_impact = (
                    f"Business performance remains strong across monitored dimensions with a health score of {health_score}/100 (EXCELLENT). "
                    f"Continue optimization and growth initiatives."
                )

        # Prohibited words invariant assertion for CRITICAL / AT_RISK status
        if status_val in ("CRITICAL", "AT_RISK"):
            prohibited_words = ["stable", "healthy", "normal", "baseline monitoring", "no action required"]
            impact_lower = expected_impact.lower()
            for word in prohibited_words:
                if word in impact_lower:
                    expected_impact = (
                        f"Business performance is severely degraded across multiple dimensions (Health Score: {health_score}/100 - {status_val}). "
                        f"Immediate emergency corrective action is required to contain operational risk and prevent further deterioration."
                    )
                    break

        return ExecutiveSummary(
            dataset_id=dataset_id,
            generated_at=datetime.now(timezone.utc),
            primary_issue=primary_issue,
            severity=primary_sev,
            top_root_cause=top_rca_title,
            top_recommendation=top_rec_title,
            key_risks=key_risks,
            overall_confidence=overall_conf,
            confidence_breakdown=confidence_breakdown,
            business_health_score=health_score,
            business_health_status=health_status,
            expected_business_impact=expected_impact,
            health_score_explanation=health_explanation,
        )

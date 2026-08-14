"""ExecutiveSummaryBuilder synthesizing high-level executive insights, risk rankings, and health scoring."""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID

from app.core.constants import FindingSeverity, RecommendationPriority
from app.intelligence.health_score import BusinessHealthScoreEngine
from app.intelligence.models import ExecutiveSummary
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

        # 6. Calculate Business Health Score
        health_score, health_status = BusinessHealthScoreEngine.calculate(
            findings=finding_list,
            root_causes=rca_list,
            recommendations=rec_list,
        )

        # 7. Formulate Strategic Business Impact Narrative
        if top_rca_title and top_rec_title:
            expected_impact = (
                f"Primary business risk '{primary_issue}' is driven by '{top_rca_title}'. "
                f"Immediate execution of '{top_rec_title}' is projected to mitigate ongoing operational exposure "
                f"and restore business health (Current Health Score: {health_score}/100 - {health_status.value})."
            )
        elif top_rec_title:
            expected_impact = (
                f"Executing '{top_rec_title}' is recommended to address identified operational bottlenecks "
                f"(Business Health Score: {health_score}/100 - {health_status.value})."
            )
        else:
            expected_impact = (
                f"Business operations are stable with a health score of {health_score}/100 ({health_status.value}). "
                f"Continue baseline metric monitoring."
            )

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
        )

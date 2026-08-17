"""Executive Intelligence Engine for Phase 12.7."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.execution.constants import (
    EXECUTIVE_INTELLIGENCE_ENGINE_VERSION,
    STRATEGIC_SNAPSHOT_METRIC_VERSION,
    ExecutiveAttentionLevel,
    ExecutiveFindingSeverity,
    StrategicPriority,
    calculate_executive_attention_level,
    calculate_finding_severity,
)


class ExecutiveIntelligenceEngine:
    """
    Deterministic executive intelligence consolidation engine generating findings with severity,
    opportunities, risk briefings, and rule-based executive recommendations.
    """

    ENGINE_VERSION = EXECUTIVE_INTELLIGENCE_ENGINE_VERSION
    SNAPSHOT_METRIC_VERSION = STRATEGIC_SNAPSHOT_METRIC_VERSION

    @classmethod
    def generate_executive_intelligence(
        cls,
        initiatives: List[Dict[str, Any]],
        diagnostics: Dict[str, Any],
        attention_score: float = 0.0,
        portfolio_maturity_score: float = 100.0,
        portfolio_roi: float = 0.0,
        total_value_at_risk: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Generates deterministic executive intelligence summaries, findings, opportunities, and recommendations.
        """
        now = datetime.now(timezone.utc)
        warnings: List[str] = []

        attention_level = calculate_executive_attention_level(attention_score)

        findings: List[Dict[str, Any]] = []
        opportunities: List[Dict[str, Any]] = []
        risks: List[Dict[str, Any]] = []
        recommendations: List[Dict[str, Any]] = []

        # 1. Evaluate Findings from Diagnostics & Concentration
        val_conc = diagnostics.get("value_concentration", {})
        top_20_share = val_conc.get("top_20_percent_value_share", 0.0)
        
        if top_20_share >= 70.0:
            severity = calculate_finding_severity(impact_score=80.0, affected_share_pct=top_20_share)
            findings.append({
                "id": str(uuid.uuid4()),
                "title": "Severe Portfolio Value Concentration",
                "description": f"Top 20% of strategic initiatives generate {top_20_share:.1f}% of total portfolio value.",
                "severity": severity,
                "impact_score": 80.0,
                "evidence": {
                    "top_20_percent_value_share": top_20_share,
                    "herfindahl_index": val_conc.get("herfindahl_index", 0.0),
                },
                "affected_initiative_ids": [
                    i["initiative_id"] for i in diagnostics.get("high_value_initiatives", [])[:5]
                ],
            })

        dep_conc = diagnostics.get("dependency_concentration", {})
        single_points = dep_conc.get("single_point_of_failure_count", 0)
        if single_points > 0:
            severity = calculate_finding_severity(impact_score=85.0, affected_share_pct=min(100.0, single_points * 20.0))
            findings.append({
                "id": str(uuid.uuid4()),
                "title": "Critical Single Points of Failure Detected",
                "description": f"{single_points} strategic initiative(s) serve as critical bottlenecks with >= 3 downstream dependents.",
                "severity": severity,
                "impact_score": 85.0,
                "evidence": {
                    "single_point_of_failure_count": single_points,
                    "max_dependent_initiatives": dep_conc.get("max_dependent_initiatives", 0),
                },
                "affected_initiative_ids": [],
            })

        underperforming = diagnostics.get("underperforming_initiatives", [])
        if underperforming:
            severity = calculate_finding_severity(impact_score=70.0, affected_share_pct=(len(underperforming) / max(1, len(initiatives))) * 100.0)
            findings.append({
                "id": str(uuid.uuid4()),
                "title": "Delivery Underperformance in Strategic Portfolio",
                "description": f"{len(underperforming)} initiative(s) are exhibiting degraded execution health (< 60) or delayed outcome realization.",
                "severity": severity,
                "impact_score": 70.0,
                "evidence": {
                    "underperforming_count": len(underperforming),
                    "initiatives": [u.get("title") for u in underperforming[:3]],
                },
                "affected_initiative_ids": [u["initiative_id"] for u in underperforming],
            })

        gov_bottlenecks = diagnostics.get("governance_bottlenecks", [])
        if gov_bottlenecks:
            severity = calculate_finding_severity(impact_score=60.0, affected_share_pct=(len(gov_bottlenecks) / max(1, len(initiatives))) * 100.0)
            findings.append({
                "id": str(uuid.uuid4()),
                "title": "Governance Checkpoint Bottlenecks",
                "description": f"{len(gov_bottlenecks)} initiative(s) have overdue reviews or unresolved high-risk governance actions.",
                "severity": severity,
                "impact_score": 60.0,
                "evidence": {
                    "bottlenecks_count": len(gov_bottlenecks),
                },
                "affected_initiative_ids": [g["initiative_id"] for g in gov_bottlenecks],
            })

        # 2. Opportunities (High ROI, Acceleration candidates)
        high_roi = diagnostics.get("high_roi_initiatives", [])
        if high_roi:
            opportunities.append({
                "id": str(uuid.uuid4()),
                "title": "Accelerate High-Yield Strategic Initiatives",
                "description": f"{len(high_roi)} initiative(s) demonstrate high capital efficiency and outsized ROI realization.",
                "potential_value_gain": "High Capital ROI Acceleration",
                "action_type": "RESOURCE_ALLOCATION",
                "initiative_ids": [h["initiative_id"] for h in high_roi],
            })

        # 3. Top Risks
        high_risk_low_val = diagnostics.get("high_risk_low_value_initiatives", [])
        if high_risk_low_val:
            risks.append({
                "id": str(uuid.uuid4()),
                "title": "Disproportionate Risk Exposure on Low-Yield Initiatives",
                "description": f"{len(high_risk_low_val)} initiative(s) carry severe delivery risk with limited strategic yield.",
                "risk_level": "HIGH",
                "exposure_amount": sum(float(i.get("actual_cost", 0.0)) for i in high_risk_low_val),
                "affected_initiatives_count": len(high_risk_low_val),
                "initiative_ids": [r["initiative_id"] for r in high_risk_low_val],
            })

        if total_value_at_risk > 0:
            risks.append({
                "id": str(uuid.uuid4()),
                "title": "Portfolio Benefit Realization Gap at Risk",
                "description": f"${total_value_at_risk:,.2f} in expected strategic benefits remains unconfirmed or delayed.",
                "risk_level": "CRITICAL" if total_value_at_risk > 500000 else "MEDIUM",
                "exposure_amount": total_value_at_risk,
                "affected_initiatives_count": len(diagnostics.get("critical_outcome_exposures", [])),
                "initiative_ids": [o["initiative_id"] for o in diagnostics.get("critical_outcome_exposures", [])],
            })

        # 4. Deterministic Executive Recommendations
        if single_points > 0:
            recommendations.append({
                "id": str(uuid.uuid4()),
                "priority": StrategicPriority.ESCALATE,
                "title": "Decouple Critical Path Dependencies",
                "rationale": "Single point of failure initiatives pose severe systemic delay risks across dependent initiatives.",
                "action_items": [
                    "Conduct architectural dependency review",
                    "Establish dedicated buffer milestones for upstream blockers",
                    "Assign executive sponsor to bottleneck initiatives",
                ],
                "target_entity_type": "PORTFOLIO",
                "target_entity_id": None,
            })

        if len(underperforming) > 0:
            recommendations.append({
                "id": str(uuid.uuid4()),
                "priority": StrategicPriority.RESTRUCTURE,
                "title": "Initiate Remediation for Underperforming Initiatives",
                "rationale": "Delivery degradation requires immediate operational stabilization or scope recalibration.",
                "action_items": [
                    "Audit resource constraints on delayed milestones",
                    "Execute mid-stage governance checkpoint",
                    "Re-align outcome targets to achievable baseline",
                ],
                "target_entity_type": "INITIATIVE",
                "target_entity_id": underperforming[0]["initiative_id"] if underperforming else None,
            })

        if len(high_roi) > 0:
            recommendations.append({
                "id": str(uuid.uuid4()),
                "priority": StrategicPriority.ACCELERATE,
                "title": "Fast-Track Capital Delivery for High-ROI Drivers",
                "rationale": "High-performing initiatives should receive priority funding and resourcing to capture early market value.",
                "action_items": [
                    "Authorize secondary phase resource allocations",
                    "Remove non-critical approval gates for on-track deliverables",
                ],
                "target_entity_type": "PORTFOLIO",
                "target_entity_id": None,
            })

        return {
            "executive_attention_level": attention_level,
            "top_findings": findings,
            "top_opportunities": opportunities,
            "top_risks": risks,
            "recommendations": recommendations,
            "data_quality_warnings": warnings,
            "calculated_at": now,
        }

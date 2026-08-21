"""Business Health Score Engine calculating deterministic 0-100 enterprise health index."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from app.core.constants import BusinessHealthStatus, RecommendationPriority
from app.intelligence.constants import (
    CATASTROPHIC_EXTRA_PENALTY,
    FINDING_SEVERITY_PENALTIES,
    MAX_FINDING_PENALTY,
    MAX_RCA_PENALTY,
    MAX_RECOMMENDATION_RECOVERY_BONUS,
    RCA_HIGH_IMPACT_PENALTY,
    RCA_HIGH_IMPACT_THRESHOLD,
    RCA_MODERATE_IMPACT_PENALTY,
    RCA_MODERATE_IMPACT_THRESHOLD,
    RECOMMENDATION_RECOVERY_BONUS_PER_ITEM,
    SYSTEMIC_FAILURE_PENALTY,
    SYSTEMIC_FAILURE_THRESHOLD,
    health_score_to_status,
)

if TYPE_CHECKING:
    from app.models.diagnostic_finding import DiagnosticFinding
    from app.models.recommendation import Recommendation
    from app.models.root_cause_analysis import RootCauseAnalysis


class BusinessHealthScoreEngine:
    """
    Computes a deterministic 0-100 Business Health Score and categorical status.
    
    Evaluates:
        1. Diagnostic Finding Severities (CRITICAL -18, HIGH -10, MEDIUM -5, LOW -2).
        2. Catastrophic Finding Modifiers (+6 penalty for severe metric breaches).
        3. Multiple Critical Failure Multiplier (-10 systemic failure penalty for >= 3 critical findings).
        4. Root Cause Impact Magnitudes (High impact -8, Moderate impact -4).
        5. Actionable Recommendation Quick-Wins (+2 bonus per high-impact/low-effort mitigation).
    
    Score Mapping:
        - 90–100: EXCELLENT
        - 75–89:  HEALTHY
        - 60–74:  WATCH_LIST
        - 40–59:  AT_RISK
        - 0–39:   CRITICAL
    """

    @classmethod
    def calculate(
        cls,
        findings: Optional[List[DiagnosticFinding]] = None,
        root_causes: Optional[List[RootCauseAnalysis]] = None,
        recommendations: Optional[List[Recommendation]] = None,
    ) -> Tuple[int, BusinessHealthStatus]:
        """Calculates the composite health score bounded in [0, 100]."""
        score, status, _ = cls.calculate_with_explanation(findings, root_causes, recommendations)
        return score, status

    @classmethod
    def calculate_with_explanation(
        cls,
        findings: Optional[List[DiagnosticFinding]] = None,
        root_causes: Optional[List[RootCauseAnalysis]] = None,
        recommendations: Optional[List[Recommendation]] = None,
    ) -> Tuple[int, BusinessHealthStatus, Dict[str, Any]]:
        """
        Calculates the composite health score bounded in [0, 100] and returns full explainability breakdown.
        """
        finding_list = findings or []
        rca_list = root_causes or []
        rec_list = recommendations or []

        # 1. Base Score
        base_score = 100

        # 2. Finding Severity Deductions & Catastrophic Modifiers
        raw_finding_penalty = 0
        critical_count = 0
        high_count = 0
        medium_count = 0
        low_count = 0
        catastrophic_count = 0

        for f in finding_list:
            sev_str = (f.severity.value if hasattr(f.severity, "value") else str(f.severity)).upper()
            base_pen = FINDING_SEVERITY_PENALTIES.get(sev_str, 5)

            if sev_str == "CRITICAL":
                critical_count += 1
            elif sev_str == "HIGH":
                high_count += 1
            elif sev_str == "MEDIUM":
                medium_count += 1
            elif sev_str == "LOW":
                low_count += 1

            # Check catastrophic flags and escalation multipliers
            supp_data = f.supporting_data if isinstance(f.supporting_data, dict) else {}
            extra_ctx = supp_data.get("extra_context") if isinstance(supp_data.get("extra_context"), dict) else {}

            is_catastrophic = bool(
                supp_data.get("catastrophic_flag")
                or extra_ctx.get("catastrophic_flag")
                or getattr(f, "catastrophic_flag", False)
            )
            escalation_mult = float(
                extra_ctx.get("escalation_multiplier")
                or supp_data.get("escalation_multiplier")
                or 1.0
            )

            pen = base_pen
            if is_catastrophic:
                pen += CATASTROPHIC_EXTRA_PENALTY
                catastrophic_count += 1
            if escalation_mult > 1.0:
                pen = int(round(pen * escalation_mult))

            raw_finding_penalty += pen

        finding_deduction = min(MAX_FINDING_PENALTY, raw_finding_penalty)

        # 3. Multiple Critical Failure Multiplier (Systemic Failure Penalty)
        systemic_failure_penalty = 0
        if critical_count >= SYSTEMIC_FAILURE_THRESHOLD:
            systemic_failure_penalty = SYSTEMIC_FAILURE_PENALTY

        # 4. Root Cause Impact Deductions
        raw_rca_penalty = 0
        for rca in rca_list:
            impact = getattr(rca, "impact_score", 0.50)
            if impact >= RCA_HIGH_IMPACT_THRESHOLD:
                raw_rca_penalty += RCA_HIGH_IMPACT_PENALTY
            elif impact >= RCA_MODERATE_IMPACT_THRESHOLD:
                raw_rca_penalty += RCA_MODERATE_IMPACT_PENALTY

        rca_deduction = min(MAX_RCA_PENALTY, raw_rca_penalty)

        # 5. Actionable Mitigation Recovery Bonus
        raw_bonus = 0
        for r in rec_list:
            is_critical = (
                r.priority == RecommendationPriority.CRITICAL
                if hasattr(r, "priority")
                else False
            )
            is_quick_win = (
                getattr(r, "estimated_impact_score", 0.0) >= 0.80
                and getattr(r, "estimated_effort_score", 1.0) <= 0.50
            )
            if is_critical or is_quick_win:
                raw_bonus += RECOMMENDATION_RECOVERY_BONUS_PER_ITEM

        recovery_bonus = min(MAX_RECOMMENDATION_RECOVERY_BONUS, raw_bonus)

        # 6. Composite Final Score
        total_deductions = finding_deduction + systemic_failure_penalty + rca_deduction
        final_score = int(round(max(0, min(100, base_score - total_deductions + recovery_bonus))))
        status = health_score_to_status(final_score)

        explanation = {
            "base_score": base_score,
            "critical_findings": critical_count,
            "high_findings": high_count,
            "medium_findings": medium_count,
            "low_findings": low_count,
            "catastrophic_modifiers": catastrophic_count,
            "systemic_failure_penalty": systemic_failure_penalty,
            "finding_deduction": finding_deduction,
            "rca_deduction": rca_deduction,
            "recovery_bonus": recovery_bonus,
            "final_score": final_score,
        }

        return final_score, status, explanation

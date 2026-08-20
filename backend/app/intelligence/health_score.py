"""Business Health Score Engine calculating deterministic 0-100 enterprise health index."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Tuple

from app.core.constants import BusinessHealthStatus, RecommendationPriority
from app.intelligence.constants import (
    FINDING_SEVERITY_PENALTIES,
    MAX_FINDING_PENALTY,
    MAX_RCA_PENALTY,
    MAX_RECOMMENDATION_RECOVERY_BONUS,
    RCA_HIGH_IMPACT_PENALTY,
    RCA_HIGH_IMPACT_THRESHOLD,
    RCA_MODERATE_IMPACT_PENALTY,
    RCA_MODERATE_IMPACT_THRESHOLD,
    RECOMMENDATION_RECOVERY_BONUS_PER_ITEM,
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
        2. Root Cause Impact Magnitudes (High impact -8, Moderate impact -4).
        3. Actionable Recommendation Quick-Wins (+2 bonus per high-impact/low-effort mitigation).
    
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
        """
        Calculates the composite health score bounded in [0, 100].
        """
        finding_list = findings or []
        rca_list = root_causes or []
        rec_list = recommendations or []

        # 1. Base Score
        score = 100

        # 2. Finding Severity Deductions
        raw_finding_penalty = 0
        for f in finding_list:
            sev_str = f.severity.value if hasattr(f.severity, "value") else str(f.severity)
            penalty = FINDING_SEVERITY_PENALTIES.get(sev_str.upper(), 5)
            raw_finding_penalty += penalty

        finding_deduction = min(MAX_FINDING_PENALTY, raw_finding_penalty)

        # 3. Root Cause Impact Deductions
        raw_rca_penalty = 0
        for rca in rca_list:
            impact = getattr(rca, "impact_score", 0.50)
            if impact >= RCA_HIGH_IMPACT_THRESHOLD:
                raw_rca_penalty += RCA_HIGH_IMPACT_PENALTY
            elif impact >= RCA_MODERATE_IMPACT_THRESHOLD:
                raw_rca_penalty += RCA_MODERATE_IMPACT_PENALTY

        rca_deduction = min(MAX_RCA_PENALTY, raw_rca_penalty)

        # 4. Actionable Mitigation Recovery Bonus
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

        # 5. Composite Final Score
        final_score = int(round(max(0, min(100, score - finding_deduction - rca_deduction + recovery_bonus))))
        status = health_score_to_status(final_score)

        return final_score, status
